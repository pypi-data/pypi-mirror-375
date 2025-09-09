import os
import click

@click.command()
@click.argument("template")
@click.argument("name")
def new_cmd(template, name):
    """Crea un nuevo proyecto a partir de una plantilla."""
    valid_templates = ["fastapi", "flask"]

    if template not in valid_templates:
        click.echo(f"❌ La plantilla '{template}' no existe.")
        raise click.Abort()

    if os.path.exists(name):
        click.echo(f"❌ El directorio {name} ya existe.")
        raise click.Abort()

    os.makedirs(name, exist_ok=True)
    click.echo(f"✅ Proyecto '{name}' creado usando la plantilla '{template}'.")
    return 0
