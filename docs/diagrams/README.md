# ERD PostgreSQL của DistriFlow

Các ảnh và nguồn DOT ở đây được sinh từ bảng vật lý trong PostgreSQL, không suy diễn quan hệ từ tên cột. Metadata: [database-schema.json](../database-schema.json). Báo cáo có từ điển dữ liệu từng bảng: [README gốc](../../README.md).

- [ERD đầy đủ](erd-full.svg): 30 bảng, 40 foreign key tại thời điểm đối chiếu 26/11/2026.
- [Tài khoản và danh mục](erd-catalog.svg).
- [Nhập kho và số dư](erd-inbound.svg).
- [Xuất kho và đóng kiện](erd-outbound.svg).
- [Bàn giao và ghi xuất](erd-handover.svg).
- [Hạ tầng và legacy](erd-infrastructure.svg): không vẽ FK giả cho actor/object ID dạng chuỗi.

Bảng xanh thuộc nhóm chính, bảng xám là bảng tham chiếu rút gọn. Nhãn đường nối chỉ cardinality vật lý. PK/UK nhiều cột phải đọc theo tổ hợp trong từ điển dữ liệu.

Đọc lại metadata (chỉ đọc database):

```powershell
cd distriflow/backend
python -m app.setup.schema_report
python -m app.setup.schema_report --render
```

Công cụ vẽ SVG chạy local, không gửi schema ra ngoài. Khi cần tái dựng trên máy mới, cài dependency vào thư mục công cụ đã loại khỏi Git:

```powershell
cd distriflow
npm install --prefix .tools/erd-renderer --no-audit --no-fund @viz-js/viz@3.31.0
cd ..
node docs/diagrams/render-erd.mjs docs/diagrams/erd-catalog.dot
```

Lệnh cuối in SVG ra stdout; không tự ghi đè báo cáo hoặc sửa dữ liệu. Mã Mermaid đầy đủ: [database.erd.mmd](../../distriflow/contracts/database.erd.mmd).

File SQL live là bản chụp DDL để đối chiếu, không chứa bản ghi và không thay thế backup/restore đầy đủ. Startup và thay đổi schema vẫn dùng Alembic, không chạy dump live đè lên database đang sử dụng.

Sau migration `20261126_02`, bảng `storage_locations` có thêm 4 tọa độ kệ nullable:
`rack_row`, `rack_level`, `rack_bay`, `rack_depth`; metadata/ERD catalog và ERD đầy đủ
đã cập nhật, tổng 149 cột. Có thể ghi SVG bằng tùy chọn
`--output docs/diagrams/erd-catalog.svg`; chỉ sinh file ảnh local từ DOT, không sửa database.

Revision hiện tại `20261126_03`: chuyển sang kệ đơn 8 × 10 × 10; `rack_bay` là cột 1–10,
`rack_depth` giữ để tương thích và luôn bằng 1 khi có tọa độ. Không đổi số bảng/cột/FK,
giữ nguyên ID, mã vị trí và liên kết số dư. Ràng buộc CHECK mới nằm trong metadata/từ điển.

Revision mới nhất `20261126_04` bổ sung tên hồ sơ, dấu xóa mềm và version ở `users`,
loại hàng cung cấp ở `organizations`. ERD catalog/full và metadata đã cập nhật:
30 bảng, 153 cột, 40 FK; không thêm bảng tài khoản/đối tác trùng lặp.
