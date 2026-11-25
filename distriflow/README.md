# DistriFlow

Báo cáo, sơ đồ hệ thống và ma trận access: [README ở thư mục gốc](../README.md).

- API: `backend/start.ps1` → http://127.0.0.1:8000/docs
- Frontend: `frontend/start.ps1` → http://127.0.0.1:5173/login
- PostgreSQL: `docker compose --env-file infra/.env -f infra/compose.yaml up -d db`, cổng localhost:55432.
- Tài khoản local: `backend/accounts.local.json`; database mới chỉ chuyển tài khoản/hash hiện có, không chuyển demo.
- Startup migrate bằng Alembic, không seed dữ liệu nghiệp vụ. Khai báo kho thật ở Danh mục rồi gán tài khoản ở Tài khoản & phạm vi.
- OpenAPI: `contracts/openapi.json`, sinh từ FastAPI.

Dependencies: Python 3.12 (`backend/requirements.txt`), Node 22 và pnpm 9 (`frontend/pnpm-lock.yaml`).
