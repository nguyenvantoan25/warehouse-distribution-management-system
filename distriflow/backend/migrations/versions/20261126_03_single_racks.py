"""Convert 5 paired positions to 10 single columns, preserving IDs, codes and stock."""

from alembic import op

revision = "20261126_03"
down_revision = "20261126_02"
branch_labels = None
depends_on = None

ALL_NULL = "rack_row IS NULL AND rack_level IS NULL AND rack_bay IS NULL AND rack_depth IS NULL"
ALL_PRESENT = "rack_row IS NOT NULL AND rack_level IS NOT NULL AND rack_bay IS NOT NULL AND rack_depth IS NOT NULL"
SINGLE_CHECK = f"({ALL_NULL}) OR ({ALL_PRESENT} AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 AND rack_bay BETWEEN 1 AND 10 AND rack_depth = 1)"
DOUBLE_CHECK = f"({ALL_NULL}) OR ({ALL_PRESENT} AND rack_row BETWEEN 1 AND 8 AND rack_level BETWEEN 1 AND 10 AND rack_bay BETWEEN 1 AND 5 AND rack_depth BETWEEN 1 AND 2)"
COORDINATES = ["warehouse_id", "rack_row", "rack_level", "rack_bay", "rack_depth"]


def upgrade():
    with op.batch_alter_table("storage_locations") as batch:
        batch.drop_constraint("ck_storage_rack_coordinate", type_="check")
        batch.drop_constraint("uq_storage_rack_coordinate", type_="unique")
    # Remove uniqueness while remapping: old bay 1/back becomes column 2, which may
    # temporarily coincide with old bay 2/front. No row or stock association is deleted.
    op.execute(
        "UPDATE storage_locations SET rack_bay = (rack_bay - 1) * 2 + rack_depth, rack_depth = 1 WHERE rack_row IS NOT NULL"
    )
    with op.batch_alter_table("storage_locations") as batch:
        batch.create_check_constraint("ck_storage_rack_coordinate", SINGLE_CHECK)
        batch.create_unique_constraint("uq_storage_rack_coordinate", COORDINATES)


def downgrade():
    with op.batch_alter_table("storage_locations") as batch:
        batch.drop_constraint("ck_storage_rack_coordinate", type_="check")
        batch.drop_constraint("uq_storage_rack_coordinate", type_="unique")
    op.execute(
        "UPDATE storage_locations SET rack_depth = CASE WHEN rack_bay % 2 = 1 THEN 1 ELSE 2 END, rack_bay = (rack_bay + 1) / 2 WHERE rack_row IS NOT NULL"
    )
    with op.batch_alter_table("storage_locations") as batch:
        batch.create_check_constraint("ck_storage_rack_coordinate", DOUBLE_CHECK)
        batch.create_unique_constraint("uq_storage_rack_coordinate", COORDINATES)
