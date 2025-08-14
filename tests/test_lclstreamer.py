from typer.testing import CliRunner

from lclstreamer.cmd.lclstreamer import app

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    print(result.stdout)
    print("---")
    print(result.output)
