# Saturated Activation Detection

The goal is to add explicit detection for saturated activations. This will augment the existing `NeuralDbg` engine to better explain vanishing gradient failures.

## Proposed Changes

### NeuralDbg Engine

#### [MODIFY] [neuraldbg.py](file:///home/kuro/Documents/NeuralDBG/neuraldbg.py)
- Update `_compute_activation_stats` to include a `saturation_ratio`.
- Update `_detect_activation_shift` to consider `saturation_ratio` changes.
- Add a specific method `_explain_saturated_activations` to provide hypotheses.
- Integrate this new explanation into `explain_failure`.

## Verification Plan

### Automated Tests
I will create a new test file `tests/repro_saturation.py` that uses a Tanh-based MLP and initializes it to force saturation (e.g., very large weights), then verifies that `NeuralDbg` detects this.

```bash
python3 tests/repro_saturation.py
```

### Manual Verification
Reviewing the generated Mermaid graph to ensure the "Saturated Activation" events are correctly linked to subsequent "Vanishing Gradient" events.
