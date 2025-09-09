import os
import shutil
from click.testing import CliRunner
from hexaboost.cli.commands.init_cmd import init_cmd

def test_init_cmd_creates_project(tmp_path):
    runner = CliRunner()
    project_name = tmp_path / "test_project"

    result = runner.invoke(init_cmd, [str(project_name)])

    assert result.exit_code == 0
    assert project_name.exists()
    assert project_name.is_dir()

    # Limpieza
    shutil.rmtree(project_name, ignore_errors=True)
