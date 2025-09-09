import click
from pathlib import Path

@click.command(name="sync-readme", help="Sincroniza README.md en varios idiomas.")
def sync_readme_cmd():
    """
    Sincroniza README.md en diferentes idiomas (README.en.md, README.pt.md).
    """
    click.echo("📖 Sincronizando README.md en todos los idiomas...")
    base = Path("README.md")
    if not base.exists():
        click.echo("❌ No se encontró README.md en el directorio actual.")
        raise SystemExit(1)

    content = base.read_text(encoding="utf-8")

    for lang in ["en", "pt"]:
        target = Path(f"README.{lang}.md")
        target.write_text(content, encoding="utf-8")
        click.echo(f"✅ Generado {target.name}")

    raise SystemExit(0)
