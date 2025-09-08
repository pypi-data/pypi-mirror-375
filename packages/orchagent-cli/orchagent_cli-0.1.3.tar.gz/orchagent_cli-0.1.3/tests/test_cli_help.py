from typer.testing import CliRunner
from orchcli.main import app


runner = CliRunner()


def test_root_help():
    r = runner.invoke(app, ["--help"]) 
    assert r.exit_code == 0
    assert "Orchagent CLI" in r.stdout
    assert "auth" in r.stdout and "threads" in r.stdout and "runs" in r.stdout


def test_auth_whoami_no_token(monkeypatch, tmp_path):
    # Ensure SDK looks at a temp token file
    monkeypatch.setenv("ORCHAGENT_TOKEN_FILE", str(tmp_path / "token.json"))
    r = runner.invoke(app, ["auth", "whoami"]) 
    assert r.exit_code == 0
    assert "No token" in r.stdout

