# 05 — Quy trình triển khai 3 thành viên và nghiệm thu

## Nguyên tắc nhánh Git
- `main`: ổn định và demo cuối; `develop`: bản tích hợp; mỗi agent tạo feature từ `develop`.
- `feat/admin` / `feat/retailer-shipper` / `feat/supplier-distributor`; chia tiếp `feat/<area>-<uc-id>` nếu cùng owner làm nhiều task để PR nhỏ.
- Quy tắc merge: mở PR vào `develop`; check CI + ít nhất 1 reviewer không phải tác giả; schema hoặc shared component có owner review; **không force push nhánh chung**.
- Commit: `feat(admin): M06.02 picking screen`, `fix(handover): M06.04 idempotent finalize`, `test(inventory): TC03 concurrent reservation`.
- Khuyến nghị CODEOWNERS để review tự động (nhưng vẫn tránh bottleneck bằng thỏa thuận người thay thế).

## Kịch bản triển khai theo vertical slices
### Slice 0 — Nền tảng (cả nhóm phối hợp)
- Tạo Vue/Vite TS và FastAPI/PostgreSQL/Alembic skeleton; compose dev; CI; README; `.env.example` không secrets.
- Chốt source-of-truth, role/owner scope, API errors/pagination, enum states, cơ chế idempotency, design tokens.
- Agent 1: shell/auth + shared UI. Agent 2: typed API mocks retail/shipper. Agent 3: typed API mocks supplier/inbound.

### Slice 1 — Nhập kho và tồn (P0)
- Agent 3: M03 inbound API + inventory ledger và service; unit/integration tests.
- Agent 1: M03 UI admin + M04 tồn; Agent 3: M03 supplier UI. Demo một lô nhập thành tồn chính xác.

### Slice 2 — Yêu cầu xuất + giữ hàng (P0)
- Agent 2: M05, M06 API approve/reserve; Agent 1: admin duyệt/soạn; Agent 2: retail portal.
- Test tranh tồn, phân quyền chủ hàng, không trừ tồn khi chỉ soạn/đóng gói.

### Slice 3 — Điều phối + mobile + biên bản (P0)
- Agent 2: M07/08 + handover API. Agent 1: desktop điều phối và xác nhận kho; Agent 2: shipper mobile + scan/confirm.
- Agent 3: inventory issue trong cùng transaction + idempotency. Test 2 xác nhận, retry, mất mạng.

### Slice 4 — Reports, notifications, hardening
- Agent 1: M09.01–02, M10.01 từ DB thật; cả nhóm chạy end-to-end/P0; P1 sau đó.

## 10 test kịch bản nguồn Excel (chưa được chạy thực tế)
| Test | Kịch bản | Đầu ra quan trọng |
|---|---|---|
| TC01 | Nhập kho đúng kế hoạch | Chỉ hoàn tất nhập mới tạo tồn |
| TC02 | Nhập có sai lệch | Chênh số tốt/hỏng/cách ly/thiếu và owner đúng |
| TC03 | Hai đơn tranh cùng tồn | Lock ngăn giữ vượt khả dụng |
| TC04 | Soạn hàng và đóng gói | Soạn xong, total on_hand không giảm |
| TC05 | Hai phương án shipper | Gán đúng người, không đổi mode tùy tiện |
| TC06 | Mã kiện sai hoặc trùng | 3 kiện; sai/trùng không tăng tiến độ |
| TC07 | Bàn giao hai bên và gửi lặp | 1 biên bản, 1 stock posting |
| TC08 | Mất mạng khi nhận hàng | Không giả thành công, reconnect đối chiếu |
| TC09 | Khóa hàng đã được giữ | Giữ/khóa không chồng lấn, dừng đơn |
| TC10 | Đổi shipper trước bàn giao (P1) | Phiên cũ hết hiệu lực, người mới quét lại |

## Quality gates
- FE: `npm run lint`, `npm run type-check`, `npm run test:unit`, `npm run build`, Playwright E2E main flows.
- BE: `ruff check .`, `pytest`, API contract checks, `alembic upgrade head` từ DB trắng, test DB PostgreSQL thật cho concurrency.
- QA: test role/record scope; validation; forged owner/shipper ID; idempotent retry; status mismatch; browser mobile.
- Trường hợp môi trường không có script nào, agent phải thêm script đúng rồi chạy thay vì báo giả “đã test”.

## Definition of Done cho một UC
- Tài liệu: UC ID, priority, actor, state pre/post, error, API mapping, UI mapping.
- UI: không trùng component, có loading/empty/error, responsive theo device, text tiếng Việt, role guard.
- Backend: endpoint thật, auth/record permission, validation, transaction và audit; DB migration đã review.
- Test: happy path + edge cases + quyền; với P0 quan trọng phải có integration/E2E.
- Demo: thao tác thật từ trình duyệt qua API và PostgreSQL, dữ liệu có thể tái tạo bằng seed.
- Nhận xét: thiếu API/test => trạng thái “FE demo” hoặc “chưa tích hợp”, không được ghi “hoàn thành”.

## Họp và bàn giao
- Tối thiểu mỗi buổi/sprint cập nhật: việc đã merge, UC chạy, chặn bởi ai, API thay đổi, migration pending, test fail.
- Mỗi PR tối đa một nhóm chức năng và mô tả screenshot + test + cách reproduce.
- Tranh luận về nghiệp vụ phải dựa UC/BR ID từ Excel; quyết định mới đưa vào ADR, không im lặng sửa tài liệu gốc.
