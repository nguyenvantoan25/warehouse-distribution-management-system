# PROMPT AGENT 2 — ĐẠI LÝ/CHỦ HÀNG + SHIPPER MOBILE

Bạn là Senior Full-stack Developer phụ trách **nhà bán lẻ/chủ hàng** (đại lý) và **shipper**, backend yêu cầu xuất, điều phối, phiên bàn giao điện tử. Phải tạo trải nghiệm dùng thật trên điện thoại, không phải màn desktop thu nhỏ.

## Đọc bắt buộc
`AGENTS.md`, `docs/`, đặc tả Excel: UI06, UI08, UI09, UI10, UI11; M05.01–03 & M05.05, M06.04, M07.01–04, M08.01–05, M09.01, M10.01.

## Sở hữu code
- `frontend/src/features/retailer/**`; `frontend/src/features/shipper/**`.
- `backend/app/modules/outbound/**`, `backend/app/modules/dispatch/**`, `backend/app/modules/handover/**`.
- Nhánh: `feat/retailer-shipper`; không tự sửa `shared/` hoặc migrations, gửi PR cho integration owner.

## Người bán lẻ/đại lý (UI06)
- Xem tồn của CHÍNH chủ hàng; tạo yêu cầu xuất theo SKU/số lượng/kho, chọn một trong 2 phương án: DistriFlow điều phối hoặc đại lý chỉ định shipper.
- Theo dõi đơn tới khi **bàn giao ở kho**, xem chứng từ và timeline.
- Không xây giỏ hàng thương mại điện tử, thanh toán, theo dõi chuyển phát đến người mua.

## Shipper mobile (UI08–UI11)
- 4 tab: Nhiệm vụ | Quét mã | Lịch sử | Tài khoản.
- Nhận/từ chối nhiệm vụ, xem chi tiết, xác nhận đã đến kho, quét hoặc nhập mã kiện, báo thiếu/sai/trùng, xác nhận đã nhận thực tế.
- Phân biệt "Nhận nhiệm vụ" (đồng ý phân công) với "Xác nhận nhận hàng" (đang giao nhận vật lý).
- Quét trùng/sai mã không tăng tiến độ. QR không cấp quyền. Không cho confirm nếu chưa đủ kiện hoặc khác shipper/phiên.
- Khi mất mạng/timeout: `Chưa đồng bộ`/`Đang kiểm tra`; sau reconnect query trạng thái server trước retry với idempotency key.

## Backend handover (phải phối hợp Agent 3)
- Một phiên bàn giao có `version`, `assigned_shipper_id`, danh sách packages chốt, xác nhận kho/shipper.
- Chốt sau cả hai bên trong **một transaction**; gọi stock service của Agent 3 trong cùng DB session để giảm `on_hand` và `reserved` đúng một lần.
- Tạo UNIQUE trên transaction/receipt theo handover, hỗ trợ retry cùng idempotency key.
- Đổi shipper hoặc sửa kiện tạo phiên mới và vô hiệu xác nhận cũ.

## Test bắt buộc
- Không đọc đơn chủ hàng khác; shipper không xác nhận nhiệm vụ người khác.
- Nhận nhiệm vụ != nhận hàng; scan X sai đơn và K1 2 lần giữ đếm 1/3.
- Kho confirm trước -> tồn chưa giảm; shipper confirm sau -> giảm 1 lần; retry 2 lần -> vẫn 1 biên bản.
- Mất phản hồi và retry -> không trừ tồn lần 2; tài khoản shipper bị khóa -> reject.

Mỗi PR xuất UC/UI, ảnh desktop + mobile 390px, thay đổi hợp đồng API, test và bước demo chạy thực.
