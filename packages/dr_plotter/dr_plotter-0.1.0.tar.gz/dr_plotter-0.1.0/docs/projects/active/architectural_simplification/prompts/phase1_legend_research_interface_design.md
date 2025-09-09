# Phase 1: Legend System Research & Interface Design

## Strategic Objective

Research the current legend system implementation to identify all hardcoded positioning calculations and design a clean two-tier interface that makes GROUPED_BY_CHANNEL functionality discoverable while preserving all power features.

## Problem Context

The legend system has valuable sophisticated functionality but suffers from interface complexity and hardcoded positioning calculations. We need to understand the current implementation deeply before designing the simplified interface.

## Requirements & Constraints

**Must Research**:
- All hardcoded positioning calculations and magic numbers in legend system
- Current LegendConfig parameters and their usage patterns
- GROUPED_BY_CHANNEL implementation and its dependencies
- Integration points with FigureManager and visual encoding system

**Must Design**:
- Two-tier interface (simple strings → LegendConfig for power users)
- Three-tier positioning approach (matplotlib defaults → layout hints → manual coordinates)
- Clear mapping from current functionality to new interface

**Cannot Break**:
- Any existing functionality - this is pure research and design
- Current examples - new interface must support all current use cases

## Decision Frameworks

**Research Depth vs Speed**:
- Focus on positioning calculations and interface complexity
- Document patterns rather than every implementation detail
- Prioritize understanding user-facing complexity over internal implementation

**Interface Design Approach**:
- Simple string interface for common cases: `legend="grouped"`, `legend="subplot"`, `legend="figure"`  
- LegendConfig preservation for all current power features
- Clear upgrade path from simple to advanced usage

## Success Criteria

**Research Completeness**:
- All hardcoded positioning calculations identified with line numbers
- Current LegendConfig parameters catalogued with usage examples
- GROUPED_BY_CHANNEL functionality fully understood
- Integration complexity with other systems documented

**Interface Design Quality**:
- Two-tier interface design with clear examples
- All current functionality mapped to new interface
- Simple cases require minimal configuration
- Power features remain fully accessible

**Strategic Value**:
- Clear recommendation on positioning simplification approach
- Interface that makes GROUPED functionality discoverable
- Implementation roadmap for Phase 2

## Quality Standards

**Reference**: Follow `docs/processes/design_philosophy.md` principles

**Research Standards**:
- Focus on user-facing complexity, not implementation perfection
- Document patterns and pain points, not every code detail
- Identify architectural courage opportunities

**Design Standards**:
- Progressive disclosure from simple to advanced
- Preserve all current capabilities
- Make power features discoverable

## Adaptation Guidance

**If Current System is More Complex Than Expected**:
- Focus on the most problematic hardcoded calculations first
- Document complexity patterns rather than cataloguing every detail
- Recommend incremental simplification if wholesale replacement seems risky

**If Interface Design Reveals Conflicts**:
- Prioritize GROUPED_BY_CHANNEL discoverability
- Preserve manual positioning control as non-negotiable
- Simplify common cases even if some edge cases become more verbose

**If Integration Points are Extensive**:
- Design interface changes to minimize integration disruption  
- Document integration requirements for Phase 2
- Consider backward compatibility during transition

## Documentation Requirements

**Research Output**:
- List of all hardcoded positioning calculations with file:line references
- Current LegendConfig parameter inventory with usage examples
- GROUPED_BY_CHANNEL functionality documentation
- Integration complexity assessment

**Design Output**:
- Complete two-tier interface specification with examples
- Three-tier positioning approach design
- Migration strategy from current to new interface
- Implementation recommendations for Phase 2

**Strategic Insights**:
- Key simplification opportunities identified
- User experience improvements prioritized
- Technical risks and mitigation strategies