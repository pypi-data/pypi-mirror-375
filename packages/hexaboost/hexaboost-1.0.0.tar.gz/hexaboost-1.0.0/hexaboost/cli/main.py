import click
from hexaboost.cli.commands.init_cmd import init_cmd
from hexaboost.cli.commands.new_cmd import new_cmd
from hexaboost.cli.commands.sync_readme_cmd import sync_readme_cmd


@click.group(help="🚀 Hexaboost CLI - Herramienta para iniciar proyectos rápidamente.")
def cli():
    """CLI principal de Hexaboost."""
    pass


# Registrar los subcomandos
cli.add_command(init_cmd, "init")
cli.add_command(new_cmd, "new")
cli.add_command(sync_readme_cmd, "sync-readme")


if __name__ == "__main__":
    cli()
