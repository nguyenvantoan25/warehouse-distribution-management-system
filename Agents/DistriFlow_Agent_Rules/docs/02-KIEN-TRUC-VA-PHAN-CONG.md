# 02 — Kiến trúc mono-repo & phân công

## Một repo, một FE, một BE, một PostgreSQL

```
distriflow/
  AGENTS.md
  docs/
  prompts/
  contracts/
    openapi.yaml                # bản hợp đồng chốt; đồng bộ từ FastAPI
  frontend/
    package.json
    src/
      main.ts
      App.vue
      app/                       # app shell, bootstrap, permissions
      router/                    # routes + guards
      styles/                    # tokens.css, tailwind imports
      shared/
        api/                     # duy nhất http client, error handler
        components/              # Base*, DataTable, StatusBadge, etc.
        composables/
        types/                   # types dùng chung/generate OpenAPI
      features/
        admin/                   # Agent 1: pages, components, services
        retailer/                # Agent 2
        shipper/                 # Agent 2
        supplier/                # Agent 3
      mocks/                     # mock chỉ trong dev & tests
    tests/
  backend/
    app/
      main.py
      core/                      # db, config, auth middleware, errors
      modules/
        auth/                    # Agent 1
        catalog/                 # Agent 1
        platform/                # Agent 1; reports/notifications/audit
        inbound/                 # Agent 3
        inventory/               # Agent 3
        outbound/                # Agent 2
        dispatch/                # Agent 2
        handover/                # Agent 2
    alembic/versions/           # merge-only Agent 1
    tests/
  infra/
    compose.yaml
    .env.example
  .github/
    pull_request_template.md
    workflows/ci.yml
```

## Stack được khuyến nghị (quyết định dự án, không phải ràng buộc từ Excel)
- Vue 3 SFC + Composition API + TypeScript + Vite, Pinia, Vue Router; Tailwind CSS v4, lucide-vue-next.
- Dùng `npm create vue@latest` và bật TypeScript, Router, Pinia, Vitest, ESLint, Prettier, E2E Playwright. `npm run type-check` phải chạy riêng (Vite build không tự type-check).
- Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, Alembic, `psycopg`, pytest; có dependency version lock.
- PostgreSQL 16, migrate bằng Alembic, Docker Compose cho dev; không chạy `create_all()` thay cho migrations ở production.
- Không cần microservices, Redis, Kafka, WebSocket cho P0. Có thể dùng HTTP polling nhẹ cho notifications; chỉ thêm khi chứng minh nhu cầu.

## Ownership có một người chịu trách nhiệm cuối
| Phần | Owner | Người tích hợp/phụ thuộc |
|---|---|---|
| App shell/auth/catalog/router/design tokens | 1 | 2,3 đều dùng |
| Admin nhập, tồn, xuất, bàn giao, điều phối, reports | 1 FE | API 2,3 |
| Retailer portal + shipper mobile | 2 FE | auth 1; stock 3 |
| Xuất, nhiệm vụ, phiên bàn giao & biên nhận | 2 BE | auth 1, stock ledger 3 |
| Supplier portal | 3 FE | auth/catalog 1 |
| Nhập, phân vị trí, stock ledger, giữ/xuất tồn | 3 BE | dùng bởi 1,2 |
| Migration ordering, shared DTO, CI, code review API breaking | 1 (integration) | cả nhóm review |

## Thỏa thuận giữa BE2 và BE3
- Inventory service expose các hàm transaction-aware với SQLAlchemy Session truyền vào (`reserve_stock`, `release_reservation`, `issue_reserved_stock`, `get_owner_balance`).
- Handover service (Agent 2) giữ lock trên đúng handover/session, xác thực đủ điều kiện, gọi `issue_reserved_stock(session, ...)` và tạo receipt trong **cùng SQL transaction**. Hàm inventory không commit riêng.
- Cần unique idempotency guard và ledger posting. Agent 1 review migration trước merge.

## Đối chiếu route FE đề xuất
- `/login`
- `/admin/dashboard`, `/admin/inbounds`, `/admin/inventory`, `/admin/outbounds`, `/admin/handovers`, `/admin/dispatch`, `/admin/catalog`, `/admin/users`, `/admin/reports`
- `/retailer/dashboard`, `/retailer/inventory`, `/retailer/outbound-requests`, `/retailer/documents`
- `/supplier/dashboard`, `/supplier/inbound-requests`, `/supplier/inbound-requests/new`, `/supplier/receipts`
- `/shipper/tasks`, `/shipper/tasks/:id`, `/shipper/scan`, `/shipper/history`, `/shipper/profile`
- Không tạo 4 ứng dụng Vite riêng; dùng layouts theo vai trò, một router và một auth store.

## Đồ thị phụ thuộc triển khai

```
Auth / Roles / Catalog (Agent 1)
       |                     \
Inbound + Inventory (Agent 3)  Retailer request (Agent 2)
       |                      /
Stock reservation service ----/
       |                     \
Admin picking & packing (A1 UI + A2 API)
       |                           \
Dispatch & Shipper (A1 UI + A2 API/mobile)
       |                            \
Dual confirmation + receipt (A2), stock posting (A3)
       |
Reports, notifications, end-to-end acceptance
```

## Thỏa thuận trước khi làm song song
- Khóa `organization_id`, `owner_id`, `warehouse_id`, `sku_id`, `request_id`, `handover_id` và enum status.
- Đồng ý cách auth và phân quyền trên server, cách trả lỗi và pagination, ranh giới workflow của 2 phương án shipper.
- Agent 1 tạo skeleton và 6 shared component trước, rồi mở PR sớm; không buộc Agents 2/3 chờ toàn bộ backend hoàn thành: phát triển theo contract và typed mocks.
- Họp tích hợp sau mỗi vertical slice, không chờ tới cuối kỳ mới merge.
