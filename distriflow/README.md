# DistriFlow

Nền tảng bàn giao điện tử giữa kho và shipper tại kho. Mã nguồn này triển khai vertical slice P0: tồn kho, yêu cầu xuất, phân công, quét kiện, xác nhận song phương và biên nhận.

## Chạy dự án

```bash
docker compose -f infra/compose.yaml up --build
```

- Frontend: `http://localhost:5173`
- API/OpenAPI: `http://localhost:8000/docs`

Để chạy trực tiếp, xem `.env.example`, cài `frontend` bằng npm và `backend` bằng Python 3.12.
