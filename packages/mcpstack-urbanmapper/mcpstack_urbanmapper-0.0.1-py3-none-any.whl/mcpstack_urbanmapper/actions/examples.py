from __future__ import annotations

from .pipeline import um_build_pipeline_code
from .shared import EXAMPLES


def um_list_examples() -> list[str]:
    return list(EXAMPLES.keys())


def um_get_example_code(name: str) -> str:
    ex = EXAMPLES.get(name)
    if not ex:
        raise ValueError(f"Unknown example '{name}'. Valid: {list(EXAMPLES.keys())}")
    params = ex.get("params", {})
    repo_id = params["repo_id"]
    place = params["place"]
    urban_layer_type = params["layer"]
    group_by_key = params["group_by_key"]
    lon = params.get("lon")
    lat = params.get("lat")
    geom = params.get("geometry_column")
    agg = params.get("aggregation", {}) or {}
    values_from = agg.get("values_from")
    aggregation_method = agg.get("method", "count")
    output_column = agg.get("output_column", "metric")
    viz = params.get("visualiser") or {}
    viz_type = viz.get("type")
    viz_style = viz.get("style")
    viz_preset = viz.get("preset")
    return um_build_pipeline_code(
        repo_id=repo_id,
        urban_layer_type=urban_layer_type,
        place=place,
        group_by_key=group_by_key,
        longitude_column=lon,
        latitude_column=lat,
        geometry_column=geom,
        values_from=values_from,
        aggregation_method=aggregation_method,
        output_column=output_column,
        visualiser_type=viz_type,
        visualiser_style=viz_style if viz_style else None,
        visualiser_preset=viz_preset if viz_preset else None,
    )
