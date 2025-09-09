from __future__ import annotations

from typing import Any

from .shared import STAGES


def _get_stage(stage: str) -> dict[str, Any]:
    return STAGES.get(stage, {}) if isinstance(STAGES, dict) else {}


def um_list_urban_layers() -> list[str]:
    return list(_get_stage("urban_layer").get("types", {}).keys())


def um_explain_primitive(stage: str, technique: str) -> dict:
    stage_info = _get_stage(stage)
    types = stage_info.get("types", {})
    prims = stage_info.get("primitives", {})
    entry = types.get(technique) or prims.get(technique)
    if not entry:
        return {"error": f"Unknown technique '{technique}' for stage '{stage}'."}
    return {"stage": stage, "technique": technique, "context": entry}
