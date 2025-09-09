import os

def ensure_dir(path: str):
    """Crea un directorio si no existe."""
    if not os.path.exists(path):
        os.makedirs(path)
