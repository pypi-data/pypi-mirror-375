from click.testing import CliRunner
from hexaboost.cli.commands.init_cmd import init_cmd
from pathlib import Path

def test_init_cmd_creates_project():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(init_cmd, ["my_project"])

        # Verifica que terminó bien
        assert result.exit_code == 0

        # Verifica que el directorio fue creado
        assert Path("my_project").exists()
