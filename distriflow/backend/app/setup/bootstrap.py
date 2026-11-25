"""Copy existing authentication hashes only into an empty PostgreSQL database."""

import argparse
import sqlite3
from pathlib import Path
from sqlalchemy import select, func
from app import models
from app.core.database import Base, SessionLocal, engine


def import_accounts(source_path):
    source = Path(source_path).resolve(strict=True)
    if engine.dialect.name != "postgresql":
        raise ValueError("Account bootstrap requires PostgreSQL")
    with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, username, password_hash, role, active FROM users"
        ).fetchall()
    if not rows:
        raise ValueError("Source has no accounts")
    with SessionLocal.begin() as db:
        for table in Base.metadata.sorted_tables:
            if db.scalar(select(func.count()).select_from(table)):
                raise ValueError("Target is not empty; account bootstrap was refused")
        db.add_all(
            [
                models.User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    active=bool(row["active"]),
                    warehouse_scope="",
                )
                for row in rows
            ]
        )
    return len(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Import authentication only; no demo/business records"
    )
    parser.add_argument("--accounts-from-sqlite", required=True)
    args = parser.parse_args()
    count = import_accounts(args.accounts_from_sqlite)
    print(
        f"Imported {count} existing account hashes. Business data remains empty. Warehouse scopes are unassigned."
    )


if __name__ == "__main__":
    main()
