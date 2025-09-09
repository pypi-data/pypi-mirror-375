from __future__ import annotations

import json
from typing import Any

from .discovery import um_list_urban_layers
from .shared import (
    get_default_visualiser,
    get_pipeline_defaults,
    get_visualiser_presets,
    safe_csv_name,
)


def um_build_pipeline_code(
    repo_id: str,
    urban_layer_type: str,
    place: str,
    group_by_key: str,
    longitude_column: str | None = None,
    latitude_column: str | None = None,
    geometry_column: str | None = None,
    values_from: str | None = None,
    aggregation_method: str = "count",
    output_column: str = "metric",
    number_of_rows: int | None = None,
    streaming: bool | None = None,
    include_imputer: bool | None = None,
    address_column: str | None = None,
    include_filter: bool | None = None,
    visualiser_type: str | None = None,
    visualiser_style: dict[str, Any] | None = None,
    visualiser_preset: str | None = None,
    visualise_columns: list[str] | None = None,
    csv_path: str | None = None,
    include_comments: bool = False,
) -> str:
    valid_layers = um_list_urban_layers()
    if urban_layer_type not in valid_layers:
        raise ValueError(
            f"Unknown urban_layer_type '{urban_layer_type}'. Valid: {valid_layers}"
        )
    if not group_by_key:
        raise ValueError(
            "group_by_key is required and cannot be inferred automatically."
        )
    if not geometry_column and (not longitude_column or not latitude_column):
        raise ValueError(
            "Provide either geometry_column OR both longitude_column and latitude_column."
        )

    pdefs = get_pipeline_defaults()
    number_of_rows = int(
        number_of_rows
        if number_of_rows is not None
        else pdefs.get("number_of_rows", 5000)
    )
    streaming = bool(
        streaming if streaming is not None else pdefs.get("streaming", True)
    )
    include_imputer = bool(
        include_imputer
        if include_imputer is not None
        else pdefs.get("include_imputer", True)
    )
    include_filter = bool(
        include_filter
        if include_filter is not None
        else pdefs.get("include_filter", True)
    )

    csv_out = csv_path or safe_csv_name(repo_id)

    if geometry_column:
        mapping_clause = f'.with_mapping(geometry_column="{geometry_column}", output_column="{group_by_key}")'
        loader_columns = f'.with_columns(geometry_column="{geometry_column}")'
        cast_block = ""
    else:
        mapping_clause = (
            f'.with_mapping(longitude_column="{longitude_column}", '
            f'latitude_column="{latitude_column}", '
            f'output_column="{group_by_key}")'
        )
        loader_columns = (
            f'.with_columns(longitude_column="{longitude_column}", '
            f'latitude_column="{latitude_column}")'
        )
        cast_block = (
            f"data['{longitude_column}'] = data['{longitude_column}'].astype(float)\n"
            f"data['{latitude_column}'] = data['{latitude_column}'].astype(float)\n"
        )

    imputer_step = ""
    if include_imputer and not geometry_column:
        if address_column:
            imputer_step = (
                '    ("imputer", (\n'
                "        mapper.imputer\n"
                '        .with_type("AddressGeoImputer")\n'
                f'        .on_columns("{longitude_column}", "{latitude_column}", "{address_column}")\n'
                "        .build()\n"
                "    )),\n"
            )
        else:
            imputer_step = (
                '    ("imputer", (\n'
                "        mapper.imputer\n"
                '        .with_type("SimpleGeoImputer")\n'
                f'        .on_columns("{longitude_column}", "{latitude_column}")\n'
                "        .build()\n"
                "    )),\n"
            )

    filter_step = (
        '    ("filter", mapper.filter.with_type("BoundingBoxFilter").build()),\n'
        if include_filter
        else ""
    )

    if aggregation_method == "count":
        enr_step = (
            '    ("enricher", (\n'
            "        mapper.enricher\n"
            f'        .with_data(group_by="{group_by_key}")\n'
            f'        .count_by(output_column="{output_column}")\n'
            "        .build()\n"
            "    )),\n"
        )
    else:
        if not values_from:
            raise ValueError(
                "values_from must be provided when aggregation_method is not 'count'."
            )
        enr_step = (
            '    ("enricher", (\n'
            "        mapper.enricher\n"
            f'        .with_data(group_by="{group_by_key}", values_from="{values_from}")\n'
            f'        .aggregate_by(method="{aggregation_method}", output_column="{output_column}")\n'
            "        .build()\n"
            "    )),\n"
        )

    if not visualiser_type or not visualiser_style:
        dv = get_default_visualiser()
        visualiser_type = visualiser_type or dv["type"]
        if not visualiser_style:
            preset_name = visualiser_preset or dv.get("preset")
            if preset_name:
                visualiser_style = get_visualiser_presets(visualiser_type).get(
                    preset_name, None
                )
        if not visualiser_style:
            visualiser_style = {}

    style_json = json.dumps(visualiser_style, ensure_ascii=False)
    vis_step = (
        '    ("visualiser", (\n'
        f'        mapper.visual.with_type("{visualiser_type}").with_style({style_json}).build()\n'
        "    )),\n"
    )

    viz_cols = visualise_columns or [output_column]
    viz_cols_json = json.dumps(viz_cols, ensure_ascii=False)

    c_hdr = (
        "# --- Auto-generated by MCP UrbanMapper (YAML-driven defaults) ---\n"
        if include_comments
        else ""
    )
    c_pipe = "# 1) Define the pipeline\n" if include_comments else ""
    c_prev = "# Optional: preview the pipeline structure\n" if include_comments else ""
    c_comp = "# 2) Compose & immediately visualise\n" if include_comments else ""

    code = f"""{c_hdr}import urban_mapper as um
from urban_mapper.pipeline import UrbanPipeline
from IPython.display import display as _display

# HF→CSV pre-step
mapper = um.UrbanMapper()
data = (
    mapper.loader
    .from_huggingface("{repo_id}", number_of_rows={number_of_rows}, streaming={streaming!s})
    {loader_columns}
    .load()
)
{cast_block}data.to_csv("{csv_out}", index=False)

{c_pipe}pipeline = UrbanPipeline([
    ("urban_layer", (
        mapper.urban_layer
        .with_type("{urban_layer_type}")
        .from_place("{place}")
        {mapping_clause}
        .build()
    )),
    ("loader", (
        mapper.loader
        .from_file("{csv_out}")
        {loader_columns}
        .build()
    )),
{imputer_step}{filter_step}{enr_step}{vis_step}])

{c_prev}pipeline.preview()

{c_comp}_ = pipeline.compose_transform()
_viz = pipeline.visualise({viz_cols_json})
try:
    _display(_viz)
except Exception:
    pass
"""
    return code
