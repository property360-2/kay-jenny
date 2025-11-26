# ⚙️ 03 — Development Phases

**Project:** Sales & Inventory Management System

---

## 🧩 **Phase 1: Initialization & Project Setup**

### 🎯 Objectives

Establish the project foundation, environment, and base schema.

### ✅ Tasks

* Initialize full-stack structure:

  * `/backend` → Express + Prisma + MySQL
  * `/frontend` → React/Next.js + Tailwind CSS
* Setup `.env` and database connection.
* Create initial **Prisma schema** with migrations.
* Seed base roles (`ADMIN`, `CASHIER`).
* Setup folder structure: `controllers`, `routes`, `middlewares`, `models`.
* Test DB connection via sample route (`/health`).

### 📦 Deliverables

* `schema.prisma` finalized (with all tables).
* `backend` initialized and connected to MySQL.
* `frontend` initialized with Tailwind UI base.
* `.env` configured properly.

---

## 🔐 **Phase 2: Authentication & Role-Based Access Control**

### 🎯 Objectives

Implement secure login for Admin and Cashier users only.

### ✅ Tasks

* Create `User` model & authentication routes (`/auth/login`).
* Password hashing (bcrypt).
* JWT-based login system (with expiration).
* Role-based middleware:

  * `AdminGuard` → full access.
  * `CashierGuard` → POS module only.
* Protected API routes setup (e.g. `/products`, `/orders`).
* Admin dashboard access control.

### 📦 Deliverables

* `/auth` routes (login/logout).
* `/users` CRUD (Admin only).
* Middleware: `authGuard`, `roleGuard`.
* Token validation on frontend.

---

## 🧾 **Phase 3: Product & Inventory Management (Admin)**

### 🎯 Objectives

Enable full CRUD for products and stock manipulation with soft-archive logic.

### ✅ Tasks

* `/products` endpoints (Create, Read, Update, Archive).
* Add/edit product details (name, price, stock, threshold, image).
* Admin can **add or subtract** stock directly.
* Implement `isArchived` logic (instead of deletion).
* Auto-hide archived products from POS & Kiosk.
* Low-stock alert logic on admin dashboard.

### 📦 Deliverables

* Inventory management page (Admin UI).
* Low-stock alert widget.
* Archive toggle on product edit.
* API: `/api/products` complete.

---

## 💰 **Phase 4: Payment & Order Core (Backend + POS)**

### 🎯 Objectives

Establish full transactional workflow for orders, payments, and stock deduction.

### ✅ Tasks

* Create `/orders` routes and models.
* Create `/payments` routes and models.
* Implement logic:

  * On `Payment.status = SUCCESS` → deduct stock.
  * Auto-update order status → `IN_PROGRESS`.
* Create cashier POS panel (React):

  * View all active orders.
  * Mark cash payments as “Paid”.
  * Mark orders as “Finished”.
* Demo online payment simulation (auto-success).

### 📦 Deliverables

* Fully working POS panel.
* `/orders`, `/payments` backend routes.
* Order life cycle: `PENDING → IN_PROGRESS → FINISHED`.
* Auto stock deduction verified.

---

## 📱 **Phase 5: Customer Kiosk (QR Flow)**

### 🎯 Objectives

Implement customer-facing mobile web interface for ordering via QR code.

### ✅ Tasks

* Public kiosk page (no login).
* Display product list (excluding archived/low stock).
* Add to cart + checkout system.
* Generate order number after checkout.
* Allow customer to choose:

  * **Pay at Counter (Cash)**
  * **Online Demo Payment (Simulated)**
* Display real-time order status (polling or socket).

### 📦 Deliverables

* `/kiosk` UI complete (mobile-friendly).
* Order confirmation + order status view.
* Demo payment page.
* QR code link integration (static or table-specific).

---

## 📊 **Phase 6: Analytics & Dashboard**

### 🎯 Objectives

Provide Admin with insights for operations and decision-making.

### ✅ Tasks

* Backend analytics endpoints:

  * Total sales (daily, weekly, monthly).
  * Top-selling products.
  * Low-stock summary.
  * Sales per cashier.
* Create dashboard UI (charts & summaries).
* Use Recharts / Chart.js for data visualization.
* Optimize DB queries for performance.

### 📦 Deliverables

* `/dashboard` (Admin view).
* Sales overview charts.
* Best-seller table.
* Low-stock alert cards.

---

## 🕵️ **Phase 7: Audit Trail & Archive System**

### 🎯 Objectives

Implement transparent tracking and non-destructive data archiving.

### ✅ Tasks

* Create `/audit` and `/archive` routes (Admin only).
* Log every important action:

  * Product CRUD
  * Stock update
  * Payment processing
  * User actions
* Save logs in `AuditTrail` with full context (who, what, when).
* Implement archive process:

  * Copy old data into `Archive` table (as JSON).
  * Mark original record as archived (if applicable).
* Build Admin UI for viewing audit & archive entries.

### 📦 Deliverables

* `/audit` backend + dashboard viewer.
* `/archive` backend + restore feature (optional).
* Integrated audit hooks across system actions.

---

## 🚀 **Phase 8: Finalization & Deployment**

### 🎯 Objectives

Prepare system for public/demo use and ensure stability.

### ✅ Tasks

* Final UI/UX polish (mobile & desktop views).
* Add loading and error handling states.
* Environment separation (DEV / PROD).
* Deploy backend to Render or Hostinger.
* Deploy frontend to Vercel or Netlify.
* Test end-to-end: Kiosk → POS → Payment → Analytics → Audit.

### 📦 Deliverables

* Fully deployed live demo system.
* Documentation (`README.md`, setup guide).
* MVP ready for client use or presentation.

---

## 🧠 Development Flow Summary

| Phase | Focus          | Key Output                        |
| ----- | -------------- | --------------------------------- |
| 1     | Initialization | Project & DB setup                |
| 2     | Authentication | Secure access control             |
| 3     | Inventory      | Product CRUD & soft-archive       |
| 4     | Payments       | Orders, payments, stock deduction |
| 5     | Kiosk          | Customer mobile ordering          |
| 6     | Analytics      | Admin dashboard insights          |
| 7     | Audit/Archive  | Full transparency & traceability  |
| 8     | Deployment     | Production-ready live system      |

---
