import os
import django
import typer
from typing import Optional  # <-- NUEVO
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich import box

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_manager.settings')
django.setup()

# --- INICIALIZAR TYPER Y RICH ---
# La app principal que contendrá los subcomandos
app = typer.Typer(
    help="CLI tool to manage my personal library.", no_args_is_help=True)

# Creamos los grupos lógicos
book_app = typer.Typer(
    help="Manage your books, comics, and mangas.", no_args_is_help=True)
loan_app = typer.Typer(
    help="Manage book loans to friends.", no_args_is_help=True)

# Conectamos los grupos a la app principal
app.add_typer(book_app, name="book")
app.add_typer(loan_app, name="loan")

console = Console()

# --- 1. LEER (LISTA GENERAL Y BÚSQUEDA) ---


@book_app.command(name="list")
def list_books(
    search: Optional[str] = typer.Option(
        None, "--search", "-s", help="Search by title"),
    author: Optional[str] = typer.Option(
        None, "--author", "-a", help="Filter by author name"),
    publisher: Optional[str] = typer.Option(
        None, "--publisher", "-p", help="Filter by publisher"),
    genre: Optional[str] = typer.Option(
        None, "--genre", "-g", help="Filter by genre"),
    unread: bool = typer.Option(
        False, "--unread", "-u", help="Show only unread books"),
):
    """Fetches, filters, and displays books in the library."""
    from catalog.models import Book

    # 1. Consulta base
    query = Book.objects.all()

    # 2. Aplicar filtros dinámicos si el usuario pasó argumentos
    if search:
        # icontains busca coincidencias ignorando mayúsculas
        query = query.filter(title__icontains=search)
    if author:
        query = query.filter(author__name__icontains=author)
    if publisher:
        query = query.filter(publisher__icontains=publisher)
    if genre:
        query = query.filter(genres__name__icontains=genre)
    if unread:
        query = query.filter(is_read=False)

    # 3. Orden alfabético por título y eliminar duplicados (por si un libro tiene varios géneros)
    books = query.order_by('title').distinct()

    if not books:
        console.print(
            "[bold yellow]No books found matching your criteria.[/bold yellow]")
        return

    # 4. Diseño de tabla mejorado con estilo ROUNDED y contador
    table = Table(
        title="📚 [bold gold1]My Personal Library[/bold gold1]",
        title_justify="center",
        box=box.ROUNDED,  # Bordes redondeados más estéticos
        # Pie de tabla
        caption=f"[dim italic]Total books found: {books.count()}[/dim italic]",
        header_style="bold cyan"
    )

    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="magenta")
    table.add_column("Author", style="green")
    table.add_column("Format", style="blue")
    table.add_column("Read", justify="center")

    for book in books:
        author_name = book.author.name if book.author else "Unknown"
        is_read_status = "[bold green]✅[/bold green]" if book.is_read else "[bold red]❌[/bold red]"

        # Construcción visual del título
        title_display = f"[bold]{book.title}[/bold]"
        if book.is_series:
            title_display += f"\n[dim cyan]↳ Serie (Vols: {book.owned_volumes or 'N/A'})[/dim cyan]"

        table.add_row(
            str(book.id),
            title_display,
            author_name,
            book.get_format_type_display(),
            is_read_status
        )

    console.print(table)
    print("\n")

# --- 2. AÑADIR ---


@book_app.command(name="add")
def add_book():
    """Interactive prompt to add a new book."""
    from catalog.models import Book, Author, Genre

    console.print(
        "\n[bold cyan]📖 Let's add a new book to your library![/bold cyan]\n")

    title = Prompt.ask("Title")
    author_name = Prompt.ask("Author")
    publisher = Prompt.ask("Publisher (Editorial)", default="")

    console.print(
        "[dim]Available formats: NOVEL, COMIC, MANGA, ANTHOLOGY[/dim]")
    format_type = Prompt.ask(
        "Format", choices=["NOVEL", "COMIC", "MANGA", "ANTHOLOGY"], default="NOVEL")

    # Lógica condicional para Mangas y Cómics
    is_series = False
    total_volumes = None
    owned_volumes = ""

    if format_type in ["COMIC", "MANGA"]:
        is_series = Confirm.ask("Is this a multi-volume series?")
        if is_series:
            total_volumes = IntPrompt.ask(
                "How many total volumes exist currently?", default=0)
            owned_volumes = Prompt.ask(
                "Which volumes do you own? (e.g., 1, 2, 3 or 1-5)")

    genres_input = Prompt.ask("Genres (comma-separated)")
    is_read = Confirm.ask("Have you read this completely?")

    author, _ = Author.objects.get_or_create(
        name=author_name.strip()) if author_name else (None, False)

    book = Book.objects.create(
        title=title.strip(), author=author, publisher=publisher,
        format_type=format_type, is_read=is_read,
        is_series=is_series, total_volumes=total_volumes, owned_volumes=owned_volumes
    )

    if genres_input:
        for g_name in [g.strip() for g in genres_input.split(',') if g.strip()]:
            genre, _ = Genre.objects.get_or_create(name=g_name)
            book.genres.add(genre)

    console.print(
        f"\n[bold green]✅ Successfully added '{book.title}'![/bold green]\n")

# --- 3. EDITAR ---


@book_app.command(name="edit")
def edit_book(book_id: int = typer.Argument(..., help="The ID of the book to edit")):
    """Edit an existing book's details."""
    from catalog.models import Book, Author

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        console.print(
            f"[bold red]❌ Book with ID {book_id} not found.[/bold red]")
        return

    console.print(f"\n[bold cyan]✏️  Editing: {book.title}[/bold cyan]\n")

    # Se pide la nueva información, usando la actual como valor por defecto
    new_title = Prompt.ask("Title", default=book.title)
    current_author = book.author.name if book.author else ""
    new_author = Prompt.ask("Author", default=current_author)

    book.title = new_title
    if new_author != current_author:
        author, _ = Author.objects.get_or_create(name=new_author.strip())
        book.author = author

    book.save()
    console.print(
        f"\n[bold green]✅ Book ID {book.id} successfully updated![/bold green]\n")

# --- 4. DETALLES DE SERIE ---


@book_app.command(name="details")
def show_details(book_id: int = typer.Argument(..., help="The ID of the book/series to inspect")):
    """Shows specific details and owned volumes of a comic/manga."""
    from catalog.models import Book

    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        console.print("[bold red]❌ Book not found.[/bold red]")
        return

    console.print(f"\n[bold magenta]Title:[/bold magenta] {book.title}")
    console.print(
        f"[bold magenta]Author:[/bold magenta] {book.author.name if book.author else 'Unknown'}")
    console.print(
        f"[bold magenta]Publisher:[/bold magenta] {book.publisher or 'Not specified'}")

    if book.is_series:
        console.print(
            f"[bold cyan]Total Volumes Released:[/bold cyan] {book.total_volumes or 'Unknown'}")
        console.print(
            f"[bold green]Volumes Owned:[/bold green] {book.owned_volumes or 'None'}")
    print("\n")

# --- GRUPO: PRÉSTAMOS (LOANS) ---


@loan_app.command(name="lend")
def lend_book():
    """Lend a book to a friend."""
    from catalog.models import Book, Friend, Loan

    console.print("\n[bold cyan]🤝 Lend a Book[/bold cyan]\n")

    book_id = typer.prompt("Enter the Book ID you want to lend", type=int)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        console.print("[bold red]❌ Book not found.[/bold red]")
        return

    friend_name = Prompt.ask("Friend's Name")

    # Buscamos al amigo o lo creamos
    friend, _ = Friend.objects.get_or_create(name=friend_name.strip())

    # Registramos el préstamo
    Loan.objects.create(book=book, friend=friend)

    console.print(
        f"\n[bold green]✅ '{book.title}' has been lent to {friend.name}![/bold green]")
    console.print("[dim]They have 30 days to return it.[/dim]\n")


@loan_app.command(name="status")
def loan_status():
    """View all active loans and due dates."""
    from catalog.models import Loan
    from django.utils import timezone

    # Filtramos los préstamos que aún no han sido devueltos
    active_loans = Loan.objects.filter(returned=False).order_by('due_date')

    if not active_loans:
        console.print(
            "[bold green]No active loans. All your books are safely home![/bold green]")
        return

    table = Table(title="🤝 Active Loans", box=box.ROUNDED,
                  header_style="bold cyan")
    table.add_column("Loan ID", justify="right", style="cyan")
    table.add_column("Book", style="magenta")
    table.add_column("Friend", style="green")
    table.add_column("Due Date", justify="center")
    table.add_column("Status", justify="center")

    today = timezone.now().date()

    for loan in active_loans:
        # Lógica visual para saber si un préstamo está atrasado
        if loan.due_date < today:
            status = "[bold red]OVERDUE![/bold red]"
            due_str = f"[bold red]{loan.due_date}[/bold red]"
        else:
            status = "[green]On time[/green]"
            due_str = str(loan.due_date)

        table.add_row(
            str(loan.id), loan.book.title, loan.friend.name, due_str, status
        )

    console.print(table)
    print("\n")


@loan_app.command(name="return")
def return_book(loan_id: int = typer.Argument(..., help="The ID of the loan to mark as returned")):
    """Mark a lent book as returned."""
    from catalog.models import Loan

    try:
        loan = Loan.objects.get(id=loan_id)
        if loan.returned:
            console.print(
                "[bold yellow]This book was already returned.[/bold yellow]")
            return

        loan.returned = True
        loan.save()
        console.print(
            f"[bold green]✅ Awesome! '{loan.book.title}' has been returned by {loan.friend.name}.[/bold green]")

    except Loan.DoesNotExist:
        console.print("[bold red]❌ Loan ID not found.[/bold red]")


if __name__ == "__main__":
    app()
