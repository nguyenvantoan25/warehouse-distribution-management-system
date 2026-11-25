"""Read-only database evidence. Counts only; never emits account hashes or credentials."""

import json
from datetime import datetime, timezone
from sqlalchemy import select, func, text
from app import models
from app.core.database import Base, engine


def status():
    with engine.connect() as connection:
        counts = {
            table.name: connection.scalar(select(func.count()).select_from(table))
            for table in Base.metadata.sorted_tables
        }
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
        version = (
            connection.scalar(text("SELECT version()"))
            if engine.dialect.name == "postgresql"
            else "sqlite"
        )
    return {
        "observedAt": datetime.now(timezone.utc).isoformat(),
        "database": engine.dialect.name,
        "serverVersion": version,
        "schemaRevision": revision,
        "rowCounts": counts,
        "businessDataPolicy": "No demo business data imported; accounts only from existing local authentication store.",
    }


if __name__ == "__main__":
    print(json.dumps(status(), ensure_ascii=False, indent=2))
