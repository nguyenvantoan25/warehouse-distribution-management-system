from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.auth.access import require_access
from app.modules.auth.models import User
from .dashboard import dashboard as read_dashboard
from .audit import audit as read_audit

router = APIRouter(tags=["platform"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(require_access("dashboard.read")),
):
    return read_dashboard(db, user)


@router.get("/audit-logs")
def audit(
    db: Session = Depends(get_db), user: User = Depends(require_access("audit.read"))
):
    return read_audit(db, user)
