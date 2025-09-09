import click

@click.command()
def sync_cmd():
    """Sincroniza los archivos README.md en varios idiomas."""
    click.echo("🔄 Sincronizando READMEs...")
