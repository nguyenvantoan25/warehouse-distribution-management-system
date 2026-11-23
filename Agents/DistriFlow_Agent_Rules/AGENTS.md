# AGENTS.md — QUY TẮC BẮT BUỘC DỰ ÁN DISTRIFLOW

> Áp dụng cho Codex, Cursor, Claude Code, Copilot, hoặc AI coding agent đọc được tệp hướng dẫn repo.
> Agent phải đọc file này trước khi đọc code và trước khi viết/sửa file.

## 0. Mục tiêu và thứ tự ưu tiên
1. Mục tiêu: website **bàn giao vận đơn/kiện điện tử giữa kho và shipper ngay tại kho**.
2. Nguồn nghiệp vụ bắt buộc: `reference-inputs/DistriFlow_Dac_ta_UC_Chi_tiet.xlsx`. Kiểm tra `Danh mục UC`, `Đặc tả UC`, `Giao diện`, `Quy tắc và trạng thái`, `Nghiệm thu` trước khi lập trình chức năng.
3. Nguồn UI tham khảo: `reference-inputs/DistriFlow Logistics Platform (1).zip` (React/Figma demo). CHỈ tham khảo bố cục/mẫu dữ liệu; KHÔNG dùng React, TSX, lucide-react, recharts hoặc giỏ hàng/ship đến khách cuối trong dự án Vue.
4. Thứ tự ưu tiên khi có xung đột: an toàn dữ liệu & nghiệp vụ Excel > API contract đã chốt > kiến trúc repo > design system chung > demo UI.
5. Không tự suy diễn phần thiếu. Ghi câu hỏi/giả định vào PR; không phát triển mô-đun P1 nếu P0 chưa chạy thông suốt.

## 1. Công nghệ đã chốt
- Frontend: Vue 3 + Vite + TypeScript, Composition API, `<script setup lang="ts">`, Vue Router, Pinia, Axios hoặc fetch wrapper duy nhất, Tailwind CSS v4, lucide-vue-next.
- Backend: Python 3.12 + FastAPI + Pydantic v2 + SQLAlchemy 2.x + Alembic + pytest.
- DB: PostgreSQL 16; PostgreSQL là **nguồn sự thật duy nhất**, không lưu trạng thái nghiệp vụ vĩnh viễn trong localStorage.
- API: REST `/api/v1`, JSON UTF-8, OpenAPI ở backend `/openapi.json`; dùng một contract cho 3 nhóm.
- Tooling: npm, ESLint, Prettier, vue-tsc, Vitest, Playwright, Ruff; Docker Compose cho môi trường dev nếu cần.
- Sử dụng đúng phiên bản đã pin trong repo, KHÔNG tự nâng version/package manager hoặc thêm thư viện tương đương trùng lặp.

## 2. Vai trò (RBAC) và phạm vi dữ liệu
- `WAREHOUSE_ADMIN` (quản trị kho), `DISPATCH_MANAGER` (điều phối), `RETAILER_OWNER` (nhà bán lẻ/chủ hàng), `SUPPLIER` (nhà cung cấp), `SHIPPER` (người nhận tại kho).
- Một tài khoản có thể được cấp nhiều vai trò; quyền còn phụ thuộc tổ chức, chủ hàng, kho, nhiệm vụ được giao.
- Nhà bán lẻ chỉ đọc/ghi dữ liệu thuộc chủ hàng của mình. Supplier chỉ xem yêu cầu nhập được gắn quan hệ cung ứng. Shipper chỉ thấy các nhiệm vụ đang/đã được gán đúng phạm vi.
- Frontend guard/ẩn nút để cải thiện UX; backend bắt buộc kiểm tra quyền TỪNG endpoint và TỪNG bản ghi; không tin `owner_id`, `role`, `user_id` từ client.
- Không thêm vai trò `DISTRIBUTOR` độc lập trước khi nhóm thống nhất UC; trước mắt xem là subtype của `SUPPLIER`.

## 3. Bất biến nghiệp vụ (không được vi phạm)
- Mỗi dòng tồn phải thuộc **một nhà bán lẻ/chủ hàng** xác định.
- `on_hand = available + reserved + other_unavailable`; ba phần không chồng nhau; không số âm; không cộng SKU/đơn vị khác nhau.
- Gửi yêu cầu xuất KHÔNG giữ hàng. Duyệt xuất phải giữ đúng số lượng bằng giao dịch DB chống tranh chấp đồng thời.
- Soạn, đóng gói và quét QR KHÔNG trừ tổng tồn.
- Chỉ khi **kho và shipper được phân công hợp lệ đều xác nhận cùng phiên bản bàn giao**, server mới chốt MỘT transaction: ghi xuất, giảm tồn tổng, giảm giữ, chuyển trạng thái, tạo một biên bản.
- Thao tác retry/idempotent: một handover được ghi xuất **đúng một lần** kể cả gửi lặp hoặc mất phản hồi. Dùng unique constraint + transaction + idempotency key.
- Đổi shipper/sửa danh sách kiện làm mất hiệu lực phiên và xác nhận cũ. QR là định danh kiện, KHÔNG phải chứng thực/quyền.
- Từ chối shipper do đại lý chỉ định KHÔNG tự chuyển sang phương án DistriFlow điều phối.
- Không tự xuất một phần P0; thiếu/sai kiện thì khóa tiến trình, ghi sự cố, xử lý theo UC.
- Mất mạng/timeout trên shipper => “Chưa đồng bộ/Đang kiểm tra”, KHÔNG tuyên bố thành công khi chưa xác minh server.
- Chứng từ đã hoàn tất và lịch sử giao dịch không xóa/sửa trực tiếp. Sai lệch xử lý bằng chứng từ/correction có audit.
- Không triển khai giao tận người mua, thu hộ COD, thanh toán, giỏ hàng bán lẻ hay bản đồ định vị shipper nếu chưa được bổ sung UC.

## 4. Cấu trúc code và ranh giới sở hữu
- `frontend/src/app`, `frontend/src/shared`, `frontend/src/router`, `frontend/src/styles`: **shared** — mọi thay đổi cần PR và review nhóm.
- `frontend/src/features/admin`: Agent 1.
- `frontend/src/features/retailer`, `frontend/src/features/shipper`: Agent 2.
- `frontend/src/features/supplier`: Agent 3.
- `backend/app/modules/auth`, `catalog`, `platform`: Agent 1.
- `backend/app/modules/outbound`, `dispatch`, `handover`: Agent 2.
- `backend/app/modules/inbound`, `inventory`: Agent 3.
- `backend/alembic/versions`, `contracts`, `backend/app/core`: chỉ Agent 1/integration owner merge sau review domain owner; agent khác gửi PR đề xuất thay đổi.
- Cấm agent sửa module của người khác để “fix nhanh” mà không có sự đồng ý/PR.

## 5. Chuẩn FE bắt buộc — dùng `docs/03-FE-DESIGN-SYSTEM.md`
- Dùng một design system với token CSS, một `AppShell`, `PageHeader`, `DataTable`, `StatusBadge`, `ConfirmDialog`, `DetailDrawer`, `BaseInput`, `EmptyState`, `LoadingState`, `ErrorState`.
- Desktop tham chiếu 1440px, sidebar 240px, header 64px; mobile shipper tham chiếu 390px, chính một cột, nút chính 48–52px.
- Màu theo Excel: primary `#087F8C`, sidebar `#172B3A`, background `#F4F6F8`, body font sans Việt 14–16px.
- Mỗi trang phải có loading, empty, error, forbidden, success; button disabled có lý do; dữ liệu bắt nguồn API/domain store.
- Shipper có ĐÚNG bốn nav mobile: **Nhiệm vụ | Quét mã | Lịch sử | Tài khoản**; chuông thông báo riêng.
- Nhãn `Nhận nhiệm vụ` khác với `Xác nhận nhận hàng`; quét sai/trùng không tăng tiến độ.
- Ưu tiên component chia nhỏ; không tạo file App.vue chứa hàng nghìn dòng hoặc copy code layout cho 3 vai trò.
- Không dùng mảng mock/hardcode ở component sau khi đã có API; nếu mock để unblock thì giữ trong `mocks/` và đánh dấu rõ.

## 6. Chuẩn API, dữ liệu, bảo mật
- API DTO và status enum định nghĩa một lần trong `contracts/openapi.yaml`/OpenAPI backend; frontend dùng types sinh từ schema hoặc khai báo type tập trung.
- Kết quả lỗi thống nhất `{ "error": { "code": "...", "message": "...", "details": {} }, "request_id": "..." }`.
- Phân trang/filter/sort thống nhất; dùng ISO-8601 timezone offset hoặc UTC; DB `timestamptz`, giá trị thời gian hiển thị theo người dùng; ID UUID.
- Giao dịch tồn và bàn giao dùng SQL transaction, lock thích hợp, unique constraints và audit; không giải quyết bằng state phía client.
- Không commit `.env`, mật khẩu, cookie/token, tài khoản thật hoặc connection string production.
- Validate dữ liệu đầu vào ở API, enum trạng thái, ràng buộc FK/unique/check; password hash dùng thuật toán phù hợp; xác thực phiên có cơ chế thu hồi khi khóa tài khoản.
- API quyền theo role + record scope, CSRF nếu dùng cookie auth; CORS theo danh sách origin, không dùng wildcard cho credential.

## 7. Quy trình agent thực hiện mỗi task
1. Đọc mô tả task, UC ID/UI ID/độ ưu tiên, và file liên quan. Chỉ rõ **actor, precondition, happy path, errors, state transitions, stock impact**.
2. Xem cấu trúc code hiện tại, kiểm tra code/contract có sẵn; KHÔNG tự viết lại thư viện chung.
3. Lập kế hoạch ngắn gồm file sẽ sửa, API cần dùng, test cần chạy. Nếu chạm phạm vi người khác, tạo proposal trước.
4. Triển khai theo đúng feature folder và reuse UI component; route có auth/role guard.
5. Có unit test + API/integration test khi chạm nghiệp vụ; tạo E2E cho P0 quan trọng. Test quyền chéo người dùng.
6. Chạy FE lint/typecheck/test/build và BE lint/test/migration tùy phạm vi; nếu không chạy được phải nêu rõ.
7. Nộp PR có UC ID, ảnh chụp FE, API đã tích hợp, tác động DB, checklists, demo steps, giới hạn còn lại.
8. Không được nói "đã hoàn thành" nếu chỉ có giao diện mock hoặc màn hình tĩnh.

## 8. Tiêu chuẩn hoàn thành và cấm đoán
- P0 chính: tạo nhập → duyệt/kiểm nhận/xếp vị trí → thấy tồn đúng chủ hàng → yêu cầu xuất → duyệt giữ → soạn/đóng kiện → tạo/gán nhiệm vụ → shipper nhận việc/quét đủ kiện → hai xác nhận → biên nhận → số tồn chính xác.
- Mỗi hành động thay đổi trạng thái phải có trạng thái trước/sau và lịch sử kiểm toán; không sửa số tồn trực tiếp từ UI.
- Không lược bỏ test gửi lặp, mất mạng, chủ hàng khác, shipper khác, thiếu kiện, khóa hàng đã giữ.
- Không tự merge `main/master`, không push force vào nhánh chung, không viết cả 3 phần chung một branch.
- Đọc thêm tài liệu chi tiết trong `docs/` và prompt vai trò tương ứng trong `prompts/`.
