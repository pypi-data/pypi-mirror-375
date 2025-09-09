from click.testing import CliRunner
from hexaboost.cli.commands.new_cmd import new_cmd
from pathlib import Path

def test_new_cmd_creates_project_from_template():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(new_cmd, ["fastapi", "my_service"])

        # Verifica que terminó bien
        assert result.exit_code == 0
        assert Path("my_service").exists()

def test_new_cmd_invalid_template():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(new_cmd, ["invalid", "bad_service"])

        # Debe fallar
        assert result.exit_code != 0
