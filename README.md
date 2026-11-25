# DistriFlow — báo cáo triển khai PostgreSQL

Mã nguồn: [distriflow](./distriflow). Báo cáo nằm ngoài folder code. Cập nhật ngày 23/11/2026.

## 1. Trạng thái thực tế và nguồn dữ liệu

Theo lựa chọn của bạn: **PostgreSQL trống để tự nhập dữ liệu qua giao diện**, không chuyển dữ liệu demo và không dựng số liệu kinh doanh.

- PostgreSQL đã chạy bằng container riêng, chỉ bind localhost cổng **55432**.
- Phiên bản quan sát: **PostgreSQL 16.15**, schema Alembic **20261123_01**.
- Chỉ chuyển **5 tài khoản và password hash hiện có** từ SQLite, giữ mật khẩu bạn đã cập nhật. Không chuyển session hoặc phạm vi kho/đối tác demo.
- Tất cả bảng nghiệp vụ đang trống: kho, tổ chức, SKU, vị trí, cung ứng, tồn, nhập, xuất, nhiệm vụ, kiện và biên nhận đều **0 bản ghi** tại thời điểm kiểm tra.
- SQLite cũ và các backup vẫn giữ nguyên; chưa xóa hoặc sửa dữ liệu nghiệp vụ cũ.
- Dashboard đọc database; không có dữ liệu thì hiển thị 0/trống. KPI là toàn bộ phiếu trong kho; biểu đồ là 30 ngày gần nhất. Giao diện ghi rõ nguồn database và thời điểm tải.

Bằng chứng số lượng từng bảng: [database-status.json](./docs/database-status.json). Đây là ảnh chụp trạng thái có timestamp, không phải dữ liệu live sau khi bạn bắt đầu nhập. Đọc lại bất kỳ lúc nào:

~~~powershell
cd distriflow/backend
python -m app.setup.status
~~~

**Chưa có dữ liệu nghiệp vụ thật được cung cấp.** Không gọi dữ liệu test/demo là dữ liệu thật. Các tên, SKU và số lượng trong bộ kiểm thử chỉ là fixture ở database kiểm thử, không nằm trong database sử dụng.

## 2. Những gì đã sửa

- Chuyển cấu hình runtime sang PostgreSQL qua psycopg; bỏ fallback tự động về SQLite.
- Thêm Alembic với revision DDL cố định; startup chỉ nâng schema, không tự seed.
- Thêm foreign key thật cho chủ hàng/SKU/kho của inventory_balances.
- Tách seed demo thành app/demo_seed.py, chỉ cho phép chạy khi chỉ định SQLite và xác nhận demo. app/seed.py nay chỉ tương thích lệnh cũ bằng cách migrate schema, không chèn dữ liệu.
- Thêm bootstrap chỉ chuyển tài khoản/hash; từ chối target đã có dữ liệu, không copy chứng từ/tồn.
- Thêm khai báo kho đầu tiên trên giao diện và quản lý phạm vi tài khoản/membership, để bạn tự cấu hình từ database trống.
- Tách frontend admin thành dashboard, dispatch, handover; admin chỉ giữ layout.
- Tách schema khỏi router của auth/catalog/inventory; tách session service, tồn kho service, dashboard và audit thành file riêng.
- Giữ luồng nhập → giữ hàng → soạn/đóng kiện → shipper → xác nhận kho; xuất tồn theo số lượng SKU, không theo số kiện.
- Giữ CSRF, access policy, scope, version, idempotency và audit transaction.

Hướng dẫn Sites được áp dụng ở chế độ local cho phần giao diện: giữ Vue/thiết kế hiện có, bổ sung trạng thái trống và kiểm thử responsive. Không publish lên hosting ngoài.

## 3. Cách chạy

Docker Desktop cần đang chạy. Từ thư mục gốc:

~~~powershell
# Bật PostgreSQL riêng của dự án
docker compose --env-file distriflow/infra/.env -f distriflow/infra/compose.yaml up -d db

# Terminal backend: migrate rồi chạy, KHÔNG seed demo
.\distriflow\backend\start.ps1

# Terminal frontend
.\distriflow\frontend\start.ps1
~~~

- Giao diện: http://127.0.0.1:5173/login
- API: http://127.0.0.1:8000/docs
- Liveness: http://127.0.0.1:8000/health
- Database readiness: http://127.0.0.1:8000/health/ready
- Không chạy thêm tiến trình cùng cổng nếu đã có ứng dụng đang chạy.

### Cấu hình

- backend/.env chứa DATABASE_URL tới PostgreSQL localhost:55432 và COOKIE_SECURE.
- infra/.env chứa mật khẩu PostgreSQL riêng; cả hai file đã loại khỏi Git.
- Ví dụ cấu hình: [backend/.env.example](./distriflow/backend/.env.example), [infra/.env.example](./distriflow/infra/.env.example).
- Biến môi trường shell có độ ưu tiên cao hơn .env. Không chia sẻ URL có mật khẩu.
- Dùng COOKIE_SECURE=true khi có HTTPS.
- Tài khoản local: [accounts.local.json](./distriflow/backend/accounts.local.json), không đưa vào Git.

Sửa password trong JSON **không tự đổi password hash trong PostgreSQL**. Đổi mật khẩu tương tác:

~~~powershell
cd distriflow/backend
python -m app.manage password admin
~~~

Lệnh thu hồi session cũ; không tự sửa file JSON. Các mật khẩu bạn đã yêu cầu đồng bộ trước đó được giữ khi chuyển tài khoản.

### Cài máy mới

Python 3.12+, Node 22/pnpm 9, Docker Desktop:

~~~powershell
cd distriflow/backend
python -m pip install -r requirements.txt
# Cấu hình backend/.env, infra/.env và bật PostgreSQL trước
python -m app.setup.migrate
cd ../frontend
corepack pnpm install --frozen-lockfile
~~~

Bootstrap tài khoản chỉ cần khi tạo database mới có sẵn SQLite nguồn và chủ đích giữ tài khoản:

~~~powershell
cd distriflow/backend
python -m app.setup.bootstrap --accounts-from-sqlite distriflow.db
~~~

**Không chạy lại bootstrap trên database đang dùng.** Nó từ chối nếu target đã có bất kỳ record nào; không xóa hoặc ghi đè để ép nhập.

## 4. Nhập dữ liệu thật lần đầu

1. Đăng nhập admin, vào **Danh mục & vị trí → Kho**, nhập tên kho thực tế. Tài khoản admin được gán kho vừa khai báo; chưa hỗ trợ admin tạo thêm nhiều kho ngoài scope.
2. Vào **Đối tác**, nhập supplier và chủ hàng/retailer thật.
3. Trong Danh mục, nhập **SKU + tên hàng + đơn vị cơ sở**, **vị trí kho**, **quan hệ supplier/chủ hàng/SKU**.
4. Vào **Tài khoản & phạm vi**, gán kho cho dispatch/shipper; gán kho và đúng tổ chức cho supplier/retailer. Tài khoản được thay đổi cần đăng nhập lại.
5. Supplier hoặc admin tạo yêu cầu nhập; admin duyệt, kiểm nhận hàng tốt/cách ly và xác nhận vị trí cất. Chỉ bước cất hàng mới tăng tồn.
6. Retailer hoặc admin tạo yêu cầu xuất; admin duyệt giữ hàng, soạn và đóng kiện.
7. Điều phối gán shipper nếu chọn DistriFlow. Shipper nhận, báo đến kho, đối chiếu đủ mã và xác nhận.
8. Admin xác nhận tại kho: xuất đúng lượng SKU và tạo một biên nhận trong cùng transaction.

Không có nút tự sinh tồn đầu kỳ giả. Nếu cần tồn đầu kỳ, cần chứng từ nhập phản ánh số lượng kiểm đếm thật. Hiện không có import Excel/CSV tự động.

## 5. Cấu trúc file theo module

~~~text
Class/
  README.md
  docs/
    database-status.json             Bằng chứng metadata/số lượng thực tế
    screenshots/
  distriflow/
    backend/
      app/
        main.py                      Bootstrap API, routers, error/health
        models.py                    Registry SQLAlchemy
        core/
          config.py                  .env và cấu hình
          database.py                Engine/session, pool pre-ping
          commands.py                Transaction, replay và audit
          schemas.py                 Version và dòng hàng dùng chung
        setup/
          migrate.py                 Alembic upgrade
          bootstrap.py               Chuyển account hash, không nghiệp vụ
          status.py                  Đọc metadata/số lượng, không secrets
        modules/
          auth/
            models.py access.py schemas.py service.py router.py scopes.py
          catalog/
            models.py schemas.py service.py router.py
          inbound/
            models.py schemas.py service.py router.py
          outbound/
            models.py schemas.py service.py router.py
          inventory/
            models.py schemas.py service.py router.py
          dispatch/
            models.py schemas.py projections.py service.py commands.py router.py
          handover/
            models.py schemas.py service.py router.py
          platform/
            dashboard.py audit.py router.py
        manage.py                    Đổi mật khẩu tương tác
        seed.py                      Migrate-only, không chèn demo
        demo_seed.py                 Demo SQLite có chốt xác nhận
      migrations/
        env.py script.py.mako
        versions/20261123_01_initial_schema.py
      alembic.ini
      tests/
        test_access.py test_workflow.py test_onboarding.py
        run_postgres.py              Database kiểm thử riêng
        serve_e2e.py                 API E2E với SQLite cô lập
      start.ps1 requirements.txt
    frontend/src/
      app/access.ts                  Session và can(permission)
      router/index.ts                Guard tất cả matched routes
      features/
        admin/AdminLayout.vue        Shell quản trị
        dashboard/                   DashboardPage, FlowChart
        dispatch/                    Điều phối
        handover/                    List, detail, TaskTable, useOperations
        auth/                        Login, forbidden
        accounts/                    Gán kho và tổ chức tài khoản
        catalog/                     Danh mục, kho và đối tác
        inbound/ outbound/           Chứng từ nhập/xuất
        inventory/                   Tồn và lịch sử
        partner/ shipper/            Cổng đối tác và shipper
      shared/api/                    HTTP/CSRF/idempotency
      shared/components/             Form/bảng/trạng thái
      shared/types/                  DTO
    contracts/
      openapi.json
      schema.postgresql.sql          SQL sinh từ revision Alembic
    infra/
      compose.yaml .env.example
~~~

### Kiến trúc hệ thống

~~~mermaid
flowchart TB
    U[Admin / Điều phối / Supplier / Retailer / Shipper] --> FE[Vue 3 / TypeScript]
    FE --> RG[Route guard / access]
    FE --> HTTP[HTTP / cookie / CSRF / command key]
    HTTP -->|/api/v1| API[FastAPI routers + schemas]
    API --> AUTH[Auth / quyền / kho / membership]
    AUTH --> CAT[Catalog]
    AUTH --> IN[Inbound]
    AUTH --> OUT[Outbound]
    AUTH --> DIS[Dispatch]
    AUTH --> HAN[Handover]
    AUTH --> PL[Dashboard / Audit]
    OUT --> DIS
    IN --> INV[Inventory service]
    OUT --> INV
    HAN --> INV
    CAT --> CMD[Transaction / replay / audit]
    IN --> CMD
    OUT --> CMD
    DIS --> CMD
    HAN --> CMD
    CMD --> PG[(PostgreSQL 16 / dữ liệu sử dụng)]
    INV --> PG
    PL --> PG
    MIG[Alembic / frozen revisions] -->|DDL| PG
    TEST[API tests] --> TPG[(distriflow_module_tests)]
    E2E[Browser workflow fixtures] --> TS[(SQLite E2E riêng)]
~~~

Test không dùng database nghiệp vụ để ghi chứng từ. Kiểm thử live PostgreSQL chỉ đăng nhập, đọc trạng thái trống rồi logout.

## 6. ERD PostgreSQL

Chia thành các nhóm để dễ đọc; cùng tên bảng ở hai sơ đồ là cùng một bảng. Các cạnh dưới đây là FK thật, ngoại trừ chỗ ghi rõ quan hệ chuỗi ở phần ghi chú.

### Tài khoản và danh mục

~~~mermaid
erDiagram
    users ||--o{ access_sessions : authenticates
    users ||--o{ partner_memberships : belongs
    organizations ||--o{ partner_memberships : members
    organizations ||--o{ skus : owns
    organizations ||--o{ supply_relationships : supplier_or_owner
    skus ||--o{ supply_relationships : allowed
    warehouses ||--o{ storage_locations : contains
    users {
        string id PK
        string username UK
        string password_hash
        string role
        string warehouse_scope
        boolean active
    }
    skus {
        string id PK
        string code UK
        string owner_id FK
        string name
        string base_unit
    }
    organizations {
        string id PK
        string name
        string kind
        boolean active
    }
~~~

users.warehouse_scope hiện vẫn là tên kho dạng chuỗi, được service kiểm tra; chưa đổi thành FK hoặc mô hình nhiều kho. pickup_tasks.shipper_id và warehouse_name cũng là chuỗi legacy; không giả định đã có FK ở hai cột này.

### Nhập, xuất và tồn

~~~mermaid
erDiagram
    organizations ||--o{ inbound_requests : supplier_or_owner
    warehouses ||--o{ inbound_requests : receives
    inbound_requests ||--|{ inbound_lines : contains
    skus ||--o{ inbound_lines : item
    inbound_lines ||--o| inbound_postings : stocked_once
    inventory_balances ||--o{ inbound_postings : increases
    organizations ||--o{ outbound_requests : owns
    warehouses ||--o{ outbound_requests : fulfills
    outbound_requests ||--|{ outbound_lines : contains
    skus ||--o{ outbound_lines : item
    outbound_lines ||--o{ outbound_allocations : reserves
    inventory_balances ||--o{ outbound_allocations : allocated_from
    organizations ||--o{ inventory_balances : owner_FK
    skus ||--o{ inventory_balances : sku_code_FK
    warehouses ||--o{ inventory_balances : warehouse_FK
    inventory_balances ||--o| balance_locations : located
    storage_locations ||--o{ balance_locations : stores
    inventory_balances {
        string id PK
        string owner_id FK
        string sku_code FK
        string warehouse_id FK
        int on_hand
        int reserved
        int unavailable
    }
    outbound_requests {
        string id PK
        string owner_id FK
        string warehouse_id FK
        string shipper_mode
        string shipper_id
        string status
        int version
    }
~~~

### Kiện, bàn giao và ghi xuất

~~~mermaid
erDiagram
    outbound_requests ||--o| outbound_tasks : links
    pickup_tasks ||--o| outbound_tasks : links
    pickup_tasks ||--|{ packages : contains
    packages ||--o{ package_items : contents
    outbound_lines ||--o{ package_items : packed_quantity
    pickup_tasks ||--o{ stock_reservations : holds
    inventory_balances ||--o{ stock_reservations : reserved_from
    stock_reservations ||--o| inventory_postings : issued_once
    pickup_tasks ||--o{ inventory_postings : issue
    inventory_balances ||--o{ inventory_postings : decreases
    pickup_tasks ||--o{ package_scans : scans
    packages ||--o{ package_scans : checked
    pickup_tasks ||--o{ handover_confirmations : confirms
    pickup_tasks ||--o| handover_receipts : receipt
~~~

Hai bảng hạ tầng command_receipts và audit_logs lưu actor/action/key/response hoặc trạng thái trước/sau. ID actor/đối tượng trong hai bảng là chuỗi, không có FK. Bảng stock_movements và idempotency_requests giữ để tương thích legacy, không dùng cho giao dịch mới.

### Ràng buộc chính

- available = on_hand - reserved - unavailable.
- Check không âm trên reserved/unavailable; on_hand phải đủ reserved + unavailable.
- inventory_balances có FK chủ hàng, SKU code và kho trong PostgreSQL mới; không tự ALTER SQLite cũ.
- Biên nhận duy nhất theo task; posting xuất duy nhất theo reservation; posting nhập duy nhất theo dòng nhập.
- Scan duy nhất theo task/kiện; xác nhận duy nhất theo task/bên/version.
- Cùng actor/key/nội dung replay response, khác nội dung trả 409.
- Thiếu một SKU khi giữ/xuất thì rollback toàn lệnh, không ghi một phần.

## 7. Class và luồng transaction

~~~mermaid
classDiagram
    class InboundRequest {
        status: string
        version: int
    }
    class OutboundRequest {
        status: string
        version: int
        shipper_mode: string
    }
    class PickupTask {
        shipper_id: string
        status: string
        version: int
    }
    class InventoryBalance {
        on_hand: int
        reserved: int
        unavailable: int
    }
    class StockReservation {
        quantity: int
        state: string
    }
    class Receipt {
        number: string
        issued_at: datetime
    }
    class InboundService {
        <<module>>
        create()
        review()
        receive()
        putaway()
    }
    class OutboundService {
        <<module>>
        create()
        approve()
        pick()
        pack()
        cancel()
    }
    class HandoverService {
        <<module>>
        scan()
        shipper_confirm()
        warehouse_confirm()
    }
    class InventoryService {
        <<module>>
        issue_reserved_stock()
        hold_stock()
    }
    class Commands {
        <<module>>
        execute()
    }
    InboundService ..> InboundRequest
    InboundService ..> InventoryBalance
    OutboundService ..> OutboundRequest
    OutboundService ..> PickupTask
    OutboundService ..> StockReservation
    PickupTask "1" --> "*" StockReservation
    StockReservation "*" --> "1" InventoryBalance
    HandoverService ..> PickupTask
    HandoverService ..> InventoryService
    HandoverService ..> Receipt
    Commands ..> InboundService
    Commands ..> OutboundService
    Commands ..> HandoverService
~~~

Model là lớp SQLAlchemy thật. Hộp stereotype module biểu diễn file service viết bằng hàm, không phải class Python giả.

~~~mermaid
sequenceDiagram
    actor Kho
    participant Router
    participant Commands
    participant Handover
    participant Inventory
    participant PG as PostgreSQL
    Kho->>Router: Xác nhận kho + version + key + CSRF
    Router->>PG: Kiểm tra quyền và task trong kho
    Router->>Commands: execute
    Commands->>PG: Tìm command receipt actor/key
    alt Cùng lệnh đã hoàn tất
        PG-->>Commands: Response đã lưu
    else Lệnh mới
        Commands->>Handover: warehouse_confirm
        Handover->>PG: Kiểm tra version và xác nhận shipper
        Handover->>Inventory: issue_reserved_stock
        Inventory->>PG: Khóa reservation/số dư; UPDATE có điều kiện
        Handover->>PG: Xác nhận kho + biên nhận + trạng thái
        Commands->>PG: Audit + command receipt + COMMIT
        Note over Commands,PG: Lỗi bất kỳ: ROLLBACK, không xuất một phần
    end
    Commands-->>Kho: Kết quả
~~~

## 8. Chức năng và phân quyền

| Module | Chức năng | Người dùng/phạm vi |
| --- | --- | --- |
| Auth | Login/logout, cookie HttpOnly, CSRF, hồ sơ access | User active, session còn hạn |
| Tài khoản | Gán kho và đúng tổ chức, thu hồi phiên tài khoản đổi scope | Admin; chỉ tài khoản chưa gán hoặc cùng kho |
| Catalog | Tạo/xem kho đầu tiên, đối tác, SKU, vị trí, cung ứng | Admin tạo; đối tác đọc phần liên quan |
| Inbound | Gửi, duyệt/từ chối, kiểm nhận tốt/cách ly, cất tăng tồn | Supplier của mình; admin trong kho |
| Outbound | Gửi, duyệt giữ hàng, soạn, đóng kiện, hủy trước packing | Retailer của mình; admin xử lý |
| Inventory | Số dư theo owner/SKU/vị trí, lịch sử, khóa/mở lượng hàng | Admin quản lý; retailer chỉ tồn của mình |
| Dispatch | Phân công shipper cùng kho, nhận và báo đến kho | Dispatch/admin; shipper đúng nhiệm vụ |
| Handover | Quét đủ kiện, xác nhận hai bên, ghi xuất, biên nhận JSON/in chi tiết | Shipper được phân và admin kho |
| Platform | Dashboard 30 ngày, audit API | Admin/dispatch xem dashboard; admin xem audit |

Nguồn quyền: auth/access.py. Frontend dùng can(permission), router kiểm tra mọi matched route; backend kiểm tra độc lập. Sai quyền/phạm vi trả 403/404; version cũ/sai bước/xung đột trả 409.

Luồng trạng thái: nhập submitted → approved → received → stocked; từ chối từ submitted. Xuất submitted → approved → picked → packed → handed_over; chỉ hủy ở submitted/approved và giải phóng phần đã giữ. Task ready_for_handover → pending_confirmations → handed_over.

API đầy đủ: [openapi.json](./distriflow/contracts/openapi.json). POST nghiệp vụ cần Idempotency-Key và CSRF; chuyển bước cần version. Account scope là cấu hình quản trị, chưa dùng version riêng.

## 9. Kiểm chứng và bảo trì schema

Đã kiểm tra đợt này:

- 17 backend tests đạt trên **PostgreSQL thật** trong database distriflow_module_tests, schema cô lập từng test rồi dọn.
- 17 backend tests nhanh đạt trên SQLite in-memory, không phải bằng chứng thay thế PostgreSQL.
- 3 E2E module đạt: danh mục lưu reload, khởi tạo kho/gán scope, full nhập → xuất → bàn giao.
- 6 E2E live/giao diện đạt: xác nhận PostgreSQL trống, desktop/mobile và tab shipper.
- TypeScript/Vite build đạt; Alembic check không có khác biệt model/schema.
- Có cảnh báo deprecation thư viện/UTC legacy, không phải lỗi test. Chưa kiểm thử tải cao hoặc production.

~~~powershell
cd distriflow/backend
python -m alembic current
python -m alembic check
python -m pytest -q
python -m tests.run_postgres
cd ../frontend
corepack pnpm run build
corepack pnpm run test:modules
corepack pnpm run test:e2e
~~~

Trước lần chạy PostgreSQL tests đầu tiên, tạo database kiểm thử riêng:

~~~powershell
docker compose --env-file distriflow/infra/.env -f distriflow/infra/compose.yaml exec -T db createdb -U distriflow distriflow_module_tests
~~~

Không chạy test ghi nghiệp vụ trên database sử dụng. Test postgres-empty chỉ phù hợp **trước khi nhập dữ liệu thật**; sau đó chạy bộ responsive riêng bằng Playwright reference-layout.spec.ts. Các ảnh trong screenshots/modules là fixture kiểm thử, không phải số liệu vận hành.

Alembic quản lý revision và nâng schema bằng upgrade head theo [tài liệu chính thức](https://alembic.sqlalchemy.org/en/latest/tutorial.html). Container dùng volume bền vững và healthcheck theo [PostgreSQL Official Image](https://hub.docker.com/_/postgres). Không dùng docker compose down -v hoặc downgrade trên dữ liệu thật khi chưa có backup/được phê duyệt.

## 10. Giới hạn còn lại

- Một role/một kho theo tên cho mỗi user; chưa nhiều-kho, chưa tạo/xóa tài khoản hoặc đổi role qua UI.
- Danh mục chủ yếu tạo/xem; chưa sửa/xóa/nhập Excel hàng loạt.
- Lượng hàng nguyên theo đơn vị cơ sở, chưa số lẻ/quy đổi/lot/serial/hạn dùng.
- Đóng kiện tự chia lượng nguyên, chưa packing tương tác; biên nhận JSON và in trình duyệt, chưa PDF/ký số.
- Chưa chuyển kho, hoàn/đảo sau đóng gói/bàn giao, kiểm kê, báo cáo chuyên sâu, cấu hình nghiệp vụ hoặc tích hợp hãng vận chuyển.
- Cần rate limit login, giám sát, backup/restore theo lịch, HTTPS và tải đồng thời quy mô lớn trước production.
- Docker DB đã kiểm chứng; profile full api/web có sẵn nhưng chưa được kiểm chứng triển khai toàn bộ bằng container.
