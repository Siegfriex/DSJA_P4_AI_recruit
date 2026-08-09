from __future__ import annotations

import json
import tempfile
from pathlib import Path

import duckdb
import jsonschema
import yaml


def validate_contract(root: Path) -> dict:
    legacy_path = root / "contracts/v2.1.2_legacy/p4_contract.yaml"
    bridge_path = root / "contracts/v2.1.3_bridge/p4_contract.yaml"
    schema_path = root / "contracts/v2.1.3_bridge/bridge.schema.json"
    legacy = yaml.safe_load(legacy_path.read_text(encoding="utf-8"))
    bridge = yaml.safe_load(bridge_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(bridge, schema)
    legacy_tables = set(legacy["tables"])
    bridge_tables = set(bridge["tables"])
    missing = legacy_tables.difference(bridge_tables)
    if missing:
        raise ValueError(f"2.1.3 removed legacy tables: {sorted(missing)}")
    added = bridge_tables.difference(legacy_tables)
    expected = {"core.postingSourceBlock", "core.sectionSourceBlock", "core.semanticChunk"}
    if added != expected:
        raise ValueError(f"unexpected bridge tables: {sorted(added)}")
    for table, definition in bridge["tables"].items():
        if "validPostingFlag" in definition.get("columns", {}):
            raise ValueError(f"validPostingFlag is forbidden: {table}")
    reserved = bridge["rules"]["reservedFields"]["highDemandScore"]
    if reserved.get("requiredValue", "NOT_NULL") is not None:
        raise ValueError("highDemandScore must be reserved NULL")
    ddl = (root / "contracts/v2.1.3_bridge/warehouse_duckdb.sql").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="p4-contract-") as temp:
        connection = duckdb.connect(str(Path(temp) / "contract.duckdb"))
        connection.execute(ddl)
        physical = {
            f"{row[0]}.{row[1]}"
            for row in connection.execute(
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_type='BASE TABLE'"
            ).fetchall()
        }
        connection.close()
    physical_missing = bridge_tables.difference(physical)
    if physical_missing:
        raise ValueError(f"DDL missing physical tables: {sorted(physical_missing)}")
    return {
        "status": "PASS",
        "legacyTableCount": len(legacy_tables),
        "bridgeTableCount": len(bridge_tables),
        "addedTables": sorted(added),
        "ddlPhysicalTableCount": len(physical),
    }
