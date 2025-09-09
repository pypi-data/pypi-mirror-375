from typer.testing import CliRunner
from orchcli.main import app
import json


runner = CliRunner()


def test_templates_secrets_write_to_file(tmp_path):
    out = tmp_path / "secrets.json"
    r = runner.invoke(app, ["templates", "secrets", "openai", "-o", str(out)])
    assert r.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "providers" in data and "openai" in data["providers"]
    assert "api_key" in data["providers"]["openai"]


def test_templates_secrets_refuse_overwrite(tmp_path):
    out = tmp_path / "secrets.json"
    out.write_text("{}")
    r = runner.invoke(app, ["templates", "secrets", "openai", "-o", str(out)])
    assert r.exit_code != 0
    # With --force it succeeds
    r2 = runner.invoke(app, ["templates", "secrets", "openai", "-o", str(out), "--force"])
    assert r2.exit_code == 0

