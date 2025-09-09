from click.testing import CliRunner
from hexaboost.cli.commands.sync_readme_cmd import sync_readme_cmd
from pathlib import Path

def test_sync_readme_cmd():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Crear README.md base
        Path("README.md").write_text("# Proyecto Base\nContenido de prueba", encoding="utf-8")

        result = runner.invoke(sync_readme_cmd)

        # Verifica que terminó bien
        assert result.exit_code == 0
        assert Path("README.en.md").exists()
        assert Path("README.pt.md").exists()
