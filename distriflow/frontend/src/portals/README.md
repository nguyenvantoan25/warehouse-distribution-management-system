# Các cổng giao diện

Một ứng dụng Vue, một bản build/deploy; các cổng có route riêng và tải trang qua dynamic import.

| Thư mục | Vai trò | Đường dẫn |
| --- | --- | --- |
| operations | WAREHOUSE_ADMIN, DISPATCH_MANAGER | /admin |
| supplier | SUPPLIER | /supplier |
| retailer | RETAILER_OWNER | /retailer |
| shipper | SHIPPER, bản web dự phòng | /shipper/tasks |

`app/portals.ts` xác định role thuộc cổng và trang chủ. `router/index.ts` ghép route,
kiểm tra cả cổng lẫn permission trên mọi route cha/con. Backend vẫn là nơi quyết định
quyền thao tác và phạm vi dữ liệu; lazy loading không phải cơ chế bảo mật.

Layout nhà cung cấp và nhà bán lẻ có menu riêng, tái sử dụng `shared/layouts/PartnerShell.vue`.
Các trang nghiệp vụ/API client dùng lại từ `features/`; không sao chép logic tồn kho,
nhập kho hoặc xuất kho vào từng cổng. Operations tiếp tục dùng layout vận hành hiện có.

`/partner/inbounds`, `/partner/outbounds`, `/partner/inventory` là redirect tương thích
bookmark cũ; không còn layout đối tác trộn role. Đường dẫn đích vẫn bị kiểm tra quyền.

Shipper native nằm tại `../../../android-shipper`, dùng chung backend nhưng build APK riêng.
Nếu sau này cần domain hoặc chu kỳ phát hành riêng, có thể tách entrypoint/build theo
cổng; hiện chưa tạo ba ứng dụng frontend độc lập hoặc ba backend trùng nghiệp vụ.
