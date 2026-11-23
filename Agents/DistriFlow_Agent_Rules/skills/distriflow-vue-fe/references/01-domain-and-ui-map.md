# 01 — Phạm vi, chức năng, thuật ngữ và map UI

## Phạm vi được cố định từ Excel nguồn
- 10 module, 50 UC, 35 P0 + 15 P1, 15 UI. 5 actor hệ thống: nhà cung cấp, quản trị kho, nhà bán lẻ/chủ hàng, quản lý điều phối, shipper.
- 4 nhóm tổ chức/nhân sự không đồng nghĩa 4 actor: nhóm kho có thể kiêm điều phối nhưng quyền tách riêng.
- Nhà bán lẻ là **chủ hàng**; supplier nhập cho chủ hàng được chỉ định. Dữ liệu tồn và chứng từ theo chủ hàng. Đây là **giả định PV01 cần được nhóm/giảng viên chốt**.
- Hệ thống kết thúc khi kho và shipper xác nhận bàn giao **tại kho**. Không giao cuối, COD, doanh thu/thanh toán.
- Hai phương án vận chuyển: **chủ hàng chỉ định shipper** hoặc **DistriFlow điều phối**; không tự chuyển phương án khi bị từ chối.
- “Vận đơn điện tử” trong đề tài = chứng từ/yêu cầu xuất, danh sách kiện, nhiệm vụ nhận, phiên bàn giao và biên bản nhận tại kho; không đồng nghĩa bill vận tải giao tận nơi.
- "Nhà phân phối" xuất hiện trong yêu cầu người dùng nhưng chưa là actor riêng của Excel; map làm loại tổ chức nhà cung cấp cho P0; muốn tách phải lập UC, permissions, UI, tests và được phê duyệt.

## Danh mục module chuẩn
| Mã | Module | P0/P1 | Gợi ý owner backend |
|---|---|---|---|
| M01 | Truy cập và tài khoản | 2/2 | Agent 1 |
| M02 | Quản lý danh mục | 4/1 | Agent 1 |
| M03 | Quản lý nhập kho | 5/1 | Agent 3 (UI nhập admin: Agent 1) |
| M04 | Quản lý tồn kho | 3/3 | Agent 3 (UI admin + retailer: Agents 1,2) |
| M05 | Yêu cầu xuất nhà bán lẻ | 4/1 | Agent 2 |
| M06 | Thực hiện xuất kho | 5/0 | Agent 2 (UI admin: Agent 1) |
| M07 | Điều phối nhận hàng tại kho | 4/1 | Agent 2 (UI desktop: Agent 1) |
| M08 | Shipper điện thoại | 5/1 | Agent 2 |
| M09 | Tổng quan và báo cáo | 2/2 | Agent 1 (data services Agents 2,3) |
| M10 | Thông báo và hỗ trợ | 1/3 | Agent 1 (producer events: toàn nhóm) |

## Ma trận 15 UI → owner FE
| UI | Trang | Thiết bị | Agent | UC chính |
|---|---|---|---|---|
| UI01 | Tổng quan quản trị kho | Desktop | 1 | M09.01, M03.06, M04.01, M06.01 |
| UI02 | Nhập kho | Desktop | 1 | M03.03–06 |
| UI03 | Tồn kho | Desktop, theo quyền | 1/2 reuse | M04.01–06 |
| UI04 | Soạn/đóng gói/bàn giao | Desktop | 1 | M06.01–05 |
| UI05 | Cổng nhà cung cấp | Desktop | 3 | M03.01, M03.02, M03.06, M09.01 |
| UI06 | Cổng nhà bán lẻ | Desktop | 2 | M04.01, M05.01–05, M09.01 |
| UI07 | Điều phối | Desktop | 1 | M07.01–05 |
| UI08 | Nhiệm vụ shipper | Mobile | 2 | M08.01, M08.06 |
| UI09 | Chi tiết nhận hàng | Mobile | 2 | M08.02, M08.05 |
| UI10 | Quét/đối chiếu kiện | Mobile | 2 | M08.03, M08.05 |
| UI11 | Xác nhận và biên nhận | Mobile | 2 | M08.04, M08.06, M06.04 |
| UI12 | Danh mục | Desktop | 1 | M02.01–05 |
| UI13 | Truy cập và tài khoản | Desktop/mobile | 1 (shared) | M01.01–04 |
| UI14 | Báo cáo | Desktop | 1 | M09.02–04 |
| UI15 | Thông báo và hỗ trợ | Desktop/mobile | 1 (shared shell) | M10.01–04 |

> Đây là bản **phân công triển khai**, không thay đổi chủ thể thực hiện trong Use Case. Một UI có thể chứa nhiều UC, một UC có thể xuất hiện ở nhiều UI. P1 ở UI không bắt buộc ở sprint P0.

## Danh sách P0 theo tuyến tính (không bỏ qua)
1. M01.01–02 / M02.01–04: auth, rights, đối tác, SKU, kho, shipper.
2. M03.01, M03.03–06: nhập, duyệt, kiểm nhận, phân vị trí, kết quả.
3. M04.01–02, M04.06: tồn theo chủ, lịch sử, khóa/mở khóa.
4. M05.01–03, M05.05: yêu cầu xuất, chọn shipper, theo dõi, chứng từ.
5. M06.01–05: duyệt/giữ, soạn, đóng, bàn giao, xử lý thiếu.
6. M07.01–04: điều phối, phân công/xác minh, theo dõi.
7. M08.01–05: shipper nhận nhiệm vụ, đến kho, đối chiếu, confirm, báo sự cố.
8. M09.01–02 / M10.01: tổng quan, báo cáo nhập-xuất-tồn, thông báo.

## Loại trừ đối với demo React trong ZIP
- `src/App.tsx` hiện có các concept `CartView`, `TrackingView` với giao hàng sau khi rời kho, giá bán, doanh thu; không triển khai chúng như tính năng thật khi chuyển sang Vue.
- Dùng bố cục thẻ, sidebar, bảng và mobile interaction của demo để tham khảo thẩm mỹ. Chuyển **tư duy giao diện**, không dịch từng dòng React TSX sang Vue.
- File `AGENTS.md` trong ZIP nhắc React/tsx và Vite server Figma Make: không sao chép vào repo Vue mới; dùng `AGENTS.md` của bộ quy tắc này.
