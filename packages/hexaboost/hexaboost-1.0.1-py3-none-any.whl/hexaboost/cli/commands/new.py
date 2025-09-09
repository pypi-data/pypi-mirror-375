import click

@click.command()
def new_cmd():
    """Crea un nuevo proyecto desde una plantilla específica."""
    click.echo("📦 Creando nuevo proyecto desde plantilla...")
