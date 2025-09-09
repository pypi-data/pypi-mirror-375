# Tactical Prompt: Task 1B - Analyze Current Decorator Usage Patterns

## Strategic Objective
Understand how the verification system is actually used in practice across all examples to ensure the consolidated system supports real usage patterns without breaking existing functionality.

## Problem Context
The verification decorators are used across 25+ example files with various parameter patterns. Understanding these usage patterns is essential for designing a unified interface that serves actual needs rather than theoretical completeness.

## Requirements & Constraints
**Must Analyze**:
- All example files that use verification decorators (found via grep for `@verify_`)
- Parameter specification patterns (`EXPECTED_CHANNELS`, legend counts, etc.)
- Decorator stacking patterns (multiple decorators on same function)
- Output expectations and current debugging workflows

**Key Usage Questions**:
- What verification scenarios are most common vs edge cases?
- How are expected values currently specified and validated?
- Which decorator combinations are actually used together?
- What parameter patterns repeat across multiple examples?

## Decision Frameworks
**Usage Pattern Classification**:
- **Common patterns** (used in 5+ examples) vs **Occasional patterns** (2-4 examples) vs **Rare patterns** (1 example)
- **Simple configurations** vs **Complex configurations** vs **Edge case configurations**
- **Standalone decorator usage** vs **Multi-decorator stacking** vs **Decorator with custom parameters**

**Consolidation Priority**:
- High priority: Patterns used in 80%+ of examples
- Medium priority: Patterns that represent important use cases even if infrequent
- Low priority: One-off configurations that might be simplified away

## Success Criteria
**Usage Pattern Documentation**:
- [ ] All 25+ example files analyzed with verification decorator usage catalogued
- [ ] Parameter specification patterns identified and frequency-ranked
- [ ] Common verification scenarios documented (basic plots, grouped plots, faceted plots, etc.)
- [ ] Decorator stacking patterns and their purposes understood

**Consolidation Design Input**:
- [ ] Clear picture of what the unified interface must support
- [ ] Identification of parameter patterns that can be simplified or standardized
- [ ] Understanding of output format expectations from current examples

## Quality Standards
**Representative Analysis**: Don't just sample - analyze all usage to catch edge cases that matter
**Parameter Detail**: Document exact parameter structures currently used, including complex nested configurations
**Output Context**: Note how verification output is currently used in the debugging workflow

## Adaptation Guidance
**If examples vary widely**: Document the variation patterns - this informs whether we need flexible interfaces or can standardize
**If parameter structures are inconsistent**: Document the inconsistencies clearly - this informs interface cleanup opportunities
**If some decorators seem unused**: Note this but don't assume they can be eliminated without understanding why they exist

## Documentation Requirements
Create detailed usage analysis that will drive unified interface design:
- Example-by-example usage inventory
- Parameter pattern frequency analysis
- Verification scenario categorization
- Interface requirements for unified system
- Recommendations for parameter simplification opportunities