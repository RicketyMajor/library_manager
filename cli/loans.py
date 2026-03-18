import typer
import httpx
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
loan_app = typer.Typer(help="Manage book loans.", no_args_is_help=True)

API_LOANS = "http://localhost:8000/api/books/loans/"


@loan_app.command(name="list")
def list_loans():
    """Muestra todos los préstamos activos desde el servidor."""
    try:
        response = httpx.get(API_LOANS)
        response.raise_for_status()
        loans = response.json()
    except Exception as e:
        console.print(f"[bold red]❌ Error de conexión: {e}[/bold red]")
        return

    # Filtramos para mostrar solo los no devueltos
    active_loans = [loan for loan in loans if not loan.get('returned')]

    if not active_loans:
        console.print(
            "[yellow]No tienes libros prestados actualmente.[/yellow]")
        return

    table = Table(
        title="🤝 [bold cyan]Libros Prestados Activos[/bold cyan]", box=box.ROUNDED)
    table.add_column("ID", justify="right", style="dim")
    table.add_column("Libro", style="magenta")
    table.add_column("Amigo", style="green")
    table.add_column("Fecha Préstamo", style="cyan")

    for loan in active_loans:
        table.add_row(
            str(loan.get('id')),
            loan.get('book_title', 'Desconocido'),
            loan.get('friend_name', 'Desconocido'),
            loan.get('loan_date', '')[:10]
        )

    console.print(table)


API_FRIENDS = "http://localhost:8000/api/books/friends/"


@loan_app.command(name="return")
def return_book(loan_id: int):
    """Marca un libro prestado como devuelto."""
    try:
        # En DRF, usamos PATCH para actualizar solo un campo (returned = True)
        response = httpx.patch(
            f"{API_LOANS}{loan_id}/", json={"returned": True})
        if response.status_code == 200:
            console.print(
                "[bold green]✅ ¡Libro devuelto con éxito a tu biblioteca![/bold green]")
        else:
            console.print(
                "[bold red]❌ No se pudo registrar la devolución.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Error de conexión: {e}[/bold red]")
