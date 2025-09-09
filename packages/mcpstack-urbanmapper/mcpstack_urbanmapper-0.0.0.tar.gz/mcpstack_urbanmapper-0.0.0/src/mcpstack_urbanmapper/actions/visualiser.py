from __future__ import annotations

from typing import Any

from .shared import STAGES, get_visualiser_presets


def _viz_section() -> dict[str, Any]:
    viz = STAGES.get("visualiser")
    if not isinstance(viz, dict):
        raise RuntimeError("Missing 'visualiser' section in um_contexts.yaml.")
    return viz


def um_list_visualisers() -> list[str]:
    viz = _viz_section()
    types = viz.get("types")
    if not isinstance(types, dict) or not types:
        raise RuntimeError("Missing or empty 'visualiser.types' in um_contexts.yaml.")
    return list(types.keys())


def um_visualiser_style_schema(viz_type: str) -> dict:
    viz = _viz_section()
    types = viz.get("types")
    if not isinstance(types, dict) or not types:
        raise RuntimeError("Missing or empty 'visualiser.types' in um_contexts.yaml.")
    spec = types.get(viz_type)
    if not isinstance(spec, dict):
        valid = ", ".join(types.keys())
        raise ValueError(f"Unknown visualiser '{viz_type}'. Valid: {valid}")
    return {
        "allowed_style_keys": spec.get("allowed_style_keys", []),
        "notes": spec.get("notes", []),
        "examples": spec.get("examples", {}),
    }


def um_visualiser_presets(viz_type: str) -> dict[str, dict[str, Any]]:
    return get_visualiser_presets(viz_type)
