# Walkthrough: Dissect 2.0 - Orchestration Visualizer

Successfully pivoted Dissect from algorithm detection to an **AI Agent Orchestration Visualizer**.
- **`dissect explain`**: Automated LLM-based trace analysis for bottleneck detection and optimization.
- **🌡️ Latency Heatmaps**: Visual bottleneck detection in interactive HTML.

## What Changed

### Phase 3: Feature Expansion (Ongoing)
#### 🌡️ Latency Heatmaps
- **Backend**: Added execution time normalization and `heat_score` calculation.
- **UI**: Added interactive toggle in HTML exporter for bottleneck detection.
- **Logic**: Dynamic HSL color scaling (Green to Red).

### Phase 2: Open-Source Launch (Completed)

### Archived (Moved to Algoritmi)
- `dissect/detectors/` → `archive/`
- `dissect/scanner.py` → `archive/`
- `dissect/ast_normalizer.py` → `archive/`

### New Core Modules
| File | Purpose |
|---|---|
| [graph.py](file:///home/kuro/Documents/Dissect/dissect/graph.py) | OrchestrationGraph data structure with nodes, edges, critical path |
| [explain.py](file:///home/kuro/Documents/Dissect/dissect/explain.py) | AI-powered trace analysis (OpenAI/Ollama) |
| [trace_receiver.py](file:///home/kuro/Documents/Dissect/dissect/trace_receiver.py) | OpenTelemetry & LangChain trace parsers |
| [exporters/](file:///home/kuro/Documents/Dissect/dissect/exporters/) | Mermaid, DOT, HTML export formats |
| [cli.py](file:///home/kuro/Documents/Dissect/dissect/cli.py) | New `trace`, `visualize`, `serve` commands |

## New CLI Usage

```bash
# Parse and inspect a trace
python3 -m dissect.cli trace --file trace.json

# Generate interactive HTML
python3 -m dissect.cli visualize --file trace.json --format html

# Generate Mermaid diagram
python3 -m dissect.cli visualize --file trace.json --format mermaid

# AI-Powered Analysis (NEW)
export OPENAI_API_KEY="sk-..."
python3 -m dissect.cli explain --file trace.json --provider openai
```

## Verification Results

```
✓ Parsed successfully!
  Name: Trace
  Nodes: 7
  Edges: 6

  Critical Path (750ms):
    → User Query (50ms)
    → Writer Agent (400ms)
    → Claude Call (300ms)

## Phase 3 Verification (Heatmaps)
- **Score Calculation**: 0.0 (Fastest) to 1.0 (Slowest) verified via `test_graph.py`.
- **UI Interaction**: Gradient rendering (HSL 120 -> 0) verified in `visualize`.
```

## Generated Visualization

![Interactive Demo](/home/kuro/.gemini/antigravity/brain/aa252a15-bec2-4bd2-a6ff-37bd01849699/dissect_v2_demo_1770657475382.png)

### Demo Recording
[Watch the interaction demo](file:///home/kuro/.gemini/antigravity/brain/aa252a15-bec2-4bd2-a6ff-37bd01849699/dissect_v2_demo_1770657437837.webp)

## Heatmap Demonstration
The following recording shows the interactive Heatmap toggle and the automatic bottleneck detection (Red nodes = high latency).

![Latency Heatmap Interaction Demo](/home/kuro/.gemini/antigravity/brain/aa252a15-bec2-4bd2-a6ff-37bd01849699/latency_heatmap_demo_1770660170572.webp)

## Next Steps
1. Install dependencies: `pip install -e .`
2. Test with real LangChain/CrewAI traces
3. Build real-time streaming server
