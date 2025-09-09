# Process Guides for Multi-Agent Collaboration

This directory contains guides for effective collaboration with different types of AI agents working on this codebase.

## 🎯 Quick Start

**New to this system?** Read this document first, then the specific guide for your intended agent interaction.

**Experienced user?** Jump directly to the appropriate agent guide below.

## 🤖 Agent Roles and Guides

### Strategic Collaborator (`strategic_collaboration_guide.md`)
**When to use**: Complex problems, architectural decisions, project planning, code reviews
**Role**: Strategic thinking partner and conductor who orchestrates multi-agent work
**Strengths**: Analysis, decision frameworks, process design, quality orchestration

### Tactical Executor (`tactical_execution_guide.md`) 
**When to use**: Implementing specific features, writing code, detailed technical work
**Role**: Skilled performer who executes strategic guidance with technical expertise
**Strengths**: Implementation, adaptation, testing, code organization, edge case handling

### Fresh Eyes Reviewer (`fresh_eyes_review_guide.md`)
**When to use**: Periodic architectural health checks, identifying principle drift
**Role**: Independent auditor who evaluates codebase against core principles  
**Strengths**: Objective assessment, pattern recognition, architectural insight

### Documentation Organizer (`documentation_organizer_guide.md`)
**When to use**: Documentation cleanup, knowledge organization, content strategy
**Role**: Knowledge architect who maintains accessible information systems
**Strengths**: Information architecture, content synthesis, lifecycle management

## 📋 How to Use These Guides

### For Agent Interactions

**1. Choose the Right Agent Type**
- Match your need to the agent role descriptions above
- Different agents excel at different types of work

**2. Share the Appropriate Guide**
- Ask the agent to read the relevant guide document first
- This establishes role, expectations, and collaboration patterns

**3. Provide Task Context**
- Share relevant codebase information and background
- Reference any related documents or previous work
- Clarify success criteria and constraints

### For Multi-Agent Workflows

**Strategic → Tactical Pattern** (most common):
1. Strategic Collaborator analyzes problem and creates implementation prompts
2. Tactical Executor implements based on strategic guidance
3. Strategic Collaborator reviews results and synthesizes insights

**Fresh Eyes Assessment**:
1. Fresh Eyes Reviewer evaluates codebase health
2. User and Strategic Collaborator discuss findings
3. Strategic Collaborator creates improvement plans
4. Tactical Executor implements improvements

**Documentation Maintenance**:
1. Documentation Organizer assesses information landscape
2. User collaborates on reorganization strategy  
3. Documentation Organizer executes content migration and synthesis
4. Results enable more effective future agent interactions

## 🧭 Core Philosophy

All agents operate according to the **DR methodology** principles found in `design_philosophy.md`:

- **Clarity Through Structure**: Code and processes should be self-evident
- **Architectural Courage**: Prefer clean solutions over incremental complexity
- **Fail Fast, Surface Problems**: Issues should be immediately apparent
- **Focus on Researcher Workflow**: Minimize friction between idea and implementation

## 🎼 The Conductor Paradigm

**Strategic agents** are **conductors** - they set vision, tempo, and coordination
**Tactical agents** are **performers** - they execute with technical expertise within the strategic framework

This separation allows each agent type to focus on their strengths while maintaining architectural consistency.

## 🔄 Success Patterns

**Effective Collaboration Indicators**:
- Strategic agents provide decision frameworks rather than prescriptive implementations
- Tactical agents adapt creatively within strategic constraints
- Fresh eyes reviews catch architectural drift before it compounds
- Documentation stays organized and accessible as knowledge grows

**Quality Outcomes**:
- Codebase complexity decreases or stays flat as functionality grows
- New team members can understand and contribute quickly
- Architectural principles remain clear and consistently applied
- Knowledge is preserved and accessible across time

## 🚫 Common Pitfalls

**Wrong Agent for the Task**:
- Using tactical agents for strategic planning
- Asking strategic agents for detailed implementation
- Using embedded collaborators when fresh perspective is needed

**Insufficient Context**:
- Not sharing relevant background information
- Skipping the appropriate agent guide
- Unclear success criteria or constraints

**Role Confusion**:
- Strategic agents becoming too prescriptive about implementation details
- Tactical agents not making decisions within their authority
- Fresh eyes reviewers getting caught up in historical context

## 📚 Additional Resources

**Foundation Documents**:
- `design_philosophy.md` - Core methodology and principles
- `../CLAUDE.md` - Project-specific requirements and conventions

**Process Evolution**:
These guides evolve based on what works in practice. If you discover better collaboration patterns or notice gaps, suggest improvements to help refine the system.

---

**Remember**: These agents are tools to help you think and build more effectively. Choose the right tool for the job, provide clear context, and trust each agent type to excel within their area of expertise.