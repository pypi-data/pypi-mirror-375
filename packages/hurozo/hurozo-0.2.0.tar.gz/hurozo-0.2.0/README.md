# Hurozo CLI

Hurozo is a visual agent builder and execution platform. You compose agents as graphs of nodes, connect inputs and outputs, and save them to run via API calls, webhooks, or the UI. The Hurozo CLI helps you:

- Scaffold runnable Python projects for your saved agents
- List available agents in your account
- Run agents programmatically using Python

The CLI is designed for quick prototyping and integration into scripts or services.

## Features

- Scaffold a minimal Python project with `main.py` for selected agents
- Instantiate agents by name or by UUID directly
- Prefill input keys in the scaffolded script (when the agent defines required inputs)
- Lightweight `Agent` class for invoking agents via the Hurozo API

## Installation

Install from PyPI:

```
pip install hurozo
```

This will provide the `hurozo` console command and the `hurozo` Python package.

## Authentication

The CLI and the `Agent` class use a bearer token to access your Hurozo account.

- `HUROZO_API_TOKEN`: required. A user or org API token.

Example:

```
export HUROZO_API_TOKEN=...your token...
```

## Commands

- `hurozo init [dirname]`
  - Interactively select one or more agents from your account
  - Scaffolds a minimal project in `dirname` (creates `requirements.txt` and `main.py`)
  - `main.py` instantiates each selected agent by display name and pre-fills `.input({...})` if inputs are defined
  - When run, `main.py` will execute all selected agents and print their results

- `hurozo list`
  - Lists accessible agents with their display names and UUIDs

- `hurozo help [command]`
  - Shows help for a specific command

## Python API

The packaged Python module also exposes a small API for running agents directly:

```
from hurozo import Agent

# Name-based: resolves display name → UUID at runtime
bruno = Agent("Bruno")
bruno.input({"naam": "De Hengst"})
print(bruno.run())

# UUID-based: skip resolution and use UUID directly
bruno = Agent("2375125b-1455-40fa-8458-d319cdef9b32d", True)
print(by_id.run())
```

Both styles call the Hurozo backend execute endpoint under the hood. Name-based resolution fetches your agent list and prefers exact (case-sensitive) name matches, falling back to case-insensitive.

## Scaffolded Project Layout

When you run `hurozo init my-agent`, the CLI generates:

- `requirements.txt` – dependencies: `hurozo`, `python-dotenv`, `requests`
- `main.py` – a runnable script that:
  - imports `Agent` from `hurozo`
  - defines one variable per selected agent using its display name
  - fills in `.input({...})` from the agent’s defined input keys (if available)
  - calls `.run()` for each agent and prints the results
- `.env` (optional) – if not present, a template is created with a `HUROZO_API_TOKEN` placeholder

Run it with:

```
cd my-agent
pip install -r requirements.txt
export HUROZO_API_TOKEN=...your token... (or set it in .env)
python main.py
```

## Environment Variables

- `HUROZO_API_TOKEN` – required for both listing agents and executing them
- `NO_COLOR` – if set, disables colored output in the CLI

## Designing agents
- Go to https://app.hurozo.com/ to design your agents visually. Save your agent, create an API token, and scaffold a project with `hurozo init`.

## Troubleshooting

- Missing token: ensure `HUROZO_API_TOKEN` is set in your shell or `.env`
- Name resolution fails: the CLI falls back to using the provided string; switch to UUID-based invocation by passing `True` as the second `Agent` argument
- Inputs missing at runtime: open the agent in the Hurozo UI and ensure inputs are defined; re-run `hurozo init` to regenerate a script with updated keys

