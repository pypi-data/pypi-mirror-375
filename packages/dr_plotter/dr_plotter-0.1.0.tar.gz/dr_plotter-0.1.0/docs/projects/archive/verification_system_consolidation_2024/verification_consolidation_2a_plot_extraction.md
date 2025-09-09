# Tactical Prompt: Consolidate Plot Feature Extraction Components

## Strategic Objective
Create a unified, clean data extraction layer for the verification system by eliminating massive duplication in plot property extraction logic. This establishes a solid foundation for later verification logic consolidation.

## Problem Context
The discovery audit revealed extensive duplication in matplotlib data extraction across multiple files:
- **501 lines** in `plot_property_extraction.py` with main extraction functions
- **Duplicate legend extraction** scattered across `verif_decorators.py` 
- **Color/marker processing repeated** across all verification files with inconsistent interfaces
- **9+ legend extraction functions** doing essentially identical work

This consolidation creates a clean foundation layer without touching verification logic.

## Requirements & Constraints
**Must Consolidate**:
- All color processing logic scattered across files into single implementation
- All legend extraction logic (9+ functions) into unified interface
- All collection property extraction (scatter, line, violin, bar, image) into consistent format
- All utility functions (tolerance comparison, size conversion, marker identification) into shared layer

**Must Preserve**:
- All current extraction capabilities and data formats
- Integration with existing verification code during transition
- All matplotlib object types currently supported

**Files to Modify**:
- Create new: `src/dr_plotter/scripting/plot_data_extractor.py` 
- Update: `src/dr_plotter/scripting/plot_property_extraction.py` (remove duplicates, redirect to new module)
- Update: `src/dr_plotter/scripting/verif_decorators.py` (remove extraction logic)
- Update: Other verification files to use new unified interface

## Decision Frameworks

**Consolidation Approach**:
- **Single entry points** vs **Multiple specialized functions**: Create one main function per data type (colors, markers, etc.) that handles all collection types internally
- **Error handling strategy**: Consistent exception handling vs graceful degradation - choose consistent exceptions to fail fast
- **Return format standardization**: All extraction functions return same dictionary structure with consistent key names

**Interface Design**:
- **Public API complexity**: Minimize - prefer `extract_colors(obj)` over `extract_scatter_colors()` + `extract_line_colors()` + etc.
- **Type detection**: Automatic vs explicit - detect collection/legend type automatically within unified functions
- **Data format**: Maintain current RGBA tuple format for colors, string format for markers, float format for sizes

**Migration Strategy**:
- **Backward compatibility**: Create new unified functions first, then update callers, then remove old functions
- **Testing approach**: Ensure new unified functions return identical data to current scattered implementations
- **Import management**: Update imports progressively, don't break existing verification code during transition

## Success Criteria

**Code Consolidation**:
- [ ] Single `extract_colors()` function replaces all scattered color extraction logic
- [ ] Single `extract_legend_properties()` function replaces 9+ legend extraction functions  
- [ ] Single `extract_collection_properties()` function handles all collection types consistently
- [ ] All utility functions (tolerance comparison, size conversion) in shared utilities module

**Interface Consistency**:
- [ ] All extraction functions return consistent dictionary format
- [ ] Consistent error handling across all extraction operations (fail fast with clear exceptions)
- [ ] Single import point for all extraction functionality
- [ ] No duplicate matplotlib integration logic across files

**Functional Preservation**:
- [ ] All current data extraction capabilities maintained
- [ ] Existing verification code continues to work during transition
- [ ] All matplotlib object types still supported
- [ ] Return data formats identical to current implementation

## Quality Standards
**Clean Architecture**: Clear separation between unified extraction layer and verification logic
**Single Responsibility**: Each function has one clear purpose (extract colors, extract legends, etc.)
**Consistent Interfaces**: All extraction functions follow same parameter and return value patterns
**Error Clarity**: Failures provide clear information about what extraction failed and why

## Adaptation Guidance
**If extraction logic differs subtly**: Document the differences clearly but consolidate to single implementation - choose the most robust approach
**If return formats are inconsistent**: Standardize on the most complete format, ensure all callers can handle it
**If matplotlib integration is complex**: Simplify to common patterns, eliminate special cases where possible
**If utility functions overlap**: Consolidate to single implementation, remove all duplicates

## Documentation Requirements
**Create implementation document** showing:
- New unified extraction interface design
- Mapping from old scattered functions to new consolidated functions
- Any behavior changes or standardizations made during consolidation
- List of functions eliminated and their replacements

**Implementation Approach**:
1. **Create new unified extraction module** with clean interfaces
2. **Update all callers** to use unified interface 
3. **Remove old scattered extraction logic** completely
4. **Verify functional equivalence** through existing example runs

This consolidation eliminates the foundation layer duplication that makes the verification system unnecessarily complex and hard to maintain.