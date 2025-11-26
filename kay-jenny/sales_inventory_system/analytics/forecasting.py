"""
Sales Forecasting using Holt-Winters Exponential Smoothing (ETS)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sales_inventory_system.orders.models import Payment
from decimal import Decimal


def prepare_sales_data(days=30):
    """
    Prepare historical sales data for forecasting

    Args:
        days: Number of days of historical data to use

    Returns:
        pandas.Series: Time series of daily revenue
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    # Get daily revenue data - optimized to single database query
    # Instead of querying per date, use TruncDate to group all in one query
    daily_data = Payment.objects.filter(
        status='SUCCESS',
        created_at__date__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('amount')
    ).order_by('date')

    # Create lookup dictionary for fast access
    data_dict = {
        item['date']: float(item['total'] or 0)
        for item in daily_data
    }

    # Build sales data, filling in zeros for days with no sales
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    sales_data = []

    for date in date_range:
        daily_revenue = data_dict.get(date.date(), 0.0)
        sales_data.append(daily_revenue)

    # Create time series
    ts = pd.Series(sales_data, index=date_range)

    return ts


def forecast_sales_holt_winters(historical_data, forecast_periods=7, seasonal_periods=7):
    """
    Forecast sales using Holt-Winters Exponential Smoothing

    Args:
        historical_data: pandas.Series of historical sales data
        forecast_periods: Number of periods to forecast
        seasonal_periods: Length of seasonal cycle (7 for weekly seasonality)

    Returns:
        dict: Contains forecast values, confidence intervals, and model info
    """
    try:
        # Ensure we have enough data for seasonal model
        if len(historical_data) < seasonal_periods * 2:
            # Use simple exponential smoothing if not enough data
            model = ExponentialSmoothing(
                historical_data,
                trend='add',
                seasonal=None
            )
        else:
            # Use full Holt-Winters with trend and seasonality
            model = ExponentialSmoothing(
                historical_data,
                trend='add',
                seasonal='add',
                seasonal_periods=seasonal_periods
            )

        # Fit the model
        fitted_model = model.fit()

        # Generate forecast
        forecast = fitted_model.forecast(steps=forecast_periods)

        # Calculate fitted values (for plotting historical fit)
        fitted_values = fitted_model.fittedvalues

        # Calculate prediction intervals (95% confidence)
        # Simple approximation using residual standard error
        residuals = historical_data - fitted_values
        std_error = np.std(residuals)

        # Confidence intervals widen as we go further into future
        forecast_dates = pd.date_range(
            start=historical_data.index[-1] + timedelta(days=1),
            periods=forecast_periods,
            freq='D'
        )

        confidence_intervals = []
        for i in range(forecast_periods):
            # Widening interval factor (increases with time)
            width_factor = 1 + (i * 0.1)
            lower = forecast.iloc[i] - (1.96 * std_error * width_factor)
            upper = forecast.iloc[i] + (1.96 * std_error * width_factor)

            confidence_intervals.append({
                'date': forecast_dates[i].strftime('%Y-%m-%d'),
                'lower': max(0, float(lower)),  # Revenue can't be negative
                'upper': float(upper)
            })

        # Prepare forecast data
        forecast_data = []
        for i, value in enumerate(forecast):
            forecast_data.append({
                'date': forecast_dates[i].strftime('%Y-%m-%d'),
                'value': float(value),
                'day_name': forecast_dates[i].strftime('%A')
            })

        # Prepare historical data for return
        historical_list = []
        for date, value in historical_data.items():
            historical_list.append({
                'date': date.strftime('%Y-%m-%d'),
                'value': float(value),
                'day_name': date.strftime('%A')
            })

        # Model statistics
        mse = float(np.mean(residuals**2))
        stats = {
            'aic': float(fitted_model.aic),
            'bic': float(fitted_model.bic),
            'mse': mse,
            'mae': float(np.mean(np.abs(residuals))),
            'rmse': float(np.sqrt(mse))
        }

        return {
            'success': True,
            'forecast': forecast_data,
            'historical': historical_list,
            'confidence_intervals': confidence_intervals,
            'statistics': stats,
            'model_type': 'Holt-Winters Exponential Smoothing',
            'seasonal_periods': seasonal_periods
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Unable to generate forecast. This may be due to insufficient data.'
        }


def forecast_sales(days_back=30, days_ahead=7):
    """
    Main function to generate sales forecast

    Args:
        days_back: Number of historical days to use
        days_ahead: Number of days to forecast

    Returns:
        dict: Forecast results
    """
    # Prepare data
    historical_data = prepare_sales_data(days=days_back)

    # Check if we have any data
    if historical_data.sum() == 0:
        return {
            'success': False,
            'error': 'No historical sales data available',
            'message': 'Please ensure there are completed orders in the system.'
        }

    # Generate forecast
    forecast_result = forecast_sales_holt_winters(
        historical_data,
        forecast_periods=days_ahead,
        seasonal_periods=7  # Weekly seasonality
    )

    if forecast_result['success']:
        # Add summary statistics
        forecast_values = [f['value'] for f in forecast_result['forecast']]
        historical_values = [h['value'] for h in forecast_result['historical']]

        forecast_result['summary'] = {
            'historical_avg': float(np.mean(historical_values)),
            'historical_total': float(np.sum(historical_values)),
            'forecast_avg': float(np.mean(forecast_values)),
            'forecast_total': float(np.sum(forecast_values)),
            'forecast_min': float(np.min(forecast_values)),
            'forecast_max': float(np.max(forecast_values))
        }

    return forecast_result
