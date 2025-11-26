# FJC PIZZA - FEATURES & FUNCTIONALITY GUIDE

## DOCUMENT CONTROL

- **System Name**: FJC Pizza Sales & Inventory Management System
- **Version**: 1.0
- **Document Type**: Feature Documentation
- **Target Audience**: End Users, Developers, Product Managers

---

## TABLE OF CONTENTS

1. [Feature Overview](#feature-overview)
2. [Authentication & User Management](#authentication--user-management)
3. [Product & Inventory Management](#product--inventory-management)
4. [Order Management & Processing](#order-management--processing)
5. [Payment Processing](#payment-processing)
6. [Analytics & Reporting](#analytics--reporting)
7. [Audit Trail & Compliance](#audit-trail--compliance)
8. [System Features](#system-features)

---

## FEATURE OVERVIEW

### Feature Matrix

| Feature Category | Feature Name | Customer | Cashier | Admin |
|------------------|--------------|----------|---------|-------|
| **Authentication** | User Login | - | ✅ | ✅ |
| | User Registration | - | - | ✅ |
| | Session Management | - | ✅ | ✅ |
| | Password Reset | - | ✅ | ✅ |
| **Products** | Browse Products | ✅ | ✅ | ✅ |
| | Search Products | ✅ | ✅ | ✅ |
| | View Product Details | ✅ | ✅ | ✅ |
| | Create Product | - | - | ✅ |
| | Edit Product | - | - | ✅ |
| | Archive Product | - | - | ✅ |
| | Manage Stock | - | View | ✅ |
| | Set Low-Stock Alert | - | - | ✅ |
| **Orders** | Create Order (Kiosk) | ✅ | ✅ | ✅ |
| | View Order Details | ✅ | ✅ | ✅ |
| | Update Order Status | - | ✅ | ✅ |
| | Track Order Status | ✅ | - | - |
| | View Order History | ✅ | ✅ | ✅ |
| | Cancel Order | - | ✅ | ✅ |
| **Payments** | Select Payment Method | ✅ | - | - |
| | Process Payment | - | ✅ | ✅ |
| | View Payment Status | ✅ | ✅ | ✅ |
| | Handle Payment Failure | - | ✅ | ✅ |
| **Analytics** | Sales Dashboard | - | Limited | ✅ |
| | Product Performance | - | - | ✅ |
| | Cashier Metrics | - | Own only | ✅ |
| | Revenue Reports | - | - | ✅ |
| | Sales Forecast | - | - | ✅ |
| **System** | Audit Trail | - | - | ✅ |
| | Archive Management | - | - | ✅ |
| | User Management | - | - | ✅ |
| | System Settings | - | - | ✅ |

---

## AUTHENTICATION & USER MANAGEMENT

### Feature 1: User Login

**Purpose**: Authenticate users and provide role-based access

**Who Uses It**: Cashiers, Administrators

**Access**: `/accounts/login/`

#### How It Works
```
User enters username and password
    ↓
System validates against database
    ↓
If correct:
  ├─ Session created
  ├─ User redirected to dashboard
  └─ Role determines which dashboard:
     ├─ ADMIN → Admin Dashboard
     └─ CASHIER → POS Dashboard

If incorrect:
  └─ Error message shown
  └─ Prompt to try again
```

#### Security Features
- Password hashed with PBKDF2 (one-way encryption)
- Session timeout (auto-logout after 2 hours)
- Secure session cookies
- CSRF protection on login form
- IP logging for security audits

#### Key Information
- **Session Duration**: 2 hours (can be extended)
- **Failed Login Attempts**: No automatic lockout (future enhancement)
- **Session Storage**: Database-backed (not memory)
- **Password Requirements**: (Django default, no complexity requirements)

---

### Feature 2: User Account Management

**Purpose**: Create, edit, and manage user accounts

**Who Uses It**: Administrators only

**Access**: `/accounts/users/` (list), `/accounts/users/create/` (add), `/accounts/users/<id>/edit/` (edit)

#### Create User
```
Admin clicks "Create User"
    ↓
Form appears with fields:
├─ Username (unique, required)
├─ Email (optional)
├─ Password (auto-generated or custom)
├─ First/Last Name
├─ Phone Number
└─ Role (ADMIN or CASHIER)
    ↓
Admin fills form
    ↓
System validates:
├─ Username not already in use
├─ Email valid (if provided)
└─ Required fields filled
    ↓
User created
├─ Password hashed
├─ AuditTrail logged: WHO created, WHEN
└─ User receives credentials
```

#### Edit User
```
Admin selects user to edit
    ↓
Current information displayed:
├─ Name
├─ Email
├─ Phone
├─ Role
└─ Status (Active/Archived)
    ↓
Admin modifies fields
    ↓
System updates record:
├─ AuditTrail logged with before/after snapshot
├─ Email sent if role changed
└─ Session invalidated if changing own password
```

#### Archive User (Soft Delete)
```
Admin clicks "Archive" on user
    ↓
Confirmation dialog shown:
└─ "Archiving this user will prevent them from logging in"
    ↓
Admin confirms
    ↓
System marks is_archived = True
├─ User cannot login anymore
├─ Historical data preserved
├─ AuditTrail logged
└─ User can be restored if needed
```

---

### Feature 3: Session Management

**Purpose**: Keep users logged in while working, with automatic timeout

**Details**:
- **Session Duration**: 2 hours (configurable)
- **Auto-Logout**: Yes, after inactivity period
- **"Remember Me"**: Not available (for security)
- **Logout**: Manual logout available on all pages
- **Session Persistence**: Across page refreshes
- **Multiple Sessions**: One per browser window (typical behavior)

#### How to Logout
```
Click "Logout" button (top right of any page)
    ↓
System:
├─ Clears session data
├─ Invalidates session token
├─ Deletes session from database
└─ Redirects to login page
```

---

### Feature 4: Password Management

**Purpose**: Secure password storage and recovery

**Features**:
- **Password Hashing**: PBKDF2 with 600,000 iterations
- **Reset Functionality**: Email-based password reset (admin initiates)
- **Reset Token**: Time-limited (1 hour expiration)
- **Password Change**: User can change password on profile page
- **Password Requirements**: No specific complexity rules (Django default)

#### Password Reset Process (Admin)
```
Admin finds user who forgot password
    ↓
Admin clicks "Reset Password" on user detail
    ↓
System generates:
├─ Unique reset token
├─ Expiration time (1 hour)
└─ Reset link
    ↓
Admin shares reset link with user
    ↓
User clicks link
    ↓
User enters new password
    ↓
System:
├─ Validates token (not expired, valid user)
├─ Hashes new password
├─ Updates record
└─ Invalidates token
```

---

## PRODUCT & INVENTORY MANAGEMENT

### Feature 1: Product Catalog Management

**Purpose**: Maintain menu/product list with full CRUD operations

**Who Uses It**: Administrators (manage), All users (view)

**Access**: `/products/` (list), `/products/create/` (add), `/products/<id>/edit/` (edit)

#### View Products
```
Admin goes to /products/
    ↓
System displays all products:
├─ Grid or list view
├─ Showing: Name, Price, Stock, Category, Status
├─ Pagination: 12 products per page
└─ Sorting/Filtering options
```

#### Create Product
```
Admin clicks "Create Product"
    ↓
Form with fields:
├─ Product Name (required, unique)
├─ Description (optional)
├─ Category (PIZZA, SIDES, DRINKS, DESSERTS)
├─ Price (decimal, required)
├─ Initial Stock (integer, required)
├─ Reorder Threshold (quantity that triggers alert)
└─ Product Image (optional, JPG/PNG)
    ↓
Admin submits form
    ↓
System validates:
├─ Name not duplicate
├─ Price > 0
├─ Stock >= 0
└─ Image format valid
    ↓
Product created:
├─ Assigned unique ID
├─ Default status: ACTIVE
├─ AuditTrail logged
└─ Immediately visible in kiosk
```

#### Edit Product
```
Admin clicks "Edit" on product
    ↓
Current details displayed
    ↓
Admin modifies fields (any of: name, description, price, stock, threshold, image)
    ↓
System updates:
├─ Validates changes
├─ Updates database
├─ Logs AuditTrail with before/after snapshot
├─ Updates kiosk in real-time
└─ If stock=0: Auto-hides from kiosk
```

#### Archive Product (Soft Delete)
```
Admin clicks "Archive" on product
    ↓
Confirmation dialog:
└─ "Archiving will remove from menu and hide from kiosk"
    ↓
Admin confirms
    ↓
System:
├─ Marks is_archived = True
├─ Product disappears from kiosk immediately
├─ Historical data preserved (orders referencing it still valid)
├─ AuditTrail logged
└─ Can be restored if needed
```

---

### Feature 2: Stock Management

**Purpose**: Track inventory levels and manage stock

**Who Uses It**: Administrators (manage), Cashiers (view), System (auto-deduct)

#### View Stock Levels
```
Admin dashboard shows:
├─ All products with current stock
├─ Stock status indicators:
│  ├─ Green: Healthy (stock > threshold)
│  ├─ Yellow: Low (stock < threshold)
│  └─ Red: Out (stock = 0)
└─ Quick filters: Show only low/out of stock
```

#### Manual Stock Adjustment
```
Admin clicks product to edit
    ↓
Finds "Stock" field (shows current level)
    ↓
Admin enters new stock number
    ↓
System records:
├─ Old quantity
├─ New quantity
├─ Change amount
├─ Timestamp
└─ Reason (e.g., "Received delivery", "Correction")
    ↓
Updates database
    ↓
AuditTrail logged:
├─ WHO adjusted
├─ WHEN (timestamp)
├─ FROM/TO amounts
└─ Full snapshot for audit
    ↓
Kiosk updated in real-time:
├─ If stock=0: Hide product
├─ If stock>0: Update displayed amount
└─ If stock<threshold: Alert admin
```

#### Automatic Stock Deduction
```
Trigger: Payment marked SUCCESS (by cashier or system)
    ↓
System automatically:
├─ Fetches Order and all OrderItems
├─ For each OrderItem:
│  ├─ Gets Product
│  ├─ Reduces stock by OrderItem.quantity
│  └─ Saves Product
└─ No manual intervention needed
    ↓
AuditTrail logged automatically:
├─ User: Cashier or System
├─ Action: UPDATE
├─ Before/after stock levels
└─ Timestamp: Exact moment of deduction
    ↓
Kiosk updated in real-time:
├─ If stock drops below threshold: Alert shown
├─ If stock drops to 0: Product hidden
└─ Customers see accurate availability
```

---

### Feature 3: Low-Stock Alerts

**Purpose**: Notify admin when stock falls below reorder level

**How It Works**:
```
Product configuration:
├─ Name: Pepperoni Pizza
├─ Current Stock: 15 units
└─ Reorder Threshold: 5 units

When stock drops to <= threshold:
├─ Admin dashboard shows yellow alert
├─ Alert includes: Product name, current stock, threshold
└─ Click alert → Edit product page

Admin actions:
├─ Order more stock from supplier
├─ Update stock level once received
└─ Alert automatically clears once stock > threshold

When stock reaches 0:
├─ Red alert shown on dashboard
├─ Product automatically hidden from kiosk
├─ Customers cannot order it
└─ Alert remains until stock > 0
```

**Alert Display**:
```
Dashboard Alert Box:
┌─────────────────────────────────────┐
│ LOW STOCK ALERTS                    │
├─────────────────────────────────────┤
│ ⚠️ Pepperoni Pizza: 2 units left   │
│ 🔴 Extra Large: Out of stock (0)   │
│ ⚠️ Garlic Knots: 4 units left      │
└─────────────────────────────────────┘
```

---

## ORDER MANAGEMENT & PROCESSING

### Feature 1: Order Creation

#### Via Kiosk (Customer)
```
Customer browses products
    ↓
Adds items to cart (session-based)
    ↓
Proceeds to checkout
    ↓
System creates Order:
├─ Generates unique order number: ORD-XXXXXXXX
├─ Sets customer name (if provided)
├─ Sets status: PENDING
├─ Calculates total from items
└─ Creates OrderItem records for each item
    ↓
System creates Payment record:
├─ Linked to Order (1-to-1)
├─ Payment method: CASH or ONLINE_DEMO
└─ Initial status: PENDING (CASH) or SUCCESS (ONLINE_DEMO)
    ↓
If ONLINE_DEMO payment:
├─ Stock automatically deducted
├─ Order visible to kitchen immediately
└─ AuditTrail logged
    ↓
Order number displayed to customer
    ↓
Customer can track order status
```

#### Via POS (Cashier - Manual Entry)
```
Cashier clicks "Create Order" on POS
    ↓
Form appears:
├─ Customer name (optional)
├─ Payment method (CASH, ONLINE_DEMO)
└─ Product selection
    ↓
Cashier selects products and quantities
    ↓
System creates Order (same as kiosk)
├─ Order number generated
├─ OrderItems created
└─ Payment record created
    ↓
Cashier can process payment immediately
    ↓
Order visible to kitchen
```

---

### Feature 2: Order Status Management

**Purpose**: Track order through preparation to delivery

**Status Workflow**:
```
PENDING
  ├─ Order received, payment pending (CASH orders)
  ├─ Or awaiting kitchen to see order
  │
  └─ Cashier confirms payment
      ↓
  IN_PROGRESS
  ├─ Payment confirmed
  ├─ Kitchen actively preparing
  │
  └─ Kitchen finishes
      ↓
  FINISHED
  ├─ Order ready for customer pickup
  ├─ Visible in customer tracking
  │
  └─ Customer picks up

  OR at any time:

  CANCELLED
  ├─ Order cancelled before payment
  ├─ Stock not deducted
  └─ Payment not processed
```

#### View Order Status (Customer)
```
Customer enters order number: ORD-A7F3K9X2
    ↓
System displays:
├─ Current status with timeline
├─ Estimated wait time
├─ Items in order
└─ Total paid
    ↓
Status examples:
├─ "PENDING - Waiting for payment confirmation" (CASH orders)
├─ "IN_PROGRESS - Your order is being prepared"
└─ "FINISHED - Ready for pickup at counter"
```

#### Update Order Status (Cashier)
```
Cashier views order in POS
    ↓
Clicks "Change Status"
    ↓
Options shown:
├─ IN_PROGRESS (after payment confirmed)
└─ FINISHED (when ready)
    ↓
Cashier selects new status
    ↓
System updates:
├─ Order.status changed
├─ Customer tracking updated
├─ AuditTrail logged with timestamp
└─ Kitchen notified (if Kitchen Display System)
```

---

### Feature 3: Order Items & Pricing

**Purpose**: Track individual items in order with historical pricing

**How It Works**:
```
When order created:
└─ For each item added:
   ├─ Create OrderItem record
   ├─ Store: Product ID, Quantity, Product Name (snapshot)
   ├─ Store: Product Price at time of order (snapshot)
   ├─ Calculate: Subtotal = Price × Quantity
   └─ Keep historical accuracy
    ↓
Why snapshots?
├─ If product price changes later, order shows original price
├─ Historical accuracy for invoices
├─ Prevents retroactive price changes
├─ Audit trail shows exact what customer paid
    ↓
Order Total Calculation:
└─ SUM of all OrderItem.subtotal
   └─ Automatically calculated, not editable
```

**Example**:
```
Order ORD-A7F3K9X2 created at 2:30 PM

OrderItem 1:
├─ Product: Large Pepperoni Pizza
├─ Quantity: 1
├─ Product Price (snapshot): $12.99
└─ Subtotal: $12.99

OrderItem 2:
├─ Product: Garlic Knots (6pc)
├─ Quantity: 2
├─ Product Price (snapshot): $3.99 each
└─ Subtotal: $7.98

OrderItem 3:
├─ Product: Cola (2L)
├─ Quantity: 1
├─ Product Price (snapshot): $3.99
└─ Subtotal: $3.99

Order Total: $12.99 + $7.98 + $3.99 = $24.96

Later at 3:00 PM, admin changes "Garlic Knots" price to $4.99
↓
This order STILL shows $3.99 (ordered price preserved)
Next new orders will use $4.99
↓
Historical accuracy maintained
```

---

## PAYMENT PROCESSING

### Feature 1: Payment Methods

**Purpose**: Support multiple payment options

**Available Methods**:
1. **CASH (Pay at Counter)**
   - Customer receives order number
   - Doesn't pay at kiosk
   - Stock not deducted yet
   - Cashier confirms payment later
   - Status: PENDING (until cashier confirms)

2. **ONLINE_DEMO (Simulated Online Payment)**
   - Instant payment processing
   - No real money transferred (demo mode)
   - Stock immediately deducted
   - Order visible to kitchen right away
   - Status: SUCCESS (immediate)

#### CASH Payment Flow
```
Customer selects CASH at checkout
    ↓
Order created with Payment.method = CASH
    ↓
Payment.status = PENDING (waiting for payment)
    ↓
Stock NOT deducted yet
    ↓
Customer gets order number
    ↓
Cashier sees PENDING order in POS
    ↓
Customer approaches counter with cash
    ↓
Cashier receives payment
    ↓
Cashier clicks "Confirm Payment" in POS
    ↓
System:
├─ Sets Payment.status = SUCCESS
├─ Sets Payment.processed_by = [cashier name]
├─ Sets Payment.processed_at = [timestamp]
├─ Sets Order.status = IN_PROGRESS
├─ Deducts stock from inventory
├─ Creates AuditTrail entry
└─ Order moves to kitchen queue
    ↓
Kitchen sees order and starts preparing
```

#### ONLINE_DEMO Payment Flow
```
Customer selects ONLINE_DEMO at checkout
    ↓
Order created with Payment.method = ONLINE_DEMO
    ↓
System automatically:
├─ Sets Payment.status = SUCCESS
├─ Deducts stock immediately
├─ Sets Order.status = PENDING (waiting to start prep)
└─ Creates AuditTrail entry
    ↓
Customer receives order number immediately
    ↓
Kitchen can see order right away
    ↓
Cashier notes payment already processed (no confirmation needed)
```

---

### Feature 2: Payment Status Tracking

**Purpose**: Monitor payment processing and confirm successful transactions

**Payment Statuses**:
- **PENDING**: Waiting for payment (CASH orders awaiting confirmation)
- **SUCCESS**: Payment processed successfully (ready to prepare)
- **FAILED**: Payment failed or declined (requires resolution)

#### Payment Status View (Admin)
```
Admin can see:
├─ All orders with payment status
├─ Payment method for each order
├─ Processed by: Which cashier confirmed
├─ Timestamp: When payment was processed
└─ Can search/filter by status
```

#### Handle Failed Payment
```
Payment.status = FAILED
    ↓
Reason might be:
├─ Customer cancelled before payment
├─ Invalid payment info
├─ Payment gateway error (in future)
└─ Cashier error

Actions:
├─ Retry payment (CASH: cashier tries again)
├─ Cancel order (return stock to inventory)
└─ AuditTrail logs all attempts
```

---

### Feature 3: Payment Reconciliation

**Purpose**: Ensure all transactions are accounted for

**Daily Reconciliation Process**:
```
End of day/shift:

Cashier counts cash drawer
    ↓
Admin accesses analytics
    ↓
System shows:
├─ Total CASH payments collected (today)
├─ Breakdown by status (SUCCESS, PENDING, FAILED)
├─ Amount per cashier
└─ List of all transactions

Admin compares:
├─ Actual cash count vs. System total
├─ Any discrepancies? Investigate via AuditTrail
└─ Resolve with complete action history

Example reconciliation:
System says: $2,500 in CASH payments
Actual count: $2,487
Discrepancy: $13

Check audit trail:
├─ Find order ORD-2151 = $13 (CANCELLED)
├─ Payment status = SUCCESS (should be reversed)
├─ Issue: Order cancelled but payment not refunded
└─ Action: Create refund entry

System now matches actual cash
Record complete in audit trail
```

---

## ANALYTICS & REPORTING

### Feature 1: Sales Dashboard

**Purpose**: View key business metrics at a glance

**Access**: `/analytics/dashboard/` (Admin only)

**Metrics Displayed**:
```
1. REVENUE
   ├─ Today's total
   ├─ Week-to-date
   ├─ Month-to-date
   └─ Year-to-date
   └─ Comparison with previous period (↑/↓%)

2. ORDER METRICS
   ├─ Total orders (today)
   ├─ Average order value
   ├─ Orders by status (PENDING, IN_PROGRESS, FINISHED)
   └─ Trend (↑/↓ from yesterday)

3. PRODUCT PERFORMANCE
   ├─ Top 5 products by quantity sold
   ├─ Top 5 products by revenue
   ├─ Slowest selling items
   └─ Product category breakdown

4. OPERATIONAL METRICS
   ├─ Low-stock alerts (count)
   ├─ Payment success rate
   ├─ Order fulfillment time (average)
   └─ Cashier performance (orders processed)

5. FINANCIAL SUMMARY
   ├─ Revenue breakdown by payment method
   ├─ CASH vs. ONLINE_DEMO comparison
   └─ Projected daily/monthly revenue
```

**Dashboard Layout**:
```
┌──────────────────────────────────────────────────┐
│ SALES DASHBOARD                                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  QUICK STATS:                                    │
│  Today: $2,847.50 (↑12%)  |  89 Orders  |  ✓    │
│                                                  │
│  ┌─────────────────────────┬──────────────────┐  │
│  │ REVENUE TREND (7 days)  │ TOP PRODUCTS     │  │
│  │ [Chart showing uptrend] │ 1. Pepperoni (89)│  │
│  │                         │ 2. Margherita(56)│  │
│  │ Avg: $2,635/day         │ 3. Knots (412)   │  │
│  └─────────────────────────┴──────────────────┘  │
│                                                  │
│  ALERTS:                                         │
│  ⚠️ Pepperoni: Low stock (2 left)               │  │
│  🔴 Extra Large: Out of stock                   │  │
│                                                  │
│  [Export] [Print] [More Details]                │
└──────────────────────────────────────────────────┘
```

---

### Feature 2: Sales Forecast

**Purpose**: Predict future sales based on historical trends

**Access**: `/analytics/forecast/` (Admin only)

**How It Works**:
```
System analyzes:
├─ Historical order data (last 30/60/90 days)
├─ Pattern recognition (busiest hours/days)
├─ Seasonal trends
└─ Product popularity trends
    ↓
Generates forecast for:
├─ Next 7 days (daily prediction)
├─ Next 30 days (weekly prediction)
└─ Confidence level (high/medium/low)
    ↓
Business uses forecast for:
├─ Staff scheduling (more staff for busy days)
├─ Inventory planning (order stock before peak)
├─ Revenue projection
└─ Menu planning (feature lesser-used items)
```

**Forecast Display**:
```
Sales Forecast - Next 7 Days
┌────────────────────────────────────────┐
│ Day      Predicted Orders  Confidence  │
├────────────────────────────────────────┤
│ Monday   78 orders         HIGH        │
│ Tuesday  65 orders         MEDIUM      │
│ Wednesday 72 orders        HIGH        │
│ Thursday  89 orders        HIGH        │
│ Friday   124 orders        HIGH        │
│ Saturday 156 orders        HIGH        │
│ Sunday   98 orders         MEDIUM      │
├────────────────────────────────────────┤
│ Average: 97.4 orders/day               │
│ Trend: ↑ Increasing (5% week-over-week)│
└────────────────────────────────────────┘
```

---

### Feature 3: Custom Reports

**Purpose**: Generate detailed reports for business analysis

**Available Reports**:
1. **Daily Sales Report**
   - Date range
   - Total revenue
   - Orders by status
   - Payment breakdown
   - Top products
   - Cashier performance

2. **Product Performance Report**
   - Sales by product
   - Revenue contribution
   - Trend analysis
   - Stock movements

3. **Cashier Performance Report**
   - Orders processed
   - Payment success rate
   - Average transaction value
   - Shift summary

4. **Financial Summary**
   - Revenue trends
   - Cost analysis (if integrated)
   - Margin analysis
   - Profitability

**Generate Report**:
```
Admin clicks "Create Report"
    ↓
Selects:
├─ Report type
├─ Date range
├─ Filters (cashier, product, etc.)
└─ Export format (PDF, Excel, CSV)
    ↓
System:
├─ Aggregates data
├─ Formats report
└─ Generates file
    ↓
Admin downloads/prints report
    ↓
Can share with stakeholders
```

---

## AUDIT TRAIL & COMPLIANCE

### Feature 1: Complete Action Logging

**Purpose**: Maintain transparent record of all system actions

**What Gets Logged**:
- User creation, edit, archive
- Product creation, edit, archive, stock changes
- Order creation, status updates
- Payment processing
- Any data modification

**Information Logged**:
```
For each action:
├─ WHO: User that performed action (username)
├─ WHAT: Type of action (CREATE, UPDATE, DELETE, ARCHIVE)
├─ WHEN: Exact timestamp (date + time + timezone)
├─ WHERE: Model affected (Order, Product, User, etc.)
├─ RECORD: Specific record ID
├─ SNAPSHOT: Complete data state before/after change
└─ HOW: IP address (for security audit)
```

**Access**: `/system/audit/` (Admin only)

**Audit Trail View**:
```
Admin can:
├─ View complete action history
├─ Filter by date range
├─ Filter by user
├─ Filter by model type
├─ Filter by action type
├─ Search by record ID
└─ View full data snapshots
```

**Example Audit Entry**:
```
Date: Oct 31, 2024 3:45 PM
User: John Smith (Cashier)
Action: UPDATE
Model: Payment
Record ID: 1847
Description: "Confirmed payment for order ORD-A7F3K9X2"

Before State:
{
  "status": "PENDING",
  "processed_by": null,
  "processed_at": null
}

After State:
{
  "status": "SUCCESS",
  "processed_by": "John Smith",
  "processed_at": "2024-10-31 15:45:00"
}

IP Address: 192.168.1.100
```

---

### Feature 2: Data Archive & Restoration

**Purpose**: Preserve deleted data and allow recovery if needed

**What Gets Archived**:
- Deleted users (when archived)
- Deleted products (when archived)
- Any soft-deleted records

**Archive Contains**:
- Complete record data (JSON format)
- Timestamp of archival
- User who archived it
- Reason for archival
- Option to restore

**Access**: `/system/archive/` (Admin only)

**Restore Process**:
```
Admin sees archived item
    ↓
Clicks "Restore"
    ↓
Confirmation dialog shown
    ↓
Admin confirms restore
    ↓
System:
├─ Restores all fields to original values
├─ Sets is_archived = False
├─ Creates new AuditTrail entry: RESTORE
└─ Item is active again
```

**Example**:
```
Product "Small Hawaiian" archived June 2024
    ↓
Archive contains:
├─ Name: Small Hawaiian
├─ Price: $9.99
├─ Stock: 0
├─ Category: PIZZA
├─ Archived by: Sarah (Admin)
├─ Reason: "Discontinued due to low sales"
└─ Can restore? Yes

If admin clicks restore:
├─ Product reactivated
├─ Immediately visible in kiosk
├─ Stock level restored (0)
└─ AuditTrail: "Restored by Sarah, Oct 31 2024"
```

---

### Feature 3: Compliance Reporting

**Purpose**: Generate reports for regulatory compliance

**Available Compliance Reports**:
1. **Audit Trail Export**
   - All actions in date range
   - User accountability
   - Changes to financial records
   - Complete data snapshots

2. **Transaction Report**
   - All orders and payments
   - Payment methods breakdown
   - Discrepancies and reversals
   - Financial reconciliation

3. **Data Integrity Report**
   - Verify data consistency
   - Check for orphaned records
   - Verify referential integrity
   - Flag anomalies

**Generate Compliance Report**:
```
Admin: Needs report for auditor
    ↓
Clicks "Compliance Reports"
    ↓
Selects:
├─ Date range: Jan 1 - Dec 31, 2024
├─ Report type: Full Audit Trail
└─ Format: CSV (for analysis)
    ↓
System generates report with:
├─ Every action from Jan-Dec
├─ User ID, timestamp, action type
├─ Before/after data snapshots
├─ IP addresses logged
└─ No filters (complete transparency)
    ↓
Admin downloads and provides to auditor
    ↓
Auditor verifies:
├─ All transactions recorded
├─ No unauthorized changes
├─ Data integrity maintained
└─ Compliance confirmed ✓
```

---

## SYSTEM FEATURES

### Feature 1: Real-Time Updates

**Purpose**: Keep information current without page reloads

**Uses Technology**: AJAX and Alpine.js

**What Updates Real-Time**:
- Stock levels (when order placed)
- Cart total (when items added/removed)
- Order status (when updated by cashier)
- Low-stock alerts (when triggered)
- Sales dashboard (refreshes every 30 seconds)

**Example - Adding to Cart**:
```
Customer clicks "Add to Cart"
    ↓
JavaScript captures product ID and quantity
    ↓
AJAX sends request to server
    ↓
Server:
├─ Adds to session['cart']
├─ Calculates new totals
└─ Returns updated cart data (JSON)
    ↓
JavaScript updates display:
├─ Cart count badge updated
├─ Total price recalculated
├─ Toast message shown
└─ NO page reload
```

### Feature 2: Mobile-Responsive Design

**Purpose**: Work on any device (desktop, tablet, phone)

**Features**:
- Responsive layout (adapts to screen size)
- Touch-friendly buttons (large tap targets)
- Mobile-optimized navigation
- Readable on all devices
- Works offline partially (cart continues to work)

**Tested On**:
- Desktop (1920+ width)
- Tablet (768-1024px)
- Mobile (375-767px)
- Portrait and landscape

---

### Feature 3: Session-Based Shopping Cart

**Purpose**: Fast, efficient shopping without database overhead

**How It Works**:
```
Session Storage (Not Database):
{
  'cart': {
    '5': 2,      # Product ID 5, Quantity 2
    '8': 1,      # Product ID 8, Quantity 1
    '12': 3      # Product ID 12, Quantity 3
  }
}

Benefits:
├─ No database queries for cart changes
├─ Extremely fast (in-memory)
├─ Automatic cleanup when session expires
├─ Simple implementation
└─ Scales well with many customers

Drawback:
└─ Lost if browser closed (acceptable for quick ordering)
```

---

### Feature 4: Search & Filtering

**Purpose**: Help users find what they need quickly

**Product Search** (Kiosk):
- Search by product name
- Filter by category
- Show/hide low-stock items
- Sort by price or popularity

**Order Search** (All):
- Search by order number
- Search by customer name
- Filter by date range
- Filter by status (PENDING, FINISHED, etc.)
- Filter by payment method

---

### Feature 5: Notifications & Alerts

**Types of Alerts**:
1. **Low-Stock Alert**
   - Display: Admin dashboard
   - When: Stock < threshold
   - Action: Click to adjust stock or reorder

2. **Out-of-Stock Alert**
   - Display: Admin dashboard (red)
   - When: Stock = 0
   - Action: Product hidden from kiosk automatically

3. **Payment Discrepancy Alert**
   - Display: Admin dashboard
   - When: Cash count doesn't match system
   - Action: Click to investigate via audit trail

4. **Error Notifications**
   - Display: Toast messages (top/bottom of page)
   - Types: Validation errors, connection errors, etc.
   - Duration: 5 seconds auto-dismiss

5. **Success Confirmations**
   - Display: Toast messages
   - Examples: "Order created!", "Payment processed!"
   - Color: Green
   - Duration: 3 seconds auto-dismiss

---

## SUMMARY

The FJC Pizza system provides comprehensive features covering:

✅ **User Management**: Authentication, role-based access, password reset
✅ **Inventory**: Product CRUD, stock tracking, low-stock alerts
✅ **Ordering**: Multi-channel (kiosk + POS), status tracking, quick checkout
✅ **Payments**: Multiple methods, secure processing, reconciliation
✅ **Analytics**: Sales dashboard, forecasting, custom reports
✅ **Compliance**: Complete audit trail, data archival, restoration
✅ **Performance**: Real-time updates, mobile-responsive, fast operations

All features work together to provide a seamless experience for customers, efficient operations for cashiers, and comprehensive visibility for administrators.

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Next Review**: January 2026
