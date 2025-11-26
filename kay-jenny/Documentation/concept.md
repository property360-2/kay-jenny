# 🛒 Sales & Inventory Management System — Concept Document

## 🎯 Project Vision

A **Django-powered Sales and Inventory Management System** built for onsite retail, cafés, or kiosk-style businesses — combining a robust backend, CDN-optimized frontend, and a reusable **Atomic Design Component System (Atoms → Molecules → Organisms)**.

The goal is to digitize walk-in transactions while maintaining **speed, modularity, and transparency** — customers order seamlessly, cashiers process instantly, and admins manage the business with analytics and audit visibility.

---

## 👥 User Roles

| Role                    | Description                                           | Key Functions                                                                                                                                     |
| ----------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧑‍💼 **Admin**         | Manages all system resources, users, and analytics.   | - CRUD for products<br>- Stock management<br>- Manage users (Admin/Cashier)<br>- View analytics<br>- View audit logs & archives                   |
| 💰 **Cashier**          | Operates the POS terminal and handles walk-in orders. | - View all orders<br>- Process cash payments<br>- Mark orders as finished<br>- View live order list                                               |
| 📱 **Customer (Guest)** | Orders directly through QR code access.               | - Scan QR → Open kiosk page<br>- Browse products<br>- Add to cart & checkout<br>- Pay online (demo) or at counter<br>- View order number & status |

---

## 🧠 System Overview

The system combines **Django backend logic** with **frontend modularity**.
It’s designed to be fast, maintainable, and scalable using:

* **Django ORM & Signals** for database actions and audit logs.
* **Static files served via CDN** for ultra-fast loading.
* **Reusable components** grouped by Atomic Design structure for maintainable UI.

---

| Layer         | Tech                                  | Why                                            |
| ------------- | ------------------------------------- | ---------------------------------------------- |
| Backend       | **Django 5 + SQLite/MySQL**           | Battle-tested, simple migrations, ORM built-in |
| Frontend      | **Django Templates + Tailwind (CDN)** | Server-rendered pages, no build step           |
| Interactivity | **HTMX + Alpine.js**                  | Light JS for modals, status refresh, etc.      |
| Design System | **Atomic Folder Layout**              | Organized templates for reuse                  |
| Auth          | **Django Auth + Groups**              | Built-in user/role management                  |
| Logging       | **Signals + Custom Audit Model**      | Tracks all changes transparently               |

---

## 📱 Customer (Kiosk) Flow

1. **QR Scan** → Opens kiosk URL (mobile web).
2. **Browse Products** → Only active items shown (non-archived).
3. **Add to Cart** → Stored in session until checkout.
4. **Checkout** → Choose payment method:

   * 💵 **Cash (at counter)** → `Payment: PENDING`
   * 💳 **Online Demo** → `Payment: SUCCESS (Simulated)`
5. **After Payment:**

   * Stock auto-deducts.
   * Order → `IN_PROGRESS`.
   * Customer gets order number & real-time status updates.

---

## 💰 Cashier Flow

1. Opens **POS interface** (cashier dashboard).
2. Views incoming `PENDING` orders.
3. Confirms **cash payments** → marks payment `SUCCESS`.
4. System deducts stock and moves order → `IN_PROGRESS`.
5. Marks completed orders as `FINISHED`.
6. Can print or show receipt summary if needed.

---

## 🧮 Admin Flow

1. Logs in to **Admin Dashboard**.
2. Manages all **products, users, and reports**.
3. Can **increase/decrease stock** directly (no restock table).
4. Archives items or users instead of deleting.
5. Monitors sales analytics:

   * Total sales & revenue
   * Best-selling products
   * Low-stock warnings
   * Cashier performance
6. All admin actions (CRUD, payments, stock changes) are logged in **AuditTrail**.

---

## 🔄 Order & Payment Lifecycle

| Step               | Description                             | Trigger                        |
| ------------------ | --------------------------------------- | ------------------------------ |
| **1. Pending**     | Order placed, unpaid                    | Customer checkout              |
| **2. In Progress** | Payment successful                      | Cashier/online payment success |
| **3. Finished**    | Order fulfilled                         | Cashier marks as done          |
| **4. Cancelled**   | (Optional) Order voided, stock restored | Manual action by admin/cashier |

**Payment Flow:**

* Cash payments → created by cashier.
* Online demo payments → simulated automatically.
* All payments recorded in `Payment` table for analytics.

---

## 📦 Inventory Logic

* Each product holds current `stock` and `threshold`.
* When a successful payment occurs → system **auto-deducts stock**.
* When stock < threshold → triggers **low-stock alert** in dashboard.
* Admins can manually adjust stock quantities anytime.
* Archived products are hidden from Kiosk & POS.

---

## 🕵️ Audit Trail

* Every major action is recorded (User, Action, Table, Record, Timestamp).
* Includes data snapshot in JSON for full traceability.
* Created via **Django signals** for automatic logging.

**Example Logs:**

* “Admin1 updated stock of Product #32 (20 → 45)”
* “Cashier2 marked Payment #145 as SUCCESS”
* “Admin archived Product #9”

---

## 📁 Archive System

* Prevents permanent deletion of important records.
* Archived entries are copied as JSON snapshots in the `Archive` table.
* Includes who archived it and when.
* Admin can restore records manually if needed.

---

## 📊 Analytics Overview

Admins can view:

* 💵 Total sales (daily/weekly/monthly)
* 📦 Top-selling products
* ⚠️ Low-stock alerts
* 👤 Cashier performance & transactions
* 🕒 Audit activity timeline

Lightweight charts (Chart.js or ApexCharts via CDN) display data dynamically.

---

## 🎨 Frontend Structure (Atomic Design)

| Level         | Description                | Example                                 |
| ------------- | -------------------------- | --------------------------------------- |
| **Atoms**     | Smallest reusable UI parts | Buttons, Inputs, Badges                 |
| **Molecules** | Combinations of atoms      | Product Card, Order Row, Modal          |
| **Organisms** | Full UI sections           | POS Table, Kiosk Grid, Dashboard Panels |

This hierarchy ensures **consistency, maintainability, and reusability** across the Admin, Cashier, and Customer interfaces.

---

## ✅ MVP Scope

| Module               | Key Features                                           |
| -------------------- | ------------------------------------------------------ |
| **Customer (Kiosk)** | QR access, browse, cart, checkout, demo payments       |
| **Cashier (POS)**    | Order processing, cash payments, mark finished         |
| **Admin Dashboard**  | CRUD inventory, manage users, archive & analytics      |
| **Audit & Archive**  | Full action logs & non-destructive data storage        |
| **Analytics**        | Sales summaries, performance metrics, low-stock alerts |

---

## 🚀 Future Enhancements

* Real payment gateway integration (PayMaya / GCash API).
* Multi-branch inventory syncing.
* Real-time WebSocket updates for orders.
* Automated forecasting for restocking.
* Email/SMS receipt notifications.

---
