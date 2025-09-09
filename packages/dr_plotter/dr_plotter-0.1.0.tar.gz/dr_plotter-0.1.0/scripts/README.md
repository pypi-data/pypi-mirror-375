# DR Plotter Scripts

## plot_bump.py

A comprehensive CLI script for creating bump plots that show data recipe rankings across different model sizes from DataDecide evaluation data.

```bash
# Examples

# Show best performing recipes across all model sizes
uv run python scripts/plot_bump.py --data "best_ppl"

# Compare core datasets with specific model sizes
uv run python scripts/plot_bump.py --params 60M 150M 300M 1B --data "core_datasets"

# All recipes with exclusions, save to file
uv run python scripts/plot_bump.py --data all --exclude-data "FineWeb-Pro" "C4" --save bump_plot.png
```

### Basic Usage

```bash
uv run python scripts/plot_bump.py [metric] [options]
```

### Required Arguments

- `metric`: The metric to plot for rankings (default: `pile-valppl`)

### Data Selection Options

```bash
# Named recipe groups (recommended)
--data "best_ppl"           # Top-performing recipes by perplexity
--data "core_datasets"      # Essential datasets: C4, Falcon, Dolma1.6++
--data "dolma17_variants"   # Dolma1.7 ablation studies
--data "dclm_variants"      # DCLM-Baseline with quality control variants

# Specific model sizes
--params 60M 150M 300M 1B
--params all --exclude-params 4M 6M 8M

# All data with exclusions
--data all --exclude-data "FineWeb-Pro" "C4"
```

### Named Recipe Groups

```bash
# Performance-based groupings
"best_ppl" "good_ppl" "medium_ppl" "poor_ppl"      # By perplexity performance
"best_olmes" "good_olmes" "medium_olmes" "poor_olmes"  # By OLMES performance

# Dataset families  
"core_datasets"        # C4, Falcon, Dolma1.6++
"dolma17_variants"     # Dolma1.7 ablation studies
"dclm_variants"        # DCLM-Baseline quality control variants
"falcon_cc_variants"   # Falcon+CC quality control variants
"fineweb_variants"     # FineWeb-Pro and FineWeb-Edu
"mix_with_baselines"   # Mixed DCLM/Dolma ratios

# Predefined sets
"base"        # Core 8 recipes without quality control
"base_qc"     # Core recipes + all quality control variants
"no_ablations" # All recipes excluding ablation studies
```

### Output Control

```bash
--save plot.png    # Save to file
--no-show          # Don't display interactively  
--figsize 14 10    # Figure size width height (default: 12 8)
```

### Visual Features

- **X-axis**: Model sizes (4M → 6M → 8M → ... → 1B)
- **Y-axis**: Ranking position (1 = best performance)
- **Lines**: Data recipe trajectories with distinct colors
- **Left labels**: Recipe names at initial rankings  
- **Floating annotations**: Perplexity values over each point
- **Extended color palette**: Supports 20+ distinct recipes

---

## plot_bump_timesteps.py

A complementary CLI script for creating bump plots that show data recipe rankings across training timesteps for a single model size from DataDecide evaluation data.

```bash
# Examples

# Show ranking evolution during training for 150M model
uv run python scripts/plot_bump_timesteps.py pile-valppl 150M --data "best_ppl"

# Focus on specific training phase for 1B model  
uv run python scripts/plot_bump_timesteps.py pile-valppl 1B --data "core_datasets" --min-step 10000 --max-step 50000

# All recipes with step filtering, save to file
uv run python scripts/plot_bump_timesteps.py pile-valppl 300M --data all --min-step 5000 --save timestep_bump.png
```

### Basic Usage

```bash
uv run python scripts/plot_bump_timesteps.py <metric> <model_size> [options]
```

### Required Arguments

- `metric`: The metric to plot for rankings (e.g., `pile-valppl`) 
- `model_size`: Single model size to analyze (e.g., `150M`, `1B`)

### Data Selection Options

```bash
# Same named recipe groups as plot_bump.py
--data "best_ppl"           # Top-performing recipes
--data "core_datasets"      # Essential datasets  
--data all --exclude-data "FineWeb-Pro"  # All with exclusions
```

### Training Step Filtering

```bash
--min-step 5000     # Start analysis from step 5000
--max-step 30000    # End analysis at step 30000
--min-step 10000 --max-step 50000  # Focus on specific training phase
```

### Output Control

```bash
--save plot.png    # Save to file
--no-show          # Don't display interactively
--figsize 14 8     # Figure size width height (default: 14 8)
```

### Visual Features

- **X-axis**: Training steps (formatted as 5.0k, 10.0k, etc.)
- **Y-axis**: Ranking position (1 = best performance)
- **Lines**: Data recipe trajectories with distinct colors
- **Left labels**: Recipe names at initial rankings
- **Floating annotations**: Perplexity values over each point
- **Extended color palette**: Supports 20+ distinct recipes

### Key Differences from plot_bump.py

- **Single model size**: Analyzes training dynamics for one parameter size
- **Time dimension**: X-axis shows training steps instead of model sizes
- **Step filtering**: Can focus on specific phases of training
- **Training insights**: Shows how rankings evolve during optimization

---

## plot_seeds.py

A comprehensive CLI script for plotting training curves with multiple seeds from DataDecide evaluation data.

```bash
# Examples
uv run python scripts/plot_seeds.py pile-valppl \
      --params 1B 90M 10M \
      --data C4 Dolma1.7 \
      --legend subplot

uv run python scripts/plot_seeds.py pile-valppl \
      --params all \
      --data all \
      --legend subplot \
      --no-sharey --no-sharex
```

### Basic Usage

```bash
uv run python scripts/plot_seeds.py <metric> [options]
```

### Required Arguments

- `metric`: The metric to plot (e.g., `pile-valppl`, `mmlu_average_acc_raw`)

### Data Selection Options

```bash
# Specific model sizes and data recipes
--params 10M 60M 90M
--data C4 Dolma1.7 "DCLM-Baseline"

# Use all available with exclusions
--params all --exclude-params 750M 1.4B
--data all --exclude-data "FineWeb-Pro"
```

### Legend Strategies

```bash
--legend subplot   # Individual legends per subplot (default)
--legend grouped   # Multi-channel grouped legends
--legend figure    # Single figure-level legend
```

### Axis Configuration

```bash
--xlog             # Logarithmic x-axis scaling
--ylog             # Logarithmic y-axis scaling
--no-sharex        # Disable x-axis sharing across subplots
--no-sharey        # Disable y-axis sharing across subplots
```

### Output Control

```bash
--save plot.png    # Save to file
--no-show          # Don't display interactively
--figsize-per-subplot 4.5   # Figure size per subplot (default: 4.0)
```

### Example Commands

```bash
# Basic plot with default settings
uv run python scripts/plot_seeds.py pile-valppl --params 10M 60M --data C4 Dolma1.7

# Log scaling with figure legend
uv run python scripts/plot_seeds.py pile-valppl --params 10M 60M --data C4 Dolma1.7 --legend figure --xlog

# All model sizes except large ones
uv run python scripts/plot_seeds.py mmlu_average_acc_raw --params all --exclude-params 750M 1.4B --data C4

# Save high-resolution plot without display
uv run python scripts/plot_seeds.py pile-valppl --params 10M 60M --data all --save results.png --no-show

# Custom layout with independent y-axes
uv run python scripts/plot_seeds.py pile-valppl --params all --data C4 Dolma1.7 --no-sharey --figsize-per-subplot 5.0
```

### Data Preparation

The script automatically:
- Filters data to requested parameter sizes and data recipes  
- Applies smart metric filtering (ppl/olmes filters only when all metrics are in one category)
- Handles missing values by dropping NaN entries after melting
- Orders data categorically according to specified parameter and data orders

### Output

Creates faceted plots with:
- **Rows**: Model parameter sizes
- **Columns**: Data recipes  
- **Lines**: Different random seeds (colored and labeled)
- **Axes**: Training steps (x) vs metric values (y)
- **Titles**: Automatic subplot titles and figure title
- **Legends**: Configurable legend strategies with seed labels

---

## plot_means.py

A flexible CLI script for plotting mean training curves with customizable faceting layouts from DataDecide evaluation data. This script aggregates across seeds to show averaged performance with configurable dimensional organization.

```bash
# Examples

# row based faceting
uv run python scripts/plot_means.py \
      --row="params" --row_values 10M 60M 90M \
      --lines="metrics"  --line_values pile-valppl wikitext_103-valppl \
      --fixed="data" --fixed-values C4

# rows -> cols
uv run python scripts/plot_means.py \
      --col="params" --col_values 10M 60M 90M \
      --lines="metrics"  --line_values pile-valppl wikitext_103-valppl \
      --fixed="data" --fixed-values C4

# col=params lines=metrics -> col=params lines=data
uv run python scripts/plot_means.py \
      --col="params" --col_values 10M 60M 90M \
      --lines="data"  --line_values C4 Dolma1.7 \
      --fixed="metrics" --fixed-values pile-valppl

# Sweep the model size, looking at metric vs proxy
PARAMS=1B; uv run python scripts/plot_means.py \
      --col="metrics" --col_values pile-valppl mmlu_average_correct_prob mmlu_average_acc_raw \
      --lines="data"  --line_values C4 Dolma1.7 \
      --fixed="params" --fixed-values ${PARAMS} \
      --no-sharex --no-sharey --save ./${PARAMS}_C4_Dolma_metrics_sweep.png

```

### Basic Usage

```bash
uv run python scripts/plot_means.py --row="dimension" --lines="dimension" [options]
```

### Required Arguments

- `--row` OR `--col`: Dimension to use for row/column faceting (`params`, `data`, `metrics`)
- `--lines`: Dimension to use for line grouping within each subplot (`params`, `data`, `metrics`) 
- `--line_values`: Values for the line dimension (e.g., `pile-valppl wikitext_103-valppl`)

### Dimensional Configuration

```bash
# Faceting (choose one)
--row="params"           # Create row of subplots for each parameter size
--col="data"            # Create column of subplots for each data recipe

# Line grouping within subplots  
--lines="metrics"       # Different colored lines for each metric

# Value selection
--row_values 10M 60M    # Specific values for row dimension
--col_values C4 Dolma1.7 # Specific values for column dimension  
--line_values pile-valppl wikitext_103-valppl  # Specific values for line dimension

# Fixed dimension (for unused dimensions)
--fixed="data"          # Hold data constant
--fixed-values C4       # Use only C4 data recipe
```

### Shared Options (same as plot_seeds.py)

```bash
# Legend strategies
--legend subplot        # Individual legends per subplot (default)
--legend grouped       # Multi-channel grouped legends
--legend figure        # Single figure-level legend

# Axis configuration
--xlog --ylog          # Logarithmic scaling
--xlim 0 1000         # X-axis limits
--ylim 2.5 4.0        # Y-axis limits
--no-sharex --no-sharey # Disable axis sharing

# Output control
--save plot.png --no-show --figsize-per-subplot 4.5

# Data filtering
--exclude-params 750M 1.4B --exclude-data "FineWeb-Pro"
```

### Example Commands

```bash
# Compare metrics across parameter sizes (fixed data)
uv run python scripts/plot_means.py --row="params" --lines="metrics" \
  --row_values 10M 60M 90M --line_values pile-valppl wikitext_103-valppl \
  --fixed="data" --fixed-values C4

# Compare data recipes across metrics (fixed model size)
uv run python scripts/plot_means.py --row="metrics" --lines="data" \
  --row_values pile-valppl mmlu_average_acc_raw \
  --line_values C4 Dolma1.7 "DCLM-Baseline" --fixed="params" --fixed-values 60M

# Column layout with figure legend
uv run python scripts/plot_means.py --col="data" --lines="params" \
  --col_values C4 Dolma1.7 --line_values 10M 60M 90M \
  --fixed="metrics" --fixed-values pile-valppl --legend figure

# Complex comparison with axis limits
uv run python scripts/plot_means.py --row="params" --lines="metrics" \
  --row_values 10M 60M --line_values pile-valppl c4_en-valppl \
  --fixed="data" --fixed-values C4 --ylim 2.5 4.5 --xlog
```

### Data Preparation

The script automatically:
- **Aggregates across seeds** before plotting (prevents NaN gaps in curves)
- Loads only data needed for specified dimensions (efficient filtering)
- Applies smart metric filtering for mixed ppl/olmes metrics
- Handles missing values during aggregation process

### Output

Creates faceted mean plots with:
- **Rows/Columns**: Any dimension (params, data, metrics)
- **Lines**: Any other dimension with different colors and proper legends
- **Fixed dimensions**: Held constant as specified 
- **Axes**: Training steps (x) vs aggregated metric values (y)
- **Titles**: Automatic titles including fixed dimension values
- **Legends**: All strategies supported with dimension-specific channel titles

### Key Differences from plot_seeds.py

- **Aggregated data**: Shows mean curves instead of individual seeds
- **Flexible layout**: Any dimension can be rows, columns, or lines
- **Fixed dimensions**: Ability to hold dimensions constant
- **Gap-free curves**: Proper aggregation eliminates missing data gaps
- **Fewer data points**: More efficient for comparing averaged performance
