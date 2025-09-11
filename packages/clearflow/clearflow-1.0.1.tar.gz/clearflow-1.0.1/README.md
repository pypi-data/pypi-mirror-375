# ClearFlow

[![Coverage Status](https://coveralls.io/repos/github/artificial-sapience/clearflow/badge.svg?branch=main)](https://coveralls.io/github/artificial-sapience/clearflow?branch=main)
[![PyPI](https://badge.fury.io/py/clearflow.svg)](https://pypi.org/project/clearflow/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/clearflow?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/clearflow)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt)

Compose type-safe flows for emergent AI. 100% test coverage, zero dependencies.

## Why ClearFlow?

- **100% test coverage** – Every path proven to work
- **Type-safe transformations** – Errors caught at development time, not runtime
- **Immutable state** – No hidden mutations
- **Zero dependencies** – No hidden failure modes
- **Single exit enforcement** – No ambiguous endings
- **AI-Ready Documentation** – llms.txt for optimal coding assistant integration

## Quick Start

```bash
pip install clearflow
```

> **Upgrading from v0.x?** See the [Migration Guide](MIGRATION.md) for breaking changes.

## AI Assistant Integration

ClearFlow provides comprehensive documentation in [llms.txt](https://llmstxt.org/) format for optimal AI assistant support.

### Claude Code Setup

Add ClearFlow documentation to Claude Code with one command:

```bash
claude mcp add-json clearflow-docs '{
    "type":"stdio",
    "command":"uvx",
    "args":["--from", "mcpdoc", "mcpdoc", "--urls", "ClearFlow:https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt"]
}'
```

For IDEs (Cursor, Windsurf), see the [mcpdoc documentation](https://github.com/langchain-ai/mcpdoc#configuration).

### Direct URL Access

Use these URLs directly in any AI tool that supports llms.txt:

- **Minimal index** (~2KB): <https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms.txt>
- **Full documentation** (~63KB): <https://raw.githubusercontent.com/artificial-sapience/clearflow/main/llms-full.txt>

## Examples

| Name | Description |
|------|-------------|
| [Chat](examples/chat/) | Simple conversational flow with OpenAI |
| [Portfolio Analysis](examples/portfolio_analysis/) | Multi-specialist workflow for financial analysis |
| [RAG](examples/rag/) | Full retrieval-augmented generation with vector search |

## Core Concepts

### `Node[TIn, TOut]`

A unit that transforms state from `TIn` to `TOut` (or `Node[T]` when types are the same).

- `prep(state: TIn) -> TIn` – optional pre-work/validation  
- `exec(state: TIn) -> NodeResult[TOut]` – **required**; return new state + outcome  
- `post(result: NodeResult[TOut]) -> NodeResult[TOut]` – optional cleanup/logging  

Nodes are frozen dataclasses that execute async transformations without mutating input state.

### `NodeResult[T]`

Holds the **new state** and an **outcome** string used for routing.

### `flow()`

A function that creates a flow with **explicit routing**:

```python
flow("Name", start_node)
  .route(start_node, "outcome1", next_node)
  .route(next_node, "outcome2", final_node)
  .end(final_node, "done")  # exactly one termination
```

**Routing**: Routes are `(node, outcome)` pairs. Each outcome must have exactly one route.  
**Type inference**: The flow infers types from start to end, supporting transformations.  
**Composability**: A flow is itself a `Node` – compose flows within flows.

## ClearFlow vs PocketFlow

| Aspect | ClearFlow | PocketFlow |
|--------|-----------|------------|
| **State** | Immutable, passed via `NodeResult` | Mutable, passed via `shared` param |
| **Routing** | Outcome-based explicit routes | Action-based graph edges |
| **Termination** | Exactly one exit enforced | Multiple exits allowed |
| **Type safety** | Full Python 3.13+ generics | Dynamic (no annotations) |

ClearFlow emphasizes **robust, type-safe orchestration** with validation and guardrails. PocketFlow emphasizes **brevity and flexibility** with minimal overhead.

## Development

### Install uv

- Please see [official uv docs](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) for other ways to install uv.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone and set up development environment

```bash
git clone https://github.com/artificial-sapience/clearflow.git
cd ClearFlow
uv sync --all-extras     # Creates venv and installs deps automatically
./quality-check.sh       # Run all checks
```

## License

[MIT](LICENSE)

## Acknowledgments

Inspired by [PocketFlow](https://github.com/The-Pocket/PocketFlow)'s Node-Flow-State pattern.
