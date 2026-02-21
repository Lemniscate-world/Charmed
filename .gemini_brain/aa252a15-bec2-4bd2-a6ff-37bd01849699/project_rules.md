# Dissect - Project Rules & Guidelines

> **Instructions for the AI Agent**
> These rules define how we build Dissect. Follow them strictly to maintain the "Strategic Battle Plan" and product quality.

---

## 1. Core Philosophy

### 🇨🇭 Switzerland Positioning (Neutrality)
- **Rule**: We are framework-agnostic.
- **Implementation**: Never import heavy dependencies (like `langchain`, `crewai`, `autogen`) in core modules.
- **Why**: Dissect must be lightweight. Users shouldn't need to install 5GB of AI frameworks just to visualize a trace.

### 🎨 Beauty is a Feature
- **Rule**: Visualization outputs must be "Boardroom Ready" (beautiful, dark mode, interactive).
- **Implementation**: Use gradients, animations, and clean typography in HTML exports. No "developer art".
- **Why**: Design is our main differentiator against crude developer tools.

### 🚀 Zero-Config Magic
- **Rule**: Things should work without setup.
- **Implementation**: `trace_receiver.py` must auto-detect formats. CLI must have sensible defaults.

---

## 2. Architecture Rules

### The Graph is the Source of Truth
- All data flows through `OrchestrationGraph` (`dissect/graph.py`).
- **Flow**: `Raw Trace (JSON)` → `TraceParser` → `OrchestrationGraph` → `Exporter` → `Visual`.
- Never bypass the Graph to go straight from Trace to Visual.

### Loose Coupling
- **Parsers**: Each framework parser (`CrewAIParser`, `AutoGenParser`) should be independent.
- **Exporters**: Exporters should valid for *any* `OrchestrationGraph`, not specific to a framework.

---

## 3. Coding Standards

### Python
- **Type Hinting**: Mandatory for all function signatures.
- **Docstrings**: Required for all classes and public methods.
- **Testing**: Every new parser needs a matching trace file in `examples/` and a unit test in `tests/`.

### Frontend (HTML Exporter)
- **Single File**: Generated HTML must be self-contained (embedded CSS/JS). No external CDNs if possible (for offline support).
- **Performance**: capable of rendering 1000+ nodes without lag (use Canvas/WebGL if DOM gets too heavy, currently SVG is fine for <500).

---

## 4. Workflows

### When Adding a New Framework
1.  Find a sample trace (or generate one).
2.  Create a subclass of `TraceParser` in `trace_receiver.py`.
3.  Map framework-specific concepts (Agent, Tool, Task) to Dissect `NodeType`.
4.  Add auto-detection logic to `parse_trace_file`.
5.  Add a unit test.

### When Modifying Visualization
1.  Edit `HTML_TEMPLATE` in `dissect/exporters/html.py`.
2.  Regenerate all example workflows (`examples/*.html`).
3.  Verify interactivity (Zoom/Pan/Play).

---

## 5. Forbidden Patterns 🚫
- ❌ Hardcoding framework names in generic visualization logic.
- ❌ Using `print()` for logging (use generic logger or CLI output).
- ❌ Requiring an API key to run basic visualizations.
