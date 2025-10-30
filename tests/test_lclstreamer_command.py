import traceback

from typer.testing import CliRunner
from click.testing import Result

from lclstreamer.cmd.lclstreamer import app

runner: CliRunner = CliRunner()


def test_app():
    result: Result = runner.invoke(app, ["--help"])
    print("--- Output")
    print(result.output)
    if result.exception is not None:
        print("--- Exceptions")
        print(result.exception)
        traceback.print_tb(result.exc_info[2])

    assert result.exit_code == 0
