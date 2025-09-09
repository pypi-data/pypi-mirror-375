from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table

from orchagent import OrchClient
import json as _json


app = typer.Typer(help="Orchagent CLI")
auth_app = typer.Typer(help="Auth commands")
threads_app = typer.Typer(help="Thread commands")
runs_app = typer.Typer(help="Run commands")
approvals_app = typer.Typer(help="Approvals commands")
chat_app = typer.Typer(help="Interactive chat")

config_app = typer.Typer(help="Configure defaults")
app.add_typer(auth_app, name="auth")
app.add_typer(threads_app, name="threads")
app.add_typer(runs_app, name="runs")
app.add_typer(approvals_app, name="approvals")
app.add_typer(chat_app, name="chat")
templates_app = typer.Typer(help="Templates and helpers")
app.add_typer(templates_app, name="templates")
app.add_typer(config_app, name="config")


def _load_config() -> dict:
    cfg_path = Path.home() / ".orchcli" / "config.json"
    if cfg_path.exists():
        try:
            return _json.loads(cfg_path.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def _client(base_url: Optional[str]) -> OrchClient:
    if base_url:
        return OrchClient(base_url=base_url)
    # Fallback to env or config file
    cfg = _load_config()
    return OrchClient(base_url=cfg.get("base_url"))


def _load_json(path: Optional[str]) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


@auth_app.command()
def register(email: str = typer.Option(...), password: str = typer.Option(..., prompt=True, hide_input=True), base_url: Optional[str] = None):
    c = _client(base_url)
    token = c.auth.register(email=email, password=password, save=True)
    print(f"[green]Registered[/green]. Token saved. ({token[:8]}...)")


@auth_app.command()
def login(email: str = typer.Option(...), password: str = typer.Option(..., prompt=True, hide_input=True), base_url: Optional[str] = None):
    c = _client(base_url)
    token = c.auth.login(email=email, password=password, save=True)
    print(f"[green]Logged in[/green]. Token saved. ({token[:8]}...)")


@auth_app.command()
def whoami(base_url: Optional[str] = None):
    c = _client(base_url)
    tok = c.auth.get_token()
    if tok:
        print(f"Token present ({tok[:12]}...)")
    else:
        print("[yellow]No token found.[/yellow]")


@auth_app.command()
def logout(base_url: Optional[str] = None):
    c = _client(base_url)
    # Clear token by writing empty
    c.auth.set_token("", save=True)
    print("[green]Logged out[/green].")


@config_app.command("init")
def config_init(base_url: str = typer.Option(..., help="Default API base URL")):
    cfg_dir = Path.home() / ".orchcli"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / "config.json"
    cfg = {"base_url": base_url}
    cfg_path.write_text(_json.dumps(cfg, indent=2), encoding='utf-8')
    try:
        cfg_path.chmod(0o600)
    except Exception:
        pass
    print(f"[green]Config saved[/green] at {cfg_path}")


@threads_app.command()
def create(spec: str = typer.Option(..., help="Workflow JSON path"), base_url: Optional[str] = None, q: bool = typer.Option(False, "-q", help="quiet id-only")):
    c = _client(base_url)
    tid = c.threads.create_from_file(spec)
    if q:
        print(tid)
        return
    print(f"[green]Thread created:[/green] {tid}")


@threads_app.command("secrets")
def set_secrets(thread_id: str, secrets_file: str = typer.Option(..., help="JSON file with secrets"), base_url: Optional[str] = None):
    c = _client(base_url)
    secrets = _load_json(secrets_file)
    c.threads.set_secrets(thread_id, secrets)
    print("[green]Thread secrets updated.[/green]")


@threads_app.command("history")
def history(thread_id: str, limit: int = 20, base_url: Optional[str] = None):
    c = _client(base_url)
    table = Table("role", "content", "created_at")
    for it in c.threads.history(thread_id, limit=limit):
        content = it.content[:80] + ("..." if len(it.content) > 80 else "")
        table.add_row(it.role, content, it.created_at)
    print(table)


@runs_app.command("send")
def send(thread_id: str, prompt: str = typer.Option(..., "--prompt"), inputs_file: Optional[str] = None, secrets_file: Optional[str] = None, base_url: Optional[str] = None, q: bool = typer.Option(False, "-q")):
    c = _client(base_url)
    inputs = _load_json(inputs_file)
    secrets = _load_json(secrets_file)
    run = c.runs.send_message(thread_id, user_prompt=prompt, inputs=inputs or None, secrets=secrets or None)
    if q:
        print(run["run_id"])
        return
    print(f"[green]Run started:[/green] {run['run_id']}")


@runs_app.command("stream")
def stream(run_id: str, base_url: Optional[str] = None):
    c = _client(base_url)
    try:
        for evt in c.runs.stream_events(run_id):
            msg = evt.get("message") or evt.get("type")
            print(f"{evt.get('type')} - {msg}")
            if evt.get("type") in ("run.completed", "error"):
                break
    except KeyboardInterrupt:
        pass


@app.command("meta")
def meta(base_url: Optional[str] = None):
    """Fetch and display API capabilities; warn on deprecations."""
    c = _client(base_url)
    try:
        info = c.get_meta()
    except Exception as e:
        print(f"[red]Failed to fetch /meta:[/red] {e}")
        raise typer.Exit(code=1)

    # Print deprecation warnings, if any
    depr = (info or {}).get("deprecations") or []
    if depr:
        print("[yellow]Deprecations detected:[/yellow]")
        for d in depr:
            # Each item can be a string or dict with fields
            if isinstance(d, str):
                print(f"[yellow]- {d}[/yellow]")
                continue
            name = d.get("name") or d.get("feature") or "unknown"
            msg = d.get("message") or ""
            until = d.get("sunset") or d.get("sunset_date")
            extra = f" (sunsets: {until})" if until else ""
            print(f"[yellow]- {name}: {msg}{extra}[/yellow]")

    print(_json.dumps(info, indent=2))


@runs_app.command("resume")
def resume(run_id: str, base_url: Optional[str] = None):
    c = _client(base_url)
    res = c.runs.resume(run_id)
    print(res)


@approvals_app.command("approve")
def approve(run_id: str, tool: str = typer.Option(...), args_keys: Optional[str] = typer.Option(None, help="comma-separated"), base_url: Optional[str] = None):
    c = _client(base_url)
    keys = [k.strip() for k in args_keys.split(",")] if args_keys else []
    res = c.approvals.approve(run_id, tool=tool, args_keys=keys)
    print(res)


@approvals_app.command("clear")
def clear(all: bool = False, user: Optional[str] = None, base_url: Optional[str] = None):
    c = _client(base_url)
    res = c.approvals.clear(all=all, user_id=user)
    print(res)


@chat_app.command("start")
def chat_start(spec: Optional[str] = typer.Option(None, help="Workflow JSON path to create a thread"), thread_id: Optional[str] = None, base_url: Optional[str] = None):
    c = _client(base_url)
    if not (spec or thread_id):
        raise typer.BadParameter("Provide either --spec or --thread-id")
    if not thread_id:
        thread_id = c.threads.create_from_file(spec)
        print(f"[green]Thread created:[/green] {thread_id}")
    while True:
        try:
            prompt = input("You: ").strip()
        except KeyboardInterrupt:
            print()
            break
        if not prompt or prompt.lower() in {"exit", "quit"}:
            break
        run = c.runs.send_message(thread_id, user_prompt=prompt)
        run_id = run["run_id"]
        for evt in c.runs.stream_events(run_id):
            msg = evt.get("message") or evt.get("type")
            print(f"{evt.get('type')} - {msg}")
            if evt.get("type") == "auth.required":
                det = evt.get("details", {})
                url = det.get("redirect_url")
                if url:
                    print(f"Please authenticate at: {url}")
                input("Press Enter to resume...")
                c.runs.resume(run_id)
            if evt.get("type") in ("run.completed", "error"):
                break


@templates_app.command("secrets")
def secrets(
    provider: str = typer.Argument(..., help="openai|openai_compatible|anthropic|gemini|ollama|tavily"),
    out: Optional[str] = typer.Option(None, "--out", "-o", help="Write to file path instead of stdout"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file if present"),
):
    """Emit a secrets.json template for the given provider.

    If --out is provided, writes the JSON to that path (600 perms).
    Otherwise, prints to stdout.
    """
    import sys
    here = Path(__file__).parent.parent.parent
    path = here / 'templates' / 'secrets' / f'{provider}.json'
    if not path.exists():
        print(f"[red]Unknown provider template: {provider}[/red]")
        raise typer.Exit(code=1)
    content = path.read_text(encoding='utf-8')
    if not out:
        sys.stdout.write(content)
        return
    out_path = Path(out)
    if out_path.exists() and not force:
        print(f"[red]Refusing to overwrite existing file:[/red] {out_path}. Use --force to overwrite.")
        raise typer.Exit(code=2)
    out_path.write_text(content, encoding='utf-8')
    try:
        out_path.chmod(0o600)
    except Exception:
        pass
    print(f"[green]Wrote template to[/green] {out_path}")
