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
        status='COMPLETED',
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
        # Validate input data
        if len(historical_data) == 0:
            raise ValueError("Historical data is empty")

        # Remove any NaN or infinite values
        historical_data = historical_data.dropna()
        historical_data = historical_data[np.isfinite(historical_data)]

        if len(historical_data) < 3:
            raise ValueError("Insufficient historical data for forecasting")

        # Determine best seasonal periods based on data length
        # Need at least 2 complete seasons for seasonal decomposition
        min_data_required = seasonal_periods * 2

        if len(historical_data) < min_data_required:
            # Not enough data for seasonal model, use trend-only model
            model = ExponentialSmoothing(
                historical_data,
                trend='add',
                seasonal=None,
                initialization_method='estimated'
            )
        else:
            # Use full Holt-Winters with trend and seasonality
            try:
                # Try multiplicative seasonal first (better for varied magnitude data)
                model = ExponentialSmoothing(
                    historical_data,
                    trend='add',
                    seasonal='mul',
                    seasonal_periods=seasonal_periods,
                    initialization_method='estimated'
                )
            except Exception:
                try:
                    # Fall back to additive if multiplicative fails
                    model = ExponentialSmoothing(
                        historical_data,
                        trend='add',
                        seasonal='add',
                        seasonal_periods=seasonal_periods,
                        initialization_method='estimated'
                    )
                except Exception:
                    # Final fallback: trend-only model
                    model = ExponentialSmoothing(
                        historical_data,
                        trend='add',
                        seasonal=None,
                        initialization_method='estimated'
                    )

        # Fit the model with optimized parameters
        fitted_model = model.fit(optimized=True)

        # Generate forecast
        try:
            forecast = fitted_model.forecast(steps=forecast_periods)
        except Exception as e:
            raise ValueError(f"Forecast generation failed: {str(e)}")

        # Calculate fitted values (for plotting historical fit)
        fitted_values = fitted_model.fittedvalues

        # Calculate prediction intervals (95% confidence)
        # Use residual standard error for better confidence intervals
        residuals = historical_data.iloc[len(historical_data) - len(fitted_values):].values - fitted_values.values

        # Handle edge cases in residuals
        residuals = residuals[np.isfinite(residuals)]
        if len(residuals) > 0:
            std_error = np.std(residuals)
        else:
            std_error = np.mean(historical_data) * 0.1  # Use 10% of mean as fallback

        # Ensure std_error is not zero or negative
        if std_error <= 0:
            std_error = np.mean(historical_data) * 0.1 if np.mean(historical_data) > 0 else 1.0

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
        if len(residuals) > 0:
            mse = float(np.mean(residuals**2))
            mae = float(np.mean(np.abs(residuals)))
            rmse = float(np.sqrt(mse))
        else:
            mse = 0.0
            mae = 0.0
            rmse = 0.0

        try:
            aic = float(fitted_model.aic)
            bic = float(fitted_model.bic)
        except Exception:
            aic = 0.0
            bic = 0.0

        stats = {
            'aic': aic,
            'bic': bic,
            'mse': mse,
            'mae': mae,
            'rmse': rmse
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

        # Prepare split confidence intervals for JavaScript chart (alternative format)
        forecast_result['confidence_intervals_lower'] = [
            {'date': ci['date'], 'value': ci['lower']}
            for ci in forecast_result['confidence_intervals']
        ]
        forecast_result['confidence_intervals_upper'] = [
            {'date': ci['date'], 'value': ci['upper']}
            for ci in forecast_result['confidence_intervals']
        ]

    return forecast_result


def forecast_ingredient_stock(days_ahead=7):
    """
    Forecast ingredient stock levels and predict low stock situations

    Algorithm:
    1. Get all active ingredients
    2. Calculate daily usage rate from StockTransaction DEDUCTION history (30 days)
    3. Project current stock forward based on usage rate
    4. Identify when stock will fall below min_stock threshold

    Returns:
        dict: Ingredient forecasts with low stock warnings
    """
    from sales_inventory_system.products.models import Ingredient, StockTransaction
    from django.utils import timezone
    from datetime import timedelta

    try:
        ingredients = Ingredient.objects.filter(is_active=True)
        start_date = timezone.now() - timedelta(days=30)

        forecasts = []
        low_stock_warnings = []

        for ingredient in ingredients:
            # Get DEDUCTION transactions in last 30 days
            deductions = StockTransaction.objects.filter(
                ingredient=ingredient,
                transaction_type='DEDUCTION',
                created_at__gte=start_date
            ).values_list('quantity', 'created_at')

            if not deductions:
                daily_usage_rate = 0
            else:
                total_deducted = sum(abs(float(qty)) for qty, _ in deductions)
                dates = [created_at.date() for _, created_at in deductions]
                if dates:
                    days_span = (max(dates) - min(dates)).days + 1
                    days_span = max(days_span, 1)
                else:
                    days_span = 30

                daily_usage_rate = total_deducted / days_span

            current_stock = float(ingredient.current_stock)
            min_stock = float(ingredient.min_stock)

            # Project stock levels
            projected_stock = []
            days_until_low_stock = None
            days_until_depleted = None

            for day in range(days_ahead + 1):
                projected = current_stock - (daily_usage_rate * day)
                projected_stock.append({
                    'day': day,
                    'stock': max(0, projected),
                    'below_minimum': projected < min_stock,
                    'depleted': projected <= 0
                })

                if days_until_low_stock is None and projected < min_stock:
                    days_until_low_stock = day

                if days_until_depleted is None and projected <= 0:
                    days_until_depleted = day

            # Determine status
            if days_until_depleted is not None and days_until_depleted <= days_ahead:
                status = 'critical'
                message = f'Will be depleted in {days_until_depleted} days'
                low_stock_warnings.append({
                    'ingredient': ingredient,
                    'days_until_critical': days_until_depleted,
                    'severity': 'critical',
                    'message': message
                })
            elif days_until_low_stock is not None and days_until_low_stock <= days_ahead:
                status = 'warning'
                message = f'Will fall below minimum in {days_until_low_stock} days'
                low_stock_warnings.append({
                    'ingredient': ingredient,
                    'days_until_critical': days_until_low_stock,
                    'severity': 'warning',
                    'message': message
                })
            elif current_stock < min_stock:
                status = 'low'
                message = 'Already below minimum stock level'
            else:
                status = 'ok'
                message = 'Stock levels healthy'

            forecasts.append({
                'ingredient': ingredient,
                'current_stock': current_stock,
                'min_stock': min_stock,
                'daily_usage_rate': round(daily_usage_rate, 2),
                'projected_stock': projected_stock,
                'status': status,
                'message': message,
                'days_until_low_stock': days_until_low_stock,
                'days_until_depleted': days_until_depleted,
            })

        low_stock_warnings.sort(key=lambda x: x['days_until_critical'])

        return {
            'success': True,
            'forecasts': forecasts,
            'low_stock_warnings': low_stock_warnings[:10],
            'total_ingredients': len(forecasts),
            'critical_count': sum(1 for f in forecasts if f['status'] == 'critical'),
            'warning_count': sum(1 for f in forecasts if f['status'] == 'warning'),
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Unable to generate ingredient forecast'
        }
