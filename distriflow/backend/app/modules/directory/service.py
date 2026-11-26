import hashlib
import uuid
from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from app.core.commands import utcnow
from app.modules.auth.access import password_hash
from app.modules.auth.models import AccessSession, User
from app.modules.catalog.models import Organization, PartnerMembership

ROLES = ("SHIPPER", "SUPPLIER", "RETAILER_OWNER")


def visible_users(actor):
    return or_(
        User.warehouse_scope == actor.warehouse_scope, User.warehouse_scope == ""
    )


def organizations(db, user_id):
    return db.scalars(
        select(Organization)
        .join(PartnerMembership, PartnerMembership.organization_id == Organization.id)
        .where(PartnerMembership.user_id == user_id)
    ).all()


def profile(db, user):
    linked = organizations(db, user.id)
    org = linked[0] if len(linked) == 1 else None
    return {
        "id": user.id,
        "username": user.username,
        "name": user.display_name or (org.name if org else user.username),
        "role": user.role,
        "active": user.active,
        "deleted": user.deleted_at is not None,
        "warehouseName": user.warehouse_scope,
        "version": user.version,
        "organizationId": org.id if org else None,
        "organizationCount": len(linked),
        "suppliedGoods": (
            org.supplied_goods if org and user.role == "SUPPLIER" else None
        ),
    }


def listing(db, actor):
    users = db.scalars(
        select(User)
        .where(visible_users(actor), User.role.in_(ROLES), User.deleted_at.is_(None))
        .order_by(User.username)
    ).all()
    # Legacy organizations without a live account can be explicitly linked during create.
    occupied = (
        select(PartnerMembership.organization_id)
        .join(User, User.id == PartnerMembership.user_id)
        .where(User.deleted_at.is_(None))
    )
    unlinked = db.scalars(
        select(Organization)
        .where(Organization.active.is_(True), Organization.id.not_in(occupied))
        .order_by(Organization.name)
    ).all()
    return {
        "accounts": [profile(db, u) for u in users],
        "unlinkedPartners": [
            {
                "id": o.id,
                "name": o.name,
                "kind": o.kind,
                "suppliedGoods": o.supplied_goods,
            }
            for o in unlinked
        ],
    }


def target(db, actor, user_id):
    user = db.scalar(
        select(User)
        .where(User.id == user_id, visible_users(actor), User.role.in_(ROLES))
        .with_for_update()
    )
    if user is None:
        raise HTTPException(
            404, "Không tìm thấy tài khoản thuộc ba nhóm trong phạm vi quản lý"
        )
    return user


def check_version(user, version):
    if user.deleted_at is not None or user.version != version:
        raise HTTPException(409, "Tài khoản đã thay đổi hoặc đã xóa; hãy tải lại")


def other_members(db, organization_id, user_id):
    return (
        db.scalar(
            select(User.id)
            .join(PartnerMembership, PartnerMembership.user_id == User.id)
            .where(
                PartnerMembership.organization_id == organization_id,
                User.id != user_id,
                User.deleted_at.is_(None),
            )
        )
        is not None
    )


def goods_for(role, value):
    if role == "SUPPLIER" and not value:
        raise HTTPException(422, "Nhà cung cấp cần khai báo loại hàng cung cấp")
    if role != "SUPPLIER" and value:
        raise HTTPException(422, "Chỉ nhà cung cấp có loại hàng cung cấp")
    return value if role == "SUPPLIER" else None


def safe_payload(cmd, key, actor_id):
    if not key or len(key) > 200:
        raise HTTPException(400, "Thiếu hoặc sai Idempotency-Key")
    payload = cmd.model_dump(exclude={"password"})
    password = getattr(cmd, "password", None)
    if password is not None:
        # execute stores only a request fingerprint, never this payload. Use a slow,
        # command-specific secret digest so the receipt is not a fast password verifier.
        salt = hashlib.sha256((actor_id + ":" + key).encode()).digest()
        payload["credentialDigest"] = hashlib.scrypt(
            password.get_secret_value().encode(), salt=salt, n=16384, r=8, p=1
        ).hex()
    return payload


def ensure_username(db, username, user_id=None):
    existing = db.scalar(select(User.id).where(User.username == username))
    if existing is not None and existing != user_id:
        raise HTTPException(409, "Tên tài khoản đã tồn tại, kể cả tài khoản đã xóa")


def create(db, actor, cmd):
    ensure_username(db, cmd.username)
    goods = goods_for(cmd.role, cmd.supplied_goods)
    expected = {"SUPPLIER": "SUPPLIER", "RETAILER_OWNER": "RETAILER"}.get(cmd.role)
    if not expected and cmd.organization_id:
        raise HTTPException(422, "Shipper không gán tổ chức đối tác")
    org = None
    if expected:
        if cmd.organization_id:
            org = db.scalar(
                select(Organization)
                .where(Organization.id == cmd.organization_id)
                .with_for_update()
            )
            if not org or not org.active or org.kind != expected:
                raise HTTPException(422, "Đối tác không tồn tại hoặc sai loại")
            if other_members(db, org.id, ""):
                raise HTTPException(
                    409, "Đối tác đã có tài khoản; không tự gộp hoặc chuyển tài khoản"
                )
            org.name = cmd.name
            org.supplied_goods = goods
        else:
            org = Organization(name=cmd.name, kind=expected, supplied_goods=goods)
            db.add(org)
            db.flush()
    user = User(
        id=str(uuid.uuid4()),
        username=cmd.username,
        display_name=cmd.name,
        password_hash=password_hash(cmd.password.get_secret_value()),
        role=cmd.role,
        warehouse_scope=actor.warehouse_scope,
        active=True,
    )
    db.add(user)
    db.flush()
    if org:
        db.add(PartnerMembership(user_id=user.id, organization_id=org.id))
        db.flush()
    return profile(db, user)


def update(db, user, cmd):
    check_version(user, cmd.version)
    ensure_username(db, cmd.username, user.id)
    goods = goods_for(user.role, cmd.supplied_goods)
    linked = organizations(db, user.id)
    expected = {"SUPPLIER": "SUPPLIER", "RETAILER_OWNER": "RETAILER"}.get(user.role)
    if expected:
        if len(linked) > 1 or (linked and linked[0].kind != expected):
            raise HTTPException(
                409,
                "Liên kết đối tác cũ không đơn nhất; cần kiểm tra phạm vi trước khi sửa",
            )
        org = linked[0] if linked else None
        if org is None:
            org = Organization(name=cmd.name, kind=expected, supplied_goods=goods)
            db.add(org)
            db.flush()
            db.add(PartnerMembership(user_id=user.id, organization_id=org.id))
        elif other_members(db, org.id, user.id) and (
            org.name != cmd.name or org.supplied_goods != goods
        ):
            raise HTTPException(
                409,
                "Đối tác dùng chung nhiều tài khoản; không đổi thông tin dùng chung từ tài khoản này",
            )
        org.name = cmd.name
        org.supplied_goods = goods
    user.username = cmd.username
    user.display_name = cmd.name
    if cmd.password is not None:
        user.password_hash = password_hash(cmd.password.get_secret_value())
    # Also bump version if only shared organization fields changed.
    user.version += 1
    db.execute(delete(AccessSession).where(AccessSession.user_id == user.id))
    db.flush()
    return profile(db, user)


def remove(db, user, cmd):
    check_version(user, cmd.version)
    user.active = False
    user.deleted_at = utcnow()
    for org in organizations(db, user.id):
        if not other_members(db, org.id, user.id):
            org.active = False
    db.execute(delete(AccessSession).where(AccessSession.user_id == user.id))
    db.flush()
    return profile(db, user)
