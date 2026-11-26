# DistriFlow Shipper — Android native

Ứng dụng Android riêng cho vai trò **SHIPPER**, dùng Java/native Android Views. Không phải WebView và không đóng gói các màn hình quản trị của website.

## APK cài thử

[DistriFlow-Shipper-debug.apk](../artifacts/DistriFlow-Shipper-debug.apk) — Android 8.0/API 26 trở lên. Đây là bản **debug ký bằng debug certificate**, không phải bản phát hành production/Google Play. App ID: `com.distriflow.shipper.debug`.

Mật khẩu/tài khoản không nằm trong APK. App không tự tạo nhiệm vụ hoặc dữ liệu nghiệp vụ. Đăng nhập bằng tài khoản shipper trên cùng backend PostgreSQL của website.

## Chức năng

- Cấu hình địa chỉ máy chủ trước đăng nhập.
- Đăng nhập shipper bằng endpoint riêng; admin/dispatch/supplier/retailer bị từ chối trước khi tạo session.
- Danh sách nhiệm vụ được phân cho chính tài khoản, nhận nhiệm vụ, báo đến kho.
- Xem kiện và tiến độ đối chiếu từ máy chủ; nhập mã/đầu đọc bàn phím, xác nhận nhận hàng khi đủ mã.
- Chờ kho xác nhận; xem nhiệm vụ hoàn tất trong Lịch sử, xem tài khoản và đăng xuất.
- Gửi version, CSRF và Idempotency-Key; lỗi mạng/5xx giữ nguyên body và key của lệnh để thử lại. Không tự báo thành công khi mất kết nối.

Chưa tích hợp camera QR/barcode, push notification, GPS hoặc hàng đợi offline bền vững. Mất mạng không thể xác nhận hàng. Đóng app có thể mất phiên/lệnh chờ trong RAM: đăng nhập lại và tải trạng thái máy chủ trước khi tiếp tục.

## Cài lên điện thoại qua USB

Máy hiện tại có thể dùng script tự tìm platform-tools, không cần adb nằm trong PATH:

```powershell
.\distriflow\android-shipper\install-usb.ps1
# Nhiều thiết bị: thêm -Serial SERIAL_CUA_DIEN_THOAI
```

Script chỉ cài khi chọn được đúng một thiết bị đã cho phép USB debugging; không tự chọn trong nhiều thiết bị. Nếu muốn thực hiện thủ công, làm các bước dưới đây.

1. Bật Developer options và USB debugging trên điện thoại, kết nối USB và chấp thuận khóa máy tính.
2. Backend phải đang chạy và đã có endpoint `/api/v1/auth/shipper-login` mới.
3. Dùng Android platform-tools/adb:

```powershell
adb devices
# Nếu có nhiều thiết bị, thêm -s SERIAL vào từng lệnh
adb install -r distriflow/artifacts/DistriFlow-Shipper-debug.apk
adb reverse tcp:8000 tcp:8000
```

Mở **DistriFlow Shipper (Test)**, nhập máy chủ `http://127.0.0.1:8000` rồi đăng nhập shipper. USB reverse chuyển kết nối trên điện thoại về backend localhost của máy tính, không cần mở cổng database/API ra Internet. Sau khi rút/cắm USB có thể phải chạy lại reverse.

Chuyển APK sang điện thoại để cài thủ công cũng được, nhưng cài APK riêng **không** tạo đường kết nối tới backend. Nếu không dùng USB, cần API HTTPS thực sự truy cập được hoặc backend/Wi-Fi nội bộ được cấu hình phù hợp. Không nhập localhost của máy tính khi điện thoại không có USB reverse.

Kết thúc thử nghiệm có thể gỡ đường reverse bằng `adb reverse --remove tcp:8000` (thêm serial nếu cần). App có thể phải gỡ phiên bản debug cũ trước khi cài nếu debug certificate của máy build khác nhau; gỡ app sẽ xóa cấu hình cục bộ.

## Kết nối và bảo mật

- Bản debug chấp nhận HTTP **chỉ** localhost, emulator/IPv4 nội bộ. Bản release chỉ chấp nhận HTTPS.
- Android Emulator chuẩn có thể dùng `http://10.0.2.2:8000` để truy cập localhost máy phát triển theo [tài liệu Android](https://developer.android.com/studio/run/emulator-networking-address).
- Native HTTP có cookie jar riêng trong RAM, gửi HttpOnly session cookie và CSRF; không phụ thuộc CORS của browser.
- Không lưu password/session/CSRF trong SharedPreferences hoặc file. Chỉ lưu URL server. Tắt backup app.
- Không bỏ qua TLS certificate; không tự theo HTTP redirect; không log thông tin đăng nhập.
- API không cho shipper đọc nhiệm vụ người khác; app không truy cập PostgreSQL trực tiếp.

## Cấu trúc

```text
android-shipper/
  app/src/main/java/com/distriflow/shipper/
    config/ServerAddress.java          Kiểm tra URL/TLS/IP test
    api/ApiClient.java                 HTTP/cookie/CSRF/timeout
    api/ApiException.java              Lỗi có HTTP status
    data/ShipperRepository.java        Đăng nhập, tasks, lệnh, retry
    data/TaskRules.java                Điều kiện đối chiếu/xác nhận
    ui/MainActivity.java               Màn hình native và thao tác nền
  app/src/test/                       Kiểm thử URL và rule kiện
  app/src/debug/AndroidManifest.xml    HTTP nội bộ cho bản test
  app/src/main/AndroidManifest.xml     Release mặc định chặn cleartext
  gradle/wrapper/                      Gradle wrapper
  build.ps1                           Build, test và chép APK bàn giao
```

## Build lại

Cần JDK 17 trở lên, Android SDK Platform 35 và SDK build-tools. Dùng AGP 9.2.1 / Gradle 9.4.1 theo [ma trận tương thích Android](https://developer.android.com/build/releases/agp-9-2-0-release-notes). Máy hiện tại dùng JDK 21.

Mở folder này bằng Android Studio hoặc cấu hình `local.properties` với `sdk.dir` của máy. File này đã loại khỏi Git.

```powershell
cd distriflow/android-shipper
.\build.ps1
# Hoặc:
.\gradlew.bat assembleDebug testDebugUnitTest
```

APK gốc: `app/build/outputs/apk/debug/app-debug.apk`. Script chép sang `distriflow/artifacts/DistriFlow-Shipper-debug.apk` và in SHA-256. Bản release cần keystore/chữ ký do chủ dự án quản lý; không tự tạo hoặc nhúng khóa release.

Thông tin file/checksum bản đã build: [shipper-build.json](../artifacts/shipper-build.json). APK là build artifact và đã loại khỏi Git; source Android/Gradle wrapper vẫn nằm trong project để build lại.

## Mức kiểm chứng ngày 26/11/2026

- `assembleDebug` thành công; APK có chữ ký APK Signature Scheme v2 hợp lệ.
- 15 JVM unit tests đạt (URL và quy tắc kiện).
- 23 backend tests đạt, bao gồm 3 test dành cho đăng nhập Android, CSRF và own-task scope.
- Đã thử khởi động giả lập riêng, nhưng ADB còn offline; đã dừng giả lập và API test. **Chưa xác nhận luồng UI end-to-end trên Android, chưa kiểm thử điện thoại thật.**
- API dành cho fixture Android dùng SQLite riêng (`tests/serve_android_e2e.py`), không ghi dữ liệu test vào PostgreSQL sử dụng.
