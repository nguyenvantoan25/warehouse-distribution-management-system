from alembic import command
from alembic.config import Config
from app.core.config import BACKEND_DIR


def upgrade():
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    command.upgrade(config, "head")


if __name__ == "__main__":
    upgrade()
