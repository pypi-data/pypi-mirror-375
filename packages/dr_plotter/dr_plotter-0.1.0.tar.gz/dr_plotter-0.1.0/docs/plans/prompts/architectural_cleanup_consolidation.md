# Architectural Cleanup and Consolidation

## Strategic Objective

Execute high-value consolidation improvements identified in fresh eyes architectural review to enhance code consistency and enforce DR methodology principles. These changes will improve policy compliance and type consistency without requiring major refactoring.

## Problem Context

Architectural assessment revealed strong adherence to DR principles with minor stylistic inconsistencies:
- 44 comment/docstring instances violating zero-comments policy across 9 files
- Type definitions scattered across multiple files instead of centralized
- Inconsistent import organization patterns
- Small opportunities for constant extraction

All identified issues are low-risk consolidation opportunities that will enhance consistency while maintaining existing functionality.

## Requirements & Constraints

**Must-haves**:
- Remove ALL comments and docstrings while preserving functionality
- Consolidate type definitions into central `types.py` location
- Maintain existing API interfaces and behavior
- Follow established codebase patterns and conventions
- Ensure all tests continue to pass

**Integration Points**:
- Type imports may need updating across multiple files
- Import reorganization must not break functionality
- Code must remain self-documenting through naming

**What Must Not Break**:
- Public API interfaces
- Existing functionality and behavior
- Test suite execution
- Import dependencies between modules

## Decision Frameworks

**Comments/Docstrings Removal**:
- **Preserve vs Remove**: Remove ALL instances - zero-comments policy is absolute
- **Self-Documentation**: Ensure code clarity through naming when removing explanatory comments
- **Function Headers**: Replace docstrings with clear function names and type hints

**Type Consolidation Strategy**:
- **Centralization vs Distribution**: Centralize all type aliases in `types.py`
- **Import Impact**: Update imports systematically across affected files
- **Type Organization**: Group related types logically within `types.py`

**Import Organization**:
- **Standard Pattern**: Follow existing well-organized files as templates
- **Grouping Strategy**: Standard library → Third party → Local imports with blank lines
- **Alphabetical vs Logical**: Use alphabetical within groups for consistency

**Constant Extraction**:
- **Threshold for Extraction**: Extract values used multiple times or with semantic meaning
- **Location Decision**: Class constants vs module constants vs dedicated constants file
- **Naming Convention**: Follow existing `consts.py` patterns

## Success Criteria

**Policy Compliance**:
- Zero matches for comment search: `grep -r "^\s*#\|^\s*\"\"\"" src/` returns nothing
- All docstrings removed while maintaining code clarity

**Type Consistency**:
- All type aliases consolidated into `types.py`
- No duplicate type definitions across files
- Consistent import patterns for types

**Code Quality**:
- All existing tests pass without modification
- Import organization follows consistent pattern across all files
- No functionality changes or API breaks
- Net code reduction through consolidation

**Validation Checks**:
- `pytest` passes all tests
- Import statements work correctly
- No circular import dependencies introduced
- Code remains self-documenting and clear

## Quality Standards

**Follow Established Patterns**:
- Study existing well-organized files (`figure.py`, `base.py`) for import patterns
- Maintain existing naming conventions and code style
- Use type hints comprehensively as replacement for docstring information

**DR Methodology Adherence**:
- Ensure code remains self-documenting through structure and naming
- Apply "Leave No Trace" principle - clean up completely
- Favor bold, clean solutions over incremental preservation
- Expect net code reduction through consolidation

**Reference**: Follow `docs/processes/tactical_execution_guide.md` for baseline execution philosophy, especially architectural courage principles.

## Adaptation Guidance

**When Encountering Edge Cases**:
- **Complex Comments**: If comment contains crucial logic explanation, extract to descriptively named function
- **Type Dependencies**: If type consolidation creates circular imports, use `TYPE_CHECKING` pattern
- **Import Conflicts**: If reorganization breaks functionality, prioritize working code over perfect organization

**Discovery Process**:
1. Start with comment/docstring removal to understand code clarity needs
2. Identify all type aliases across codebase before consolidating
3. Test import changes incrementally to catch dependency issues early
4. Validate functionality after each major change category

**Escalation Triggers**:
- Type consolidation creates circular import dependencies
- Comment removal reveals truly necessary explanatory content
- Import reorganization breaks functionality in unexpected ways
- Any changes that require modifying public APIs

## Documentation Requirements

**Process Documentation**:
- Document which files had comments/docstrings removed
- List all type aliases moved to `types.py` and their source locations
- Record any import organization patterns discovered
- Note any constants extracted and their new locations

**Validation Evidence**:
- Confirm test suite passes after changes
- Verify comment search returns zero matches
- Document any edge cases encountered and how they were resolved

**Insights for Future Work**:
- Patterns discovered about code organization
- Any architectural insights gained during consolidation
- Recommendations for preventing similar inconsistencies
- Quality improvement suggestions for ongoing development

## File-Specific Guidance

**Priority Files for Comments/Docstrings Removal**:
- `src/dr_plotter/scripting/datadec_utils.py` (function docstrings)
- Plotter files with method-level comments
- Any files with module-level docstrings

**Type Consolidation Sources**:
- `GroupInfo`, `ComponentStyles` from various files
- Scattered type aliases in plotter modules
- Configuration-related types across config files

**Import Organization Targets**:
- Files with inconsistent import grouping
- Modules with mixed standard/third-party/local ordering
- Files missing blank line separation between import groups