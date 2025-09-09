import os
import shutil
from click.testing import CliRunner
from hexaboost.cli.commands.new_cmd import new_cmd, TEMPLATES_DIR

def test_new_cmd_creates_project_from_template(tmp_path):
    runner = CliRunner()
    template_name = "python-fastapi"
    project_name = tmp_path / "generated_project"

    result = runner.invoke(new_cmd, [template_name, str(project_name)])

    assert result.exit_code == 0
    assert project_name.exists()
    assert (project_name / "README.md").exists()

    # Limpieza
    shutil.rmtree(project_name, ignore_errors=True)

def test_new_cmd_invalid_template(tmp_path):
    runner = CliRunner()
    project_name = tmp_path / "generated_project"

    result = runner.invoke(new_cmd, ["invalid-template", str(project_name)])

    assert "no encontrada" in result.output.lower()
    assert not project_name.exists()
