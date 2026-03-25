import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich import box
from rich.align import Align
from rich.prompt import Prompt

console = Console()
dir_app = typer.Typer(
    help="Gestiona los directorios y colecciones maestras.", no_args_is_help=True)

# 🚀 Asegúrate de que las rutas coincidan con tu urls.py
API_DIR = "http://localhost:8000/api/books/directories/"
API_LIBRARY = "http://localhost:8000/api/books/library/"


@dir_app.command("create")
def create_dir():
    """Crea una nueva carpeta maestra con un color personalizado."""
    console.print("\n[bold cyan]📁 CREAR NUEVO DIRECTORIO[/bold cyan]")
    name = Prompt.ask("Nombre de la saga o colección (ej. Green Lantern)")

    console.print("\n[dim]Paleta de renderizado en terminal:[/dim]")
    colors = ["red", "green", "yellow", "blue", "magenta", "cyan", "white"]
    for c in colors:
        console.print(f"  [{c}]■ {c.capitalize()}[/{c}]")

    color = Prompt.ask("\nElige un color para este universo",
                       choices=colors, default="cyan")

    try:
        resp = httpx.post(
            API_DIR, json={"name": name.strip(), "color_hex": color})
        if resp.status_code == 201:
            console.print(
                f"\n[bold green]✅ Directorio '{name}' creado y montado exitosamente.[/bold green]\n")
        else:
            console.print(f"\n[bold red]❌ Error: {resp.text}[/bold red]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Error de red: {e}[/bold red]")


@dir_app.command("list")
def list_dirs():
    """Muestra el sistema de archivos actual y su peso (cantidad de libros)."""
    try:
        resp = httpx.get(API_DIR)
        resp.raise_for_status()
        dirs = resp.json()

        # Hacemos un fetch a la biblioteca para calcular el peso de cada directorio
        resp_books = httpx.get(API_LIBRARY)
        books = resp_books.json()

    except Exception as e:
        console.print(f"[bold red]❌ Error de red: {e}[/bold red]")
        return

    if not dirs:
        console.print(
            "\n[yellow]No hay directorios creados aún. Usa 'dir create' para empezar.[/yellow]\n")
        return

    table = Table(
        title="📁 [bold cyan]SISTEMA DE ARCHIVOS[/bold cyan] 📁", box=box.SIMPLE_HEAVY)
    table.add_column("ID Virtual", style="dim")
    table.add_column("Directorio")
    table.add_column("Volumen (Obras)", justify="center")

    for d in dirs:
        # 🚀 LA MAGIA VISUAL: Creamos el prefijo [D-X] en la terminal, manteniendo el ID entero en PostgreSQL
        d_id = d.get('id')
        color = d.get('color_hex', 'cyan')
        name = d.get('name', 'Unknown')

        # Calculamos cuántos libros apuntan a esta llave foránea
        count = sum(1 for b in books if b.get('directory') == d_id)

        table.add_row(
            f"[D-{d_id}]",
            f"[{color}]■ {name}[/{color}]",
            str(count)
        )

    console.print()
    console.print(Align.center(table))
    console.print()


@dir_app.command("add")
def add_to_dir(
    dir_id: int = typer.Argument(...,
                                 help="ID numérico del directorio (ej. 1)"),
    book_ids: str = typer.Argument(...,
                                   help="IDs de los libros separados por coma (ej. 14,15,16)")
):
    """Inyección Masiva: Mueve múltiples libros dentro de un directorio de golpe."""
    console.print(
        f"\n[dim]Iniciando transferencia al directorio D-{dir_id}...[/dim]")

    ids = [i.strip() for i in book_ids.split(",") if i.strip().isdigit()]
    if not ids:
        console.print(
            "[bold red]❌ No se proporcionaron IDs numéricos válidos.[/bold red]")
        return

    success_count = 0
    for b_id in ids:
        try:
            # Usamos PATCH para actualizar únicamente la llave foránea 'directory'
            resp = httpx.patch(f"{API_LIBRARY}{b_id}/",
                               json={"directory": dir_id})
            if resp.status_code == 200:
                success_count += 1
                console.print(
                    f"  [green]✔ Tomo #{b_id} transferido exitosamente.[/green]")
            else:
                console.print(
                    f"  [red]❌ Falló el tomo #{b_id}: {resp.text}[/red]")
        except Exception as e:
            console.print(
                f"  [red]❌ Error de red con el tomo #{b_id}: {e}[/red]")

    console.print(
        f"\n[bold magenta]✨ Operación finalizada. {success_count} tomos anidados.[/bold magenta]\n")
