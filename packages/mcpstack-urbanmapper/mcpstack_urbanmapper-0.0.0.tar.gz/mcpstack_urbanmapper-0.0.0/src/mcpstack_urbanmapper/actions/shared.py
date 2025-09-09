from __future__ import annotations

import importlib.resources as pkg_res
import re
from typing import Any

try:
    from .. import contexts as _ctx_pkg
except Exception:
    _ctx_pkg = None

# Load YAML contexts
try:
    import yaml  # type: ignore

    _CONTEXTS_TEXT = (
        pkg_res.files(_ctx_pkg).joinpath("um_contexts.yaml").read_text(encoding="utf-8")
        if _ctx_pkg
        else ""
    )
    CONTEXTS: dict[str, Any] = yaml.safe_load(_CONTEXTS_TEXT) if _CONTEXTS_TEXT else {}
except Exception:
    CONTEXTS = {}

DEFAULTS: dict[str, Any] = CONTEXTS.get("defaults", {})
STAGES: dict[str, Any] = CONTEXTS.get("stages", {})
PIPELINE_HINTS: dict[str, Any] = CONTEXTS.get("pipeline_hints", {})
EXAMPLES: dict[str, Any] = CONTEXTS.get("examples") or {}


def get_env_defaults() -> dict[str, str]:
    env = (DEFAULTS.get("env") or {}).copy()
    return {k: ("" if v is None else str(v)) for k, v in env.items()}


def get_visualiser_aliases() -> dict[str, str]:
    viz = STAGES.get("visualiser") or {}
    return viz.get("aliases") or {}


def _viz_family(viz_type: str) -> str:
    aliases = get_visualiser_aliases()
    return aliases.get(viz_type, viz_type.lower())


def get_visualiser_presets(viz_type: str) -> dict[str, dict[str, Any]]:
    viz = STAGES.get("visualiser") or {}
    fam = _viz_family(viz_type)
    presets = viz.get("presets", {})
    return presets.get(fam, {})


def get_default_visualiser() -> dict[str, Any]:
    dv = DEFAULTS.get("visualiser") or {}
    vtype = dv.get("type", "Interactive")
    preset = dv.get("preset")
    style = None
    if preset:
        style = get_visualiser_presets(vtype).get(preset)
    return {"type": vtype, "preset": preset, "style": style}


def get_pipeline_defaults() -> dict[str, Any]:
    return (DEFAULTS.get("pipeline") or {}).copy()


def safe_csv_name(repo_id: str) -> str:
    fname = re.sub(r"[^A-Za-z0-9_.-]+", "_", repo_id)
    return f"./{fname}.csv"
