--
-- PostgreSQL database dump
--

\restrict wjVePKn2D1DxEakUxcRlyEnEhtLauetnbRQ7F05hjMXBzcGNDhauRDXoVIzrWzL

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: access_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.access_sessions (
    token_hash character varying NOT NULL,
    user_id character varying NOT NULL,
    csrf_token character varying NOT NULL,
    expires_at timestamp without time zone NOT NULL
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.audit_logs (
    id character varying NOT NULL,
    actor_id character varying NOT NULL,
    object_id character varying NOT NULL,
    action character varying NOT NULL,
    before json NOT NULL,
    after json NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: balance_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.balance_locations (
    balance_id character varying NOT NULL,
    location_id character varying NOT NULL
);


--
-- Name: command_receipts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.command_receipts (
    id character varying NOT NULL,
    actor_id character varying NOT NULL,
    key character varying NOT NULL,
    fingerprint character varying NOT NULL,
    response json NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: handover_confirmations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.handover_confirmations (
    id character varying NOT NULL,
    task_id character varying NOT NULL,
    side character varying NOT NULL,
    version integer NOT NULL,
    actor_id character varying NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: handover_receipts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.handover_receipts (
    id character varying NOT NULL,
    task_id character varying NOT NULL,
    number character varying NOT NULL,
    issued_at timestamp without time zone NOT NULL
);


--
-- Name: idempotency_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.idempotency_requests (
    id character varying NOT NULL,
    actor_id character varying NOT NULL,
    key character varying NOT NULL,
    task_id character varying NOT NULL,
    response_status character varying NOT NULL
);


--
-- Name: inbound_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inbound_lines (
    id character varying NOT NULL,
    request_id character varying NOT NULL,
    sku_id character varying NOT NULL,
    quantity integer NOT NULL,
    good integer NOT NULL,
    quarantined integer NOT NULL
);


--
-- Name: inbound_postings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inbound_postings (
    id character varying NOT NULL,
    line_id character varying NOT NULL,
    balance_id character varying NOT NULL,
    quantity integer NOT NULL,
    quarantined integer NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: inbound_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inbound_requests (
    id character varying NOT NULL,
    code character varying NOT NULL,
    supplier_id character varying NOT NULL,
    owner_id character varying NOT NULL,
    warehouse_id character varying NOT NULL,
    status character varying NOT NULL,
    version integer NOT NULL,
    note text NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: inventory_balances; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_balances (
    id character varying NOT NULL,
    owner_id character varying NOT NULL,
    sku_code character varying NOT NULL,
    warehouse_id character varying NOT NULL,
    on_hand integer NOT NULL,
    reserved integer NOT NULL,
    unavailable integer NOT NULL,
    CONSTRAINT ck_stock_nonnegative CHECK (((on_hand >= (reserved + unavailable)) AND (reserved >= 0) AND (unavailable >= 0)))
);


--
-- Name: inventory_postings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_postings (
    id character varying NOT NULL,
    reservation_id character varying NOT NULL,
    balance_id character varying NOT NULL,
    task_id character varying NOT NULL,
    quantity integer NOT NULL,
    kind character varying NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: organizations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.organizations (
    id character varying NOT NULL,
    name character varying NOT NULL,
    kind character varying NOT NULL,
    active boolean NOT NULL,
    supplied_goods character varying(1000)
);


--
-- Name: outbound_allocations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outbound_allocations (
    id character varying NOT NULL,
    line_id character varying NOT NULL,
    balance_id character varying NOT NULL,
    quantity integer NOT NULL,
    state character varying NOT NULL
);


--
-- Name: outbound_lines; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outbound_lines (
    id character varying NOT NULL,
    request_id character varying NOT NULL,
    sku_id character varying NOT NULL,
    quantity integer NOT NULL
);


--
-- Name: outbound_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outbound_requests (
    id character varying NOT NULL,
    code character varying NOT NULL,
    owner_id character varying NOT NULL,
    warehouse_id character varying NOT NULL,
    shipper_mode character varying NOT NULL,
    shipper_id character varying NOT NULL,
    status character varying NOT NULL,
    version integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: outbound_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.outbound_tasks (
    request_id character varying NOT NULL,
    task_id character varying NOT NULL
);


--
-- Name: package_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.package_items (
    id character varying NOT NULL,
    package_id character varying NOT NULL,
    line_id character varying NOT NULL,
    quantity integer NOT NULL
);


--
-- Name: package_scans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.package_scans (
    id character varying NOT NULL,
    task_id character varying NOT NULL,
    package_id character varying NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: packages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.packages (
    id character varying NOT NULL,
    task_id character varying NOT NULL,
    code character varying NOT NULL
);


--
-- Name: partner_memberships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.partner_memberships (
    user_id character varying NOT NULL,
    organization_id character varying NOT NULL
);


--
-- Name: pickup_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pickup_tasks (
    id character varying NOT NULL,
    code character varying NOT NULL,
    warehouse_name character varying NOT NULL,
    shipper_id character varying NOT NULL,
    status character varying NOT NULL,
    version integer NOT NULL,
    shipper_accepted boolean NOT NULL,
    arrived_at_warehouse boolean NOT NULL
);


--
-- Name: skus; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.skus (
    id character varying NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    base_unit character varying NOT NULL,
    owner_id character varying NOT NULL
);


--
-- Name: stock_movements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_movements (
    id character varying NOT NULL,
    source_task_id character varying NOT NULL,
    kind character varying NOT NULL,
    quantity integer NOT NULL,
    at timestamp without time zone NOT NULL
);


--
-- Name: stock_reservations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stock_reservations (
    id character varying NOT NULL,
    task_id character varying NOT NULL,
    balance_id character varying NOT NULL,
    quantity integer NOT NULL,
    state character varying NOT NULL,
    CONSTRAINT ck_reservation_positive CHECK ((quantity > 0))
);


--
-- Name: storage_locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.storage_locations (
    id character varying NOT NULL,
    warehouse_id character varying NOT NULL,
    code character varying NOT NULL,
    rack_row integer,
    rack_level integer,
    rack_bay integer,
    rack_depth integer,
    CONSTRAINT ck_storage_rack_coordinate CHECK ((((rack_row IS NULL) AND (rack_level IS NULL) AND (rack_bay IS NULL) AND (rack_depth IS NULL)) OR ((rack_row IS NOT NULL) AND (rack_level IS NOT NULL) AND (rack_bay IS NOT NULL) AND (rack_depth IS NOT NULL) AND ((rack_row >= 1) AND (rack_row <= 8)) AND ((rack_level >= 1) AND (rack_level <= 10)) AND ((rack_bay >= 1) AND (rack_bay <= 10)) AND (rack_depth = 1))))
);


--
-- Name: supply_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.supply_relationships (
    id character varying NOT NULL,
    supplier_id character varying NOT NULL,
    owner_id character varying NOT NULL,
    sku_id character varying NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id character varying NOT NULL,
    username character varying NOT NULL,
    password_hash character varying NOT NULL,
    role character varying NOT NULL,
    warehouse_scope character varying NOT NULL,
    active boolean NOT NULL,
    display_name character varying,
    deleted_at timestamp without time zone,
    version integer DEFAULT 1 NOT NULL
);


--
-- Name: warehouses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.warehouses (
    id character varying NOT NULL,
    name character varying NOT NULL
);


--
-- Name: access_sessions access_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.access_sessions
    ADD CONSTRAINT access_sessions_pkey PRIMARY KEY (token_hash);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: balance_locations balance_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.balance_locations
    ADD CONSTRAINT balance_locations_pkey PRIMARY KEY (balance_id);


--
-- Name: command_receipts command_receipts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.command_receipts
    ADD CONSTRAINT command_receipts_pkey PRIMARY KEY (id);


--
-- Name: handover_confirmations handover_confirmations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_confirmations
    ADD CONSTRAINT handover_confirmations_pkey PRIMARY KEY (id);


--
-- Name: handover_receipts handover_receipts_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_receipts
    ADD CONSTRAINT handover_receipts_number_key UNIQUE (number);


--
-- Name: handover_receipts handover_receipts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_receipts
    ADD CONSTRAINT handover_receipts_pkey PRIMARY KEY (id);


--
-- Name: handover_receipts handover_receipts_task_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_receipts
    ADD CONSTRAINT handover_receipts_task_id_key UNIQUE (task_id);


--
-- Name: idempotency_requests idempotency_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.idempotency_requests
    ADD CONSTRAINT idempotency_requests_pkey PRIMARY KEY (id);


--
-- Name: inbound_lines inbound_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_lines
    ADD CONSTRAINT inbound_lines_pkey PRIMARY KEY (id);


--
-- Name: inbound_postings inbound_postings_line_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_postings
    ADD CONSTRAINT inbound_postings_line_id_key UNIQUE (line_id);


--
-- Name: inbound_postings inbound_postings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_postings
    ADD CONSTRAINT inbound_postings_pkey PRIMARY KEY (id);


--
-- Name: inbound_requests inbound_requests_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_requests
    ADD CONSTRAINT inbound_requests_code_key UNIQUE (code);


--
-- Name: inbound_requests inbound_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_requests
    ADD CONSTRAINT inbound_requests_pkey PRIMARY KEY (id);


--
-- Name: inventory_balances inventory_balances_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_balances
    ADD CONSTRAINT inventory_balances_pkey PRIMARY KEY (id);


--
-- Name: inventory_postings inventory_postings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_postings
    ADD CONSTRAINT inventory_postings_pkey PRIMARY KEY (id);


--
-- Name: inventory_postings inventory_postings_reservation_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_postings
    ADD CONSTRAINT inventory_postings_reservation_id_key UNIQUE (reservation_id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: outbound_allocations outbound_allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_allocations
    ADD CONSTRAINT outbound_allocations_pkey PRIMARY KEY (id);


--
-- Name: outbound_lines outbound_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_lines
    ADD CONSTRAINT outbound_lines_pkey PRIMARY KEY (id);


--
-- Name: outbound_requests outbound_requests_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_requests
    ADD CONSTRAINT outbound_requests_code_key UNIQUE (code);


--
-- Name: outbound_requests outbound_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_requests
    ADD CONSTRAINT outbound_requests_pkey PRIMARY KEY (id);


--
-- Name: outbound_tasks outbound_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_tasks
    ADD CONSTRAINT outbound_tasks_pkey PRIMARY KEY (request_id);


--
-- Name: outbound_tasks outbound_tasks_task_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_tasks
    ADD CONSTRAINT outbound_tasks_task_id_key UNIQUE (task_id);


--
-- Name: package_items package_items_package_id_line_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_items
    ADD CONSTRAINT package_items_package_id_line_id_key UNIQUE (package_id, line_id);


--
-- Name: package_items package_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_items
    ADD CONSTRAINT package_items_pkey PRIMARY KEY (id);


--
-- Name: package_scans package_scans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_scans
    ADD CONSTRAINT package_scans_pkey PRIMARY KEY (id);


--
-- Name: packages packages_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.packages
    ADD CONSTRAINT packages_code_key UNIQUE (code);


--
-- Name: packages packages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.packages
    ADD CONSTRAINT packages_pkey PRIMARY KEY (id);


--
-- Name: partner_memberships partner_memberships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.partner_memberships
    ADD CONSTRAINT partner_memberships_pkey PRIMARY KEY (user_id, organization_id);


--
-- Name: pickup_tasks pickup_tasks_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pickup_tasks
    ADD CONSTRAINT pickup_tasks_code_key UNIQUE (code);


--
-- Name: pickup_tasks pickup_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pickup_tasks
    ADD CONSTRAINT pickup_tasks_pkey PRIMARY KEY (id);


--
-- Name: skus skus_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_code_key UNIQUE (code);


--
-- Name: skus skus_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_pkey PRIMARY KEY (id);


--
-- Name: stock_movements stock_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT stock_movements_pkey PRIMARY KEY (id);


--
-- Name: stock_reservations stock_reservations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_reservations
    ADD CONSTRAINT stock_reservations_pkey PRIMARY KEY (id);


--
-- Name: stock_reservations stock_reservations_task_id_balance_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_reservations
    ADD CONSTRAINT stock_reservations_task_id_balance_id_key UNIQUE (task_id, balance_id);


--
-- Name: storage_locations storage_locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT storage_locations_pkey PRIMARY KEY (id);


--
-- Name: storage_locations storage_locations_warehouse_id_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT storage_locations_warehouse_id_code_key UNIQUE (warehouse_id, code);


--
-- Name: supply_relationships supply_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supply_relationships
    ADD CONSTRAINT supply_relationships_pkey PRIMARY KEY (id);


--
-- Name: supply_relationships supply_relationships_supplier_id_owner_id_sku_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supply_relationships
    ADD CONSTRAINT supply_relationships_supplier_id_owner_id_sku_id_key UNIQUE (supplier_id, owner_id, sku_id);


--
-- Name: idempotency_requests uq_actor_idempotency; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.idempotency_requests
    ADD CONSTRAINT uq_actor_idempotency UNIQUE (actor_id, key);


--
-- Name: command_receipts uq_command_actor_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.command_receipts
    ADD CONSTRAINT uq_command_actor_key UNIQUE (actor_id, key);


--
-- Name: handover_confirmations uq_confirmation_version; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_confirmations
    ADD CONSTRAINT uq_confirmation_version UNIQUE (task_id, side, version);


--
-- Name: stock_movements uq_stock_issue_per_task; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_movements
    ADD CONSTRAINT uq_stock_issue_per_task UNIQUE (source_task_id, kind);


--
-- Name: storage_locations uq_storage_rack_coordinate; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT uq_storage_rack_coordinate UNIQUE (warehouse_id, rack_row, rack_level, rack_bay, rack_depth);


--
-- Name: package_scans uq_task_package_scan; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_scans
    ADD CONSTRAINT uq_task_package_scan UNIQUE (task_id, package_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: warehouses warehouses_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_name_key UNIQUE (name);


--
-- Name: warehouses warehouses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.warehouses
    ADD CONSTRAINT warehouses_pkey PRIMARY KEY (id);


--
-- Name: ix_access_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_access_sessions_user_id ON public.access_sessions USING btree (user_id);


--
-- Name: ix_audit_logs_actor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_actor_id ON public.audit_logs USING btree (actor_id);


--
-- Name: ix_audit_logs_object_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_audit_logs_object_id ON public.audit_logs USING btree (object_id);


--
-- Name: ix_command_receipts_actor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_command_receipts_actor_id ON public.command_receipts USING btree (actor_id);


--
-- Name: ix_inbound_lines_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inbound_lines_request_id ON public.inbound_lines USING btree (request_id);


--
-- Name: ix_inbound_requests_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inbound_requests_owner_id ON public.inbound_requests USING btree (owner_id);


--
-- Name: ix_inbound_requests_supplier_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inbound_requests_supplier_id ON public.inbound_requests USING btree (supplier_id);


--
-- Name: ix_inventory_balances_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_balances_owner_id ON public.inventory_balances USING btree (owner_id);


--
-- Name: ix_inventory_postings_balance_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_postings_balance_id ON public.inventory_postings USING btree (balance_id);


--
-- Name: ix_inventory_postings_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_inventory_postings_task_id ON public.inventory_postings USING btree (task_id);


--
-- Name: ix_outbound_allocations_line_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_outbound_allocations_line_id ON public.outbound_allocations USING btree (line_id);


--
-- Name: ix_outbound_lines_request_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_outbound_lines_request_id ON public.outbound_lines USING btree (request_id);


--
-- Name: ix_outbound_requests_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_outbound_requests_owner_id ON public.outbound_requests USING btree (owner_id);


--
-- Name: ix_package_items_package_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_package_items_package_id ON public.package_items USING btree (package_id);


--
-- Name: ix_packages_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_packages_task_id ON public.packages USING btree (task_id);


--
-- Name: ix_pickup_tasks_shipper_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_pickup_tasks_shipper_id ON public.pickup_tasks USING btree (shipper_id);


--
-- Name: ix_skus_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_skus_owner_id ON public.skus USING btree (owner_id);


--
-- Name: ix_stock_reservations_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_stock_reservations_task_id ON public.stock_reservations USING btree (task_id);


--
-- Name: access_sessions access_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.access_sessions
    ADD CONSTRAINT access_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: balance_locations balance_locations_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.balance_locations
    ADD CONSTRAINT balance_locations_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.inventory_balances(id);


--
-- Name: balance_locations balance_locations_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.balance_locations
    ADD CONSTRAINT balance_locations_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.storage_locations(id);


--
-- Name: handover_confirmations handover_confirmations_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_confirmations
    ADD CONSTRAINT handover_confirmations_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: handover_receipts handover_receipts_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.handover_receipts
    ADD CONSTRAINT handover_receipts_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: inbound_lines inbound_lines_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_lines
    ADD CONSTRAINT inbound_lines_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.inbound_requests(id);


--
-- Name: inbound_lines inbound_lines_sku_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_lines
    ADD CONSTRAINT inbound_lines_sku_id_fkey FOREIGN KEY (sku_id) REFERENCES public.skus(id);


--
-- Name: inbound_postings inbound_postings_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_postings
    ADD CONSTRAINT inbound_postings_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.inventory_balances(id);


--
-- Name: inbound_postings inbound_postings_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_postings
    ADD CONSTRAINT inbound_postings_line_id_fkey FOREIGN KEY (line_id) REFERENCES public.inbound_lines(id);


--
-- Name: inbound_requests inbound_requests_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_requests
    ADD CONSTRAINT inbound_requests_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.organizations(id);


--
-- Name: inbound_requests inbound_requests_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_requests
    ADD CONSTRAINT inbound_requests_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.organizations(id);


--
-- Name: inbound_requests inbound_requests_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inbound_requests
    ADD CONSTRAINT inbound_requests_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: inventory_balances inventory_balances_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_balances
    ADD CONSTRAINT inventory_balances_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.organizations(id);


--
-- Name: inventory_balances inventory_balances_sku_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_balances
    ADD CONSTRAINT inventory_balances_sku_code_fkey FOREIGN KEY (sku_code) REFERENCES public.skus(code);


--
-- Name: inventory_balances inventory_balances_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_balances
    ADD CONSTRAINT inventory_balances_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: inventory_postings inventory_postings_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_postings
    ADD CONSTRAINT inventory_postings_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.inventory_balances(id);


--
-- Name: inventory_postings inventory_postings_reservation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_postings
    ADD CONSTRAINT inventory_postings_reservation_id_fkey FOREIGN KEY (reservation_id) REFERENCES public.stock_reservations(id);


--
-- Name: inventory_postings inventory_postings_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_postings
    ADD CONSTRAINT inventory_postings_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: outbound_allocations outbound_allocations_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_allocations
    ADD CONSTRAINT outbound_allocations_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.inventory_balances(id);


--
-- Name: outbound_allocations outbound_allocations_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_allocations
    ADD CONSTRAINT outbound_allocations_line_id_fkey FOREIGN KEY (line_id) REFERENCES public.outbound_lines(id);


--
-- Name: outbound_lines outbound_lines_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_lines
    ADD CONSTRAINT outbound_lines_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.outbound_requests(id);


--
-- Name: outbound_lines outbound_lines_sku_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_lines
    ADD CONSTRAINT outbound_lines_sku_id_fkey FOREIGN KEY (sku_id) REFERENCES public.skus(id);


--
-- Name: outbound_requests outbound_requests_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_requests
    ADD CONSTRAINT outbound_requests_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.organizations(id);


--
-- Name: outbound_requests outbound_requests_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_requests
    ADD CONSTRAINT outbound_requests_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: outbound_tasks outbound_tasks_request_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_tasks
    ADD CONSTRAINT outbound_tasks_request_id_fkey FOREIGN KEY (request_id) REFERENCES public.outbound_requests(id);


--
-- Name: outbound_tasks outbound_tasks_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.outbound_tasks
    ADD CONSTRAINT outbound_tasks_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: package_items package_items_line_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_items
    ADD CONSTRAINT package_items_line_id_fkey FOREIGN KEY (line_id) REFERENCES public.outbound_lines(id);


--
-- Name: package_items package_items_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_items
    ADD CONSTRAINT package_items_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.packages(id);


--
-- Name: package_scans package_scans_package_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_scans
    ADD CONSTRAINT package_scans_package_id_fkey FOREIGN KEY (package_id) REFERENCES public.packages(id);


--
-- Name: package_scans package_scans_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.package_scans
    ADD CONSTRAINT package_scans_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: packages packages_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.packages
    ADD CONSTRAINT packages_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: partner_memberships partner_memberships_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.partner_memberships
    ADD CONSTRAINT partner_memberships_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: partner_memberships partner_memberships_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.partner_memberships
    ADD CONSTRAINT partner_memberships_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: skus skus_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skus
    ADD CONSTRAINT skus_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.organizations(id);


--
-- Name: stock_reservations stock_reservations_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_reservations
    ADD CONSTRAINT stock_reservations_balance_id_fkey FOREIGN KEY (balance_id) REFERENCES public.inventory_balances(id);


--
-- Name: stock_reservations stock_reservations_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stock_reservations
    ADD CONSTRAINT stock_reservations_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.pickup_tasks(id);


--
-- Name: storage_locations storage_locations_warehouse_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.storage_locations
    ADD CONSTRAINT storage_locations_warehouse_id_fkey FOREIGN KEY (warehouse_id) REFERENCES public.warehouses(id);


--
-- Name: supply_relationships supply_relationships_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supply_relationships
    ADD CONSTRAINT supply_relationships_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.organizations(id);


--
-- Name: supply_relationships supply_relationships_sku_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supply_relationships
    ADD CONSTRAINT supply_relationships_sku_id_fkey FOREIGN KEY (sku_id) REFERENCES public.skus(id);


--
-- Name: supply_relationships supply_relationships_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.supply_relationships
    ADD CONSTRAINT supply_relationships_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.organizations(id);


--
-- PostgreSQL database dump complete
--

\unrestrict wjVePKn2D1DxEakUxcRlyEnEhtLauetnbRQ7F05hjMXBzcGNDhauRDXoVIzrWzL
