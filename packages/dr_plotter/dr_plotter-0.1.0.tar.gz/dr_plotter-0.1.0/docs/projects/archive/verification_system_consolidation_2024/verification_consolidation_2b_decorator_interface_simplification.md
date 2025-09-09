# Verification System Consolidation: Decorator Interface Simplification

## Strategic Objective

Consolidate the verification decorator complexity from multiple overlapping decorators to 2-3 clear patterns with obvious use cases. This work eliminates parameter redundancy and configuration complexity, creating an interface that "disappears into the background" and allows researchers to focus on their visualizations rather than the verification system.

## Problem Context

The current decorator interface in `verif_decorators.py` creates cognitive overhead through:

- **Multiple overlapping decorators**: `verify_example`, `verify_plot_properties`, `verify_figure_legends`, `report_subplot_line_colors`
- **Parameter redundancy**: Similar parameters across decorators with unclear interactions
- **Configuration complexity**: Optional parameters requiring deep system knowledge to use effectively
- **Unclear use cases**: No obvious guidance on when to use which decorator
- **Complex parameter combinations**: Multiple ways to specify the same verification intent

**Architectural Impact**: Researchers must learn the verification system instead of using it intuitively, violating the "Focus on Researcher Workflow" principle.

## Requirements & Constraints

**Must Preserve**:
- All current verification capabilities (legend visibility, plot properties, consistency checking)
- Explicit parameter specification approach (no auto-detection)
- Textual output for visual validation
- Integration with consolidated `plot_data_extractor.py` and `unified_verification_engine.py`

**Must Eliminate**:
- Parameter redundancy between decorators
- Configuration options that should be architectural decisions
- Multiple ways to accomplish the same verification task
- Complex parameter interactions requiring documentation

**Must Not Break**:
- Existing verification examples that use current decorators
- Core functionality: manual ground truth specification and checking
- Integration with matplotlib figure/axes objects
- Assert-based failure behavior (fail-fast principle)

**Integration Points**:
- Must work seamlessly with `plot_data_extractor.py` extraction functions
- Must use `unified_verification_engine.py` for verification logic
- Must integrate with `verification_formatter.py` for output

## Decision Frameworks

**Decorator Consolidation Strategy**:
- **A. Single universal decorator**: One decorator that handles all verification scenarios through parameters
- **B. Purpose-based decorators**: 2-3 decorators with clear, distinct purposes (e.g., basic, advanced, debugging)
- **C. Verification-type decorators**: Separate decorators for different verification aspects (legends, properties, consistency)

**Decision Criteria**: Choose A if parameters can be made intuitive, B if clear use case boundaries exist, C if verification types are truly independent.

**Parameter Design Philosophy**:
- **A. Minimal required parameters**: Most parameters have sensible defaults, few required
- **B. Explicit everything**: All verification intent must be explicitly stated
- **C. Smart defaults with overrides**: Intelligent defaults that can be overridden when needed

**Decision Criteria**: Choose B to align with explicit parameter specification preference, A only if defaults are obvious, never choose C (violates no-autodetection principle).

**Interface Complexity Management**:
- **A. Separate decorators by complexity**: Basic decorator for simple cases, advanced for complex scenarios
- **B. Progressive disclosure**: Single decorator with optional advanced parameters
- **C. Flat interface**: All options available in single interface

**Decision Criteria**: Choose A if clear complexity boundaries exist, B if advanced features are rarely needed, C if all features are equally important.

## Success Criteria

**Usability Success**:
- Researchers can choose appropriate decorator without reading documentation
- Common verification scenarios require minimal parameter specification
- Parameter names and values are self-explanatory
- No cognitive overhead understanding decorator interactions

**Architectural Success**:
- 2-3 clear decorator patterns with obvious use cases
- Zero parameter redundancy between decorators
- No configuration options for behavior that should be single design decisions
- Clear conceptual model for when to use which decorator

**Functional Success**:
- All current verification capabilities preserved
- Explicit parameter specification maintained
- Manual ground truth specification preserved
- Assert-based failure behavior maintained

## Quality Standards

**Interface Design Principles**:
- Decorator names clearly indicate their purpose and scope
- Parameter names use domain language that researchers understand
- No parameters that require understanding of verification system internals
- Clear distinction between required and optional parameters

**DR Methodology Alignment**:
- Remove ALL comments - interface should be self-documenting
- Use clear, descriptive parameter names that eliminate need for explanation
- No defensive programming in decorator logic - fail fast on invalid parameters
- Eliminate configuration complexity that serves no current purpose

**Code Organization**:
- Group related functionality within each decorator
- Extract common logic to shared functions (already consolidated in other files)
- Use comprehensive type hints for all parameters
- Follow existing dr_plotter patterns discovered during consolidation

**Integration Standards**:
- Clean imports from consolidated `plot_data_extractor.py`
- Efficient use of `unified_verification_engine.py` verification rules
- Consistent output formatting through `verification_formatter.py`

**Reference**: See `docs/processes/tactical_execution_guide.md` for baseline execution philosophy

## Adaptation Guidance

**Discovery Scenarios**:

**If current decorators have significant functional overlap**: Consolidate aggressively. Choose the clearest interface and eliminate alternatives.

**If parameter combinations create complex decision trees**: Simplify by eliminating options. Choose single best approaches rather than providing flexibility.

**If some verification features are rarely used**: Consider removing them entirely if they don't serve the core operational need.

**If decorator logic contains complex branching**: Extract to separate functions or eliminate complexity through better parameter design.

**Interface Design Decisions**:
- If multiple decorators serve similar purposes, combine them into one clear interface
- If parameters have subtle interactions, eliminate the interactions through better design
- If certain verification aspects are always used together, combine them into single decorator
- If some features require extensive configuration, question whether they should exist

**Integration and Migration**:
- Plan migration path for existing verification examples
- Consider providing temporary compatibility layer if needed (but prefer clean break)
- Update any internal examples to use new decorator interface
- Ensure new interface works with all current matplotlib plot types

**Performance and Simplicity**:
- Optimize decorator overhead to minimize impact on research workflow
- Prefer simple parameter validation over complex configuration checking
- Eliminate any verification steps that don't provide clear value to researchers

## Documentation Requirements

**Interface Design Documentation**:
- Document the 2-3 final decorator patterns with clear use case boundaries
- Record design decisions about parameter consolidation and elimination
- Document the conceptual model for choosing between decorators
- Note any verification capabilities that were eliminated and why

**Migration Guide**:
- Provide clear mapping from old decorator usage to new interface
- Document any behavioral changes in verification logic
- Note any parameters that were eliminated and their recommended replacements
- Include examples showing common verification patterns with new interface

**Implementation Decisions**:
- Record which decorators were consolidated and the rationale
- Document parameter design decisions and trade-offs made
- Note any complex logic that was simplified or eliminated
- Capture insights about decorator interface design for future reference

**User Experience Validation**:
- Test new interface with common verification scenarios
- Validate that parameter names and values are intuitive
- Confirm that verification output provides clear, actionable feedback
- Verify that decorator choice is obvious for typical use cases

**Architectural Insights**:
- Document patterns that emerged during consolidation
- Note any opportunities for further simplification discovered
- Record any verification engine features that became unnecessary
- Identify any remaining complexity that could be addressed in future work