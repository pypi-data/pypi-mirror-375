import os
import click

@click.command()
@click.argument("name")
def init_cmd(name):
    """Inicializa un nuevo proyecto vacío."""
    if os.path.exists(name):
        click.echo(f"❌ El directorio {name} ya existe.")
        raise click.Abort()

    os.makedirs(name, exist_ok=True)
    click.echo(f"✅ Proyecto '{name}' inicializado correctamente.")
    return 0
