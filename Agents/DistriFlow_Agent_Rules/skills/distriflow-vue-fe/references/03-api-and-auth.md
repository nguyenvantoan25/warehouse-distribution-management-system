# 04 — Hợp đồng API & mô hình dữ liệu PostgreSQL

> Đây là **đề xuất kỹ thuật** để AI coding agents làm việc nhất quán; không phải endpoint đã tồn tại trong bản demo React. Hãy chốt contract này trước triển khai và sinh OpenAPI thật từ backend.

## REST API v1 (gợi ý)
| Method | Route | Actor chính | Gắn UC |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Mọi người | M01.01 |
| GET | `/api/v1/auth/me` | Mọi người | M01.01 |
| GET/POST | `/api/v1/admin/users` | Quản trị kho | M01.02 |
| GET/POST | `/api/v1/partners`, `/skus`, `/warehouses`, `/shippers` | Theo quyền | M02 |
| GET/POST | `/api/v1/inbound-requests` | Supplier / kho theo phạm vi | M03.01, M03.06 |
| POST | `/api/v1/inbound-requests/{id}/submit` | Supplier | M03.01 |
| POST | `/api/v1/inbound-requests/{id}/review` | Kho | M03.03 |
| POST | `/api/v1/inbound-requests/{id}/receive` | Kho | M03.04 |
| POST | `/api/v1/inbound-requests/{id}/putaway` | Kho | M03.05 |
| GET | `/api/v1/inventory/balances`, `/inventory/movements` | Kho/chủ hàng | M04.01–02 |
| POST | `/api/v1/inventory/holds` | Kho | M04.06 |
| GET/POST | `/api/v1/outbound-requests` | Chủ hàng/kho theo phạm vi | M05.01–03 |
| POST | `/api/v1/outbound-requests/{id}/approve` | Kho | M06.01 |
| POST | `/api/v1/outbound-requests/{id}/pick` | Kho | M06.02 |
| POST | `/api/v1/outbound-requests/{id}/pack` | Kho | M06.03 |
| GET/POST | `/api/v1/pickup-tasks` | Điều phối/shipper theo quyền | M07.01–04, M08.01 |
| POST | `/api/v1/pickup-tasks/{id}/assign` | Điều phối | M07.02–03 |
| POST | `/api/v1/pickup-tasks/{id}/respond` | Đúng shipper | M08.01 |
| POST | `/api/v1/pickup-tasks/{id}/arrive` | Đúng shipper | M08.02 |
| POST | `/api/v1/handover-sessions/{id}/scan` | Đúng shipper | M08.03 |
| POST | `/api/v1/handover-sessions/{id}/warehouse-confirm` | Kho | M06.04 |
| POST | `/api/v1/handover-sessions/{id}/shipper-confirm` | Đúng shipper | M08.04 |
| GET | `/api/v1/handover-sessions/{id}/receipt` | Người có quyền | M05.05/M08.06 |
| GET | `/api/v1/dashboard`, `/api/v1/reports/inventory` | Theo quyền | M09.01–02 |
| GET | `/api/v1/notifications` | Theo quyền | M10.01 |

**Chốt route cụ thể sau review.** Đừng để mỗi agent tự đặt tên route khác nhau; frontend dùng API client sinh ra từ OpenAPI để hạn chế lệch kiểu.

## API conventions
- Header: `Authorization: Bearer ...` **hoặc** secure HttpOnly session cookie + CSRF, chốt **một** phương án. Không cho bearer JWT cố định trong localStorage; ưu tiên cookie HttpOnly + CSRF khi frontend/backend cùng domain.
- `Content-Type: application/json`; timestamps ISO 8601 UTC, API error tiếng Việt dễ hiểu, machine code tiếng Anh; `request_id` cho tracing.
- Write endpoint POST phải validate trước/sau và authorization; idempotent command dùng `Idempotency-Key` UUID và giữ nguyên key khi retry cùng operation.
- HTTP statuses thống nhất: 200/201 thành công, 400 dữ liệu lỗi, 401 chưa auth, 403 forbidden, 404 không tồn tại/không trong phạm vi, 409 trạng thái/phiên conflict, 422 validation, 500 lỗi máy chủ.
- Pagination chung `page`, `page_size`; response `{items, page, page_size, total}`. Filter owner/warehouse xử lý ở server, không để client thao tác owner tùy ý.
- `version` optimistic concurrency cho chứng từ/phiên. Handover version mismatch -> 409 và yêu cầu reload.
- Thành công tạo receipt trả về **receipt_id**, **stock movement id**, trạng thái `handed_over` từ DB; không trả success giả từ client.

## Ví dụ minh họa (đề xuất, không phải dữ liệu sản phẩm có thật)
```json
{
  "handover_session_id": "76e3cdb1-9557-4c95-9ddb-423286f1e44f",
  "version": 2,
  "pickup_task_id": "188d9ed8-e5e0-4db5-8323-317e9ca8cd0f",
  "assigned_shipper_id": "8b11d3d4-a37f-4ab4-8b02-c30e42ab433c",
  "package_codes": ["K1", "K2", "K3"],
  "warehouse_confirmed": true,
  "shipper_confirmed": false,
  "status": "pending_confirmations"
}
```
- Shipper confirm hợp lệ trên cùng version -> nếu chưa bị thay đổi thì server ghi xuất 1 lần, tạo biên nhận và trả status `handed_over`.
- Khi timeout: FE GET session/idempotency result trước khi retry. Nếu unknown, hiển thị `pending_sync`/`checking`.

## Schema quan hệ tối thiểu (đề xuất cho P0)
| Bảng | Các cột/chìa khóa chính (khái niệm) | Ghi chú |
|---|---|---|
| organizations | id, type, name, status | SUPPLIER, RETAILER, WAREHOUSE_OPERATOR... |
| users | id, email unique, password_hash, active | khóa shipper áp dụng ngay |
| user_memberships | user_id, organization_id, role, warehouse_scope | role + owner + assignment |
| supply_relationships | supplier_id, owner_id, sku_id | Supplier chỉ chọn chủ hàng được phép |
| skus | id, code unique, base_unit, owner_id? | quyết định SKU global/owner ở ADR |
| warehouses / locations | id, warehouse_id, location_code | lưu vị trí nhận/soạn |
| inbound_requests / inbound_lines | id, supplier_id, owner_id, warehouse_id, status, qty | số planned/received/accepted/quarantined |
| inventory_balances | id, owner_id, sku_id, warehouse_id, location_id, lot_id?, on_hand, reserved, unavailable | CHECK >= 0 và công thức |
| stock_movements | id, kind, quantity, owner_id, source_doc_id, idempotency_key unique? | immutable ledger, traceable |
| stock_reservations | id, outbound_line_id, balance_id, qty, state | không overbook |
| outbound_requests / outbound_lines | id, owner_id, shipper_mode, status, version | chỉ duyệt mới giữ |
| packages / package_items | id, code unique, outbound_id, version, qty | snapshot kiện |
| pickup_tasks / assignments | id, outbound_id, shipper_id, status, version | chỉ 1 assignment hiện hành |
| handover_sessions | id, outbound_id, pickup_task_id, version, status | row lock khi confirm |
| handover_confirmations | id, session_id, side, actor_id, version, at | UNIQUE(session,side,version) |
| handover_receipts | id, session_id unique, number unique, issued_at | 1 receipt cho 1 session |
| idempotency_requests | id, actor_id, key unique within scope, request_hash, response_data | retry an toàn |
| audit_logs | id, actor_id, object_type, object_id, before/after, at | append-only |
| notifications | id, recipient_id, event_type, read_at | triggered by domain events |

## Bất biến transaction SQL bắt buộc
```text
reserve(q):
  BEGIN; SELECT target balance FOR UPDATE;
  assert available >= q;
  reserved += q; available -= q;
  create reservation + audit; COMMIT;

handover_confirm(side, session_id, version, idempotency_key):
  BEGIN; check idempotency cache / lock handover_session FOR UPDATE;
  check permissions + assigned shipper + package snapshot/version;
  upsert this side confirmation with unique(session_id, side, version);
  IF both valid AND receipt absent:
     lock reservation/balances;
     apply stock issue: on_hand -= qty; reserved -= qty;
     insert immutable stock movement UNIQUE(source_handover_id, kind);
     insert handover_receipt UNIQUE(session_id);
     mark outbound/task/session handed_over;
  store idempotent result; COMMIT;
```
- Khi một bên confirm trước, không đổi tồn. Khi hai bên confirm đủ, tổng tồn và giữ cùng giảm; khả dụng **không đổi**.
- Transaction isolation + locks/quy trình đặt lock theo thứ tự nhất quán để tránh deadlock; validate concurrent race với 2 yêu cầu xuất.
- Không có hoạt động update theo kiểu `UPDATE inventory SET on_hand=...` từ frontend hoặc bất kỳ controller nào không qua domain service.

## Chuẩn an toàn & kiểm tra
- Không log plaintext password/access token hoặc QR nhạy cảm; kiểm soát rate-limit login, ghi audit tạo/sửa/duyệt/xác nhận.
- Đối tượng thuộc chủ hàng khác: trả 403/404 nhất quán, không lộ tên/đơn khác trong lỗi quét QR.
- Alembic migrations có `upgrade`/`downgrade` phù hợp và review trước merge; seed **demo** tách production data.
- Không kết nối trực tiếp FE với PostgreSQL; chỉ qua FastAPI.
