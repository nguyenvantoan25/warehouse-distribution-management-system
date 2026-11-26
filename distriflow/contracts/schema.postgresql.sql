BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 20261123_01

CREATE TABLE audit_logs (
    id VARCHAR NOT NULL, 
    actor_id VARCHAR NOT NULL, 
    object_id VARCHAR NOT NULL, 
    action VARCHAR NOT NULL, 
    before JSON NOT NULL, 
    after JSON NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_audit_logs_actor_id ON audit_logs (actor_id);

CREATE INDEX ix_audit_logs_object_id ON audit_logs (object_id);

CREATE TABLE command_receipts (
    id VARCHAR NOT NULL, 
    actor_id VARCHAR NOT NULL, 
    key VARCHAR NOT NULL, 
    fingerprint VARCHAR NOT NULL, 
    response JSON NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_command_actor_key UNIQUE (actor_id, key)
);

CREATE INDEX ix_command_receipts_actor_id ON command_receipts (actor_id);

CREATE TABLE idempotency_requests (
    id VARCHAR NOT NULL, 
    actor_id VARCHAR NOT NULL, 
    key VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    response_status VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_actor_idempotency UNIQUE (actor_id, key)
);

CREATE TABLE organizations (
    id VARCHAR NOT NULL, 
    name VARCHAR NOT NULL, 
    kind VARCHAR NOT NULL, 
    active BOOLEAN NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE pickup_tasks (
    id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    warehouse_name VARCHAR NOT NULL, 
    shipper_id VARCHAR NOT NULL, 
    status VARCHAR NOT NULL, 
    version INTEGER NOT NULL, 
    shipper_accepted BOOLEAN NOT NULL, 
    arrived_at_warehouse BOOLEAN NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (code)
);

CREATE INDEX ix_pickup_tasks_shipper_id ON pickup_tasks (shipper_id);

CREATE TABLE stock_movements (
    id VARCHAR NOT NULL, 
    source_task_id VARCHAR NOT NULL, 
    kind VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_stock_issue_per_task UNIQUE (source_task_id, kind)
);

CREATE TABLE users (
    id VARCHAR NOT NULL, 
    username VARCHAR NOT NULL, 
    password_hash VARCHAR NOT NULL, 
    role VARCHAR NOT NULL, 
    warehouse_scope VARCHAR NOT NULL, 
    active BOOLEAN NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (username)
);

CREATE TABLE warehouses (
    id VARCHAR NOT NULL, 
    name VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE access_sessions (
    token_hash VARCHAR NOT NULL, 
    user_id VARCHAR NOT NULL, 
    csrf_token VARCHAR NOT NULL, 
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (token_hash), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_access_sessions_user_id ON access_sessions (user_id);

CREATE TABLE handover_confirmations (
    id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    side VARCHAR NOT NULL, 
    version INTEGER NOT NULL, 
    actor_id VARCHAR NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    CONSTRAINT uq_confirmation_version UNIQUE (task_id, side, version)
);

CREATE TABLE handover_receipts (
    id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    number VARCHAR NOT NULL, 
    issued_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    UNIQUE (number), 
    UNIQUE (task_id)
);

CREATE TABLE inbound_requests (
    id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    supplier_id VARCHAR NOT NULL, 
    owner_id VARCHAR NOT NULL, 
    warehouse_id VARCHAR NOT NULL, 
    status VARCHAR NOT NULL, 
    version INTEGER NOT NULL, 
    note TEXT NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES organizations (id), 
    FOREIGN KEY(supplier_id) REFERENCES organizations (id), 
    FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
    UNIQUE (code)
);

CREATE INDEX ix_inbound_requests_owner_id ON inbound_requests (owner_id);

CREATE INDEX ix_inbound_requests_supplier_id ON inbound_requests (supplier_id);

CREATE TABLE outbound_requests (
    id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    owner_id VARCHAR NOT NULL, 
    warehouse_id VARCHAR NOT NULL, 
    shipper_mode VARCHAR NOT NULL, 
    shipper_id VARCHAR NOT NULL, 
    status VARCHAR NOT NULL, 
    version INTEGER NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES organizations (id), 
    FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
    UNIQUE (code)
);

CREATE INDEX ix_outbound_requests_owner_id ON outbound_requests (owner_id);

CREATE TABLE packages (
    id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    UNIQUE (code)
);

CREATE INDEX ix_packages_task_id ON packages (task_id);

CREATE TABLE partner_memberships (
    user_id VARCHAR NOT NULL, 
    organization_id VARCHAR NOT NULL, 
    PRIMARY KEY (user_id, organization_id), 
    FOREIGN KEY(organization_id) REFERENCES organizations (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE TABLE skus (
    id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    name VARCHAR NOT NULL, 
    base_unit VARCHAR NOT NULL, 
    owner_id VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES organizations (id), 
    UNIQUE (code)
);

CREATE INDEX ix_skus_owner_id ON skus (owner_id);

CREATE TABLE storage_locations (
    id VARCHAR NOT NULL, 
    warehouse_id VARCHAR NOT NULL, 
    code VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(warehouse_id) REFERENCES warehouses (id), 
    UNIQUE (warehouse_id, code)
);

CREATE TABLE inbound_lines (
    id VARCHAR NOT NULL, 
    request_id VARCHAR NOT NULL, 
    sku_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    good INTEGER NOT NULL, 
    quarantined INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(request_id) REFERENCES inbound_requests (id), 
    FOREIGN KEY(sku_id) REFERENCES skus (id)
);

CREATE INDEX ix_inbound_lines_request_id ON inbound_lines (request_id);

CREATE TABLE inventory_balances (
    id VARCHAR NOT NULL, 
    owner_id VARCHAR NOT NULL, 
    sku_code VARCHAR NOT NULL, 
    warehouse_id VARCHAR NOT NULL, 
    on_hand INTEGER NOT NULL, 
    reserved INTEGER NOT NULL, 
    unavailable INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_stock_nonnegative CHECK (on_hand >= reserved + unavailable AND reserved >= 0 AND unavailable >= 0), 
    FOREIGN KEY(owner_id) REFERENCES organizations (id), 
    FOREIGN KEY(sku_code) REFERENCES skus (code), 
    FOREIGN KEY(warehouse_id) REFERENCES warehouses (id)
);

CREATE INDEX ix_inventory_balances_owner_id ON inventory_balances (owner_id);

CREATE TABLE outbound_lines (
    id VARCHAR NOT NULL, 
    request_id VARCHAR NOT NULL, 
    sku_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(request_id) REFERENCES outbound_requests (id), 
    FOREIGN KEY(sku_id) REFERENCES skus (id)
);

CREATE INDEX ix_outbound_lines_request_id ON outbound_lines (request_id);

CREATE TABLE outbound_tasks (
    request_id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    PRIMARY KEY (request_id), 
    FOREIGN KEY(request_id) REFERENCES outbound_requests (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    UNIQUE (task_id)
);

CREATE TABLE package_scans (
    id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    package_id VARCHAR NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(package_id) REFERENCES packages (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    CONSTRAINT uq_task_package_scan UNIQUE (task_id, package_id)
);

CREATE TABLE supply_relationships (
    id VARCHAR NOT NULL, 
    supplier_id VARCHAR NOT NULL, 
    owner_id VARCHAR NOT NULL, 
    sku_id VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(owner_id) REFERENCES organizations (id), 
    FOREIGN KEY(sku_id) REFERENCES skus (id), 
    FOREIGN KEY(supplier_id) REFERENCES organizations (id), 
    UNIQUE (supplier_id, owner_id, sku_id)
);

CREATE TABLE balance_locations (
    balance_id VARCHAR NOT NULL, 
    location_id VARCHAR NOT NULL, 
    PRIMARY KEY (balance_id), 
    FOREIGN KEY(balance_id) REFERENCES inventory_balances (id), 
    FOREIGN KEY(location_id) REFERENCES storage_locations (id)
);

CREATE TABLE inbound_postings (
    id VARCHAR NOT NULL, 
    line_id VARCHAR NOT NULL, 
    balance_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    quarantined INTEGER NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(balance_id) REFERENCES inventory_balances (id), 
    FOREIGN KEY(line_id) REFERENCES inbound_lines (id), 
    UNIQUE (line_id)
);

CREATE TABLE outbound_allocations (
    id VARCHAR NOT NULL, 
    line_id VARCHAR NOT NULL, 
    balance_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    state VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(balance_id) REFERENCES inventory_balances (id), 
    FOREIGN KEY(line_id) REFERENCES outbound_lines (id)
);

CREATE INDEX ix_outbound_allocations_line_id ON outbound_allocations (line_id);

CREATE TABLE package_items (
    id VARCHAR NOT NULL, 
    package_id VARCHAR NOT NULL, 
    line_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(line_id) REFERENCES outbound_lines (id), 
    FOREIGN KEY(package_id) REFERENCES packages (id), 
    UNIQUE (package_id, line_id)
);

CREATE INDEX ix_package_items_package_id ON package_items (package_id);

CREATE TABLE stock_reservations (
    id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    balance_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    state VARCHAR NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_reservation_positive CHECK (quantity > 0), 
    FOREIGN KEY(balance_id) REFERENCES inventory_balances (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    UNIQUE (task_id, balance_id)
);

CREATE INDEX ix_stock_reservations_task_id ON stock_reservations (task_id);

CREATE TABLE inventory_postings (
    id VARCHAR NOT NULL, 
    reservation_id VARCHAR NOT NULL, 
    balance_id VARCHAR NOT NULL, 
    task_id VARCHAR NOT NULL, 
    quantity INTEGER NOT NULL, 
    kind VARCHAR NOT NULL, 
    at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(balance_id) REFERENCES inventory_balances (id), 
    FOREIGN KEY(reservation_id) REFERENCES stock_reservations (id), 
    FOREIGN KEY(task_id) REFERENCES pickup_tasks (id), 
    UNIQUE (reservation_id)
);

CREATE INDEX ix_inventory_postings_balance_id ON inventory_postings (balance_id);

CREATE INDEX ix_inventory_postings_task_id ON inventory_postings (task_id);

INSERT INTO alembic_version (version_num) VALUES ('20261123_01') RETURNING alembic_version.version_num;

-- Running upgrade 20261123_01 -> 20261126_02

ALTER TABLE storage_locations ADD COLUMN rack_row INTEGER;

ALTER TABLE storage_locations ADD COLUMN rack_level INTEGER;

ALTER TABLE storage_locations ADD COLUMN rack_bay INTEGER;

ALTER TABLE storage_locations ADD COLUMN rack_depth INTEGER;

ALTER TABLE storage_locations ADD CONSTRAINT uq_storage_rack_coordinate UNIQUE (warehouse_id, rack_row, rack_level, rack_bay, rack_depth);

ALTER TABLE storage_locations ADD CONSTRAINT ck_storage_rack_coordinate CHECK ((rack_row IS NULL AND rack_level IS NULL AND rack_bay IS NULL AND rack_depth IS NULL) OR (rack_row IS NOT NULL AND rack_level IS NOT NULL AND rack_bay IS NOT NULL AND rack_depth IS NOT NULL AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 AND rack_bay BETWEEN 1 AND 5 AND rack_depth BETWEEN 1 AND 2));

UPDATE alembic_version SET version_num='20261126_02' WHERE alembic_version.version_num = '20261123_01';

-- Running upgrade 20261126_02 -> 20261126_03

ALTER TABLE storage_locations DROP CONSTRAINT ck_storage_rack_coordinate;

ALTER TABLE storage_locations DROP CONSTRAINT uq_storage_rack_coordinate;

UPDATE storage_locations SET rack_bay = (rack_bay - 1) * 2 + rack_depth, rack_depth = 1 WHERE rack_row IS NOT NULL;

ALTER TABLE storage_locations ADD CONSTRAINT ck_storage_rack_coordinate CHECK ((rack_row IS NULL AND rack_level IS NULL AND rack_bay IS NULL AND rack_depth IS NULL) OR (rack_row IS NOT NULL AND rack_level IS NOT NULL AND rack_bay IS NOT NULL AND rack_depth IS NOT NULL AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 AND rack_bay BETWEEN 1 AND 10 AND rack_depth = 1));

ALTER TABLE storage_locations ADD CONSTRAINT uq_storage_rack_coordinate UNIQUE (warehouse_id, rack_row, rack_level, rack_bay, rack_depth);

UPDATE alembic_version SET version_num='20261126_03' WHERE alembic_version.version_num = '20261126_02';

-- Running upgrade 20261126_03 -> 20261126_04

ALTER TABLE users ADD COLUMN display_name VARCHAR;

ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP WITHOUT TIME ZONE;

ALTER TABLE users ADD COLUMN version INTEGER DEFAULT 1 NOT NULL;

ALTER TABLE organizations ADD COLUMN supplied_goods VARCHAR(1000);

UPDATE alembic_version SET version_num='20261126_04' WHERE alembic_version.version_num = '20261126_03';

COMMIT;
