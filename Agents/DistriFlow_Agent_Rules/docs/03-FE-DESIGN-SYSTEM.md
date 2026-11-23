# 03 — Frontend Skill / Design System bắt buộc

## Quy trình agent thiết kế giao diện (áp dụng mọi FE task)
1. Đọc UI ID và UC ID trong Excel, ghi actor, thiết bị, input, action, state, error; tham khảo demo React **chỉ về mặt bố cục**.
2. Kiểm tra component dùng chung đã có trước khi tạo mới; không clone `BaseTable2`, `AppModalNew`, hoặc đặt CSS tự phát.
3. Dùng Vue SFC `<script setup lang="ts">` + composables; tránh fetch trực tiếp trong `<template>` và logic nghiệp vụ trong component hiển thị.
4. Đưa API call vào `features/<feature>/api/`; state server theo query/service và auth/filters theo Pinia khi cần. Không lưu stock/receipt trong state cục bộ như nguồn sự thật.
5. Thiết kế đầy đủ: skeleton/loading, empty, error/permission denied, validation, success, pending-sync. Giữ bộ lọc sau reload nếu có lợi và không lộ dữ liệu trái quyền.
6. Kiểm tra desktop ~1440 và 1024, mobile 390 và 360, bàn phím, focus, màu và text tiếng Việt, trạng thái bị vô hiệu hóa có giải thích.
7. Chạy `npm run lint`, `npm run type-check`, `npm run test:unit`, `npm run build`; E2E cho P0.

## Design tokens: **Excel DS01/DS02 là chuẩn**
```css
:root {
  --color-primary: #087f8c;
  --color-sidebar: #172b3a;
  --color-app-bg: #f4f6f8;
  --color-surface: #ffffff;
  --color-text: #172b3a;
  --color-text-muted: #64748b;
  --color-border: #e2e8f0;
  --color-danger: #b42318;
  --radius-card: 10px;
  --sidebar-width: 240px;
  --header-height: 64px;
  --space-unit: 4px;
}
```
- Font: sans serif hỗ trợ tiếng Việt, 14–16px cho nội dung; label nằm ngoài input; tránh font 9px khiến dữ liệu khó đọc.
- Border nhẹ, nền `#F4F6F8`, surface trắng; bo góc ~10px, spacing bội 4/8; icon thống nhất `lucide-vue-next`.
- Một primary action rõ cho mỗi khu vực; cancel/delete/override cần confirm, lý do, hậu quả.
- Tất cả status badge có **màu + chữ**, tuyệt đối không màu riêng lẻ.
- Trạng thái `Chờ duyệt`, `Đã duyệt & giữ`, `Đang soạn`, `Sẵn sàng bàn giao`, `Chờ đủ xác nhận`, `Đã bàn giao` phải được chuyển từ enum backend, không đoán từ màu.

## Bộ component chung (Agent 1 owner, 2/3 đề xuất qua PR)
- Layout: `AppShell`, `DesktopSidebar`, `TopBar`, `MobileShell`, `Breadcrumbs`, `PageHeader`.
- Data: `StatCard`, `DataTable`, `PaginationBar`, `SearchFilters`, `StatusBadge`, `Timeline`, `DetailDrawer`.
- Forms: `BaseInput`, `BaseSelect`, `BaseDatePicker`, `FormField`, `BaseButton`, `ConfirmDialog`.
- Feedback: `LoadingSkeleton`, `EmptyState`, `ErrorState`, `ForbiddenState`, `PendingSyncBanner`, `Toast`.
- Domain read-only: `OwnerTag`, `DocumentCode`, `StockQuantitySummary`, `PackageScanProgress`, `HandoverChecklist`.
- Không tạo widget "bảng tồn" độc lập ở Admin và Retailer: reuse `DataTable` và schema hiển thị; chỉ đổi data scope, action theo role.

## Desktop (Admin/Supplier/Retailer)
- Sidebar 240px, topbar 64px, content có breadcrumb, heading, mô tả, search/filter và primary action.
- Trang chứng từ hiển thị mã chứng từ, chủ hàng, trạng thái, người xử lý, bước kế tiếp ở trên đầu; tab Hàng hóa/Chứng từ/Lịch sử.
- Dashboard: chỉ số gắn link tới danh sách cùng filter; không dùng 0 thay lỗi API.
- Desktop tables hỗ trợ overflow-x, search, lọc, phân trang, empty state, trạng thái và mở detail; không nhồi 50 cột một trang.

## Shipper mobile
- Width tham chiếu 390px, single column; primary CTA 48–52px; tôn trọng safe areas.
- Bottom 4 tab đúng thứ tự: `Nhiệm vụ`, `Quét mã`, `Lịch sử`, `Tài khoản`; notifications qua chuông.
- Quét QR nên có camera và fallback nhập tay; một QR chỉ nhận diện kiện, server mới quyết định quyền.
- Bộ đếm chỉ tăng khi kiện đúng và quét lần đầu trong phiên. Nút xác nhận có lý do disabled: thiếu kiện / phiên hết hạn / chưa đến kho / chờ kho confirm.
- Trình bày rõ nhiệm vụ được giao, tên kho, mã yêu cầu, số kiện, tình trạng mạng, phiên nhận.
- Mất mạng: không báo "Hoàn tất" nếu chưa được server đối chiếu. Retry phải giữ cùng idempotency key.

## Cấu trúc Vue component
```vue
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
// fetch/API được tách sang services/composable, không nhét vào template
const route = useRoute()
const loading = ref(false)
const requestId = computed(() => String(route.params.id || ''))
</script>

<template>
  <PageHeader title="Chi tiết yêu cầu" />
  <LoadingSkeleton v-if="loading" />
  <!-- Dữ liệu từ composable typed; luôn có ErrorState/EmptyState -->
</template>
```

## Definition of done riêng cho FE
- Có bằng chứng route + role guard + state API thật hoặc nhãn **MOCK/NOT-INTEGRATED**.
- Không dùng button vô tác dụng, toast "Thành công" khi request thất bại, link giả `#`, chức năng CRUD nháp không lưu được.
- Có screenshot màn chính/chi tiết/empty/error/mobile; test keyboard và thời gian loading; font tiếng Việt không tràn.
- Dùng design token, component chuẩn, responsive; test `vue-tsc` và build thực tế.
