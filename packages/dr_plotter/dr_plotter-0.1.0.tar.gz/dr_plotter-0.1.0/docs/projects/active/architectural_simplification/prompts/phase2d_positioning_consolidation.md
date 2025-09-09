# Phase 2D: Positioning Consolidation

## Strategic Objective

Consolidate all legend positioning logic into a unified system, eliminate remaining hardcoded magic numbers, and create a clean architectural foundation for legend positioning. This is the final step in architectural simplification of the legend system.

## Problem Context

Research identified positioning logic scattered across multiple files:
- `legend_manager.py` - Core positioning calculations with 12+ hardcoded values
- `figure.py` - `rect=[0, 0, 1, 0.95]` title space adjustments  
- `figure_config.py` - `tight_layout_pad: float = 0.5` default padding

Current system has complex conditional branching, mathematical positioning formulas without systematic approach, and no unified positioning calculation system.

## Requirements & Constraints

**Must Consolidate**:
- All positioning logic into unified calculation system
- Scattered hardcoded values into centralized configuration
- Complex conditional positioning logic into clear, maintainable functions
- Integration between legend positioning and tight_layout system

**Must Eliminate**:
- Magic numbers like `single_legend_x = 0.5`, `bbox_y_offset = 0.08`
- Complex conditional branching based on legend count in positioning logic
- Scattered positioning parameters across multiple files
- Mathematical positioning formulas without clear systematic approach

**Must Preserve**:
- All current visual output for existing configurations
- Every manual positioning override capability
- Integration with tight_layout and figure layout system
- Performance characteristics of current positioning system

**Cannot Break**:
- Any existing positioning behavior when manual coordinates specified
- Current visual quality and layout appearance
- Integration with Phase 2A-2C implementations
- Backward compatibility with all positioning parameters

## Decision Frameworks

**Consolidation Architecture**:
- Single PositioningCalculator class responsible for all legend positioning
- Clear separation between positioning logic and legend creation
- Unified interface for all positioning approaches (manual, hints, defaults)
- Integration point with figure layout system

**Hardcoded Value Elimination**:
- Replace magic numbers with calculated values based on figure dimensions
- Convert positioning constants to configuration parameters with defaults
- Create systematic spacing and alignment algorithms
- Maintain visual equivalence while removing hardcoded dependencies

**Integration Strategy**:
- Coordinate with tight_layout system for consistent margin management
- Unified margin calculation that considers legend positioning needs
- Clear boundaries between legend positioning and figure layout responsibilities
- Preserve current tight_layout integration behavior

## Success Criteria

**Architectural Consolidation**:
- Single, clear positioning calculation system replacing scattered logic
- All positioning logic accessible through unified interface
- Clean separation between positioning calculation and legend creation
- Maintainable code structure that eliminates complex conditional branching

**Magic Number Elimination**:
- No hardcoded positioning coordinates in legend system
- All positioning values calculated from figure dimensions, content, and configuration
- Systematic spacing and alignment algorithms replace mathematical formulas
- Configuration-based positioning that adapts to different scenarios

**Visual Quality Preservation**:
- Identical visual output for all existing manual positioning configurations
- Equivalent or improved visual quality for default positioning scenarios
- Professional legend appearance maintained across all positioning approaches
- No regression in legend placement quality or layout integration

**System Performance**:
- Positioning calculations perform comparably to current hardcoded approach
- No significant performance impact from consolidation and calculation
- Efficient caching of positioning calculations when appropriate
- Responsive positioning that scales well with complex figure layouts

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Architectural Standards**:
- Clear single responsibility for positioning calculation
- Minimal interface with maximum flexibility
- Type-safe positioning parameter handling
- Integration follows existing dr_plotter architectural patterns

**Positioning Calculator Design Pattern**:
```python
class PositioningCalculator:
    def calculate_positions(self, config: LegendConfig, 
                          figure_dimensions: FigureDimensions,
                          legend_metadata: LegendMetadata) -> PositioningResult:
        # Unified calculation that handles manual, hints, and defaults
        return self._resolve_positioning_hierarchy(config, figure_dimensions, legend_metadata)
    
    def _resolve_positioning_hierarchy(self, ...) -> PositioningResult:
        # Layer 1: Systematic defaults (replaces hardcoded values)
        # Layer 2: Layout hint calculations (from Phase 2C)  
        # Layer 3: Manual coordinate overrides
        pass
```

**Configuration Consolidation**:
```python
@dataclass
class PositioningConfig:
    # Replaces scattered hardcoded values with configurable parameters
    default_margin_bottom: float = 0.15
    legend_spacing_factor: float = 0.35
    alignment_tolerance: float = 0.05
    
    def calculate_systematic_defaults(self, figure_size, legend_count) -> PositioningValues:
        # Systematic calculation replacing magic numbers
        pass
```

## Adaptation Guidance

**If Consolidation Reveals Complex Dependencies**:
- Document dependencies clearly rather than trying to eliminate all complexity immediately
- Focus on consolidating scattered logic before optimizing internal complexity
- Maintain integration points with minimal changes to reduce risk
- Progressive consolidation over wholesale architectural changes

**If Visual Output Changes During Consolidation**:
- Prioritize maintaining current visual quality over perfect consolidation
- Document any improvements as intentional enhancements
- Test extensively with existing examples to catch visual regressions
- Adjust systematic calculations to match current proven visual output

**If Performance Impact is Significant**:
- Profile positioning calculations to identify performance bottlenecks
- Cache calculated positioning values when figure dimensions unchanged
- Optimize systematic calculations without compromising visual quality
- Consider lazy calculation approaches for complex positioning scenarios

## Documentation Requirements

**Architectural Documentation**:
- Unified positioning system architecture with clear component responsibilities
- Before/after comparison showing consolidation of scattered positioning logic
- Integration approach with figure layout and tight_layout systems
- Performance characteristics of new positioning calculation system

**Implementation Documentation**:
- Complete mapping from old hardcoded values to new systematic calculations
- Positioning calculation algorithms with mathematical basis documentation
- Configuration parameter explanations replacing hardcoded magic numbers
- Migration path from Phase 2A-2C implementations to final consolidated system

**Validation Documentation**:
- Comprehensive visual regression testing results
- Performance benchmarking comparing old vs new positioning systems
- Evidence of successful elimination of all identified magic numbers
- Integration testing with existing examples and complex legend scenarios

**Strategic Impact Assessment**:
- Legend system complexity reduction achieved through consolidation
- Maintainability improvements from unified positioning architecture
- Foundation for future legend positioning enhancements
- Overall architectural simplification success metrics