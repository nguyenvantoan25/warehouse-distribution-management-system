# warehouse-distribution-management-system
A web-based system for warehouse operations, inventory tracking, order fulfillment, and last-mile delivery management.
# Warehouse & Distribution Management System (WDMS)

**Project Status:** In Development  
**Project Type:** Team-based Web Application

## Overview

The Warehouse & Distribution Management System (WDMS) is a web-based logistics management platform designed to streamline warehouse operations, inventory control, wholesale order fulfillment, and last-mile delivery management.

The system connects suppliers, warehouse staff, wholesale customers, and delivery personnel through centralized business workflows and a shared backend.

## Planned Core Features

### Warehouse Management
- Supplier purchase order management
- Barcode-based goods receiving and outbound verification
- Inventory tracking by warehouse storage location
- Stock transfers, adjustments, and inventory audits
- Inbound and outbound order processing

### Wholesale Order Management
- Product catalog and wholesale ordering
- Order approval and stock reservation
- Picking, packing, and shipment preparation
- Order status tracking

### Delivery Management
- Courier assignment and shipment handover
- GPS-assisted delivery tracking
- Barcode-based shipment verification
- Proof of delivery and failed delivery handling

### Administration
- Role-based access control (RBAC)
- Operational dashboards and reporting
- Notifications and activity logs

## User Roles

1. **System Administrator** — Manages users, products, warehouse operations, orders, and delivery assignments.
2. **Warehouse Staff** — Handles receiving, picking, packing, inventory updates, and shipment handovers.
3. **Supplier** — Reviews and confirms supply requests.
4. **Retailer / Wholesale Customer** — Places wholesale orders and tracks shipments.
5. **Courier** — Collects shipments, updates delivery progress, and confirms deliveries.

## Planned Architecture

The project follows a monorepo structure containing three web portals, a shared backend API, and a centralized database.

- **Internal Portal:** Administrator and warehouse staff
- **Partner Portal:** Suppliers and wholesale customers
- **Delivery Portal:** Couriers and delivery operations

## Development Workflow

- `main` — Stable releases
- `develop` — Integration branch
- `feature/*` — Individual development tasks

Changes are submitted through GitHub Pull Requests for collaborative review and integration.

## Technology Stack

To be finalized during implementation.

## Project Goal

To build a centralized system that improves inventory visibility, warehouse operational accuracy, order processing efficiency, and shipment traceability.
