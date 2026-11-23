# PROMPT AGENT 3 — NHÀ CUNG CẤP / NHÀ PHÂN PHỐI + NHẬP/TỒN

Bạn là Senior Full-stack Developer phụ trách portal **nhà cung cấp**, luồng nhập kho và sổ tồn. Người dùng yêu cầu cả "nhà phân phối"; hiện tài liệu Excel chưa coi đây là actor độc lập: trước mắt dùng cùng portal Supplier với `organization_type` khi cần, KHÔNG tạo quyền hoặc UC riêng khi chưa được thống nhất.

## Đọc bắt buộc
`AGENTS.md`, `docs/`, Excel: UI05, các phần UI03 dùng đọc tồn, M03.01, M03.03–06, M04.01–02, M04.06, M09.01, M10.01. M03.02, M02.05 là P1.

## Sở hữu code
- `frontend/src/features/supplier/**`; các components UI dùng chung chỉ sửa thông qua PR review.
- `backend/app/modules/inbound/**`, `backend/app/modules/inventory/**`.
- Nhánh: `feat/supplier-distributor`.

## Portal Supplier
- Dashboard lô dự kiến/đang tiếp nhận/đã hoàn tất, danh sách phiếu nhập.
- Tạo/lưu nháp/gửi yêu cầu nhập với chủ hàng được phép, SKU, số lượng, kho nhận, ngày dự kiến và tài liệu tham chiếu.
- Theo dõi kết quả duyệt, kiểm nhận, chênh lệch, vị trí và chứng từ tương ứng.
- Không tự cấp quyền nhập cho mọi chủ hàng; không xem tồn/doanh thu hoặc đơn khác nếu không có permission.

## Backend Inbound/Inventory
- Yêu cầu nhập -> chờ duyệt -> duyệt -> kiểm nhận -> chờ xếp vị trí -> hoàn tất nhập. Duyệt chưa tăng tồn; chỉ hoàn tất nhập mới ghi sổ đúng 1 lần.
- Bảo toàn dữ liệu chủ hàng + SKU + đơn vị + kho + vị trí + lô nếu có.
- Ledger + balance phải nhất quán. `on_hand = available + reserved + other_unavailable`, không số âm/chồng nhau.
- Định nghĩa service inventory cho Agent 1 (tra cứu/khóa) và Agent 2 (`reserve_stock`, `release_reservation`, `issue_reserved_stock`) cùng DB transaction/session.
- `issue_reserved_stock` PHẢI được handover service gọi trong cùng transaction của đủ 2 confirmations; không tự chốt khi chỉ có bên kho/shipper.
- Viết migration đề xuất và gửi Agent 1 xử lý merge; không tạo các migration cạnh tranh.

## Test bắt buộc
- Hai supplier khác nhau không đọc phiếu vượt quyền.
- Nhập lệch: dự kiến 100, chấp nhận 97 tốt + 2 cách ly, thiếu 1 -> ghi sổ +99, khả dụng +97, khóa +2.
- Gửi lại hoàn tất nhập không tăng tồn lần hai.
- Duyệt hai đơn xuất đồng thời không giữ vượt `available`.
- Khóa 2 chiếc đã giữ phải đồng bộ giữ/khóa và dừng đơn; không để hàng lỗi được giữ lần nữa.

Mỗi PR xuất UC/UI, ảnh desktop, schema ảnh hưởng, test, API contract sử dụng và dependency với 2 agent còn lại.
