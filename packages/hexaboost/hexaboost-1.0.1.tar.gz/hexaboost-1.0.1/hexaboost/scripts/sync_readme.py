from pathlib import Path
import click

@click.command()
def sync_readme():
    """
    Sincroniza README.md en diferentes idiomas (README.en.md, README.pt.md).
    """
    print("📖 Sincronizando README.md en todos los idiomas...")
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
