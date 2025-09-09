def validate_project_name(name: str) -> bool:
    """Valida que el nombre del proyecto sea alfanumérico y con guiones."""
    return name.replace("-", "").isalnum()
