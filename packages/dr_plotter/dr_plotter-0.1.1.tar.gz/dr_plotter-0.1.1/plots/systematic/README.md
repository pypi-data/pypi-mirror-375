# Systematic ML Evaluation Plots

This directory contains systematic plots for ML training evaluation data created using dr_plotter's faceting system. The plots analyze performance across different data recipes, model sizes, and metrics using various organizational strategies.

## Plotting Script

### Location & Usage
**Script**: `examples/systematic_ml_plotting.py`

**Basic Usage:**
```bash
# Get help and see all options
uv run python examples/systematic_ml_plotting.py --help

# See available data and families
uv run python examples/systematic_ml_plotting.py info

# Single metric plots
uv run python examples/systematic_ml_plotting.py single --metric pile-valppl --recipes C4 Dolma1.7 --model-sizes 10M 20M 60M

# Grouped metric plots
uv run python examples/systematic_ml_plotting.py ppl-group --recipes C4 Dolma1.7 --model-sizes 10M 20M
uv run python examples/systematic_ml_plotting.py olmes-group --recipes C4 Dolma1.7 --model-sizes 10M 20M

# Model size chunks
uv run python examples/systematic_ml_plotting.py size-chunk --chunk-idx 0 --recipes C4 Dolma1.7

# Recipe family chunks
uv run python examples/systematic_ml_plotting.py recipe-family --family-name core_datasets --model-sizes 10M 20M 60M

# Performance-based recipe chunks
uv run python examples/systematic_ml_plotting.py recipe-performance --family-name best_ppl_performance --performance-type ppl --model-sizes 10M 20M
uv run python examples/systematic_ml_plotting.py recipe-performance --family-name best_olmes_performance --performance-type olmes --model-sizes 10M 20M
```

### Key Features
- **NaN filtering**: Removes NaN values to prevent line discontinuities
- **Mean + seeds visualization**: `--mean-and-seeds` shows individual seed data (low alpha) with mean overlay (high alpha)
- **Systematic naming**: Organized output with predictable filenames
- **Interactive display**: 5-second display + auto-close for smooth iteration
- **Nested directory structure**: Organized by plot type and subtype

## Directory Structure

```
plots/systematic/
├── README.md                          # This file
├── single_metrics/                    # Individual metric analysis
│   ├── ppl/                          # Perplexity metrics
│   │   ├── pile_valppl.png
│   │   ├── wikitext_103_valppl.png
│   │   └── c4_en_valppl.png
│   └── olmes/                        # OLMES/accuracy metrics
│       ├── mmlu_average_acc_raw.png
│       ├── arc_challenge_acc_raw.png
│       └── hellaswag_acc_raw.png
├── grouped_metrics/                   # Multiple metrics together
│   ├── ppl_groups/
│   │   └── ppl_group_metrics.png
│   └── olmes_groups/
│       └── olmes_group_metrics.png
└── recipe_chunks/                     # Recipe-based analysis
    ├── custom_families/              # User-defined recipe families
    │   ├── core_datasets.png
    │   ├── dolma17_variants.png
    │   ├── dclm_variants.png
    │   ├── falcon_cc_variants.png
    │   ├── fineweb_variants.png
    │   └── mix_with_baselines.png
    ├── ppl_performance_chunks/       # PPL-based performance groupings
    │   ├── best_ppl_performance.png
    │   ├── good_ppl_performance.png
    │   ├── medium_ppl_performance.png
    │   └── poor_ppl_performance.png
    └── olmes_performance_chunks/     # OLMES-based performance groupings
        ├── best_olmes_performance.png
        ├── good_olmes_performance.png
        ├── medium_olmes_performance.png
        └── poor_olmes_performance.png
```

## Recipe Family Classifications

### Custom Recipe Families

These families were designed for systematic analysis based on dataset relationships and research focus:

#### `core_datasets`
**Purpose**: Classic/foundational datasets
- C4
- Falcon  
- Dolma1.6++

#### `dolma17_variants`
**Purpose**: Dolma 1.7 with different filtering approaches
- Dolma1.7
- Dolma1.7 (no code)
- Dolma1.7 (no math, code)
- Dolma1.7 (no Reddit)
- Dolma1.7 (no Flan)

#### `dclm_variants` 
**Purpose**: DCLM with different quality control settings
- DCLM-Baseline
- DCLM-Baseline (QC 10%)
- DCLM-Baseline (QC 20%)
- DCLM-Baseline (QC 7%, FW3)
- DCLM-Baseline (QC 7%, FW2)
- DCLM-Baseline (QC FW 3%)
- DCLM-Baseline (QC FW 10%)

#### `falcon_cc_variants`
**Purpose**: Falcon+CommonCrawl with quality control variations
- Falcon+CC
- Falcon+CC (QC 10%)
- Falcon+CC (QC 20%)
- Falcon+CC (QC Orig 10%)
- Falcon+CC (QC Tulu 10%)

#### `fineweb_variants`
**Purpose**: FineWeb dataset versions
- FineWeb-Pro
- FineWeb-Edu

#### `mix_with_baselines`
**Purpose**: DCLM/Dolma mixtures with 100% baselines for comparison
- DCLM-Baseline 25% / Dolma 75%
- DCLM-Baseline 50% / Dolma 50%
- DCLM-Baseline 75% / Dolma 25%
- DCLM-Baseline *(100% representative)*
- Dolma1.7 *(100% representative)*

### Performance-Based Recipe Chunks

Performance chunks are created by ranking all 25 recipes on 1B model final-step performance, then splitting into 4 equal groups. This enables systematic analysis of high vs. low performing datasets.

#### PPL Performance Ranking (Lower = Better)
*Based on average across 11 PPL metrics at final training step (67,500) for 1B model*

**Chunk 0 - `best_ppl_performance` (avg PPL: 13.099)**
1. DCLM-Baseline 25% / Dolma 75% - **12.975**
2. Dolma1.7 (no code) - **12.997** 
3. Dolma1.7 - **13.020**
4. Dolma1.7 (no Flan) - **13.045**
5. DCLM-Baseline 50% / Dolma 50% - **13.200**
6. Dolma1.6++ - **13.226**
7. Dolma1.7 (no Reddit) - **13.227**

**Chunk 1 - `good_ppl_performance` (avg PPL: 14.568)**
8. DCLM-Baseline 75% / Dolma 25% - **13.475**
9. Dolma1.7 (no math, code) - **13.585**
10. Falcon+CC (QC Tulu 10%) - **14.591**
11. Falcon+CC (QC 20%) - **15.177**
12. Falcon+CC - **15.183**
13. Falcon+CC (QC Orig 10%) - **15.399**

**Chunk 2 - `medium_ppl_performance` (avg PPL: 16.335)**
14. DCLM-Baseline - **15.454**
15. Falcon+CC (QC 10%) - **15.773**
16. DCLM-Baseline (QC 20%) - **16.290**
17. DCLM-Baseline (QC 7%, FW2) - **16.297**
18. Falcon - **16.803**
19. DCLM-Baseline (QC 10%) - **17.396**

**Chunk 3 - `poor_ppl_performance` (avg PPL: 22.035)**
20. DCLM-Baseline (QC FW 10%) - **17.664**
21. DCLM-Baseline (QC 7%, FW3) - **19.369**
22. FineWeb-Edu - **20.391**
23. FineWeb-Pro - **20.969**
24. DCLM-Baseline (QC FW 3%) - **22.268**
25. C4 - **31.546** *(significantly worse)*

#### OLMES Performance Ranking (Higher = Better)
*Based on average across 4 OLMES metrics (mmlu_average_acc_raw, arc_challenge_acc_raw, hellaswag_acc_raw, boolq_acc_raw) at final training step for 1B model*

**Chunk 0 - `best_olmes_performance` (avg Acc: 0.466)**
1. DCLM-Baseline (QC 7%, FW2) - **0.471**
2. DCLM-Baseline (QC FW 10%) - **0.471**
3. DCLM-Baseline (QC 20%) - **0.469**
4. DCLM-Baseline (QC 10%) - **0.467**
5. Falcon+CC (QC Orig 10%) - **0.464**
6. DCLM-Baseline (QC 7%, FW3) - **0.464**
7. Falcon+CC (QC 10%) - **0.458**

**Chunk 1 - `good_olmes_performance` (avg Acc: 0.450)**
8. FineWeb-Pro - **0.455**
9. FineWeb-Edu - **0.454**
10. DCLM-Baseline - **0.452**
11. Falcon+CC (QC 20%) - **0.451**
12. Falcon+CC (QC Tulu 10%) - **0.449**
13. DCLM-Baseline (QC FW 3%) - **0.440**

**Chunk 2 - `medium_olmes_performance` (avg Acc: 0.430)**
14. DCLM-Baseline 25% / Dolma 75% - **0.436**
15. DCLM-Baseline 75% / Dolma 25% - **0.434**
16. C4 - **0.432**
17. Dolma1.7 (no code) - **0.428**
18. Dolma1.7 (no Reddit) - **0.425**
19. Falcon - **0.424**

**Chunk 3 - `poor_olmes_performance` (avg Acc: 0.408)**
20. Dolma1.7 (no math, code) - **0.422**
21. Dolma1.7 (no Flan) - **0.420**
22. DCLM-Baseline 50% / Dolma 50% - **0.419**
23. Falcon+CC - **0.419**
24. Dolma1.7 - **0.402**
25. Dolma1.6++ - **0.366** *(significantly worse)*

## Key Insights

### Performance Trade-offs
**PPL vs OLMES performance rankings show dramatic differences:**
- **PPL Champions**: Dolma variants (especially mixed with DCLM) excel at perplexity
- **OLMES Champions**: DCLM variants (especially with quality control) excel at downstream tasks
- **C4**: Poor PPL but medium OLMES performance
- **Dolma1.6++**: Medium PPL but poor OLMES performance

### Quality Control Effects
- **DCLM QC variants**: Generally improve OLMES performance but hurt PPL
- **Falcon+CC QC**: Mixed results across both metrics
- **Content filtering** (no code, no math): Generally improves PPL, hurts OLMES

### Dataset Mixing
- **Balanced DCLM/Dolma mixes**: Best PPL performance overall
- **Higher Dolma ratios**: Better PPL, worse OLMES
- **Higher DCLM ratios**: Worse PPL, better OLMES

## Updating and Interpreting Plots

### Plot Layout
- **Rows**: Typically model sizes (10M, 20M, 60M, etc.)
- **Cols**: Typically data recipes or recipe families  
- **Lines**: Different metrics (different colors)
- **X-axis**: Training steps
- **Y-axis**: Metric values (PPL or accuracy)

### Visual Patterns to Look For
1. **Convergence rates**: How quickly do lines plateau?
2. **Final performance**: Where do lines end up?
3. **Stability**: Are there fluctuations or smooth curves?
4. **Scaling patterns**: Do trends hold across model sizes?
5. **Metric correlations**: Do PPL and OLMES patterns align?

### Regenerating Plots
To update plots with new data or different configurations:

```bash
# Regenerate all PPL performance chunks
for chunk in best_ppl_performance good_ppl_performance medium_ppl_performance poor_ppl_performance; do
    uv run python examples/systematic_ml_plotting.py recipe-performance --family-name $chunk --performance-type ppl --model-sizes 10M 20M 60M 90M --no-show
done

# Regenerate all OLMES performance chunks  
for chunk in best_olmes_performance good_olmes_performance medium_olmes_performance poor_olmes_performance; do
    uv run python examples/systematic_ml_plotting.py recipe-performance --family-name $chunk --performance-type olmes --model-sizes 10M 20M 60M 90M --no-show
done

# Regenerate all custom families
for family in core_datasets dolma17_variants dclm_variants falcon_cc_variants fineweb_variants mix_with_baselines; do
    uv run python examples/systematic_ml_plotting.py recipe-family --family-name $family --model-sizes 10M 20M 60M 90M --no-show
done
```

### Plot Customization
Key parameters for customization:
- `--model-sizes`: Which model sizes to include
- `--recipes`: Which recipes to include (for non-chunk plots)
- `--mean-and-seeds`: Add individual seed visualization
- `--output-dir`: Change output directory
- `--no-show`: Skip interactive display for batch generation

---

*Generated with dr_plotter's systematic ML evaluation plotting framework*  
*Performance rankings based on 1B model final-step performance as of dataset analysis*