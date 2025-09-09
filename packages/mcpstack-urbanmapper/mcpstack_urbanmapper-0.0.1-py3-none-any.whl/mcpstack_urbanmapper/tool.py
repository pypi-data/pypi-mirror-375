from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar

from beartype import beartype
from MCPStack.core.tool.base import BaseTool

from .actions import (
    um_build_pipeline_code,
    um_explain_primitive,
    um_get_example_code,
    um_hf_dataset_schema,
    um_list_examples,
    um_list_urban_layers,
    um_list_visualisers,
    um_visualiser_presets,
    um_visualiser_style_schema,
)
from .actions.shared import get_env_defaults


@beartype
class UrbanMapper(BaseTool):
    """UrbanMapper MCP tool (pipeline-focussed, YAML-driven defaults)."""

    KNOWN_TOOLS: ClassVar[list[str]] = []

    def __init__(self, include: list[str] | None = None) -> None:
        super().__init__()
        self.include = include
        self._bound: list[Callable[..., Any]] = []
        self.required_env_vars = get_env_defaults()

    def um_list_urban_layers(self) -> list[str]:
        return um_list_urban_layers()

    def um_explain_primitive(self, stage: str, technique: str) -> dict:
        return um_explain_primitive(stage, technique)

    def um_hf_dataset_schema(
        self, repo_id: str, split: str = "train", sample_size: int = 10
    ) -> dict:
        return um_hf_dataset_schema(repo_id, split=split, sample_size=sample_size)

    def um_build_pipeline_code(
        self,
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
        return um_build_pipeline_code(
            repo_id=repo_id,
            urban_layer_type=urban_layer_type,
            place=place,
            group_by_key=group_by_key,
            longitude_column=longitude_column,
            latitude_column=latitude_column,
            geometry_column=geometry_column,
            values_from=values_from,
            aggregation_method=aggregation_method,
            output_column=output_column,
            number_of_rows=number_of_rows,
            streaming=streaming,
            include_imputer=include_imputer,
            address_column=address_column,
            include_filter=include_filter,
            visualiser_type=visualiser_type,
            visualiser_style=visualiser_style,
            visualiser_preset=visualiser_preset,
            visualise_columns=visualise_columns,
            csv_path=csv_path,
            include_comments=include_comments,
        )

    def um_list_examples(self) -> list[str]:
        return um_list_examples()

    def um_get_example_code(self, name: str) -> str:
        return um_get_example_code(name)

    def um_list_visualisers(self) -> list[str]:
        return um_list_visualisers()

    def um_visualiser_style_schema(self, viz_type: str) -> dict:
        return um_visualiser_style_schema(viz_type)

    def um_visualiser_presets(self, viz_type: str) -> dict[str, dict[str, Any]]:
        return um_visualiser_presets(viz_type)

    def actions(self):
        return [
            self.um_list_urban_layers,
            self.um_list_examples,
            self.um_list_visualisers,
            self.um_get_example_code,
            self.um_visualiser_style_schema,
            self.um_visualiser_presets,
            self.um_explain_primitive,
            self.um_hf_dataset_schema,
            self.um_build_pipeline_code,
        ]

    def to_dict(self) -> dict[str, object]:
        return {}

    @classmethod
    def from_dict(cls, params: dict[str, object]):
        return cls()
