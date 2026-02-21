# Next-Gen UI & Automated UI Testing Plan

This plan outlines the overhaul of Dissect's UI/UX to a "Next-Gen" standard and the implementation of an automated UI testing framework to ensure future quality.

## Proposed Changes

### [Component] UI/UX Overhaul: "Next-Gen" Creative Design [COMPLETED]
- Integrated Obsidian Glassmorphism and Mesh Gradients.
- Added dynamic Data-Flow Pulses and Tactile Interaction.
- Upgraded `html.py` template with advanced CSS/JS.

### [Component] UI Testing Framework [NEW]
To ensure the new rule **"Always Have Full UI Tests Ensured"** is followed, I will implement an automated verification suite.

#### [NEW] [test_ui.py](file:///home/kuro/Documents/Dissect/tests/test_ui.py)
A playwright-compatible (or `browser_subagent` based) test script that:
- Generates a variety of trace visualizations.
- Opens them in a headless browser.
- Verifies title substitution and data injection.
- Simulates clicks on "Start Trace" and verifies progress updates.
- Checks sidebar population on node clicks.

## Verification Plan

### Automated Tests
- `pytest tests/test_ui.py`: Full UI verification suite.
- `dissect/exporters/html.py` unit tests for template structure.

### Manual Verification
- Re-run `examples/crewai_nextgen.html` generation and visual review.
