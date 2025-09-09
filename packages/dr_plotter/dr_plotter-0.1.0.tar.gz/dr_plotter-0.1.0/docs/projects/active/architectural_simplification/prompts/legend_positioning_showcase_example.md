# Legend Positioning Showcase Example Implementation

## Strategic Objective

Create a comprehensive visual test example (`12_legend_positioning_showcase.py`) that demonstrates all legend positioning improvements from Phase 2 work, allowing visual verification of string interface, smart defaults, and PositioningCalculator functionality.

## Problem Context

After implementing Phase 2A-2D legend system improvements, we need a comprehensive example that validates:
- String interface functionality (`legend="grouped"`, `"figure"`, `"subplot"`, `"none"`)
- Smart defaults for GROUPED_BY_CHANNEL (context-aware titles, adaptive ncol, responsive positioning)
- PositioningCalculator integration (systematic positioning, figure-width responsiveness)
- Backward compatibility with manual overrides

## Requirements & Constraints

**Must Implement**:
- Three distinct sections testing different aspects of legend positioning system
- Follow existing example pattern with proper imports, decorators, and structure
- Use `ExampleData` methods for consistent data generation
- Visual verification of all string interface shortcuts
- Demonstrate smart defaults and responsive behavior

**Must Preserve**:
- Existing example file structure and naming conventions
- Standard imports and utility function usage
- Verification decorator patterns for validation
- Output handling with `show_or_save_plot()`

**Cannot Break**:
- Existing example infrastructure or data generation methods
- Standard example execution patterns
- File naming or organizational conventions

## Decision Frameworks

**Example Structure Organization**:
- **Section 1**: String Interface Validation (2x2 grid) - core functionality
- **Section 2**: Smart Defaults Validation (2x2 grid) - intelligence features  
- **Section 3**: PositioningCalculator Integration (1x3 grid) - responsive positioning
- Each section as separate figure for clear visual separation

**Data Generation Strategy**:
- Use existing `ExampleData` methods where possible
- Create new methods if needed for specific test scenarios
- Multi-channel data for GROUPED testing (hue_by + marker_by combinations)
- Contextual naming data with underscore patterns for smart title generation

**Validation Approach**:
- Use `@verify_figure_legends` decorators appropriate to each section
- Visual output quality as primary success metric
- Functional behavior verification for each positioning mode
- Performance characteristics documentation

## Success Criteria

**String Interface Validation**:
- All four string shortcuts (`"grouped"`, `"figure"`, `"subplot"`, `"none"`) work correctly
- `legend="grouped"` produces appropriate multiple legends for multi-channel data
- Visual output matches expected behavior for each interface type
- Error handling works for invalid string inputs

**Smart Defaults Demonstration**:
- Context-aware channel titles generated from column names (`model_size` → `Model Size`)
- Adaptive ncol calculation responds to figure width and content
- Responsive positioning adapts to legend count and figure dimensions
- Manual override preservation demonstrated alongside automatic behavior

**PositioningCalculator Integration**:
- Systematic positioning replaces hardcoded values with calculated positioning
- Figure-width responsive spacing and alignment across narrow/medium/wide figures
- Clean integration with FigureManager layout system
- Performance characteristics comparable to previous hardcoded approach

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles and existing example patterns

**File Structure Standards**:
```python
# Standard example imports
from typing import Any
from dr_plotter.figure import FigureManager
from dr_plotter.figure_config import FigureConfig
from dr_plotter.legend_manager import LegendConfig
from dr_plotter.scripting.utils import setup_arg_parser, show_or_save_plot
from dr_plotter.scripting.verif_decorators import verify_figure_legends
from plot_data import ExampleData

# Main function with verification decorator
@verify_figure_legends(expected_legend_count=X, legend_strategy="...", ...)
def main(args: Any) -> Any:
    # Section implementation
    
# Standard argument parsing and execution
if __name__ == "__main__":
    parser = setup_arg_parser(description="Legend Positioning Showcase")
    args = parser.parse_args()
    main(args)
```

**Section Implementation Pattern**:
```python
# Section 1: String Interface Validation
with FigureManager(
    figure=FigureConfig(rows=2, cols=2, figsize=(16, 12)),
    legend="figure"  # Use string interface
) as fm:
    fm.fig.suptitle("Section 1: String Interface Validation", fontsize=16)
    
    # Subplot implementations with different legend string values
    # (0,0): legend="subplot", (0,1): legend="figure" 
    # (1,0): legend="grouped", (1,1): legend="none"
```

**Data Generation Requirements**:
```python
# Required data types for comprehensive testing
multi_channel_data = ExampleData.get_multi_channel_data()  # For GROUPED testing
contextual_data = # Data with contextual column names (model_size, dataset_type)
positioning_data = # Data for testing various legend counts and positioning
```

## Adaptation Guidance

**If ExampleData Methods Don't Exist**:
- Create simple synthetic data generation within the example file
- Use pandas DataFrame construction with appropriate column names
- Focus on patterns needed for legend testing (multi-channel, contextual names)
- Document any new data generation patterns for future examples

**If PositioningCalculator Integration Has Issues**:
- Focus on demonstrating what works rather than debugging integration issues
- Document any discovered positioning behavior for future improvement
- Ensure visual comparison shows improvement over previous hardcoded approach
- Test across different figure sizes to validate responsive behavior

**If Smart Defaults Need Adjustment**:
- Document actual behavior vs expected behavior
- Focus on demonstrating functionality that works correctly
- Provide clear visual examples of context-aware title generation
- Show adaptive column calculation and responsive positioning where functional

## Documentation Requirements

**Implementation Documentation**:
- Clear section descriptions with strategic purpose of each test
- Data generation approach and any new ExampleData methods needed
- Visual verification results for each positioning mode
- Performance characteristics and behavior comparisons

**Validation Results**:
- Visual output quality assessment across all legend positioning modes
- Functional verification of string interface, smart defaults, PositioningCalculator
- Evidence of backward compatibility preservation
- User experience improvements demonstrated through simplified configuration

**Example Output**:
- Three distinct figure outputs showing different aspects of legend system
- Before/after comparison documentation (if possible to generate)
- Clear demonstration of GROUPED_BY_CHANNEL discoverability improvement
- Evidence that manual overrides continue working alongside automatic behavior

**Strategic Impact Assessment**:
- Quantification of configuration simplification achieved
- User experience improvements through string interface
- Technical debt reduction from PositioningCalculator consolidation
- Foundation established for future legend system enhancements