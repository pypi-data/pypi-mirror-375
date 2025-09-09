# Design Philosophy

## Core Mission: Empowering Researchers to Visualize Data with Ease

The library's primary purpose is to accelerate the research process by making it easy to create a wide range of publication-quality plots. The focus should always be on the user's end goal: understanding their data.

## Guiding Principles

*   **Intuitive and Consistent API:** The library should have a "learn once, use everywhere" design. The API should be predictable, well-documented, and free of surprising behavior.
*   **Flexibility and Extensibility:** Researchers should be able to create any plot they need, from simple scatter plots to complex, multi-faceted figures. The library should be designed to be easily extended with custom plotters and styles.
*   **Sensible Defaults, Powerful Customization:** Plots should look great out of the box with minimal configuration. However, every aspect of a plot should be easily customizable for those who need more control.
*   **Robust and Developer-Friendly:** The library should be well-tested, provide clear error messages, and have a clean, maintainable codebase that is easy for new contributors to understand.

## How We Achieve Our Goals: The "DR" Method

To ensure the library lives up to its principles, we adhere to a specific development methodology:

1.  **Clarity Through Structure:**
    *   **Conceptual Mapping:** The codebase should be a direct reflection of our conceptual model. Classes, files, and directories should have clear, descriptive names that make the structure of the library immediately obvious.
    *   **Atomicity:** Every component (function, class, file) should have a single, well-defined purpose. This makes the code easier to understand, test, and refactor.

2.  **Succinct and Self-Documenting Code:**
    *   **No Duplication:** Code duplication signals the need for better abstraction. 
    *   **Minimalism:** Favor concise, self-explanatory code over extensive documentation.

3.  **Architectural Courage Over Incremental Safety:**
    *   **Bold, Clean Solutions:** Prefer complete replacement over incremental additions that increase complexity.
    *   **Ruthless Legacy Elimination:** When improving functionality, completely remove what you replace rather than supporting multiple approaches.

4.  **Fail Fast, Surface Problems:**
    *   **Immediate Error Detection:** Problems should surface immediately rather than being hidden by defensive programming.
    *   **No Silent Failures:** Avoid compatibility layers and graceful degradation that mask underlying issues.

5.  **Focus on the Researcher's Workflow:**
    *   **Minimize Friction:** Every design choice should aim to reduce the friction between a researcher's idea and its visualization. If a feature is hard to use or explain, it's a candidate for simplification.
    *   **Clarity Over Cleverness:** We always prefer code that is simple and easy to understand over code that is "clever" but opaque. The goal is to make the library a tool that *disappears* into the background, allowing the researcher to focus on their work.

## Target Audience

Research engineers and scientists who value a high-level, declarative plotting library that doesn't sacrifice the power and flexibility of the underlying `matplotlib` backend.

## Implementation Guidance

This document establishes the foundational methodology and product vision. For operational guidance on applying these principles:

- **Strategic work**: See `docs/processes/strategic_collaboration_guide.md`
- **Tactical implementation**: See `docs/processes/tactical_execution_guide.md`

These guides provide role-specific applications of the DR methodology for effective multi-agent collaboration.