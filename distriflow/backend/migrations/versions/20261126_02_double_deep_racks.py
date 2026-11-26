"""Add explicit, nullable coordinates for the 800-position double-deep layout."""

from alembic import op
import sqlalchemy as sa

revision = "20261126_02"
down_revision = "20261123_01"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("storage_locations") as batch:
        for name in ("rack_row", "rack_level", "rack_bay", "rack_depth"):
            batch.add_column(sa.Column(name, sa.Integer(), nullable=True))
        batch.create_unique_constraint(
            "uq_storage_rack_coordinate",
            ["warehouse_id", "rack_row", "rack_level", "rack_bay", "rack_depth"],
        )
        batch.create_check_constraint(
            "ck_storage_rack_coordinate",
            "(rack_row IS NULL AND rack_level IS NULL AND rack_bay IS NULL AND rack_depth IS NULL) OR "
            "(rack_row IS NOT NULL AND rack_level IS NOT NULL AND rack_bay IS NOT NULL AND rack_depth IS NOT NULL "
            "AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 "
            "AND rack_bay BETWEEN 1 AND 5 AND rack_depth BETWEEN 1 AND 2)",
        )


def downgrade():
    with op.batch_alter_table("storage_locations") as batch:
        batch.drop_constraint("ck_storage_rack_coordinate", type_="check")
        batch.drop_constraint("uq_storage_rack_coordinate", type_="unique")
        for name in ("rack_depth", "rack_bay", "rack_level", "rack_row"):
            batch.drop_column(name)
