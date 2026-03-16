import os
import django
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_manager.settings')
django.setup()

app = typer.Typer(
    help="CLI tool to manage my personal library.", no_args_is_help=True)
console = Console()

# --- 1. LEER (LISTA GENERAL) ---


@app.command(name="list-books")
def list_books():
    """Fetches and displays all books in the library."""
    from catalog.models import Book
    books = Book.objects.all()

    if not books:
        console.print(
            "[bold yellow]The library is currently empty.[/bold yellow]")
        return

    table = Table(title="📚 My Personal Library", title_justify="center")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="magenta")
    table.add_column("Author", style="green")
    table.add_column("Format", style="blue")
    table.add_column("Read", justify="center")

    for book in books:
        author_name = book.author.name if book.author else "Unknown"
        is_read_status = "✅" if book.is_read else "❌"

        # Lógica visual para diferenciar series de tomos únicos
        title_display = book.title
        if book.is_series:
            title_display += f" [dim](Serie: {book.owned_volumes})[/dim]"

        table.add_row(
            str(book.id), title_display, author_name,
            book.get_format_type_display(), is_read_status
        )
    console.print(table)

# --- 2. AÑADIR ---


@app.command(name="add-book")
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


@app.command(name="edit-book")
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


@app.command(name="show-details")
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


if __name__ == "__main__":
    app()
