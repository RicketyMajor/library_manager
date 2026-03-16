import os
import django
import typer
from rich.console import Console
from rich.table import Table
# --- NUEVA IMPORTACIÓN PARA INTERACTIVIDAD ---
from rich.prompt import Prompt, Confirm

# --- EL PUENTE DE DJANGO ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_manager.settings')
django.setup()

# --- INICIALIZAR TYPER Y RICH ---
app = typer.Typer(
    help="CLI tool to manage my personal library.", no_args_is_help=True)
console = Console()

# --- COMANDO 1: LEER ---


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

        table.add_row(
            str(book.id),
            book.title,
            author_name,
            book.get_format_type_display(),
            is_read_status
        )

    console.print(table)

# --- COMANDO 2: ESCRIBIR ---


@app.command(name="add-book")
def add_book():
    """Interactive prompt to add a new book."""
    # Importamos todos los modelos necesarios aquí adentro
    from catalog.models import Book, Author, Genre

    console.print(
        "\n[bold cyan]📖 Let's add a new book to your library![/bold cyan]\n")

    # 1. Recopilar datos básicos con validación
    title = Prompt.ask("Title")
    author_name = Prompt.ask("Author")

    # Opciones de formato basadas en tu modelo
    console.print(
        "\n[dim]Available formats: NOVEL, COMIC, MANGA, ANTHOLOGY[/dim]")
    format_type = Prompt.ask(
        "Format", choices=["NOVEL", "COMIC", "MANGA", "ANTHOLOGY"], default="NOVEL")

    # Recopilar géneros separándolos por comas
    genres_input = Prompt.ask(
        "Genres (comma-separated, e.g., Fantasy, Cyberpunk)")

    # Pregunta de sí/no automatizada
    is_read = Confirm.ask("Have you read this book?")

    # 2. Lógica de Base de Datos
    # get_or_create devuelve una tupla: (objeto, booleano_si_fue_creado)
    author, _ = Author.objects.get_or_create(name=author_name.strip())

    # Creamos el libro (Aún no podemos añadir los géneros porque es una relación Muchos-a-Muchos)
    book = Book.objects.create(
        title=title.strip(),
        author=author,
        format_type=format_type,
        is_read=is_read
    )

    # 3. Procesar y añadir los géneros
    if genres_input:
        # Limpiamos los espacios alrededor de cada género ingresado
        genre_names = [g.strip() for g in genres_input.split(',')]
        for g_name in genre_names:
            if g_name:  # Evitar strings vacíos
                genre, _ = Genre.objects.get_or_create(name=g_name)
                book.genres.add(genre)  # Añadimos la relación Muchos-a-Muchos

    console.print(
        f"\n[bold green]✅ Successfully added '{book.title}' to your library![/bold green]\n")


if __name__ == "__main__":
    app()
