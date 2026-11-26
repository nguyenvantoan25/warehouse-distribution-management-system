"""Read schema metadata from the connected database, never business row contents."""

import json
import argparse
from datetime import datetime, timezone
from sqlalchemy import inspect, text
from app.core.database import engine


def collect_schema(connection):
    inspector = inspect(connection)
    tables = []
    for name in sorted(inspector.get_table_names(schema="public")):
        tables.append(
            {
                "name": name,
                "columns": [
                    {
                        "name": c["name"],
                        "type": str(c["type"]),
                        "nullable": c["nullable"],
                        "serverDefault": c.get("default"),
                    }
                    for c in inspector.get_columns(name, schema="public")
                ],
                "primaryKey": inspector.get_pk_constraint(name, schema="public"),
                "foreignKeys": inspector.get_foreign_keys(name, schema="public"),
                "uniqueConstraints": inspector.get_unique_constraints(
                    name, schema="public"
                ),
                "checkConstraints": inspector.get_check_constraints(
                    name, schema="public"
                ),
                "indexes": inspector.get_indexes(name, schema="public"),
            }
        )
    return {
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "database": connection.dialect.name,
        "schema": "public",
        "revision": connection.scalar(text("SELECT version_num FROM alembic_version")),
        "tables": tables,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--render",
        action="store_true",
        help="Emit documentation/diagram sources as JSON",
    )
    args = parser.parse_args()
    if engine.dialect.name != "postgresql":
        raise SystemExit("This report requires an actual PostgreSQL connection")
    with engine.connect() as connection:
        result = collect_schema(connection)
    if args.render:
        from app.setup.schema_render import build_artifacts

        result = build_artifacts(result)
    print(json.dumps(result, ensure_ascii=True, indent=2, default=str))


if __name__ == "__main__":
    main()
