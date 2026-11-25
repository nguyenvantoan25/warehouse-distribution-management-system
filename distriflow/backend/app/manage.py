"""Local administrative CLI. Password input is interactive and never logged."""

import argparse
from getpass import getpass
from sqlalchemy import delete, select
from app.core.database import SessionLocal
from app.modules.auth.models import User, AccessSession
from app.modules.auth.access import password_hash


def main():
    parser = argparse.ArgumentParser(
        description="DistriFlow local account administration"
    )
    parser.add_argument("action", choices=["password"])
    parser.add_argument("username")
    args = parser.parse_args()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == args.username))
        if not user:
            parser.error("Không tìm thấy tài khoản")
        password = getpass("Mật khẩu mới (ít nhất 10 ký tự): ")
        if len(password) < 10:
            parser.error("Mật khẩu phải có ít nhất 10 ký tự")
        if getpass("Nhập lại mật khẩu: ") != password:
            parser.error("Mật khẩu không trùng khớp")
        user.password_hash = password_hash(password)
        db.execute(delete(AccessSession).where(AccessSession.user_id == user.id))
        db.commit()
        print(
            "Đã cập nhật mật khẩu và thu hồi các phiên cũ. accounts.local.json không tự thay đổi."
        )


if __name__ == "__main__":
    main()
