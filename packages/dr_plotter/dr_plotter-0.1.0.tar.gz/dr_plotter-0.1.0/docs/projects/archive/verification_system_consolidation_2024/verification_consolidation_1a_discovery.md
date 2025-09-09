# Tactical Prompt: Task 1A - Identify All Verification Logic

## Strategic Objective
Map the complete verification system to understand the full scope of logic that needs consolidation. This discovery phase is critical for designing a clean unified system without losing important functionality.

## Problem Context
The verification decorator system has grown organically with duplicated logic across multiple files. Before consolidating, we need a complete inventory of what exists, what's duplicated, and what's unique to inform the unified design.

## Requirements & Constraints
**Must Document**:
- Every verification function across all three main verification files
- All data extraction functions that support verification
- Complete flow from decorator entry points to final verification logic
- Current parameter patterns and return value structures

**Files to Analyze**:
- `src/dr_plotter/scripting/verif_decorators.py` (635 lines - main decorators)
- `src/dr_plotter/scripting/verification.py` (225 lines - legend visibility logic)  
- `src/dr_plotter/scripting/plot_verification.py` (779 lines - plot property verification)
- `src/dr_plotter/scripting/plot_property_extraction.py` (501 lines - data extraction)

## Decision Frameworks
**Categorization Approach**:
- **Core verification logic** vs **Support utilities** vs **Output formatting**
- **Duplicated implementations** vs **Unique functionality** vs **Similar but different patterns**
- **Essential functionality** vs **Nice-to-have features** vs **Legacy artifacts**

**Documentation Granularity**:
- Function-level mapping for verification logic
- High-level categorization for utilities and formatters
- Interface documentation for decorator entry points

## Success Criteria
**Comprehensive Inventory**:
- [ ] Every verification function identified with purpose and current usage
- [ ] All duplication patterns clearly mapped (e.g., "color consistency checking appears in X, Y, Z functions")
- [ ] Complete decorator flow documented from @decorator through to final output
- [ ] Parameter and return value patterns catalogued for interface design

**Clear Organization**:
- [ ] Verification logic grouped by functionality (legend, plot properties, figure-level, etc.)
- [ ] Dependencies between functions clearly documented
- [ ] Current integration points with matplotlib identified

## Quality Standards
**Documentation Structure**: Create clear tables/lists showing function names, purposes, locations, and relationships
**Evidence-Based**: Document actual function signatures and current usage, not assumptions
**Complete Coverage**: Don't skip utility functions or formatters - they're part of the consolidation scope

## Adaptation Guidance
**If you find unexpected complexity**: Document it clearly but don't try to solve design issues - that's for later phases
**If functions seem identical**: Note the similarity but document any subtle differences you find
**If unclear purpose**: Document what the function does based on code reading, note uncertainty about intent

## Documentation Requirements
Create a comprehensive discovery document that will inform the unified system design:
- Function inventory with categorization
- Duplication analysis with specific examples
- Current data flow documentation
- Interface patterns and inconsistencies observed