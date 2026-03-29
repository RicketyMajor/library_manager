import httpx
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Markdown
from textual.containers import VerticalScroll
from textual import work
from .constants import API_LIBRARY


class BookDetailsScreen(Screen):
    BINDINGS = [
        ("escape, b, left", "go_back", "Volver a la Tabla"),
        ("q", "app.quit", "Salir")
    ]

    def __init__(self, book_id: str, **kwargs):
        super().__init__(**kwargs)
        self.book_id = book_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with VerticalScroll(id="details_container"):
            yield Markdown("Cargando los archivos de la base de datos...", id="details_content")
        yield Footer()

    def on_mount(self) -> None:
        self.fetch_details()

    @work(thread=True)
    def fetch_details(self) -> None:
        try:
            resp = httpx.get(f"{API_LIBRARY}{self.book_id}/", timeout=5.0)
            if resp.status_code == 200:
                book = resp.json()
                self.app.call_from_thread(self.render_details, book)
            else:
                self.app.call_from_thread(
                    self.show_error, f"Error {resp.status_code}")
        except Exception as e:
            self.app.call_from_thread(self.show_error, f"Error de red: {e}")

    def render_details(self, book: dict) -> None:
        content = self.query_one("#details_content", Markdown)
        generos_str = ", ".join(book.get('genre_list', [])) if book.get(
            'genre_list') else "Sin clasificar"
        estado = "✔ Leído" if book.get('is_read') else "✘ Pendiente"
        ubicacion = "⇋ Prestado" if book.get(
            'is_loaned') else "❖ En Estantería"

        md_text = f"""
# {book.get('title', 'Sin Título').upper()}
{f"*{book.get('subtitle')}*" if book.get('subtitle') else ""}

**Autor:** {book.get('author_name', 'Desconocido')}
**Editorial:** {book.get('publisher') or '-'} | **Formato:** {book.get('format_type', '-')} | **Géneros:** {generos_str}
**Páginas:** {book.get('page_count') or '-'} | **Publicación:** {book.get('publish_date') or '-'}

---
### ⌖ Estado Físico
* **Lectura:** {estado}
* **Ubicación:** {ubicacion}
"""
        details = book.get('details', {})
        if details:
            md_text += "### ◈ Detalles Adicionales\n"
            for k, v in details.items():
                if isinstance(v, list):
                    v = ", ".join(v)
                md_text += f"* **{k.replace('_', ' ').title()}:** {v}\n"

        desc = book.get('description')
        if desc:
            md_text += f"\n### 📖 Sinopsis\n{desc}"

        content.update(md_text)

    def show_error(self, message: str) -> None:
        self.query_one("#details_content", Markdown).update(
            f"### ❌ Error\n{message}")

    def action_go_back(self) -> None:
        self.app.pop_screen()
