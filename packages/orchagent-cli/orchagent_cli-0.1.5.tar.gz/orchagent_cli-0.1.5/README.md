# orchagent-cli

CLI for the Orchagent API, built on the `orchagent` Python SDK.

## Dev Install

```bash
# 1) Install SDK first (from the sibling repo)
cd /home/admin/Downloads/git/orchagent-python
python -m venv .venv && source .venv/bin/activate
pip install -U pip wheel
pip install -e .

# 2) Install CLI
cd /home/admin/Downloads/git/orchagent-cli
pip install -e .

# 3) Use
orch --help
```

## Examples

```bash
# Configure base URL via env (or pass --base-url to each command)
export ORCHAGENT_BASE_URL=http://localhost:8080

# Auth
orch auth register --email you@example.com --password pass123
orch auth login --email you@example.com --password pass123

# Create thread from a workflow JSON
THREAD=$(orch threads create --spec ../Orchagent/example_workflows/composio_calendar_hil_chat.json -q)
echo "Thread: $THREAD"

# Send a message and stream events
RUN=$(orch runs send $THREAD --prompt "Hi" --secrets-file secrets.json -q)
orch runs stream $RUN

# Interactive chat
orch chat start --spec ../Orchagent/example_workflows/composio_calendar_hil_chat.json
```

## Install

Recommended (isolated):

```bash
pipx install orchagent-cli
orch --help
```

Or with pip (in a venv):

```bash
python -m venv .venv && source .venv/bin/activate
pip install orchagent-cli
orch --help
```

## Secrets and Inputs Files

- `--secrets-file secrets.json`: Pass provider credentials and other secrets at run-time. The CLI wraps this under body.secrets automatically.
- `--inputs-file inputs.json`: Pass non-secret inputs (e.g., `user_id`, `event` payloads).

Secrets precedence on the server: run > thread > workflow > environment.

Common `secrets.json` examples:

- OpenAI:
```json
{"providers": {"openai": {"api_key": "sk-..."}}}
```

- OpenAI-compatible (custom base_url):
```json
{"providers": {"openai": {"api_key": "sk-...", "base_url": "https://compatible.example/api"}}}
```

- Anthropic:
```json
{"providers": {"anthropic": {"api_key": "sk-ant-..."}}}
```

- Gemini (Google GenAI):
```json
{"providers": {"google_genai": {"api_key": "AIza..."}}}
```

- Ollama (local):
```json
{"providers": {"ollama": {"base_url": "http://localhost:11434"}}}
```

- Tavily key:
```json
{"TAVILY_API_KEY": "tvly-...", "providers": {"openai": {"api_key": "sk-..."}}}
```

Security: do not commit `secrets.json`; consider `chmod 600 secrets.json`.

Generate a provider template to a file:

```bash
orch templates secrets openai -o secrets.json
# overwrite if exists
orch templates secrets openai -o secrets.json --force
```

Inspect API capabilities and deprecations:

```bash
orch meta
```

## Commands Summary

- `orch auth register --email ... --password ...`
- `orch auth login --email ... --password ...`
- `orch auth whoami | logout`
- `orch threads create --spec path.json [-q]`
- `orch threads secrets <thread_id> --secrets-file file.json`
- `orch threads history <thread_id> [--limit 20]`
- `orch runs send <thread_id> --prompt "..." [--inputs-file file.json] [--secrets-file file.json] [-q]`
- `orch runs stream <run_id>`
- `orch runs resume <run_id>`
- `orch approvals approve <run_id> --tool NAME [--args-keys k1,k2]`
- `orch approvals clear [--all] [--user EMAIL]`
- `orch chat start [--spec path.json | --thread-id th_x]`
