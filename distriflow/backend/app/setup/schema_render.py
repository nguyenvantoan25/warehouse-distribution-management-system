"""Pure renderers for verified schema metadata, with no database writes."""

from html import escape
import re

DESCRIPTIONS = {
    "users": "Tài khoản, hash mật khẩu, vai trò và phạm vi kho.",
    "access_sessions": "Phiên đăng nhập, CSRF token và hạn sử dụng.",
    "organizations": "Tổ chức nhà cung cấp hoặc chủ hàng.",
    "partner_memberships": "Liên kết tài khoản với tổ chức đối tác.",
    "warehouses": "Danh mục kho.",
    "storage_locations": "Vị trí lưu hàng trong kho.",
    "skus": "Mã hàng, tên, đơn vị cơ sở và chủ hàng.",
    "supply_relationships": "Quan hệ nhà cung cấp–chủ hàng–SKU được phép cung ứng.",
    "inbound_requests": "Phiếu yêu cầu nhập, kho nhận, chủ hàng, supplier, trạng thái/version.",
    "inbound_lines": "Chi tiết hàng kế hoạch và lượng kiểm nhận tốt/cách ly.",
    "inbound_postings": "Bút toán tăng tồn khi cất hàng đã kiểm nhận.",
    "inventory_balances": "Số dư thực tế, đã giữ và không khả dụng theo owner/SKU/kho.",
    "balance_locations": "Vị trí lưu của một dòng số dư.",
    "outbound_requests": "Phiếu yêu cầu xuất, phương án shipper, trạng thái/version.",
    "outbound_lines": "Các SKU và số lượng yêu cầu xuất.",
    "outbound_allocations": "Phân bổ lượng giữ từ số dư cho dòng xuất.",
    "outbound_tasks": "Liên kết phiếu xuất với nhiệm vụ bàn giao.",
    "pickup_tasks": "Nhiệm vụ giao nhận tại kho, shipper và trạng thái/version.",
    "packages": "Các kiện thuộc nhiệm vụ.",
    "package_items": "Lượng hàng của dòng xuất nằm trong từng kiện.",
    "stock_reservations": "Lượng giữ theo nhiệm vụ và dòng số dư.",
    "inventory_postings": "Bút toán xuất kho từ reservation khi hoàn tất bàn giao.",
    "package_scans": "Kết quả đối chiếu kiện trong nhiệm vụ.",
    "handover_confirmations": "Xác nhận từng bên, người thực hiện và version bàn giao.",
    "handover_receipts": "Biên nhận đã phát hành cho nhiệm vụ.",
    "audit_logs": "Nhật ký thao tác và trạng thái trước/sau.",
    "command_receipts": "Kết quả lệnh và fingerprint phục vụ idempotency/replay.",
    "stock_movements": "Bảng chuyển động tồn legacy; không dùng ghi giao dịch mới.",
    "idempotency_requests": "Bảng chống lặp legacy; không dùng ghi giao dịch mới.",
    "alembic_version": "Phiên bản schema do Alembic quản lý.",
}

GROUPS = [
    (
        "catalog",
        "Tài khoản và danh mục",
        [
            "users",
            "access_sessions",
            "organizations",
            "partner_memberships",
            "warehouses",
            "storage_locations",
            "skus",
            "supply_relationships",
        ],
    ),
    (
        "inbound",
        "Nhập kho và số dư",
        [
            "inbound_requests",
            "inbound_lines",
            "inbound_postings",
            "inventory_balances",
            "balance_locations",
        ],
    ),
    (
        "outbound",
        "Xuất kho và đóng kiện",
        [
            "outbound_requests",
            "outbound_lines",
            "outbound_allocations",
            "outbound_tasks",
            "packages",
            "package_items",
        ],
    ),
    (
        "handover",
        "Bàn giao và ghi xuất",
        [
            "pickup_tasks",
            "stock_reservations",
            "inventory_postings",
            "package_scans",
            "handover_confirmations",
            "handover_receipts",
        ],
    ),
    (
        "infrastructure",
        "Hạ tầng và legacy",
        [
            "audit_logs",
            "command_receipts",
            "stock_movements",
            "idempotency_requests",
            "alembic_version",
        ],
    ),
]


def table_keys(table):
    pk = set(table["primaryKey"]["constrained_columns"])
    fk = {c for f in table["foreignKeys"] for c in f["constrained_columns"]}
    uk = {
        u["column_names"][0]
        for u in table["uniqueConstraints"]
        if len(u["column_names"]) == 1
    }
    return pk, fk, uk


def relation(table, fk):
    cols = set(fk["constrained_columns"])
    unique_sets = [set(table["primaryKey"]["constrained_columns"])]
    unique_sets += [set(u["column_names"]) for u in table["uniqueConstraints"]]
    unique = any(u and u.issubset(cols) for u in unique_sets)
    nullable = any(c["nullable"] for c in table["columns"] if c["name"] in cols)
    return ("|o" if nullable else "||"), ("o|" if unique else "o{")


def selected_tables(tables, names):
    owned = set(names) if names is not None else {t["name"] for t in tables}
    referenced = {
        f["referred_table"]
        for t in tables
        if t["name"] in owned
        for f in t["foreignKeys"]
    }
    return [t for t in tables if t["name"] in owned | referenced], owned


def mermaid(tables, names=None):
    selected, owned = selected_tables(tables, names)
    lines = ["erDiagram"]
    for table in selected:
        if table["name"] in owned:
            for fk in table["foreignKeys"]:
                left, right = relation(table, fk)
                identifying = set(fk["constrained_columns"]).issubset(
                    set(table["primaryKey"]["constrained_columns"])
                )
                link = "--" if identifying else ".."
                lines.append(
                    f'    {fk["referred_table"]} {left}{link}{right} {table["name"]} : {"_".join(fk["constrained_columns"])}'
                )
    for table in selected:
        pk, fk, uk = table_keys(table)
        lines.append(f'    {table["name"]} {{')
        for col in table["columns"]:
            # Boundary entities are deliberately abbreviated; full dictionary remains authoritative.
            if table["name"] not in owned and col["name"] not in pk | uk:
                continue
            kind = re.sub(r"[^A-Za-z0-9_]", "_", col["type"].lower()).strip("_")
            marks = [
                mark
                for mark, keys in [("PK", pk), ("FK", fk), ("UK", uk)]
                if col["name"] in keys
            ]
            suffix = " " + ", ".join(marks) if marks else ""
            lines.append(f'        {kind} {col["name"]}{suffix}')
        lines.append("    }")
    return "\n".join(lines) + "\n"


def dot(tables, names=None):
    selected, owned = selected_tables(tables, names)
    lines = [
        "digraph ERD {",
        'graph [rankdir=LR, bgcolor="white", pad="0.3", nodesep="0.35", ranksep="1", fontname="Arial"];',
        'node [shape=plain, fontname="Arial", fontsize=12];',
        'edge [fontname="Arial", fontsize=10, color="#64748b", fontcolor="#334155", arrowsize=0.7];',
    ]
    for table in selected:
        pk, fk, uk = table_keys(table)
        color = "#1e40af" if table["name"] in owned else "#475569"
        label = f'<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="7" COLOR="#cbd5e1"><TR><TD COLSPAN="3" BGCOLOR="{color}"><FONT COLOR="white"><B>{escape(table["name"])}</B></FONT></TD></TR>'
        for col in table["columns"]:
            if table["name"] not in owned and col["name"] not in pk | uk:
                continue
            marks = ",".join(
                mark
                for mark, keys in [("PK", pk), ("FK", fk), ("UK", uk)]
                if col["name"] in keys
            )
            label += f'<TR><TD PORT="{escape(col["name"])}" ALIGN="LEFT">{escape(col["name"])}</TD><TD ALIGN="LEFT">{escape(col["type"])}</TD><TD PORT="{escape(col["name"])}_out">{marks}</TD></TR>'
        label += "</TABLE>"
        lines.append(f'"{table["name"]}" [label=<{label}>];')
    for table in selected:
        if table["name"] not in owned:
            continue
        for fk in table["foreignKeys"]:
            left, right = relation(table, fk)
            cardinality = (
                ("0..1" if left == "|o" else "1")
                + " : "
                + ("0..1" if right == "o|" else "0..N")
            )
            lines.append(
                f'"{fk["referred_table"]}":"{fk["referred_columns"][0]}_out":e -> "{table["name"]}":"{fk["constrained_columns"][0]}":w [label="{cardinality}"];'
            )
    return "\n".join(lines + ["}"]) + "\n"


def dictionary(tables):
    lines = [
        "## 11. Từ điển dữ liệu PostgreSQL thực tế",
        "",
        "Sinh từ metadata schema public tại thời điểm kiểm tra. PK nhiều cột là khóa ghép; UNIQUE nhiều cột là duy nhất theo tổ hợp, không phải từng cột riêng. NULL là khả năng lưu NULL trong PostgreSQL.",
        "",
        "DEFAULT dưới đây là DEFAULT ở database, không phải giá trị mặc định của Python/ORM. Dấu — nghĩa là PostgreSQL chưa khai báo DEFAULT; ứng dụng cần truyền hoặc tự gán giá trị.",
        "",
    ]
    for table in tables:
        lines += [
            f'### `{table["name"]}`',
            "",
            DESCRIPTIONS.get(
                table["name"], "Bảng bổ sung được phát hiện trong database."
            ),
            "",
            "| Cột | Kiểu PostgreSQL | NULL | Khóa | DEFAULT tại DB |",
            "| --- | --- | --- | --- | --- |",
        ]
        pk, fk, uk = table_keys(table)
        for col in table["columns"]:
            marks = (
                ", ".join(
                    mark
                    for mark, keys in [("PK", pk), ("FK", fk), ("UK", uk)]
                    if col["name"] in keys
                )
                or "—"
            )
            default = (
                str(col["serverDefault"]).replace("|", "&#124;")
                if col["serverDefault"] is not None
                else "—"
            )
            lines.append(
                f'| `{col["name"]}` | `{col["type"]}` | {"Có" if col["nullable"] else "Không"} | {marks} | {default} |'
            )
        lines += [
            "",
            "Ràng buộc đã kiểm tra:",
            "",
            f'- PRIMARY KEY: `{", ".join(table["primaryKey"]["constrained_columns"])}`.',
        ]
        for f in table["foreignKeys"]:
            lines.append(
                f'- FOREIGN KEY `{", ".join(f["constrained_columns"])}` → `{f["referred_table"]}({", ".join(f["referred_columns"])})`.'
            )
        for u in table["uniqueConstraints"]:
            lines.append(f'- UNIQUE: `{", ".join(u["column_names"])}`.')
        for c in table["checkConstraints"]:
            lines.append(f'- CHECK `{c["name"]}`: `{c["sqltext"]}`.')
        for idx in table["indexes"]:
            if not idx.get("duplicates_constraint"):
                lines.append(
                    f'- INDEX `{idx["name"]}`: `{", ".join(idx["column_names"])}`.'
                )
        lines.append("")
    return "\n".join(lines)


def build_artifacts(schema):
    tables = schema["tables"]
    groups = [
        {
            "id": key,
            "title": title,
            "mermaid": mermaid(tables, names),
            "dot": dot(tables, names),
        }
        for key, title, names in GROUPS
    ]
    return {
        "dictionary": dictionary(tables),
        "mermaid": mermaid(tables),
        "dot": dot(tables),
        "groups": groups,
    }
