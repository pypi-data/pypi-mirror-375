import click

@click.command()
def init_cmd():
    """Inicializa un nuevo proyecto Hexagonal con nombre especificado."""
    click.echo("🚀 Inicializando proyecto...")
