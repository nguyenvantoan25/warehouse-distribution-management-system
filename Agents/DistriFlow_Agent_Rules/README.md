# DISTRIFLOW | Bộ quy tắc phát triển với 3 AI Coding Agents

**Đề tài:** Xây dựng Website quản lý bàn giao vận đơn điện tử giữa kho hàng và đơn vị vận chuyển.

## Đọc theo thứ tự
1. `AGENTS.md` — quy tắc bắt buộc cho mọi agent (đặt ở thư mục gốc repo mới).
2. `docs/01-PHAM-VI-VA-UC.md` — giới hạn đề tài, 50 UC, đối chiếu UI.
3. `docs/02-KIEN-TRUC-VA-PHAN-CONG.md` — stack, cây thư mục, ownership.
4. `docs/03-FE-DESIGN-SYSTEM.md` — Frontend Skill/chuẩn thiết kế dùng chung.
5. `docs/04-API-VA-DATABASE.md` — API, RBAC, SQL, tồn, xác nhận hai bên.
6. `docs/05-QUY-TRINH-TEST.md` — Git, PR, test, Definition of Done.
7. `prompts/` — prompt khởi tạo riêng cho 3 agent và agent điều phối.
8. `templates/` — mẫu PR, bàn giao API.
9. `reference-inputs/` — hai tệp tham chiếu gốc người dùng cung cấp.

## Thực hiện
- Khởi tạo **repo mới Vue 3**; KHÔNG đổi file React cũ tại chỗ một cách máy móc.
- Copy `AGENTS.md` và thư mục `docs`, `prompts`, `templates` vào repo.
- Mở ba nhánh `feat/admin`, `feat/retailer-shipper`, `feat/supplier-distributor` từ `develop`.
- Mỗi agent đọc `AGENTS.md`, đúng prompt vai trò và đúng các mục liên quan trong file Excel.
- Chốt hợp đồng API, data model và design tokens trước khi ba người viết trang.

## Nguồn và cách giải quyết mâu thuẫn
- `DistriFlow_Dac_ta_UC_Chi_tiet.xlsx`: **đặc tả nghiệp vụ chuẩn**, 10 module, 50 UC (35 P0, 15 P1), 15 UI, 16 BR, kịch bản nghiệm thu.
- `DistriFlow Logistics Platform (1).zip`: **demo tham khảo cảm hứng UI**, hiện là React + Vite + Tailwind, có một số màn bán hàng/giao tận nơi không thuộc phạm vi Excel.
- Nếu demo và Excel mâu thuẫn: ưu tiên Excel. Không tự thêm vai trò/luồng mới. Đề xuất thay đổi ở PR/ADR và chờ nhóm chốt.

## Lưu ý quan trọng
- **Nhà phân phối** chưa được định nghĩa thành tác nhân độc lập trong bảng UC. Giai đoạn P0 coi là một dạng tổ chức nhà cung cấp, cùng portal và permission scope; chỉ tách vai trò sau khi bổ sung UC/phê duyệt.
- **Điều phối** là quyền/tác nhân riêng với **quản trị kho**, dù một tài khoản có thể mang cả hai quyền.
- P0 là bắt buộc cho bản demo xử lý hoàn chỉnh. P1 là mở rộng; không rút ngắn các kiểm tra quyền và tính đúng đắn bàn giao.
- Tài liệu này là **quy tắc/thiết kế đề xuất**, chưa phải website đã triển khai.
