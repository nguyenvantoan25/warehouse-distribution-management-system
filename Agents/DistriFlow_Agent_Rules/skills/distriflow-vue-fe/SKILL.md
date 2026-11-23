---
name: distriflow-vue-fe
description: Build or review consistent Vue 3 + Vite + TypeScript frontend pages for the DistriFlow warehouse-to-shipper electronic handover project. Use when implementing admin, supplier/distributor, retailer/dealer, dispatcher, or shipper mobile screens; mapping Excel UC/UI IDs to Vue pages; or reviewing shared components, role scopes, loading states, responsive design, and FE integration with the Python FastAPI + PostgreSQL backend.
---

# DistriFlow Vue FE — Frontend Skill

## Operating procedure
1. Read the repository `AGENTS.md` when available. Read `references/01-domain-and-ui-map.md` for actor, module and UI ownership. For specific UC behavior, read `references/source/DistriFlow_Dac_ta_UC_Chi_tiet.xlsx` (tabs `Danh mục UC`, `Đặc tả UC`, `Giao diện`, `Quy tắc và trạng thái`, `Nghiệm thu`). Treat that Excel as authoritative.
2. Identify assigned actor, UC IDs, UI IDs and P0/P1. Do not silently add order delivery to end customer, cart/checkout, COD or payment. “Nhà phân phối” has no independent actor in P0; treat as supplier organizational subtype until approved.
3. Read `references/02-design-system.md` for all UI requirements. Use Vue 3 SFC `<script setup lang="ts">`, Vue Router, Pinia, typed HTTP service, shared layout/components, Tailwind CSS v4 and lucide-vue-next.
4. Apply role & record-scope guards; actual permission enforcement is the responsibility of Python backend. Never rely on hidden buttons or client-submitted owner ID.
5. For every screen: implement loading, empty, error, forbidden, success, validation; mobile shipper also pending-sync/checking. Use server events/statuses as the source of truth, not fake counters.
6. Respect FE ownership: Admin/shared shell Agent 1, Retailer + Shipper Agent 2, Supplier Agent 3. Changing shared components/routing requires integration-owner review.
7. Read `references/03-api-and-auth.md` for API conventions before integration. Never mutate stock locally. Dual-confirmation handover is server-authoritative and idempotent.
8. Read `references/04-quality-and-acceptance.md` when writing tests or declaring done. Run lint, vue-tsc, unit tests and build; add screenshot/steps and end-to-end verification for P0.

## Critical user-facing terminology
- `Nhận nhiệm vụ`: shipper accepts assignment, NOT physical goods handover.
- `Xác nhận nhận hàng`: shipper acknowledges receiving physical packages; system completes after BOTH valid warehouse and shipper confirmations.
- `Tồn ghi sổ = Khả dụng + Giữ cho đơn + Không khả dụng khác`. Picking, packing, scanning do NOT subtract total stock.
- `Chưa đồng bộ / Đang kiểm tra`: mandatory when shipper confirmation result is unknown due to network failure; never show success without server validation.
- Shipper mobile navigation has only four tabs: `Nhiệm vụ`, `Quét mã`, `Lịch sử`, `Tài khoản`.

## Return format after coding
Summarize UC/UI IDs, files changed, API endpoints integrated, screenshots/responsive checks, automated test results, unresolved mocks, and any handoff needed from another agent. If code execution is unavailable, explicitly mark checks as not run.
