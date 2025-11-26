# ⚙️ 03 — Development Phases

**Project:** Sales & Inventory Management System
**Stack:** Django + MySQL + CDN Frontend (Atomic Design Pattern)
**note:** every phase is both backend and frontend

---

## 🧩 **Phase 1: Initialization & Project Setup**

### 🎯 Objectives

Set up Django environment, database, and initial structure for modular frontend using CDN + reusable components.

### ✅ Tasks

* Initialize Django project `sales_inventory/`.
* Create core apps:

  * `accounts` (User & Roles)
  * `products` (Inventory)
  * `orders` (Order & Payment flow)
  * `analytics` (Reports & Dashboards)
  * `system` (Audit & Archive)
* Configure MySQL connection in `settings.py`.
* Setup static and media file structure for CDN delivery.
* Prepare component folders for frontend:

  * `/static/js/components/atoms/`
  * `/static/js/components/molecules/`
  * `/static/js/components/organisms/`

### 📦 Deliverables

* Django project structure complete.
* Database connected.
* CDN-linked base template (Bootstrap/Tailwind via CDN).
* Base component folder system ready.

---

## 🔐 **Phase 2: Authentication & RBAC**

### 🎯 Objectives

Implement secure role-based authentication using Django’s auth system.

### ✅ Tasks

* Extend Django’s `AbstractUser` model → add role (`ADMIN`, `CASHIER`).
* Create login/logout views & templates.
* Restrict page access by role:

  * Admin → full system
  * Cashier → POS only
* Middleware for role validation.
* Session-based authentication (no JWT needed).
* Include “active/inactive” toggle for users.

### 📦 Deliverables

* Working login/logout system.
* Role-based route control.
* Auth middleware setup.
* Base navbar adjusts based on role.

---

## 📦 **Phase 3: Product & Inventory Management**

### 🎯 Objectives

Develop CRUD for inventory with direct stock control and archiving.

### ✅ Tasks

* Create `Product` model and views (list, create, edit, archive).
* Implement direct stock manipulation (add/subtract).
* Display low-stock alerts (`stock < threshold`).
* Archive logic: soft delete (`is_archived` true).
* Auto-hide archived products from POS/Kiosk.
* Audit trail entry on every update.

### 📦 Deliverables

* `/admin/products/` management UI.
* Stock adjustment modals.
* Low-stock alert section.
* Audit log entries for each action.

---

## 💳 **Phase 4: Orders & Payment Core**

### 🎯 Objectives

Build core transaction logic: order creation, payment, and fulfillment.

### ✅ Tasks

* Create models: `Order`, `OrderItem`, `Payment`.
* Views for:

  * Cashier POS (list, detail, mark paid).
  * Customer order submission (frontend).
* Logic:

  * Payment success → deduct inventory.
  * Auto status change: `PENDING → IN_PROGRESS → FINISHED`.
* Separate template partials for reusable UI:

  * Atom: buttons, inputs
  * Molecule: order card, payment modal
  * Organism: POS table view

### 📦 Deliverables

* POS interface (cashier-side).
* Payment simulation logic (cash/online demo).
* Fully working order life cycle.
* Inventory deduction verified.

---

## 📱 **Phase 5: Customer Kiosk Interface**

### 🎯 Objectives

Create a responsive, no-login kiosk page accessible via QR code.

### ✅ Tasks

* Public `/kiosk/` route (no auth).
* Display available products (non-archived).
* Cart functionality (session-based).
* Checkout & order submission page.
* Choose payment option (cash/online demo).
* Generate order number & show status.
* Order status auto-refresh using AJAX polling (no full reload).

### 📦 Deliverables

* `/kiosk/` mobile-friendly UI.
* Order confirmation + live order status.
* Online demo payment page.
* Reusable kiosk components (Atoms → Organisms).

---

## 📊 **Phase 6: Analytics & Dashboard**

### 🎯 Objectives

Provide real-time analytics for admins.

### ✅ Tasks

* Create analytics views:

  * Daily/weekly/monthly sales
  * Best-selling products
  * Cashier performance
  * Inventory summary
* Build dashboard with reusable charts and summary cards.
* Use lightweight charting library via CDN (Chart.js / ApexCharts).

### 📦 Deliverables

* `/dashboard/` with analytics cards & charts.
* Aggregated queries (Django ORM or Raw SQL).
* Low-stock and top-seller widgets.

---

## 🕵️ **Phase 7: Audit Trail & Archive System**

### 🎯 Objectives

Add full transparency with permanent logs and non-destructive record archiving.

### ✅ Tasks

* Create `AuditTrail` and `Archive` models.
* Use Django signals (`post_save`, `pre_delete`) to log actions automatically.
* Admin interface to view audit logs & archive records.
* Auto-archive when product/user/order is removed or hidden.
* Include JSON snapshot of original data in archive record.

### 📦 Deliverables

* `/audit/` and `/archive/` views.
* Automatic audit recording system-wide.
* Restore-from-archive (optional).

---

## 🎨 **Phase 8: Component Refinement & Reusability**

### 🎯 Objectives

Refactor UI to follow **Atomic Design** strictly and improve maintainability.

### ✅ Tasks

* Reorganize all UI parts:

  * **Atoms:** Buttons, Inputs, Labels, Badges.
  * **Molecules:** Product Cards, Order Rows, Modals.
  * **Organisms:** POS Table, Product Grid, Dashboard Layouts.
* Standardize UI states (hover, disabled, loading).
* Add a “component library” page for preview/testing.

### 📦 Deliverables

* Complete reusable component system.
* Unified design language across modules.
* Component documentation page (`/components/preview`).

---

## 🚀 **Phase 9: Optimization & Deployment**

### 🎯 Objectives

Prepare for demo and production deployment.

### ✅ Tasks

* Optimize static files (collectstatic, CDN caching).
* Configure Nginx/Cloudflare CDN routes for speed.
* Final testing (customer → cashier → admin flow).
* Deploy backend (PythonAnywhere, Render, or Hostinger).
* Test across devices (QR, mobile, desktop).

### 📦 Deliverables

* Live deployed demo site.
* Documentation (setup + deployment guide).
* MVP ready for client presentation or public demo.

---

## 🧠 Development Summary

| Phase | Focus             | Output                       |
| ----- | ----------------- | ---------------------------- |
| 1     | Project Setup     | Django + CDN structure ready |
| 2     | Authentication    | Role-based login system      |
| 3     | Inventory         | Product CRUD + archiving     |
| 4     | Orders & Payments | Transaction & POS system     |
| 5     | Kiosk             | Customer QR-based ordering   |
| 6     | Analytics         | Dashboard insights           |
| 7     | Audit/Archive     | Transparency & history       |
| 8     | UI Reusability    | Atomic component structure   |
| 9     | Deployment        | Live, optimized system       |

---

