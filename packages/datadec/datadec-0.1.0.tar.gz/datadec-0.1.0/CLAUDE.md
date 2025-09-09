# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

```bash
uv sync                    # Install dependencies
uv add -e .               # Install in dev mode
uv run ruff check         # Lint code
uv run ruff format        # Format code
```

## Architecture Overview

**Core Modules:**
- **`data.py`** - Main `DataDecide` class and `get_filtered_df()` method
- **`paths.py`** - Single source of truth: `paths.dataframes` dict maps names → file paths
- **`pipeline.py`** - ETL stages with `recompute_from` granular control
- **`constants.py`** - All hardcoded DataDecide config (~300 lines)
- **`parsing.py`** - Data transformations (includes the slow metrics expansion)
- **`model_utils.py`** - Model configs, learning rates, `param_to_numeric()`
- **`df_utils.py`** - DataFrame utilities, filtering, aggregation
- **`loader.py`** - Lazy loading and caching

**Data Pipeline Stages:**
1. `download` - Raw HF datasets
2. `metrics_expand` - JSON metrics → columns (SLOW: 2-5 min)
3. `parse` - Clean & standardize
4. `merge` - Combine perplexity + downstream  
5. `aggregate` - Stats across seeds

**Plotting System:**
- **Production:** `scripts/plot_scaling_analysis.py` - Native dr_plotter implementation
- **Archive:** `scripts/legacy_deprecated/` - Legacy system (broken, do not use)

## Key APIs

### DataDecide Interface
```python
dd = DataDecide(data_dir="./data", recompute_from="metrics_expand")

# Main properties (renamed from *_ds/*_df)
dd.full_eval, dd.mean_eval, dd.model_details, dd.dataset_details

# New unified loading
dd.load_dataframe("ppl_raw")  # Any DataFrame by name
dd.get_filtered_df()          # Filtered analysis data (default: max_steps filter)
dd.get_filtered_df(filter_types=["ppl", "max_steps"])  # Multiple filters

# Exploration
dd.paths.dataframes           # Dict: name → filename  
dd.paths.available_dataframes # List all options
```

### Native Plotting (Production System)
```python
# Use native dr_plotter patterns - NOT custom wrapper functions
with FigureManager(legend_strategy="figure_below") as fm:
    fm.plot("line", 0, i, subset, x="tokens", y="metric", hue_by="params")

# Run production plotting system
python scripts/plot_scaling_analysis.py
```

### Path Management
```python
# Always use centralized path access
path = dd.paths.get_path("dwn_metrics_expanded")  # Not individual properties
```

## Available DataFrames

Access via `dd.load_dataframe(name)`:
- **Raw:** `ppl_raw`, `dwn_raw`
- **Intermediate:** `dwn_metrics_expanded` (slow step result), `ppl_parsed`, `dwn_parsed`
- **Final:** `full_eval`, `mean_eval`, `std_eval`
- **Analysis:** `full_eval_with_details`, `mean_eval_with_lr`

## Code Conventions

- **Path access:** Always `paths.get_path(name)`, never individual properties
- **Performance:** Use assertions, not exceptions (ML performance requirement)
- **Type hints:** Required on all functions
- **Imports:** Absolute imports at top of file
- **Plotting:** Use native dr_plotter, NOT custom wrapper functions

## Working Principles

### For Implementation Agents
- **Systematic validation:** Test basic patterns before complex ones
- **Evidence-based decisions:** Quantify benefits before committing to changes
- **Quality standards:** Maintain production-ready code throughout
- **Documentation:** Create lab notebooks and strategic reports (see `docs/processes/reporting_guide.md`)
- **Native over custom:** Use library capabilities before building wrappers

### Project Documentation
- **Lab notebooks:** Technical reference with file:line references, bugs, discoveries
- **Strategic reports:** Decision context, lessons learned, reusable patterns
- **Templates:** Available in `docs/processes/` for consistent reporting

## Performance Notes

- **Bottleneck:** `list_col_to_columns(df, "metrics")` in parsing.py:95 (2-5 min)
- **Optimization:** Slow step saved as intermediate `dwn_metrics_expanded`
- **Caching:** DataFrames cached after first load
- **Granular recompute:** Use `recompute_from="metrics_expand"` to skip download

## Migration History

- **2025-08-25:** Successfully migrated from custom plotting wrappers to native dr_plotter
  - 40-92% code reduction across all plotting patterns
  - Enhanced reliability and visual quality
  - See `docs/reports/2025-08-25_dr_plotter_migration/` for complete documentation