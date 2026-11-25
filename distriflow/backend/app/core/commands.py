"""Transactional command receipts and audit log shared by domain modules."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Callable

from fastapi import HTTPException
from sqlalchemy import DateTime, JSON, String, UniqueConstraint, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.orm.exc import StaleDataError

from .database import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CommandReceipt(Base):
    __tablename__ = "command_receipts"
    __table_args__ = (UniqueConstraint("actor_id", "key", name="uq_command_actor_key"),)
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    actor_id: Mapped[str] = mapped_column(String, index=True)
    key: Mapped[str] = mapped_column(String)
    fingerprint: Mapped[str] = mapped_column(String)
    response: Mapped[dict] = mapped_column(JSON)
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    actor_id: Mapped[str] = mapped_column(String, index=True)
    object_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String)
    before: Mapped[dict] = mapped_column(JSON)
    after: Mapped[dict] = mapped_column(JSON)
    at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def execute(
    db: Session,
    actor_id: str,
    key: str | None,
    action: str,
    object_id: str,
    payload: dict,
    before: dict,
    operation: Callable[[], dict],
) -> dict:
    if not key or len(key) > 200:
        raise HTTPException(400, "Thiếu hoặc sai Idempotency-Key")
    fingerprint = hashlib.sha256(
        json.dumps([action, object_id, payload], sort_keys=True).encode()
    ).hexdigest()

    def replay():
        receipt = db.scalar(
            select(CommandReceipt).where(
                CommandReceipt.actor_id == actor_id, CommandReceipt.key == key
            )
        )
        if receipt:
            if receipt.fingerprint != fingerprint:
                raise HTTPException(
                    409, "Idempotency-Key đã được dùng cho nội dung hoặc thao tác khác"
                )
            return receipt.response
        return None

    previous = replay()
    if previous is not None:
        return previous
    try:
        result = operation()
        db.add_all(
            [
                CommandReceipt(
                    actor_id=actor_id, key=key, fingerprint=fingerprint, response=result
                ),
                AuditLog(
                    actor_id=actor_id,
                    object_id=str(result.get("id", object_id)),
                    action=action,
                    before=before,
                    after=result,
                ),
            ]
        )
        db.commit()
        return result
    except StaleDataError:
        db.rollback()
        raise HTTPException(409, "Dữ liệu vừa thay đổi, hãy tải lại trước khi thao tác")
    except OperationalError as error:
        db.rollback()
        if "locked" in str(error).lower() or "deadlock" in str(error).lower():
            raise HTTPException(
                409, "Dữ liệu đang được cập nhật đồng thời; hãy thử lại cùng lệnh"
            )
        raise
    except IntegrityError:
        db.rollback()
        previous = replay()
        if previous is not None:
            return previous
        raise HTTPException(409, "Giao dịch bị xung đột; vui lòng tải lại để kiểm tra")
    except Exception:
        db.rollback()
        raise
