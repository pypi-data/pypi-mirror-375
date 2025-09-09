<!--suppress HtmlDeprecatedAttribute -->
<div align="center">
  <h1 align="center">
    <br>
    <a href="#"><img src="assets/COVER.png" alt="UrbanMapper MCP" width="100%"></a>
    <br>
    MCPStack UrbanMapper MCP
    <br>
  </h1>
  <h4 align="center">Spatial pipelines & visualisations for cities — powered by MCPStack</h4>
</div>

<div align="center">

<a href="https://pre-commit.com/">
  <img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-1f6feb?style=for-the-badge&logo=pre-commit">
</a>
<img alt="ruff" src="https://img.shields.io/badge/Ruff-lint%2Fformat-9C27B0?style=for-the-badge&logo=ruff&logoColor=white">
<img alt="python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img alt="license" src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge">

</div>

> [!IMPORTANT]
> If you haven’t visited the MCPStack main orchestrator repository yet, please start
> there: **[MCPStack](https://github.com/MCP-Pipeline/MCPStack)**

> [!CAUTION]
> Please be aware that this MCP is in an early-alpha stage. While it is functional and can be used for various tasks, it may still contain bugs or incomplete features.
> Feel free to report any issues you encounter or suggest improvements. Even better, feel free to contribute directly!


## 💡 About The MCPStack UrbanMapper Tool

This repository provides the **first native MCP of The Urban-Mapper library @ [OSCUR](https://oscur.org/)**.

- It is **not a wrapper** around an upstream server: the MCP actions are implemented here directly.
- It lets an LLM **compose, explain, and visualise spatial pipelines** (e.g. collisions per intersection, amenities per neighborhood).
- Highly recommended to **link with the Jupyter MCP** → this enables *reproducible UrbanMapper analysis inside notebooks*, where the LLM can generate pipelines and immediately execute them in Jupyter.

**Wait, what is a Model Context Protocol (MCP) & `MCPStack` — In layman's terms ?**

The Model Context Protocol (MCP) standardises interactions with machine learning (Large Language) models,
enabling tools and libraries to communicate successfully with a uniform workflow.

On the other hand, `MCPStack` is a framework that implements the protocol, and most importantly, allowing
developers to create pipelines by stacking MCP tools of interest and launching them all in Claude Desktop.
This allows the LLM to use all the tools stacked, and of course, if a tool is not of interest, do not include it in the
pipeline and the LLM won't have access to it.

## Installation

The tool is distributed as a standard Python package. MCPStack will auto-discover it.

### Via `uv` (recommended)

```bash
uv add mcpstack-urbanmapper
```

### Via pip
```bash
pip install mcpstack-urbanmapper
```

###  (Dev) Pre-commit hooks

```bash
uv run pre-commit install
# or: pre-commit install
```

## Using With MCPStack — CLI workflow

This tool declares entry points so MCPStack can see it automatically:

```toml
[project.entry-points."mcpstack.tools"]
urbanmapper = "mcpstack_urbanmapper.tool:UrbanMapper"

[project.entry-points."mcpstack.tool_clis"]
urbanmapper = "mcpstack_urbanmapper.cli:UrbanMapperCLI.get_app"
```

### 1) (Optional) Configure environment

UrbanMapper works out of the box, but you can customise defaults:

```
MCP_URBANMAPPER_ENFORCE_HF_ONLY: "1" (default) → force Hugging Face datasets only.
MCP_URBANMAPPER_DEFAULT_SPLIT: "" (default) → default dataset split.
MCP_URBANMAPPER_DEFAULT_CRS: "EPSG:4326" (default) → default spatial CRS.
```

Use the CLI to generate a config file (by default, not necessary, only if you want to override defaults):

```bash
uv run mcpstack tools urbanmapper configure -o urbanmapper_config.json
```

### 2) Add to a pipeline

Create or extend a pipeline with UrbanMapper:

```bash
# New pipeline
uv run mcpstack pipeline urbanmapper --new-pipeline my_pipeline.json # followed by: --tool-config urbanmapper_config.json if needed
```

```bash
# Or append to an existing one
uv run mcpstack pipeline urbanmapper --to-pipeline my_pipeline.json # followed-by: --tool-config urbanmapper_config.json if needed
```

### 3) Link with Jupyter MCP (recommended)

For reproducible workflows, add both UrbanMapper and Jupyter tools to the same pipeline:

```bash
uv add mcpstack-jupyter # if not done yet
uv add mcpstack-jupyter list-tools # to confirm Jupyter is installed
uv run mcpstack tools jupyter configure --token 1117bf468693444a5608e882ab3b55d511f354a175a0df02 # or whatever else token of interest, reader is reffered to the Jupyter MCP docs
uv run mcpstack pipeline jupyter --tool-config jupyter_config.json --new-pipeline my_pipeline.json
uv run mcpstack pipeline urbanmapper --to-pipeline my_pipeline.json # followed by: --tool-config urbanmapper_config.json if needed
```

Now the LLM can:

* Generate UrbanMapper pipelines (`um_build_pipeline_code`)
* Insert them into notebooks via Jupyter MCP
* Run them, preview maps, and adjust interactively

## Programmatic API Workflow

Use the UrbanMapper tool directly in a stack:

```python
from mcpstack_urbanmapper.tool import UrbanMapper
from MCPStack.stack import MCPStackCore

pipeline = (
    MCPStackCore()
    .with_tool(UrbanMapper()) # define envs/parameters to UrbanMapper() if needed
    # add other tools (e.g. Jupyter) if needed
    .build(type="fastmcp", save_path="urbanmapper_pipeline.json")
    .run() # runs a fastmcp instance immediately (no Claude Desktop) — use the documentation for other types
)
```

### UrbanMapper Actions Overview

* `um_list_urban_layers()` → available layers (roads, intersections, etc.)
* `um_explain_primitive(stage, technique)` → explain a stage/technique
* `um_hf_dataset_schema(repo_id)` → inspect a Hugging Face dataset
* `um_build_pipeline_code(...)` → generate a complete urbam-mapper's urban pipeline code snippet
* `um_list_examples()` / `um_get_example_code(name)` → browse YAML examples to how to use UrbanMapper
* `um_visualiser_presets(viz_type)` → style presets for maps

## License

MIT — see **[LICENSE](LICENSE)**.
