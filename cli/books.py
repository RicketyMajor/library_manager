import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
book_app = typer.Typer(
    help="Manage your library books, comics, and mangas.", no_args_is_help=True)

API_LIBRARY = "http://localhost:8000/api/books/library/"
API_SCAN = "http://localhost:8000/api/books/scan/"


@book_app.command(name="list")
def list_books(
    title: str = typer.Option(None, "--title", "-t",
                              help="Filtrar por título parcial"),
    author: str = typer.Option(
        None, "--author", "-a", help="Filtrar por nombre de autor"),
    genre: str = typer.Option(None, "--genre", "-g",
                              help="Filtrar por género"),
    format_type: str = typer.Option(
        None, "--format", "-f", help="Filtrar por formato (NOVEL, MANGA, COMIC)"),
    read: bool = typer.Option(None, "--read/--unread",
                              help="Filtrar por estado de lectura")
):
    """Muestra los libros de tu biblioteca con opciones de búsqueda avanzada."""

    # Construimos el diccionario de parámetros para enviar en la URL
    params = {}
    if title:
        params['title'] = title
    if author:
        params['author'] = author
    if genre:
        params['genre'] = genre
    if format_type:
        params['format_type'] = format_type.upper()

    # Manejamos el booleano (si el usuario usó --read o --unread)
    if read is not None:
        params['is_read'] = "true" if read else "false"

    try:
        # httpx convertirá el diccionario 'params' mágicamente en ?author=X&title=Y
        response = httpx.get(API_LIBRARY, params=params)
        response.raise_for_status()
        books = response.json()
    except Exception as e:
        console.print(f"[bold red]❌ Error de conexión: {e}[/bold red]")
        return

    if not books:
        console.print(
            "[yellow]No se encontraron libros con esos filtros.[/yellow]")
        return

    # Imprimimos qué filtros estamos usando en el título de la tabla
    filters_used = ", ".join([f"{k}={v}" for k, v in params.items()])
    table_title = f"📚 [bold blue]Mi Biblioteca[/bold blue]"
    if filters_used:
        table_title += f" [dim](Filtros: {filters_used})[/dim]"

    table = Table(title=table_title, box=box.ROUNDED)
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Título", style="magenta")
    table.add_column("Autor", style="green")
    table.add_column("Formato", style="yellow")
    table.add_column("Leído", justify="center")

    for book in books:
        status = "✅" if book.get('is_read') else "❌"
        table.add_row(
            str(book.get('id')),
            book.get('title', 'Sin título'),
            book.get('author_name', 'Desconocido'),
            book.get('format_type', '-'),
            status
        )

    console.print(table)


@book_app.command(name="add")
def add_book(isbn: str):
    """Añade un libro usando el ISBN consumiendo la API remota."""
    console.print(f"Buscando y procesando el ISBN {isbn} en el servidor...")
    try:
        response = httpx.post(API_SCAN, json={"isbn": isbn})
        data = response.json()

        if response.status_code == 201:
            console.print(
                f"[bold green]{data.get('message', 'Añadido')}[/bold green] (ID: {data['book']['id']})")
        elif response.status_code == 200:
            console.print(
                f"[yellow]{data.get('message', 'Ya existe')}[/yellow]")
        else:
            console.print(
                f"[bold red]❌ Error: {data.get('error', 'Desconocido')}[/bold red]")
    except Exception as e:
        console.print(
            f"[bold red]❌ Error de conexión al servidor: {e}[/bold red]")


@book_app.command(name="delete")
def delete_book(book_id: int):
    """Elimina un libro de la biblioteca mediante la API."""
    try:
        response = httpx.delete(f"{API_LIBRARY}{book_id}/")
        if response.status_code == 204:
            console.print(
                f"[bold green]✅ Libro #{book_id} eliminado correctamente del servidor.[/bold green]")
        else:
            console.print(
                f"[bold red]❌ No se pudo eliminar. ¿Existe el ID {book_id}?[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error de conexión: {e}[/bold red]")
