import shutil
from pathlib import Path
from click.testing import CliRunner
from hexaboost.cli.commands.sync_readme_cmd import sync_readme_cmd

def test_sync_readme_cmd(tmp_path):
    # Crear README base
    readme_es = tmp_path / "README.md"
    readme_es.write_text("# Proyecto de Prueba\n", encoding="utf-8")

    # Moverse temporalmente al directorio de trabajo
    cwd = Path.cwd()
    try:
        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(sync_readme_cmd)

            assert result.exit_code == 0
            assert (tmp_path / "README.en.md").exists()
            assert (tmp_path / "README.pt.md").exists()
    finally:
        Path.chdir(cwd)
