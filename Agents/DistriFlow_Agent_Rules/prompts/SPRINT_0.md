# SPRINT 0 — GIAO VIỆC BAN ĐẦU CHO 3 NGƯỜI

## Agent 1 / Admin & tích hợp
- Khởi tạo repo, Vite Vue TS app, FastAPI app, PostgreSQL compose, ESLint/Prettier/pytest, CI.
- Design tokens theo DS01/02, AppShell, layouts, Vue Router, Pinia auth, guarded routes, shared API client, OpenAPI contract draft.
- Auth + user roles + partner/SKU/warehouse/shipper master data skeleton.
- Bàn giao: FE trang login/admin shell dùng demo data, backend `/auth/me`, migrations đầu, tài liệu `.env.example`.

## Agent 2 / Retailer + Shipper
- Đọc đúng UI06/UI08–11 và M05–08, vẽ flow request → assignment → scan → 2 confirm.
- Dùng component shell đã chốt, tạo routes và màn mock typed cho retailer and shipper; xuất API cần có thành danh sách.
- Viết test spec TC03/TC05/TC06/TC07/TC08; tạo `handover` data contract, không tự thêm stock column.
- Bàn giao: màn UI có thể tương tác với mock, API request/response fixtures, PR xin review hợp đồng.

## Agent 3 / Supplier + Inbound/Inventory
- Đọc UI05, M03, M04, TC01/TC02/TC03/TC09.
- Tạo supplier routes/mock UI; định nghĩa bảng inbound/lines, inventory balance/ledger và transaction service; làm rõ owner_id.
- Trình Agent 1 migration/contract để merge tuần tự; đồng bộ inventory service interface cho Agent 2.
- Bàn giao: mock UI, API draft, test transaction giữ/nhập xuất, data seed.

## Kết quả Sprint 0 dùng để mở khóa phát triển đồng thời
- Một source-of-truth nghiệp vụ, 1 schema/status enum, 1 design system, 1 API naming convention, 1 contract version, 1 env dev.
- Chỉ sau review và chốt các ranh giới này mới triển khai song song P0; không dựng 3 frontend riêng.
