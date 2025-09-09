import os
import shutil
from pathlib import Path
import subprocess

import pytest


@pytest.fixture
def setup_readmes(tmp_path):
    """
    Crea un entorno temporal con un README base en español
    para simular la raíz del proyecto.
    """
    # Archivos que vamos a usar
    readme_base = tmp_path / "README.md"
    readme_en = tmp_path / "README.en.md"
    readme_pt = tmp_path / "README.pt.md"

    # Crear un README base
    readme_base.write_text("# Proyecto de prueba\n", encoding="utf-8")

    # Cambiar directorio de trabajo temporalmente
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    yield tmp_path, readme_base, readme_en, readme_pt

    # Restaurar directorio original
    os.chdir(old_cwd)


def test_sync_readme_command(setup_readmes):
    tmp_path, readme_base, readme_en, readme_pt = setup_readmes

    # Ejecutar el comando como si fuera CLI
    result = subprocess.run(
        ["hexaboost", "sync-readme"],
        capture_output=True,
        text=True
    )

    # Debe ejecutarse sin errores
    assert result.returncode == 0
    assert "✨ Sincronización completada." in result.stdout

    # Debe haber generado los archivos en inglés y portugués
    assert readme_en.exists()
    assert readme_pt.exists()

    # Todos los archivos deben tener el encabezado multi-idioma
    header = "🌐 [Español](./README.md) | [English](./README.en.md) | [Português](./README.pt.md)"
    for file in [readme_base, readme_en, readme_pt]:
        content = file.read_text(encoding="utf-8").splitlines()
        assert content[0] == header
