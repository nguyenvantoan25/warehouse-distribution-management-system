# DistriFlow

Báo cáo, sơ đồ hệ thống và ma trận access: [README ở thư mục gốc](../README.md).

- API: `backend/start.ps1` → http://127.0.0.1:8000/docs
- Frontend: `frontend/start.ps1` → http://127.0.0.1:5173/login
- PostgreSQL: `docker compose --env-file infra/.env -f infra/compose.yaml up -d db`, cổng localhost:55432.
- Tài khoản local: `backend/accounts.local.json`; database mới chỉ chuyển tài khoản/hash hiện có, không chuyển demo.
- Startup migrate bằng Alembic, không seed dữ liệu nghiệp vụ. Khai báo kho thật tại Thiết lập kho (`/admin/warehouses`), rồi dùng nút Gán phạm vi ở Tài khoản & đối tác. Danh mục & vị trí chỉ gồm Sản phẩm và Vị trí kho.
- OpenAPI: `contracts/openapi.json`, sinh từ FastAPI.
- Cổng giao diện: `/admin` (vận hành), `/supplier` (nhà cung cấp), `/retailer` (nhà bán lẻ); đăng nhập chung và tự chuyển đúng role. [Cấu trúc cổng](frontend/src/portals/README.md).
- Backend dùng chung, ghép module tại `backend/app/api/router.py`; không tách API/database theo role. Shipper có Android riêng và web dự phòng `/shipper/tasks`.
- Tồn kho → Bản đồ 800 vị trí: kệ đơn cho kho thủ công, 8 hàng × 10 tầng × 10 cột. Admin khai báo kho thật rồi xác nhận tạo vị trí; không tự tạo hàng tồn. Migration kệ đơn `20261126_03`, hướng dẫn/ERD ở mục 14 báo cáo gốc.
- Tài khoản & đối tác (`/admin/accounts`): ba nhóm Shipper/Nhà cung cấp/Đại lý, thêm/sửa/xóa mềm; supplier có loại hàng cung cấp. Đường dẫn Đối tác cũ chuyển về nhóm Nhà cung cấp. Hướng dẫn, bảo mật và ERD migration `20261126_04` ở mục 16 báo cáo gốc.

Dependencies: Python 3.12 (`backend/requirements.txt`), Node 22 và pnpm 9 (`frontend/pnpm-lock.yaml`).
