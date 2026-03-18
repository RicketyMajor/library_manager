import typer
import httpx
from rich.console import Console

console = Console()
app = typer.Typer(help="Write operations for your library.",
                  no_args_is_help=True)

# Apuntamos al endpoint de escaneo que ya tenías programado
API_SCAN = "http://localhost:8000/api/books/scan/"
API_LIBRARY = "http://localhost:8000/api/books/library/"


@app.command(name="add")
def add_book(isbn: str):
    """Añade un libro usando el ISBN consumiendo la API remota."""
    console.print(f"Buscando y procesando el ISBN {isbn} en el servidor...")
    try:
        response = httpx.post(API_SCAN, json={"isbn": isbn})
        data = response.json()

        if response.status_code == 201:
            console.print(
                f"[bold green]{data['message']}[/bold green] (ID: {data['book']['id']})")
        elif response.status_code == 200:
            console.print(f"[yellow]{data['message']}[/yellow]")
        else:
            console.print(
                f"[bold red]❌ Error: {data.get('error', 'Desconocido')}[/bold red]")

    except Exception as e:
        console.print(
            f"[bold red]❌ Error de conexión al servidor: {e}[/bold red]")


@app.command(name="delete")
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
