# Chirality Framework: A Semantic Calculator

[![PyPI](https://img.shields.io/pypi/v/chirality-framework.svg)](https://pypi.org/project/chirality-framework/)
[![Python versions](https://img.shields.io/pypi/pyversions/chirality-framework.svg)](https://pypi.org/project/chirality-framework/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Publish](https://github.com/sgttomas/chirality-framework/actions/workflows/python-publish.yml/badge.svg)](https://github.com/sgttomas/chirality-framework/actions/workflows/python-publish.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/tag/sgttomas/chirality-framework?sort=semver&label=release)](https://github.com/sgttomas/chirality-framework/tags)

**Version: 19.3.0** | **Status: DDD-Compliant Architecture**

The Chirality Framework is a meta-ontological, system-agnostic methodology for mapping the solution space to a problem statement in the context of knowledge work. It creates structured semantic relationships that serve as "semantic anchors" to guide LLMs through problem-solving stages across a "semantic valley."

The framework employs two distinct phases with fundamentally different prompting strategies:
- **Phase 1** (Matrices A-E): Uses conversational prompting to build semantic understanding
- **Phase 2** (Tensors M-N): Uses Phase 1 implementation as system prompt for modular cell-by-cell construction

## Core Architecture: Two‑Phase Semantic Computation

### Phase 1: Conversational Semantic Pipeline (Matrices A-E)
Phase 1 uses a conversational dialogue history as the system prompt to create semantic understanding. The dialogue builds the concept of semantic multiplication through examples, develops key concepts organically, and establishes modal ontologies through iterative refinement. This creates a "semantic state" in the LLM that enables proper interpretation.

Semantic‑first transcript with out‑of‑band normalization:
1. **Stage A — Mechanical/Interpreted (Markdown):** Prompts produce human‑readable, markdown‑formatted matrices; the transcript stays clean and creative.
2. **Stage B — Normalization (Strict JSON):** A reusable normalizer prompt converts Stage‑A text into schema‑accurate JSON. Local validation + one diff‑driven retry ensures strict compliance. A small deterministic parser skips the LLM when markdown tables match canonical shapes.

### Phase 2: Modular Tensor Construction (Tensors M-N)
Phase 2 uses the complete Phase 1 implementation (through Matrix E) as the system prompt, then constructs tensors cell-by-cell WITHOUT rolling context. The modular design of the tensors facilitates this approach, with each cell computed independently using semantic cross products to create hierarchical structures.

For a complete technical description, see the **[Canonical Algorithm Documentation](docs/ALGORITHM.md)**.

## The Ontological Modality Path

The sequence of stations in the semantic valley is not arbitrary; it follows a deep, underlying pattern of cognitive modalities. This path describes the *type* of work being done at each stage, revealing a structured cycle of systematic processing, epistemic (knowledge-based) evaluation, and alethic (truth-based) assessment.

| Modality | Station | Operation |
| :--- | :--- | :--- |
| `Problem` | 1. Problem Statement | `[A], [B]` |
| `Systematic` | 2. Requirements | `[C] = [A] · [B]` |
| `Process` | 3. Objectives | `[D] = [A] + [F]` |
| `Epistemic` | 4. Verification | `[K] = [D]^T, [X] = [K] · [J]` |
| `Epistemic` | 5. Validation | `[Z] = shift([X])` |
| `Process` | 6. Evaluation | `[G], [P], [T], [E] = [G] · [T]` |
| `Alethic` | 7. Assessment | `[M] = [R] × [E]` |
| `Epistemic` | 8. Implementation | `[W] = [M] × [X]` |
| `Alethic` | 9. Reflection | `[U] = [W] × [P]` |
| `Alethic` | 10. Resolution | `[N] = [U] × [H]` |

**Clarifications:**
- **X/Z Modality:** Both Verification (S4) and Validation (S5) are `Epistemic`. S4 strictly precedes S5.
- **E Modality:** Evaluation (S6) is a `Process` modality, not Epistemic.

For a detailed explanation of this conceptual architecture, see the **[Project Philosophy Documentation](docs/PHILOSOPHY.md)**.

## Quick Start

The recommended way to use the framework is to compute the entire Phase 1 pipeline and view the results.

### Prerequisites
- Python 3.9+
- An OpenAI API key set as the `OPENAI_API_KEY` environment variable in a `.env` file in the project root.

### Step 1: Install and Set Up

```bash
# Install with all dependencies
pip install -e ".[dev,openai]"

# Ensure the lens catalog is generated (only needs to be done once)
python3 -m chirality.interfaces.cli lenses ensure
```

### Step 2: Run Phase‑1 (semantic‑first) and extract structured JSON

Recommended end‑to‑end (semantic transcript + strict JSON):

```bash
# Use a stronger model if desired
export CHIRALITY_MODEL=gpt-5
export CHIRALITY_TEMPERATURE=1.0

# Run Phase‑1 in relaxed (markdown) mode and extract strict JSON
python -m chirality.interfaces.cli \
  phase1-dialogue-run \
  --lens-mode auto \
  --relaxed-json \
  --extract-structured \
  --reasoning-effort low \
  --out runs/latest_run

# Artifacts
# - runs/latest_run/phase1_dialogue.jsonl                (clean transcript)
# - runs/latest_run/phase1_relaxed_output.json           (Stage‑A content)
# - runs/latest_run/phase1_structured.json               (JSON + validation report)
# - runs/latest_run/phase1_structured_matrices.json      (matrices‑only for DB ingest)
```

Stage‑A only through Matrix C (quick test):

```bash
python -m chirality.interfaces.cli \
  phase1-dialogue-run \
  --lens-mode auto \
  --relaxed-json \
  --stop-at C_interpreted \
  --extract-structured \
  --out runs/c_stageA
```

Run extraction later (CI/CD):

```bash
python -m chirality.interfaces.cli \
  phase1-extract \
  --from runs/latest_run/phase1_relaxed_output.json \
  --out  runs/latest_run/phase1_structured.json \
  --matrices-only  # optional: write only matrices
```

Print matrices (quick view):

```bash
python - <<'PY'
import json, pathlib
p = pathlib.Path('runs/latest_run/phase1_structured_matrices.json')
data = json.loads(p.read_text())
for m in ['C','F','D','K','X','Z','G','T','E']:
  if m in data['matrices']:
    print(f'== Matrix {m} ==')
    for k,v in data['matrices'][m].items():
      if isinstance(v, dict) and 'elements' in v:
        print(f'[{k}]')
        for row in v['elements']:
          print(' | '.join(map(str,row)))
        print()
PY
```


## Development

To set up the development environment and run tests, please refer to the instructions in `CONTRIBUTING.md`.

**Key Development Notes:**
- **DDD Architecture**: Clean separation of domain/application/infrastructure/interfaces layers
- **Prompt Assets**: Located in `chirality/infrastructure/prompts/assets/` following DDD principles
- **Single CLI Entry Point**: Use `chirality` command (via `chirality.interfaces.cli:main`)
- **Output Channels**: Logs go to stderr, data goes to stdout (for CI/CD integration)
- **Guard Scripts**: Run before commits to prevent legacy code drift
- **Structured outputs & transport**: Adapter uses typed input parts; Stage‑B enforces JSON via `json_object` and validates locally (plus one retry). For reasoning models (e.g., GPT‑5), unsupported sampling params (like `top_p`) are omitted automatically.

Additional docs:
- `docs/INTERFACE.md`: Producer mirror of the chirality-app contract (app mode).
- `GEMINI.md`: Guidance for using Gemini/AI assistants with this repo.
 - `CLAUDE.md`: Guidance for using Claude Code with this repo.
 - `AGENTS.md`: Notes for agentic coding assistants working on this project.
repo.
 - `CLAUDE.md`: Guidance for using Claude Code with this repo.
 - `AGENTS.md`: Notes for agentic coding assistants working on this project.
