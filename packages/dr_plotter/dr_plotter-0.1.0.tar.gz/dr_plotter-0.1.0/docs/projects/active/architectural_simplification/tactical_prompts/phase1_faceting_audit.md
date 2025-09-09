# Tactical Agent Prompt: Phase 1 Faceting System Audit

**Agent Type**: general-purpose  
**Task**: Complete analysis and mapping of current faceting system for architectural replacement  
**Expected Output**: Comprehensive audit report with actionable findings

## Mission Objective

Perform a thorough audit of the current faceting system to identify:
1. **Sophisticated functionality** that provides genuine user value and must be preserved
2. **Broken functionality** that needs to be fixed in the replacement
3. **Over-engineered complexity** that should be eliminated
4. **Integration points** that must work with the new system

## Specific Research Tasks

### Task 1: Map Current Module Structure and Complexity
**Action**: Analyze all files in `src/dr_plotter/faceting/` directory
**Focus**: 
- Read each of the 6 modules completely (`data_analysis.py`, `data_preparation.py`, `grid_computation.py`, `validation.py`, `style_coordination.py`, `types.py`)
- Identify unnecessary abstraction layers vs. genuine functionality
- Document complex validation chains and performance optimizations
- Map dependencies between modules

**Report**: Create detailed breakdown of what each module does and why it's over-engineered

### Task 2: Identify Sophisticated Functionality to Preserve
**Action**: Extract the valuable features that users actually need
**Focus**:
- Multi-variable faceting capabilities (grouping by multiple columns)
- Style coordination across subplots with legend integration
- Advanced targeting (flexible subplot positioning and arrangement)
- Professional visual output quality features

**Report**: Document exactly what sophisticated functionality must work in the replacement system

### Task 3: Document Broken Functionality 
**Action**: Test current faceting system and identify what's broken
**Focus**:
- Run `examples/faceting/simple_grid.py` and document any failures or errors
- Test faceting through `FigureManager.plot_faceted()` method
- Identify specific broken patterns or non-working features
- Document expected vs. actual behavior

**Report**: Comprehensive list of what's currently broken and what working behavior should look like

### Task 4: Map Integration Points and Dependencies
**Action**: Find all places in codebase that use faceting functionality
**Focus**:
- Search for imports from `dr_plotter.faceting` across entire codebase
- Analyze `FigureManager` integration with faceting system
- Examine `FacetingConfig` usage patterns
- Document external API surface that must be preserved

**Report**: Complete map of integration points that must work with new system

### Task 5: Analyze User Interface Patterns
**Action**: Study how users interact with faceting system
**Focus**:
- Examine all files in `examples/faceting/` directory
- Analyze `FacetingConfig` configuration patterns
- Study expected user workflows and mental models
- Identify interface patterns that work vs. those that are confusing

**Report**: User interface analysis showing what works and what should be improved

## Research Guidelines

### Investigation Approach
- **Read all faceting code completely** - don't just scan, understand each module deeply
- **Test actual functionality** - run examples and document what happens
- **Search comprehensively** - find all usage patterns across the codebase
- **Focus on evidence** - document specific broken functionality with error messages
- **Identify root causes** - understand why complexity exists vs. what value it provides

### Documentation Standards
- **Specific examples** - show exact code patterns that are over-engineered
- **Error messages** - include full tracebacks for broken functionality
- **Concrete evidence** - document specific validation chains, performance optimizations, abstractions
- **User perspective** - describe what users expect vs. what they currently get

## Expected Deliverables

### 1. Module Complexity Analysis
**Format**: Detailed breakdown for each of 6 modules
- What the module does vs. what it should do
- Specific over-engineered patterns with examples
- Dependencies and integration complexity
- Lines of code and complexity metrics

### 2. Sophisticated Functionality Inventory
**Format**: Functional requirements document
- Multi-variable faceting capabilities and requirements
- Style coordination features and requirements  
- Advanced targeting features and requirements
- Visual output quality requirements

### 3. Broken Functionality Report
**Format**: Bug report with reproduction steps
- Specific failing examples with full error messages
- Expected behavior vs. actual behavior
- Root cause analysis where possible
- Priority level for fixes

### 4. Integration Dependency Map
**Format**: Technical integration document
- All import usage across codebase
- FigureManager integration points
- FacetingConfig interface requirements
- External API compatibility requirements

### 5. User Interface Analysis
**Format**: UX analysis document
- Current user workflow patterns
- Interface patterns that work well
- Confusing or broken interface patterns
- Recommendations for simplified interfaces

## Success Criteria

**Comprehensive Coverage**: Every aspect of current faceting system analyzed and documented
**Actionable Findings**: Clear identification of what to preserve, fix, and eliminate
**Evidence-Based**: Specific examples and error messages documenting broken functionality
**User-Focused**: Analysis considers actual user needs and workflows
**Implementation-Ready**: Findings provide clear guidance for replacement system design

## Reporting Format

Create a single comprehensive report document that includes all findings organized by:
1. **Executive Summary** - key findings and recommendations
2. **Current State Analysis** - detailed breakdown of existing system
3. **Functionality Assessment** - what works, what's broken, what's over-engineered
4. **Integration Requirements** - what must be preserved for compatibility
5. **Implementation Guidance** - specific recommendations for replacement system

**File Location**: Save report as `docs/projects/active/architectural_simplification/audit_reports/faceting_system_audit_report.md`

---

**Critical Success Factor**: This audit must provide complete understanding of current system to enable confident architectural replacement. Focus on evidence-based analysis that clearly separates valuable functionality from unnecessary complexity.