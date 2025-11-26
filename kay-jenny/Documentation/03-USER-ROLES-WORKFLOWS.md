# FJC PIZZA - USER ROLES, WORKFLOWS & USE CASES

## DOCUMENT CONTROL

- **System Name**: FJC Pizza Sales & Inventory Management System
- **Version**: 1.0
- **Document Type**: User Documentation & Workflows
- **Target Audience**: All Users, Operations Team, Management

---

## TABLE OF CONTENTS

1. [User Roles Overview](#user-roles-overview)
2. [Customer/Kiosk User](#customerkiosk-user)
3. [Cashier User](#cashier-user)
4. [Administrator User](#administrator-user)
5. [Complete User Workflows](#complete-user-workflows)
6. [Use Cases & Scenarios](#use-cases--scenarios)

---

## USER ROLES OVERVIEW

The FJC Pizza system supports three distinct user types, each with specific responsibilities and permissions:

```
┌────────────────────────────────────────────────────────────────┐
│                    USER ROLES & ACCESS                         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  CUSTOMER (Unauthenticated)  CASHIER (Authenticated)  ADMIN   │
│  ├─ Browse Products          ├─ Login Required        ├─ Admin │
│  ├─ Add to Cart              ├─ View Orders           │   Login │
│  ├─ Checkout                 ├─ Process Payments      │         │
│  ├─ Select Payment           ├─ Update Order Status   ├─ Full   │
│  ├─ Receive Order Number     ├─ View History          │   System│
│  └─ Track Order Status       └─ Limited Analytics     │   Access│
│                                                      │         │
└────────────────────────────────────────────────────────────────┘
```

---

## CUSTOMER/KIOSK USER

### Profile Description

**Who**: Customers ordering food via the self-service kiosk

**Access Method**:
- Scan QR code on table or entrance
- No login required
- Mobile-friendly web interface
- Session-based cart

**Typical Characteristics**:
- First-time or repeat customers
- Varying technical proficiency
- Want fast, convenient ordering
- Prefer multiple payment options

### Permissions & Access

#### What They Can Do
✅ Browse all available products (in-stock, non-archived)
✅ View product details (name, price, image)
✅ Add items to cart with quantity selection
✅ Remove items from cart
✅ View cart summary and total
✅ Proceed to checkout
✅ Choose payment method (Cash or Online Demo)
✅ Submit order and receive order number
✅ Track order status in real-time
✅ Search for previous orders by order number

#### What They CANNOT Do
❌ Create or edit products
❌ View other customers' orders
❌ Access admin dashboard
❌ Modify inventory
❌ View financial reports
❌ Create user accounts

### Workflow: Customer Ordering Process

#### Step-by-Step Flow
```
1. DISCOVERY
   └─ Customer scans QR code
   └─ Mobile browser opens kiosk URL
   └─ System fetches active products

2. BROWSING
   └─ Customer sees product list (grid/list view)
   └─ Filters/searches for specific items
   └─ Views product details (price, description, image)
   └─ Low-stock items may show warning

3. ADDING TO CART
   └─ Customer selects quantity
   └─ Clicks "Add to Cart"
   └─ Item added to session cart (no DB storage)
   └─ Can continue shopping or proceed to cart

4. CART REVIEW
   └─ Customer views cart with:
      ├─ List of items
      ├─ Quantities
      ├─ Unit prices
      ├─ Subtotals
      └─ Total amount
   └─ Can adjust quantities
   └─ Can remove items
   └─ Can continue shopping

5. CHECKOUT
   └─ Customer reviews order summary
   └─ Enters customer name (optional)
   └─ Selects payment method:
      ├─ CASH (Pay at counter)
      └─ ONLINE_DEMO (Simulate online payment)

6. PAYMENT PROCESSING
   If CASH selected:
   └─ Order created (status: PENDING)
   └─ Payment created (status: PENDING)
   └─ Cashier confirmation required
   └─ Stock NOT deducted yet

   If ONLINE_DEMO selected:
   └─ Order created (status: PENDING)
   └─ Payment created (status: SUCCESS)
   └─ Stock automatically deducted
   └─ Order status visible immediately

7. ORDER CONFIRMATION
   └─ Order number displayed (ORD-XXXXXXXX)
   └─ Order receipt available
   └─ Customer directed to order tracking page
   └─ System creates AuditTrail entry

8. ORDER TRACKING
   └─ Customer can:
      ├─ Refresh for status updates
      ├─ See current order status
      │   ├─ PENDING: Waiting for payment confirmation
      │   ├─ IN_PROGRESS: Being prepared
      │   └─ FINISHED: Ready for pickup
      ├─ See estimated wait time
      └─ Return anytime with order number to check status
```

### Interface Walkthrough

#### Page 1: Kiosk Home (Product Listing)
```
┌─────────────────────────────────────────┐
│  FJC PIZZA ORDERING KIOSK              │
│  ═════════════════════════════════════ │
│                                         │
│  Search: [__________]  [Filter v]      │
│                                         │
│  ┌──────────┐ ┌──────────┐             │
│  │ PIZZA #1 │ │ PIZZA #2 │ ...        │
│  │ $12.99   │ │ $14.99   │             │
│  │ [ADD]    │ │ [ADD]    │             │
│  └──────────┘ └──────────┘             │
│                                         │
│  ┌──────────┐ ┌──────────┐             │
│  │ SIDES    │ │ DRINKS   │ ...        │
│  └──────────┘ └──────────┘             │
│                                         │
│  [View Cart (3)] [Search Orders]       │
└─────────────────────────────────────────┘
```

#### Page 2: Shopping Cart
```
┌─────────────────────────────────────────┐
│  YOUR CART                              │
│  ═════════════════════════════════════ │
│                                         │
│  Item                    Qty    Price   │
│  ─────────────────────────────────     │
│  Large Pizza Pepperoni    1    $12.99  │
│    [–] 1 [+]           [Remove]       │
│  Garlic Knots (6pc)       2    $7.98   │
│    [–] 2 [+]           [Remove]       │
│  Cola (2L)                1    $3.99   │
│    [–] 1 [+]           [Remove]       │
│  ─────────────────────────────────     │
│  TOTAL:                        $24.96  │
│                                         │
│  [Continue Shopping] [Proceed to Pay]  │
└─────────────────────────────────────────┘
```

#### Page 3: Checkout
```
┌─────────────────────────────────────────┐
│  CHECKOUT                               │
│  ═════════════════════════════════════ │
│                                         │
│  Order Summary:                         │
│  ─────────────────────────────────     │
│  3 items                       $24.96  │
│                                         │
│  Your Name (optional):                  │
│  [________________________]             │
│                                         │
│  How will you pay?                      │
│  ◉ Cash (Pay at counter)               │
│  ◯ Online Payment (Demo)               │
│                                         │
│  [Place Order]                          │
└─────────────────────────────────────────┘
```

#### Page 4: Order Confirmation
```
┌─────────────────────────────────────────┐
│  ORDER CONFIRMED! ✓                    │
│  ═════════════════════════════════════ │
│                                         │
│  Your Order Number:                     │
│  ┌─────────────────────┐               │
│  │  ORD-A7F3K9X2      │               │
│  └─────────────────────┘               │
│                                         │
│  Please present this number when your  │
│  order is ready for pickup.            │
│                                         │
│  Order Status: PENDING                 │
│  (Waiting for payment confirmation)    │
│                                         │
│  Estimated Wait Time: 15 minutes       │
│                                         │
│  [Track Order] [New Order] [Home]      │
└─────────────────────────────────────────┘
```

#### Page 5: Order Status Tracking
```
┌─────────────────────────────────────────┐
│  ORDER STATUS - ORD-A7F3K9X2           │
│  ═════════════════════════════════════ │
│                                         │
│  Status Timeline:                       │
│                                         │
│  ✓ PENDING (2:30 PM)                   │
│    Waiting for payment confirmation    │
│                                         │
│  → IN_PROGRESS (2:32 PM)               │
│    Your order is being prepared        │
│                                         │
│  ○ FINISHED                             │
│    Ready for pickup                    │
│                                         │
│  ─────────────────────────────────     │
│  Current Status: IN_PROGRESS           │
│  Estimated Ready: 2:45 PM              │
│                                         │
│  [Refresh] [New Order] [Home]          │
└─────────────────────────────────────────┘
```

### Key Interactions

#### Adding Item to Cart (AJAX)
```
Customer Action: Click "Add to Cart" button on product
├─ System captures product ID and quantity
├─ Validates product availability
├─ Adds to session['cart']
├─ Updates cart count badge
├─ Shows confirmation toast
└─ No page reload

Data Stored in Session (not database):
{
  'cart': {
    '5': 1,      # Product ID 5, quantity 1
    '8': 2,      # Product ID 8, quantity 2
  }
}
```

#### Quantity Adjustment (AJAX)
```
Customer Action: Change quantity in cart
├─ Update spinners (–/+)
├─ Recalculate subtotal (client-side)
├─ Update cart total
├─ Show live price updates
└─ Enable/disable checkout based on cart status
```

#### Switching Payment Methods
```
Customer Action: Select payment method at checkout
├─ CASH selected:
│  └─ System shows "Pay at counter when prompted"
│  └─ Order stays PENDING
│  └─ Cashier must confirm payment later
│
└─ ONLINE_DEMO selected:
   └─ System shows "Processing payment..."
   └─ Auto-marks payment SUCCESS
   └─ Stock immediately deducted
   └─ Order visible to kitchen
```

---

## CASHIER USER

### Profile Description

**Who**: Restaurant staff members responsible for order processing and payments

**Access Method**:
- Login via username/password
- Dedicated POS (Point-of-Sale) dashboard
- Desktop/tablet interface
- Session-based with timeout

**Typical Characteristics**:
- Fast-paced environment
- Multiple simultaneous orders
- Need clear, quick interface
- Focus on payment accuracy
- Responsible for cash handling

### Permissions & Access

#### What They Can Do
✅ Login to POS dashboard
✅ View all PENDING orders (awaiting payment)
✅ View IN_PROGRESS orders (being prepared)
✅ View order details (customer, items, total)
✅ Process cash payments
✅ Mark orders as IN_PROGRESS (payment confirmed)
✅ Mark orders as FINISHED (ready for pickup)
✅ View order history and previous receipts
✅ See low-stock alerts
✅ Limited sales analytics (own performance metrics)
✅ Print receipts/order tickets

#### What They CANNOT Do
❌ Create or modify products
❌ Create or delete users
❌ Modify order totals after creation
❌ Refund payments directly (requires manager)
❌ Change system settings
❌ Access audit trail
❌ View financial reports
❌ Manage inventory levels

### Workflow: Cashier Payment Processing

#### Step-by-Step Flow
```
1. LOGIN
   └─ Cashier enters username/password
   └─ System authenticates
   └─ Redirect to POS dashboard
   └─ Session created (auto-timeout after 2 hours)

2. DASHBOARD VIEW
   └─ Shows key metrics:
      ├─ Number of PENDING orders (red badge)
      ├─ Number of IN_PROGRESS orders (blue badge)
      ├─ Low-stock alerts (yellow warnings)
      └─ Current time and shift info

3. ORDER PROCESSING QUEUE
   └─ List of PENDING orders shows:
      ├─ Order number
      ├─ Customer name
      ├─ Total amount
      ├─ Time waiting
      └─ Payment status (all PENDING)

4. PAYMENT CONFIRMATION
   Cashier Action: Customer pays in cash
   ├─ Cashier receives cash from customer
   ├─ Counts and verifies amount matches total
   ├─ Clicks "Confirm Payment" in system
   └─ System processes:
      ├─ Updates Payment.status → SUCCESS
      ├─ Updates Order.status → IN_PROGRESS
      ├─ Triggers stock deduction (automatic)
      ├─ Creates AuditTrail entry
      └─ Order moves from PENDING to IN_PROGRESS

5. ORDER PREPARATION
   └─ Kitchen staff sees IN_PROGRESS orders
   └─ Prepares food according to order
   └─ Places order on counter when ready

6. ORDER COMPLETION
   Cashier Action: Customer picks up completed order
   ├─ Cashier verifies order number
   ├─ Gives order to customer
   ├─ Clicks "Mark Complete" in system
   └─ System processes:
      ├─ Updates Order.status → FINISHED
      ├─ Creates AuditTrail entry
      ├─ Removes from active queue
      ├─ Stores in history
      └─ Updates analytics

7. SHIFT END
   └─ Manager reconciles cash drawer
   └─ Compares:
      ├─ Total cash collected
      ├─ System-recorded payments
      └─ Discrepancies (if any)
   └─ Audit trail provides complete record
```

### Interface Walkthrough

#### Page 1: POS Dashboard (Home)
```
┌─────────────────────────────────────────────────────────┐
│  FJC PIZZA - POS SYSTEM               [Logout]          │
│  Cashier: John Smith | Shift: 10:00 AM - 6:00 PM       │
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  QUICK STATS:                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ 5        │ │ 3        │ │ 2 ITEMS  │               │
│  │ PENDING  │ │ IN PROG  │ │ LOW STK  │               │
│  │ ORDERS   │ │ ORDERS   │ │ ALERT    │               │
│  └──────────┘ └──────────┘ └──────────┘               │
│                                                         │
│  PENDING ORDERS (Waiting for Payment):                 │
│  ┌───────────────────────────────────────────────┐     │
│  │ ORD-A7F3K9X2 | John     | $24.96 | 5m ago   │[TAP]│
│  │ ORD-B2K8M5L3 | Maria    | $18.50 | 3m ago   │[TAP]│
│  │ ORD-C9J4P7R1 | Unknown  | $31.20 | 1m ago   │[TAP]│
│  │ ORD-D6H1Q2S8 | Blank    | $15.75 | <1m ago  │[TAP]│
│  │ ORD-E3L5T9V4 | Customer | $22.30 | <1m ago  │[TAP]│
│  └───────────────────────────────────────────────┘     │
│                                                         │
│  [View History] [Analytics] [Settings]                 │
└─────────────────────────────────────────────────────────┘
```

#### Page 2: Order Detail & Payment
```
┌──────────────────────────────────────────────────┐
│  ORDER DETAIL - ORD-A7F3K9X2                    │
│  ═════════════════════════════════════════════  │
│                                                 │
│  Customer: John                                 │
│  Order Time: 2:30 PM                            │
│  Status: PENDING                                │
│                                                 │
│  ITEMS:                                         │
│  ─────────────────────────────────────         │
│  Large Pizza Pepperoni     1 × $12.99 = $12.99│
│  Garlic Knots (6pc)        2 × $3.99  = $7.98 │
│  Cola (2L)                 1 × $3.99  = $3.99 │
│  ─────────────────────────────────────         │
│  SUBTOTAL:                              $24.96│
│  TAX (8%):                              $2.00 │
│  TOTAL:                                $26.96│
│                                                 │
│  Payment Method: CASH                          │
│  Status: PENDING (Waiting for payment)        │
│                                                 │
│  [Confirm Payment]     [Cancel Order]          │
│  [Print Receipt]       [Back to Queue]         │
└──────────────────────────────────────────────────┘
```

#### Page 3: In-Progress Orders
```
┌──────────────────────────────────────────────────┐
│  IN-PROGRESS ORDERS (Being Prepared)            │
│  ═════════════════════════════════════════════  │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ ORD-B2K8M5L3 | Maria | $18.50 | 8m ago │   │
│  │ Items: 2 Pizzas, 1 Drink                 │   │
│  │ [Order Detail] [Done] [Delay]            │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ ORD-C9J4P7R1 | ??? | $31.20 | 5m ago   │   │
│  │ Items: 3 Pizzas, 2 Sides, 2 Drinks      │   │
│  │ [Order Detail] [Done] [Delay]            │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  [Back to Queue] [New Order]                   │
└──────────────────────────────────────────────────┘
```

#### Page 4: Order History
```
┌──────────────────────────────────────────────────┐
│  ORDER HISTORY (Today)                          │
│  ═════════════════════════════════════════════  │
│                                                 │
│  Filter: [All ▼] [By Cashier ▼] [By Time ▼] │
│                                                 │
│  Order #        Time      Total   Status  Paid │
│  ─────────────────────────────────────────── │
│  ORD-A7F3K9X2  2:30 PM  $26.96  FINISHED ✓ │
│  ORD-B2K8M5L3  2:32 PM  $18.50  FINISHED ✓ │
│  ORD-C9J4P7R1  2:34 PM  $31.20  FINISHED ✓ │
│  ORD-D6H1Q2S8  2:35 PM  $15.75  CANCELLED ✗ │
│  ORD-E3L5T9V4  2:36 PM  $22.30  PENDING  (w) │
│  ...                                          │
│                                                 │
│  [Print Report] [Email Report]                 │
└──────────────────────────────────────────────────┘
```

### Key Interactions

#### Confirming Payment (High-Frequency Action)
```
Cashier Action: Click "Confirm Payment" button
├─ System shows confirmation dialog
├─ Displays order details for verification
├─ Cashier confirms amount matches customer's payment
├─ Clicks "Confirm"
└─ System processes:
   ├─ Updates Payment.status = SUCCESS
   ├─ Updates Order.status = IN_PROGRESS
   ├─ Deducts stock automatically
   ├─ Creates AuditTrail
   └─ Order moves to kitchen queue
```

#### Quick Order Lookup
```
Scenario: Customer says "I paid, where's my order?"
├─ Cashier enters order number in search box
├─ System displays order details
├─ Cashier checks status (PENDING/IN_PROGRESS/FINISHED)
├─ Communicates status to customer
└─ If missing: System shows exact time received
```

#### Low-Stock Alert Response
```
System Alert: "Pepperoni Pizza: Only 2 left"
├─ Cashier informs manager
├─ Manager updates stock level in system
├─ System recalculates availability
├─ If stock = 0: Product hidden from kiosk automatically
└─ AuditTrail records the adjustment
```

---

## ADMINISTRATOR USER

### Profile Description

**Who**: Restaurant manager and system administrators

**Access Method**:
- Login via username/password
- Full system dashboard
- Desktop interface preferred
- Admin panel with advanced features

**Typical Characteristics**:
- Business owner or manager
- Strategic decision-making focus
- Need comprehensive reporting
- Responsible for policies and procedures
- Focus on profitability and efficiency

### Permissions & Access

#### What They Can Do
✅ User management (create, edit, archive users)
✅ Product management (create, edit, archive products)
✅ Inventory management (adjust stock levels)
✅ View all orders (any status, any time period)
✅ View complete sales analytics
✅ Generate financial reports
✅ View performance metrics by cashier
✅ Access audit trail (complete action history)
✅ View and restore archived records
✅ Manage low-stock thresholds
✅ View sales forecasts
✅ Configure system settings
✅ Export data for analysis
✅ Access backup and restore functions

#### What They CANNOT Do
❌ Delete users or data permanently (only archive)
❌ Modify historical transaction data
❌ Override audit trail
❌ Modify source code or core system logic
❌ Change database schema directly
❌ Access server infrastructure

### Workflow: Administrative Tasks

#### Daily Admin Tasks
```
1. MORNING STARTUP
   └─ Check overnight orders/transactions
   └─ Review any failed payments
   └─ Check low-stock alerts
   └─ Verify staff attendance
   └─ Review any system issues

2. INVENTORY MANAGEMENT
   └─ Review stock levels
   └─ Check low-stock alerts
   └─ Adjust thresholds if needed
   └─ Plan reordering
   └─ Phase out underperforming items

3. PERFORMANCE REVIEW
   └─ Check daily sales total
   └─ Review top-selling items
   └─ Check cashier metrics
   └─ Identify trends
   └─ Adjust menu if needed

4. COMPLIANCE CHECKS
   └─ Audit payment records
   └─ Verify cash drawer reconciliation
   └─ Check for discrepancies
   └─ Review audit trail for anomalies
   └─ Document findings

5. USER MANAGEMENT
   └─ Create new user accounts
   └─ Reset forgotten passwords
   └─ Adjust permissions as needed
   └─ Archive inactive users
   └─ Review user activity logs

6. SHIFT END RECONCILIATION
   └─ Compare system records with actual cash
   └─ Identify any discrepancies
   └─ Review audit trail for suspicious activity
   └─ Document and investigate variances
   └─ Generate shift report
```

### Interface Walkthrough

#### Page 1: Admin Dashboard (Executive Summary)
```
┌────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                      [Settings▼][Logout]
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  TODAY'S PERFORMANCE:                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │ Revenue:    │ │ Orders:     │ │ Avg Order:  │      │
│  │ $2,847.50   │ │ 89 (↑12%)   │ │ $31.99      │      │
│  │ vs $2,534   │ │ vs 79 yest. │ │ vs $32.08   │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ALERTS & WARNINGS:                              │   │
│  │ • Pepperoni Pizza: 2 units remaining (⚠)       │   │
│  │ • Garlic Knots: 5 units remaining (⚠)          │   │
│  │ • Extra Large Pizza: Out of stock (🔴)         │   │
│  │ • Payment discrepancy: 2:45 PM (Check)         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  TOP PRODUCTS (Last 7 Days):                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 1. Large Pepperoni Pizza   247 units | $3,110.53 │  │
│  │ 2. Medium Margherita       156 units | $2,028.00 │  │
│  │ 3. Garlic Knots (6pc)      412 units | $1,646.88 │  │
│  │ 4. Cola (2L)               389 units | $1,556.11 │  │
│  │ 5. Salad (Garden)          87 units  | $870.00  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  QUICK ACTIONS:                                         │
│  [Manage Products] [Manage Users] [View Analytics]     │
│  [View Audit Log] [Archive Mgmt] [Reports]             │
└────────────────────────────────────────────────────────┘
```

#### Page 2: Product Management
```
┌────────────────────────────────────────────────────────┐
│  PRODUCT MANAGEMENT                    [Create New ▶]  │
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  Search: [_____________] [Filter ▼] [Sort ▼]          │
│                                                         │
│  Product Name          Category   Price  Stock  Status  │
│  ─────────────────────────────────────────────────── │
│  Large Pepperoni       Pizza      $12.99 2     ⚠       │
│  Medium Margherita     Pizza      $10.99 24    ✓       │
│  Small Hawaiian        Pizza      $9.99  0     🔴      │
│  Garlic Knots (6pc)    Sides      $3.99  5     ⚠       │
│  Caesar Salad          Salad      $9.99  12    ✓       │
│  Cola (2L)             Drinks     $3.99  34    ✓       │
│  [Edit] [Archive]      [View]     [More...]            │
│  ─────────────────────────────────────────────────── │
│  Large Hawaiian (Arc)  Pizza      $9.99  0     X       │
│  [Edit] [Restore]      [View]     [More...]            │
│                                                         │
│  Showing 1-10 of 45 products [Prev] [1] [2] [3] [Next]│
└────────────────────────────────────────────────────────┘
```

#### Page 3: User Management
```
┌────────────────────────────────────────────────────────┐
│  USER MANAGEMENT                       [Create New ▶]  │
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  Search: [_____________] [Filter ▼] [Sort ▼]          │
│                                                         │
│  Name              Role      Status    Last Login      │
│  ────────────────────────────────────────────────── │
│  John Smith        Cashier   Active    Today 5:30 PM  │
│  Maria Garcia      Cashier   Active    Today 4:15 PM  │
│  Ahmed Hassan      Cashier   Active    Yesterday      │
│  Sarah Johnson     Admin     Active    Today 6:45 PM  │
│  Robert Brown      Cashier   Inactive  3 weeks ago    │
│  [Edit] [Archive] [Reset Password] [View Activity]     │
│  ────────────────────────────────────────────────── │
│  Michael Chen      Cashier   Archived  Last: 1 month  │
│  [Edit] [Restore]  [View Activity]                    │
│                                                         │
│  Showing 1-10 of 23 users [Prev] [1] [2] [Next]      │
└────────────────────────────────────────────────────────┘
```

#### Page 4: Analytics Dashboard
```
┌────────────────────────────────────────────────────────┐
│  ANALYTICS DASHBOARD                   [Export ▼]      │
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  Date Range: [Oct 1 ─────────── Oct 31] [Go]          │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ REVENUE TREND (Last 30 Days)                    │   │
│  │                                                 │   │
│  │   $3500 ┤     ╭─╮                             │   │
│  │   $3000 ┤   ╭─╯ ╰─────╮                       │   │
│  │   $2500 ┤ ╭─╯         ╰─╮                     │   │
│  │   $2000 ┤─╯             ╰─                    │   │
│  │         ├──────────────────────────────────── │   │
│  │         Day 1    Day 10    Day 20    Day 30   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────┬──────────────────────────┐   │
│  │ PRODUCT PERFORMANCE  │ CASHIER PERFORMANCE      │   │
│  │                      │                          │   │
│  │ 1. Pepperoni Pizza   │ John Smith: 245 orders  │   │
│  │    $3,110 | 247 sold │ Maria Garcia: 198 ord   │   │
│  │                      │ Ahmed Hassan: 156 ord   │   │
│  │ 2. Margherita Pizza  │                          │   │
│  │    $2,028 | 156 sold │ Accuracy Rate:          │   │
│  │                      │ John: 98.2%             │   │
│  │ 3. Garlic Knots      │ Maria: 99.1%            │   │
│  │    $1,646 | 412 sold │ Ahmed: 97.8%            │   │
│  │                      │                          │   │
│  └──────────────────────┴──────────────────────────┘   │
│                                                         │
│  [View Details] [Export Data] [Print Report]           │
└────────────────────────────────────────────────────────┘
```

#### Page 5: Audit Trail
```
┌────────────────────────────────────────────────────────┐
│  AUDIT TRAIL                           [Export ▼]      │
│  ═════════════════════════════════════════════════════  │
│                                                         │
│  Filter: [Type ▼] [User ▼] [Date ▼] [Search]         │
│                                                         │
│  Date/Time          User        Action    Model   ID   │
│  ─────────────────────────────────────────────────── │
│  Oct 31 3:45 PM     John Smith  UPDATE    Payment  1847 │
│  Oct 31 3:42 PM     John Smith  CREATE    Order    2156 │
│  Oct 31 3:40 PM     Sarah Mgr   UPDATE    Product  34  │
│  Oct 31 3:35 PM     Maria       CREATE    Order    2155 │
│  Oct 31 3:30 PM     Admin       ARCHIVE   User     12  │
│  Oct 31 3:25 PM     John Smith  UPDATE    Order    2154 │
│  Oct 31 3:20 PM     Ahmed       CREATE    Order    2153 │
│  [View Details] [View Snapshot] [Revert] [More...]    │
│                                                         │
│  Showing 1-100 of 1,247 entries [Prev] [1-10] [Next] │
└────────────────────────────────────────────────────────┘
```

---

## COMPLETE USER WORKFLOWS

### Workflow 1: Complete Order-to-Delivery Cycle

```
┌──────────────────────────────────────────────────────────┐
│         COMPLETE ORDER LIFECYCLE (All Users)            │
└──────────────────────────────────────────────────────────┘

CUSTOMER (Kiosk)              CASHIER (POS)            ADMIN (Dashboard)
   │                             │                           │
   ├─ Scan QR Code              │                           │
   │                            │                           │
   ├─ Browse Products◄──────────┴─ Stock visible ──────────┬─ Monitor stock
   │  (only active, in-stock)    │                          │  levels
   │                            │                           │
   ├─ Add to Cart              │                           │
   │  (session storage)        │                           │
   │                            │                           │
   ├─ Proceed to Checkout      │                           │
   │  - Select payment method   │                           │
   │  (CASH or ONLINE_DEMO)    │                           │
   │                            │                           │
   ├─ Submit Order             │                           │
   │  - Creates Order record    │                           │
   │  - Creates Payment record  │                           │
   │  - Creates OrderItems      │                           │
   │                            │                           │
   │ If ONLINE_DEMO:            │                           │
   │  - Payment→SUCCESS        │                           │
   │  - Stock deducted         │                           │
   │                            │                           │
   │ If CASH:                   │                           │
   │  - Payment→PENDING        │                           │
   │  - Waits for cashier      │                           │
   │                            │                           │
   ├─ Receive Order Number     │                           │
   │  - Display ORD-XXXXXXXX   │                           │
   │                            │                           │
   ├─ Track Order Status◄──────┤ POS shows PENDING orders  │
   │  (refresh for updates)    │  (red badge)              │
   │                            │                           │
   │                    ┌───────┴─ Confirm Payment         │
   │                    │ (if CASH)                        │
   │                    │                                   │
   │                    ├─ Payment→SUCCESS               │
   │                    ├─ Order→IN_PROGRESS            │
   │                    ├─ Stock deducted                │
   │                    │                                 │
   │                    ├─ Kitchen sees order            │
   │                    ├─ Prepares food                 │
   │                    │                                 │
   │                    ├─ Marks FINISHED                │
   │                    │  (when ready)                   │
   │                    │                                 │
   │ Status updates◄────┤ Order ready for pickup          │
   │ (PENDING→            │                                 │
   │  IN_PROGRESS→        │                                 │
   │  FINISHED)          │                                 │
   │                    │                                 │
   ├─ Pickup Order     ├─ Give to Customer              │
   │  (present number)  ├─ Mark FINISHED (if not done)   │
   │                    │  (confirm pickup)              │
   │                    │                                 │
   │                    │ ◄────────────────────────────┤ Analytics updated
   │                    │  (AuditTrail logged)           │ (revenue, products,
   │                    │                                │  cashier metrics)
```

### Workflow 2: Stock Deduction Process

```
┌──────────────────────────────────────────────────────────┐
│        AUTOMATIC STOCK DEDUCTION (Django Signals)       │
└──────────────────────────────────────────────────────────┘

Trigger: Payment.status changed to SUCCESS

1. Payment Model Saved
   └─ post_save signal triggered

2. Signal Handler Executes
   ├─ Fetch associated Order
   ├─ Fetch all OrderItems for this Order
   └─ For each OrderItem:
      ├─ Get Product
      ├─ Reduce stock by OrderItem.quantity
      ├─ Check if now low-stock
      │  └─ If yes: Add alert to admin dashboard
      └─ Save Product

3. AuditTrail Logged
   ├─ User: Cashier or System
   ├─ Action: UPDATE
   ├─ Model: Product
   ├─ Data snapshot: Before/after stock levels
   └─ Timestamp: Exact moment of deduction

4. Inventory Updated
   └─ Available to customers:
      ├─ If stock = 0: Product hidden from kiosk
      ├─ If stock < threshold: Warning in admin
      └─ If stock > threshold: Normal display

Result: Full traceability of every stock deduction
```

### Workflow 3: Payment Discrepancy Investigation

```
┌──────────────────────────────────────────────────────────┐
│         INVESTIGATING PAYMENT DISCREPANCY               │
└──────────────────────────────────────────────────────────┘

Admin discovers: System shows $2,500 but cash drawer has $2,485

Step 1: Check Dashboard Alerts
└─ System flagged payment mismatch
└─ Links to specific orders/transactions

Step 2: Access Audit Trail
└─ Filter by date range and payment method
└─ View all CASH payment transactions
└─ See: amount, cashier, timestamp, status

Step 3: Review Orders
└─ Check orders with CASH payment
└─ Verify amounts
└─ Look for CANCELLED orders

Step 4: Identify Issue
└─ Find: Order 2151 = $15.00 (CANCELLED but payment still marked SUCCESS)
└─ Root cause: Payment not reversed when order cancelled

Step 5: View Order Details
└─ Order 2151: $15.00, Status: CANCELLED
└─ Payment: Status = SUCCESS (should be REFUNDED)
└─ Cashier: Maria Garcia, Time: 2:35 PM

Step 6: Action Audit Trail
└─ See exact sequence of events
└─ Who cancelled order, when
└─ Who marked payment success
└─ Full transparency of what happened

Step 7: Reconciliation
└─ Document in system: "Found cancelled payment $15"
└─ Create refund entry
└─ Note discrepancy resolution
└─ System records complete history

Result: Complete audit trail enables fast investigation and resolution
```

---

## USE CASES & SCENARIOS

### Use Case 1: Peak Hour Management

**Scenario**: Friday evening, 6:00 PM

**Timeline**:
```
6:00 PM - Orders start flowing in quickly
├─ 15 orders in 5-minute window via kiosk
├─ Cashiers process PENDING orders in queue
├─ Stock levels updating in real-time
└─ Kitchen busy with IN_PROGRESS orders

6:05 PM - ALERT: Pepperoni Pizza stock low (2 remaining)
├─ Admin dashboard shows yellow warning
├─ Cashier sees "Low Stock" in system
├─ Next customer ordering pepperoni → gets warning
├─ Manager notifies kitchen/supplier

6:10 PM - ALERT: Pepperoni Pizza now OUT OF STOCK
├─ System automatically hides from kiosk
├─ Customers ordering see product grayed out
├─ Manager must reorder
├─ AuditTrail shows exact time it ran out

6:15 PM - Post-Peak Analysis
└─ 50 total orders processed
└─ All payment discrepancies resolved
└─ Average order time: 3 minutes
└─ Revenue: $1,247.50
└─ Forecast shows same demand tomorrow
```

**Key System Features Used**:
- Session-based cart (fast, no DB overhead)
- Real-time stock updates (prevents overselling)
- Auto low-stock alerts (inventory planning)
- AJAX processing (no page reloads, fast UI)
- Audit trail (complete accountability)

---

### Use Case 2: End-of-Day Reconciliation

**Scenario**: Friday 9:00 PM, end of shift

**Process**:
```
Step 1: Cashier Count
├─ Count actual cash in drawer: $2,487.50
└─ Record in cash report

Step 2: System Review
├─ Admin accesses POS Dashboard
├─ Filters today's transactions by cashier
├─ System shows:
│  └─ Total recorded: $2,487.50
└─ Result: MATCH ✓

Step 3: Payment Verification
├─ View all CASH transactions
├─ Check status of each (SUCCESS/FAILED)
├─ Verify no discrepancies
└─ Review any cancelled orders

Step 4: Audit Trail Review
├─ Check all payment-related actions
├─ Verify who processed each payment
├─ Look for unusual patterns
└─ Document findings

Step 5: Analytics Review
├─ Today's total revenue: $6,842.50
├─ Orders processed: 147
├─ Average order: $46.55
├─ Top product: Pepperoni Pizza (89 orders)
└─ Busiest hour: 6:00-7:00 PM (28 orders)

Step 6: Close Shift
├─ Generate daily report
├─ Archive daily data
├─ Reset POS for next shift
└─ Store report for management review
```

**Key System Features Used**:
- AuditTrail completeness (verify every transaction)
- Payment tracking (cash reconciliation)
- Analytics aggregation (business intelligence)
- Date range filtering (daily reports)
- Archive system (historical data preservation)

---

### Use Case 3: Menu Update & Stock Adjustment

**Scenario**: Saturday morning, Manager updates menu

**Process**:
```
Step 1: Product Management
├─ Manager logs in to Admin Dashboard
└─ Opens Product Management

Step 2: Archive Old Item
├─ Finds "Small Hawaiian" (unpopular)
├─ Clicks "Archive"
├─ System archives product:
│  ├─ Hidden from kiosk
│  ├─ Stored in archive
│  └─ AuditTrail: WHO archived, WHEN, WHY
└─ Result: Won't be ordered by customers

Step 3: Create New Item
├─ Click "Create New Product"
├─ Enter details:
│  ├─ Name: "Spicy Buffalo Chicken"
│  ├─ Price: $13.99
│  ├─ Stock: 15 units
│  ├─ Threshold: 5 units
│  ├─ Category: Pizza
│  └─ Image: (uploaded)
├─ System creates product
└─ AuditTrail: NEW product created, initial stock

Step 4: Adjust Existing Stock
├─ Find "Garlic Knots" (current stock: 8)
├─ Manager received delivery overnight
├─ Update stock to 28 units
├─ System records:
│  ├─ Change: 8 → 28 units (+20)
│  ├─ Timestamp: When adjusted
│  ├─ AuditTrail: WHO adjusted, WHEN
│  └─ Reason: "Received delivery"

Step 5: Verify Menu
├─ Check Kiosk to verify:
│  ├─ "Small Hawaiian" NOT shown
│  ├─ "Spicy Buffalo Chicken" shown
│  └─ "Garlic Knots" shows 28 in stock
└─ Result: Menu correctly updated

Step 6: Communicate to Team
├─ Notify kitchen: New pizza available
├─ Alert cashiers: Stock levels updated
└─ System shows in POS: New item available
```

**Key System Features Used**:
- Soft delete (archive instead of delete)
- Auto-hiding (archived products not shown)
- Stock tracking (accurate inventory)
- AuditTrail (who changed what, when)
- Real-time updates (changes immediately visible)

---

## SUMMARY TABLE: User Capabilities

| Feature | Customer | Cashier | Admin |
|---------|----------|---------|-------|
| **Authentication** | None (Guest) | Login Required | Login Required |
| **Browse Products** | ✅ | ✅ | ✅ |
| **Create Order** | ✅ | ✅ | ✅ |
| **Process Payment** | ✅ (Choose method) | ✅ (Confirm) | ✅ (Full control) |
| **Update Order Status** | View only | ✅ | ✅ |
| **Product Management** | ❌ | ❌ | ✅ |
| **Stock Management** | View only | View only | ✅ |
| **User Management** | ❌ | ❌ | ✅ |
| **Analytics** | ❌ | Limited | ✅ |
| **Audit Trail** | ❌ | ❌ | ✅ |
| **Archive/Restore** | ❌ | ❌ | ✅ |

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Next Review**: December 2025
