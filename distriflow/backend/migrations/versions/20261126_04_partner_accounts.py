"""Directory profiles and soft deletion; preserve existing credentials and memberships."""

from alembic import op
import sqlalchemy as sa

revision = "20261126_04"
down_revision = "20261126_03"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("display_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column(
        "users",
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "organizations", sa.Column("supplied_goods", sa.String(1000), nullable=True)
    )


def downgrade():
    op.drop_column("organizations", "supplied_goods")
    op.drop_column("users", "version")
    op.drop_column("users", "deleted_at")
    op.drop_column("users", "display_name")
