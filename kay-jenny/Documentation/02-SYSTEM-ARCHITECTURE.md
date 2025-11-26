# FJC PIZZA - SYSTEM ARCHITECTURE & DESIGN

## DOCUMENT CONTROL

- **System Name**: FJC Pizza Sales & Inventory Management System
- **Version**: 1.0
- **Document Type**: Technical Architecture
- **Target Audience**: Technical Team, Architecture Review Board, Developers

---

## TABLE OF CONTENTS

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Technology Stack](#technology-stack)
4. [Database Design](#database-design)
5. [Application Architecture](#application-architecture)
6. [Security Architecture](#security-architecture)
7. [Deployment Architecture](#deployment-architecture)
8. [Scalability & Performance](#scalability--performance)

---

## ARCHITECTURE OVERVIEW

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Customer   │  │   Cashier    │  │   Admin      │              │
│  │   Kiosk UI   │  │   POS UI     │  │  Dashboard   │              │
│  │  (Mobile)    │  │  (Terminal)  │  │   (Web)      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         │                   │                  │                    │
│         └───────────────────┼──────────────────┘                    │
│                             │                                       │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                   HTTPS / REST API
                              │
┌─────────────────────────────┼───────────────────────────────────────┐
│                    APPLICATION LAYER                               │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                  Django Web Framework                      │  │
│  │  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐    │  │
│  │  │ Accounts │ │ Products │ │ Orders │ │  Analytics  │    │  │
│  │  │  (Auth)  │ │(Inventory)│ │(Payment)│ │ (Reporting) │    │  │
│  │  └─────────┘ └──────────┘ └────────┘ └──────────────┘    │  │
│  │  ┌──────────────────────┐ ┌──────────────────────────┐    │  │
│  │  │   System Module      │ │   Business Logic         │    │  │
│  │  │  (Audit/Archive)     │ │   (Order Processing)     │    │  │
│  │  └──────────────────────┘ └──────────────────────────┘    │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐     │  │
│  │  │  Django Signals (Auto-logging, Stock Management)│     │  │
│  │  └──────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                    Database Connections
                                │
┌───────────────────────────────┼───────────────────────────────────┐
│                        DATA LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │             PostgreSQL / SQLite Database                 │    │
│  │  ┌───────────┐ ┌──────────┐ ┌─────────┐ ┌────────────┐ │    │
│  │  │ Users     │ │ Products │ │ Orders  │ │ Audit Log  │ │    │
│  │  ├───────────┤ ├──────────┤ ├─────────┤ ├────────────┤ │    │
│  │  │ Payments  │ │ Archived │ │ Archive │ │ Sessions   │ │    │
│  │  └───────────┘ └──────────┘ └─────────┘ └────────────┘ │    │
│  │                                                          │    │
│  │  Indexes: model_name, record_id, created_at, user_id   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Architecture Pattern: 3-Tier Model-View-Template

The system follows Django's MVT architecture:

- **Model Layer**: Django ORM with SQLAlchemy-like query interface
- **View Layer**: Python view functions and class-based views
- **Template Layer**: Django template engine with HTML, CSS, JavaScript

This pattern provides:
- Clear separation of concerns
- Testability at each layer
- Code reusability
- Maintainability

---

## SYSTEM COMPONENTS

### 1. ACCOUNTS COMPONENT (User Management & Authentication)

#### Purpose
Manage user accounts, roles, and role-based access control.

#### Responsibilities
- User authentication (login/logout)
- User profile management
- Role assignment (Admin, Cashier)
- Password management
- User archival (soft delete)

#### Key Models
```
User (extends Django AbstractUser)
├── username: CharField (unique)
├── email: EmailField
├── password: encrypted
├── first_name, last_name: CharField
├── phone_number: CharField
├── role: CharField (choices: ADMIN, CASHIER)
├── is_active: BooleanField
├── is_archived: BooleanField
└── timestamps: created_at, updated_at
```

#### Key Views & Routes
- `LoginView` → `/accounts/login/`
- `LogoutView` → `/accounts/logout/`
- `UserListView` → `/accounts/users/` (admin only)
- `UserCreateView` → `/accounts/users/create/` (admin only)
- `UserEditView` → `/accounts/users/<id>/edit/` (admin only)
- `UserArchiveView` → `/accounts/users/<id>/archive/` (admin only)

#### Access Control
- Public: Login page
- Authenticated: Dashboard (role-specific redirect)
- Admin Only: User management, System settings
- Cashier Only: POS dashboard, Order processing

---

### 2. PRODUCTS COMPONENT (Inventory Management)

#### Purpose
Manage product catalog, inventory levels, and availability.

#### Responsibilities
- Product creation and maintenance
- Stock level tracking
- Low-stock alerts
- Product categorization
- Product images/media
- Availability determination

#### Key Models
```
Product
├── name: CharField
├── description: TextField (optional)
├── category: CharField (choices: PIZZA, SIDES, DRINKS, DESSERTS)
├── price: DecimalField
├── stock: IntegerField
├── reorder_threshold: IntegerField (low-stock trigger)
├── image: ImageField (optional)
├── is_archived: BooleanField
└── timestamps: created_at, updated_at

Properties:
├── is_low_stock: Boolean (stock < threshold)
├── is_available: Boolean (stock > 0 AND not archived)
└── visibility: Used only for non-archived, in-stock items
```

#### Key Views & Routes
- `ProductListView` → `/products/` (admin)
- `ProductCreateView` → `/products/create/` (admin)
- `ProductEditView` → `/products/<id>/edit/` (admin)
- `ProductArchiveView` → `/products/<id>/archive/` (admin)
- `ProductAPIView` → `/api/products/` (customer kiosk)

#### Business Rules
1. **Stock Management**: Only non-negative quantities allowed
2. **Availability**: Only active, in-stock products shown to customers
3. **Low-Stock Alert**: Auto-alert when stock < threshold
4. **Soft Delete**: Archive instead of permanent deletion
5. **Image Support**: Store product images for customer display

---

### 3. ORDERS COMPONENT (Order Processing & Payments)

#### Purpose
Manage complete order lifecycle from placement to fulfillment.

#### Responsibilities
- Order creation and management
- Order status workflow
- Order item management
- Payment processing
- Stock deduction
- Order history tracking

#### Key Models
```
Order
├── order_number: CharField (unique, auto-generated: ORD-XXXXXXXX)
├── customer_name: CharField
├── table_number: CharField (optional)
├── status: CharField (choices: PENDING, IN_PROGRESS, FINISHED, CANCELLED)
├── total_amount: DecimalField (auto-calculated from items)
├── notes: TextField (optional)
├── payment_method: CharField (CASH, ONLINE_DEMO, etc.)
└── timestamps: created_at, updated_at

OrderItem (Line Item)
├── order: ForeignKey to Order
├── product: ForeignKey to Product
├── quantity: IntegerField (minimum 1)
├── product_name: CharField (snapshot at time of order)
├── product_price: DecimalField (snapshot at time of order)
└── subtotal: DecimalField (auto-calculated: price × quantity)

Payment
├── order: OneToOneField to Order
├── method: CharField (CASH, ONLINE_DEMO)
├── status: CharField (PENDING, SUCCESS, FAILED)
├── amount: DecimalField
├── reference_number: CharField (transaction ID)
├── processed_by: ForeignKey to User (cashier)
└── timestamps: created_at, updated_at, processed_at
```

#### Order Status Workflow
```
PENDING
  ├─→ (payment confirmed by cashier)
  │   └─→ IN_PROGRESS (being prepared)
  │       └─→ FINISHED (ready for customer)
  │
  └─→ CANCELLED (order cancelled)
```

#### Key Views & Routes
**Customer Kiosk**:
- `KioskHomeView` → `/kiosk/` (product listing)
- `AddToCartView` → `/kiosk/add-to-cart/<product_id>/` (AJAX)
- `RemoveFromCartView` → `/kiosk/remove-from-cart/<product_id>/` (AJAX)
- `CartView` → `/kiosk/cart/`
- `CheckoutView` → `/kiosk/checkout/`
- `OrderStatusView` → `/kiosk/order/<order_number>/`

**Cashier POS**:
- `OrderListView` → `/orders/` (all orders)
- `OrderDetailView` → `/orders/<id>/`
- `ProcessPaymentView` → `/orders/<id>/process-payment/` (POST)
- `UpdateOrderStatusView` → `/orders/<id>/update-status/` (POST)
- `POSCreateOrderView` → `/orders/pos/create/` (manual entry)

#### Business Rules
1. **Auto-Numbering**: Order numbers generated automatically (ORD-XXXXXXXX)
2. **Stock Deduction**: Happens only when payment is marked SUCCESS
3. **Price Snapshot**: Store product price at time of order (for history accuracy)
4. **Minimum Quantity**: At least 1 item required per line item
5. **Total Calculation**: Automatically sum all line items
6. **Session-Based Cart**: Cart stored in session until checkout
7. **Payment Methods**: Support cash (manual confirmation) and online demo (auto-success)

#### Workflow Integration
```
KIOSK CUSTOMER PATH:
  Scan QR Code
    ↓
  View Products (fetches available items)
    ↓
  Add to Cart (session storage)
    ↓
  Proceed to Checkout
    ↓
  Select Payment (CASH or ONLINE_DEMO)
    ↓
  Create Order (status=PENDING)
    ↓
  Create Payment (status=PENDING for CASH, SUCCESS for ONLINE_DEMO)
    ↓
  If ONLINE_DEMO: Auto-deduct stock, mark Payment SUCCESS
    ↓
  Display Order Number
    ↓
  Customer can track order status

CASHIER PATH:
  View POS Dashboard
    ↓
  See PENDING orders
    ↓
  Confirm Payment (if CASH)
    ↓
  Mark IN_PROGRESS (order being prepared)
    ↓
  Mark FINISHED (order ready)
    ↓
  Order disappears from active queue
```

---

### 4. ANALYTICS COMPONENT (Business Intelligence & Reporting)

#### Purpose
Provide insights into sales performance and operational metrics.

#### Responsibilities
- Sales data aggregation
- Performance metrics calculation
- Forecasting and trend analysis
- Dashboard generation
- Report export

#### Key Features
```
Sales Dashboard
├── Total Revenue (Daily, Weekly, Monthly)
├── Top-Selling Products (Rank by quantity/revenue)
├── Low-Stock Alerts
├── Order Status Distribution
├── Cashier Performance
│   ├── Orders processed
│   ├── Average transaction value
│   └── Payment success rate
└── Revenue Trends
    ├── By hour/day/week/month
    └── By product category

Forecasting
├── Time-Series Analysis
├── Statistical Models (ARIMA, exponential smoothing)
├── Demand Prediction
└── Inventory Recommendations
```

#### Key Views & Routes
- `AnalyticsDashboardView` → `/analytics/dashboard/` (admin)
- `SalesDataAPIView` → `/analytics/api/sales-data/` (JSON for charts)
- `ForecastView` → `/analytics/forecast/` (admin)

#### Data Aggregation Logic
```python
# Sales aggregation example
sales_data = Order.objects.filter(
    status='FINISHED',
    created_at__gte=start_date
).values('product__name').annotate(
    total_quantity=Sum('orderitem__quantity'),
    total_revenue=Sum('orderitem__subtotal')
).order_by('-total_revenue')
```

---

### 5. SYSTEM COMPONENT (Audit Trail & Archive)

#### Purpose
Maintain compliance and data preservation through audit logging.

#### Responsibilities
- Action logging (all CRUD operations)
- Data preservation (archive system)
- Audit trail generation
- Archive restoration
- Compliance reporting

#### Key Models
```
AuditTrail
├── user: ForeignKey to User (who performed action)
├── action: CharField (CREATE, UPDATE, DELETE, ARCHIVE, RESTORE)
├── model_name: CharField (which model was affected)
├── record_id: IntegerField (which record was affected)
├── description: TextField (human-readable description)
├── data_snapshot: JSONField (full record state)
├── ip_address: GenericIPAddressField
└── timestamps: created_at

Archive
├── model_name: CharField
├── record_id: IntegerField
├── data: JSONField (full archived record)
├── archived_by: ForeignKey to User
├── reason: TextField (reason for archival)
└── timestamps: created_at, can_restore: Boolean
```

#### Implementation: Django Signals
```python
@receiver(post_save, sender=Order)
def log_order_changes(sender, instance, created, **kwargs):
    """Auto-log all Order changes"""
    AuditTrail.objects.create(
        user=instance.processed_by,
        action='CREATE' if created else 'UPDATE',
        model_name='Order',
        record_id=instance.id,
        data_snapshot=model_to_dict(instance),
        ip_address=get_client_ip(request)
    )
```

#### Key Views & Routes
- `AuditTrailListView` → `/system/audit/` (admin)
- `ArchiveListView` → `/system/archive/` (admin)
- `RestoreArchiveView` → `/system/archive/<id>/restore/` (admin, POST)

#### Benefits
1. **Complete Accountability**: Every action tracked
2. **Data Preservation**: Nothing permanently deleted
3. **Compliance**: Audit trail for regulatory requirements
4. **Troubleshooting**: Historical data for issue diagnosis
5. **Restore Capability**: Recover archived records if needed

---

## TECHNOLOGY STACK

### Backend Framework
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | Django | 5.2.8 | Web framework, ORM, templating, authentication |
| **Language** | Python | 3.12+ | Backend programming language |
| **App Server** | Gunicorn | 23.0.0 | WSGI application server for production |
| **Database** | PostgreSQL | 13+ | Production relational database |
| **Database** | SQLite | (built-in) | Development database |

### Frontend Technologies
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Templating** | Django Templates | Server-side HTML rendering |
| **Styling** | Tailwind CSS | Utility-first CSS framework (CDN) |
| **JavaScript** | Alpine.js | Lightweight reactive JavaScript (CDN) |
| **Dynamic Updates** | HTMX | HTML-over-the-wire for dynamic updates |
| **Icons** | Tailwind UI | Pre-built UI components and icons |

### Data Analysis & Analytics
| Library | Version | Purpose |
|---------|---------|---------|
| **NumPy** | 2.3.4 | Numerical computing and arrays |
| **Pandas** | 2.3.3 | Data manipulation and aggregation |
| **SciPy** | 1.16.3 | Scientific computing and statistics |
| **Statsmodels** | 0.14.5 | Statistical modeling and forecasting |
| **Patsy** | 1.0.2 | R-style formula interface |

### Supporting Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| **Pillow** | 12.0.0 | Image processing for product images |
| **psycopg2** | 2.9.11 | PostgreSQL database adapter |
| **dj-database-url** | 3.0.1 | Database URL parsing from environment |
| **python-dotenv** | 1.2.1 | Environment variable management |
| **WhiteNoise** | 6.11.0 | Static file serving in production |

### Infrastructure
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Hosting** | Cloud Platform (Render) | Application deployment |
| **Container** | Docker | (Optional) containerization |
| **Version Control** | Git | Source code management |
| **CI/CD** | GitHub Actions | (Optional) continuous integration |

---

## DATABASE DESIGN

### Database Schema Overview

#### User Management
```
accounts_user
├── id (PK)
├── username (UNIQUE)
├── email
├── password (hashed)
├── first_name
├── last_name
├── phone_number
├── role (ENUM: ADMIN, CASHIER)
├── is_active (BOOLEAN)
├── is_archived (BOOLEAN)
├── created_at (DATETIME)
├── updated_at (DATETIME)
└── Indexes: (username), (email), (role)
```

#### Product Catalog
```
products_product
├── id (PK)
├── name (VARCHAR)
├── description (TEXT)
├── category (VARCHAR: PIZZA, SIDES, DRINKS, DESSERTS)
├── price (DECIMAL)
├── stock (INTEGER)
├── reorder_threshold (INTEGER)
├── image (FILEPATH)
├── is_archived (BOOLEAN)
├── created_at (DATETIME)
├── updated_at (DATETIME)
└── Indexes: (category), (is_archived), (created_at)
```

#### Order Management
```
orders_order
├── id (PK)
├── order_number (VARCHAR, UNIQUE)
├── customer_name (VARCHAR)
├── table_number (VARCHAR)
├── status (VARCHAR: PENDING, IN_PROGRESS, FINISHED, CANCELLED)
├── total_amount (DECIMAL, auto-calculated)
├── notes (TEXT)
├── created_at (DATETIME)
├── updated_at (DATETIME)
└── Indexes: (order_number), (status), (created_at), (customer_name)

orders_orderitem
├── id (PK)
├── order_id (FK)
├── product_id (FK)
├── quantity (INTEGER)
├── product_name (VARCHAR, snapshot)
├── product_price (DECIMAL, snapshot)
├── subtotal (DECIMAL, auto-calculated)
└── Indexes: (order_id), (product_id)

orders_payment
├── id (PK)
├── order_id (FK, UNIQUE: one payment per order)
├── method (VARCHAR: CASH, ONLINE_DEMO)
├── status (VARCHAR: PENDING, SUCCESS, FAILED)
├── amount (DECIMAL)
├── reference_number (VARCHAR)
├── processed_by_id (FK to User)
├── created_at (DATETIME)
├── processed_at (DATETIME)
└── Indexes: (order_id), (status), (created_at), (processed_by_id)
```

#### Audit Trail
```
system_audittrail
├── id (PK)
├── user_id (FK)
├── action (VARCHAR: CREATE, UPDATE, DELETE, ARCHIVE, RESTORE)
├── model_name (VARCHAR)
├── record_id (INTEGER)
├── description (TEXT)
├── data_snapshot (JSON)
├── ip_address (VARCHAR)
├── created_at (DATETIME)
└── Indexes: (model_name), (record_id), (created_at), (user_id), (model_name, record_id, created_at)

system_archive
├── id (PK)
├── model_name (VARCHAR)
├── record_id (INTEGER)
├── data (JSON)
├── archived_by_id (FK)
├── reason (TEXT)
├── can_restore (BOOLEAN)
├── created_at (DATETIME)
└── Indexes: (model_name, record_id), (created_at)
```

### Database Relationships
```
User (1) ──── (N) Order [created/processed by]
User (1) ──── (N) Payment [processed by]
User (1) ──── (N) AuditTrail [performed action]
User (1) ──── (N) Archive [archived records]

Product (1) ──── (N) OrderItem [line items in orders]
Order (1) ──── (N) OrderItem [items in single order]
Order (1) ──── (1) Payment [payment for order]
```

### Performance Optimizations

#### Indexes Strategy
- **Frequently Queried**: created_at, status, is_archived, user_id
- **Foreign Keys**: All FK relationships automatically indexed
- **Compound Indexes**: (model_name, record_id, created_at) for audit queries
- **Search Fields**: name, order_number for search functionality

#### Query Optimization
```python
# Good: Select related to reduce queries
orders = Order.objects.select_related(
    'payment',
    'payment__processed_by'
).prefetch_related('orderitem_set')

# Good: Only fetch needed fields
products = Product.objects.filter(
    is_archived=False
).values('id', 'name', 'price')

# Good: Batch operations
Order.objects.filter(status='FINISHED').delete()  # Single query
```

---

## APPLICATION ARCHITECTURE

### Django App Structure

#### App: accounts (User Management)
```
accounts/
├── __init__.py
├── admin.py              # Django admin configuration
├── apps.py              # App configuration
├── forms.py             # User forms
├── models.py            # User model
├── tests.py             # Unit tests
├── urls.py              # URL routing
├── views.py             # Login, logout, user CRUD
└── migrations/
    └── 0001_initial.py
```

#### App: products (Inventory)
```
products/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py             # Product forms
├── models.py            # Product model
├── tests.py
├── urls.py
├── views.py             # Product CRUD views
├── management/
│   └── commands/
│       └── populate_demo_data.py  # Data seeder
└── migrations/
```

#### App: orders (Order Processing)
```
orders/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py             # Order forms
├── kiosk_urls.py       # Kiosk-specific routes
├── kiosk_views.py      # Customer kiosk views
├── models.py           # Order, OrderItem, Payment models
├── tests.py
├── urls.py             # Admin/cashier routes
├── views.py            # Order management views
└── migrations/
```

#### App: analytics (Reporting)
```
analytics/
├── __init__.py
├── admin.py
├── apps.py
├── models.py           # Analytics models (optional)
├── tests.py
├── urls.py
├── views.py            # Dashboard, forecast views
├── templatetags/       # Custom template filters
└── migrations/
```

#### App: system (Audit & Archive)
```
system/
├── __init__.py
├── admin.py
├── apps.py
├── models.py           # AuditTrail, Archive models
├── signals.py          # Django signal handlers
├── tests.py
├── urls.py
├── views.py            # Audit, archive views
└── migrations/
```

### URL Routing Structure
```
/                          → Home (redirects based on role)
/accounts/
  login/                   → Login page
  logout/                  → Logout
  users/                   → User list (admin)
  users/create/            → Create user (admin)
  users/<id>/edit/         → Edit user (admin)
  users/<id>/archive/      → Archive user (admin)

/products/
  (list)                   → Product listing (admin)
  create/                  → Create product (admin)
  <id>/edit/              → Edit product (admin)
  <id>/archive/           → Archive product (admin)

/orders/
  (list)                   → Order listing (cashier/admin)
  <id>/                   → Order detail
  <id>/update-status/     → Update status (cashier)
  <id>/process-payment/   → Process payment (cashier)
  pos/create/             → Manual POS order (cashier)

/kiosk/
  (home)                   → Product catalog (customer)
  cart/                   → Shopping cart
  checkout/               → Checkout process
  order/<order_number>/   → Order status tracking
  add-to-cart/<id>/       → Add item (AJAX)
  remove-from-cart/<id>/  → Remove item (AJAX)
  search-order/           → Search orders

/analytics/
  dashboard/              → Analytics dashboard (admin)
  api/sales-data/         → JSON API for charts
  forecast/               → Sales forecast (admin)

/system/
  audit/                  → Audit trail (admin)
  archive/                → Archive viewer (admin)
  archive/<id>/restore/   → Restore archive (admin)
```

### View Layer Architecture

#### Class-Based Views (CBV) Usage
```python
# Generic views for standard CRUD
class ProductListView(ListView):
    model = Product
    template_name = 'products/list.html'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(is_archived=False)

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/form.html'

    def form_valid(self, form):
        # Log action via signal
        return super().form_valid(form)

# Custom views for complex logic
class CheckoutView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        # Fetch products and calculate total

    def post(self, request):
        # Create Order, OrderItem, Payment
        # Handle payment method
```

#### Decorators for Access Control
```python
@login_required                    # Must be logged in
@user_passes_test(is_admin)       # Must be admin
@user_passes_test(is_cashier)     # Must be cashier
def protected_view(request):
    pass
```

### Template Layer Architecture (Atomic Design)

#### Atoms (Basic Elements)
```html
<!-- components/atoms/button.html -->
<button class="btn btn-{{ type }}">{{ label }}</button>

<!-- components/atoms/badge.html -->
<span class="badge badge-{{ status }}">{{ text }}</span>

<!-- components/atoms/input.html -->
<input type="{{ type }}" name="{{ name }}" value="{{ value }}">
```

#### Molecules (Component Combinations)
```html
<!-- components/molecules/card.html -->
<div class="card">
  {% include "components/atoms/button.html" %}
  {% include "components/atoms/badge.html" %}
</div>

<!-- components/molecules/product_card.html -->
<div class="product-card">
  <img src="{{ product.image.url }}">
  <h3>{{ product.name }}</h3>
  <p>{{ product.price }}</p>
  {% include "components/atoms/button.html" %}
</div>
```

#### Organisms (Complex Sections)
```html
<!-- components/organisms/navbar.html -->
<nav class="navbar">
  <ul class="nav-menu">
    <!-- Navigation items -->
  </ul>
</nav>

<!-- dashboards/admin.html -->
{% extends "base.html" %}
{% include "components/organisms/navbar.html" %}
{% include "components/organisms/sidebar.html" %}
```

---

## SECURITY ARCHITECTURE

### Authentication & Authorization

#### Authentication Flow
```
1. User submits login form
   ↓
2. Django authenticates username + password
   ↓
3. Password hashed with PBKDF2 (Django default)
   ↓
4. User object created/retrieved
   ↓
5. Session created and stored
   ↓
6. Redirect to role-specific dashboard
```

#### Authorization Strategy
```
# Decorator-based access control
@login_required                   # Must be authenticated
@user_passes_test(user.is_admin)  # Must have admin role
def admin_view(request):
    # Only admins can access
    pass
```

#### Session Management
- Django session framework
- Configurable session timeout
- Secure cookies (HttpOnly, Secure flags)
- Database-backed session storage

### Data Security

#### Password Security
- **Algorithm**: PBKDF2 with SHA256
- **Iterations**: 600,000 (Django default)
- **Hashing**: One-way hash, never reversible
- **Reset**: Secure email-based reset token

#### Data Encryption
- **Transit**: HTTPS/TLS for all communication
- **Storage**: Plaintext in DB (encrypted at application level if needed)
- **Backups**: Encrypted backup storage

#### Payment Data Security
```
ONLINE_DEMO Mode:
├── No real payment processing
├── Demo transaction created
├── No PCI compliance required
├── Status marked SUCCESS automatically

Future Production Mode:
├── Payment Gateway Integration (Stripe, Square)
├── PCI DSS Compliance
├── Tokenization for card storage
├── No raw card data in database
```

### CSRF Protection
- **CSRF Tokens**: On all POST/PUT/DELETE forms
- **SameSite Cookies**: Prevent cross-site attacks
- **Referer Checking**: Validate request origin

### SQL Injection Prevention
- **Django ORM**: Parameterized queries by default
- **No Raw SQL**: Avoid raw SQL except in analytics
- **Query Filtering**: Always use filter() method

### Access Control Rules

#### Admin Role
- User management (create, edit, archive)
- Product management (create, edit, archive)
- All order viewing and management
- Analytics and reporting
- Audit trail and archive access
- System configuration

#### Cashier Role
- POS dashboard access
- View assigned/pending orders
- Process payments
- Update order status
- View order history
- LIMITED analytics (own performance)

#### Customer (Unauthenticated)
- Kiosk access via QR code
- View available products
- Create orders
- Make payments
- View own order status

---

## DEPLOYMENT ARCHITECTURE

### Development Environment
```
Local Machine
├── Python virtual environment
├── SQLite database (file-based)
├── Django development server
├── Static files served by Django
└── Media files (local directory)

Database: SQLite
Server: Python manage.py runserver
Static: Direct Django serving
```

### Production Environment
```
Cloud Platform (Render)
├── Application Server
│   └── Gunicorn (4+ worker processes)
│
├── Database
│   └── PostgreSQL managed service
│
├── Static Files
│   └── WhiteNoise middleware
│
├── Media Files
│   └── Cloud storage (S3 or equivalent)
│
└── Environment
    └── Environment variables via .env

Database: PostgreSQL
Server: Gunicorn (production-grade WSGI)
Static: WhiteNoise CDN delivery
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "sales_inventory.wsgi:application"]
```

### Environment Configuration
```
Development (.env):
  DEBUG=True
  DATABASE_URL=sqlite:///db.sqlite3
  SECRET_KEY=dev-key-only
  ALLOWED_HOSTS=localhost,127.0.0.1

Production (.env):
  DEBUG=False
  DATABASE_URL=postgresql://user:password@host/dbname
  SECRET_KEY=production-secret-key
  ALLOWED_HOSTS=yourdomain.com
  SECURE_SSL_REDIRECT=True
```

---

## SCALABILITY & PERFORMANCE

### Performance Optimizations

#### Database Queries
- **Select Related**: Reduce N+1 queries
- **Prefetch Related**: Efficient bulk loading
- **Query Caching**: Cache frequent queries
- **Database Indexes**: Optimize filtered queries

#### Caching Strategy
```python
# Cache expensive aggregations
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache for 60 seconds
def analytics_dashboard(request):
    # Expensive query
    pass
```

#### Frontend Optimization
- **CDN for Static Files**: Tailwind CSS, Alpine.js via CDN
- **Lazy Loading**: Load images on scroll
- **Minification**: Compress CSS/JS
- **Compression**: GZIP compression on responses

### Scalability Considerations

#### Database Scaling
- **Read Replicas**: For read-heavy analytics
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Sharding**: By location for multi-location future

#### Application Scaling
- **Load Balancing**: Round-robin behind load balancer
- **Stateless Design**: Scalable across multiple servers
- **Session Storage**: Database-backed sessions (not memory)
- **Asynchronous Tasks**: Celery for long-running tasks (future)

#### Data Volume Projections
```
Daily Transactions:     100-500 orders
Monthly Growth:          5-10% (assumed)
Annual Data:            ~50K-100K orders
Audit Trail Size:       200K-500K entries
Storage Requirement:    ~2-5 GB (first year)
```

### Monitoring & Logging

#### Application Monitoring
- Error tracking (Sentry integration possible)
- Performance monitoring (Django Debug Toolbar in dev)
- Request logging
- Database query monitoring

#### Audit Trail Monitoring
- Real-time action logging via signals
- Audit trail queries for compliance
- Archive status verification
- User action tracking

---

## CONCLUSION

The FJC Pizza system is built on a solid, scalable architecture that provides:

1. **Clear Separation of Concerns**: Modular Django apps for each business domain
2. **Enterprise-Grade Database Design**: Normalized schema with proper indexes
3. **Security by Default**: Built-in Django security features
4. **Performance Optimizations**: Database indexing, caching, CDN
5. **Audit & Compliance**: Complete action logging and data preservation
6. **Scalability**: Architecture supports growth from single location to multi-location

The architecture is production-ready and provides a foundation for future enhancements such as real payment processing, multi-location support, mobile app integration, and advanced analytics.

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Next Review**: January 2026
