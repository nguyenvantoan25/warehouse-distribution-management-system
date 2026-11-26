import json
from pathlib import Path
from app.setup.schema_render import build_artifacts, GROUPS, mermaid


def schema():
    return json.loads(
        (
            Path(__file__).resolve().parents[3] / "docs" / "database-schema.json"
        ).read_text(encoding="utf-8")
    )


def test_diagrams_include_all_actual_foreign_keys_only():
    data = schema()
    diagram = mermaid(data["tables"])
    assert sum(" : " in line for line in diagram.splitlines()) == sum(
        len(t["foreignKeys"]) for t in data["tables"]
    )
    assert "pickup_tasks : shipper_id" not in diagram
    assert "organizations ||..o{" in diagram
    assert "pickup_tasks ||..o| handover_receipts : task_id" in diagram


def test_every_real_table_has_dictionary_and_group():
    data = schema()
    result = build_artifacts(data)
    grouped = [name for _, _, names in GROUPS for name in names]
    assert len(grouped) == len(set(grouped))
    assert set(grouped) == {t["name"] for t in data["tables"]}
    for table in data["tables"]:
        assert f'### `{table["name"]}`' in result["dictionary"]
        for column in table["columns"]:
            assert f'`{column["name"]}`' in result["dictionary"]


def test_composite_unique_is_not_marked_as_single_column_unique():
    data = schema()
    diagram = mermaid(data["tables"], ["supply_relationships"])
    entity = diagram.split("    supply_relationships {")[1].split("    }")[0]
    assert "supplier_id FK, UK" not in entity
    assert "owner_id FK, UK" not in entity
