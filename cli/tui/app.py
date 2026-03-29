import httpx
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Header, Footer, DataTable, Markdown, Input, Button, Label
from textual.containers import VerticalScroll, Vertical, Horizontal
from textual import work

API_LIBRARY = "http://localhost:8000/api/books/library/"
API_SCAN = "http://localhost:8000/api/books/scan/"

# ==============================================================================
# 📄 PANTALLA SECUNDARIA: DETALLES DEL LIBRO (FASE 40)
# ==============================================================================


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


# ==============================================================================
# 🪟 MODALES EMERGENTES (FASE 41)
# ==============================================================================
class IsbnModal(ModalScreen[str]):
    """Ventana flotante para ingresar un ISBN nuevo."""

    def compose(self) -> ComposeResult:
        with Vertical(id="isbn_dialog"):
            yield Label("📚 Añadir Nuevo Ejemplar", classes="modal_title")
            yield Label("Ingresa el código ISBN:")
            yield Input(placeholder="Ej: 9788414106222", id="isbn_input")
            with Horizontal(classes="form_buttons"):
                yield Button("Añadir", variant="success", id="btn_add")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_add":
            val = self.query_one("#isbn_input", Input).value
            self.dismiss(val)  # Cierra el modal y devuelve el valor a la App
        else:
            self.dismiss(None)


class QuickEditModal(ModalScreen[dict]):
    """Ventana flotante para editar rápidamente una ficha."""

    def __init__(self, book: dict, **kwargs):
        super().__init__(**kwargs)
        self.book = book

    def compose(self) -> ComposeResult:
        with Vertical(id="edit_dialog"):
            yield Label(f"✏️ Editando: {self.book.get('title')}", classes="modal_title")
            yield Input(value=self.book.get('title', ''), id="inp_title", placeholder="Título")
            yield Input(value=self.book.get('author_name', ''), id="inp_author", placeholder="Autor")
            yield Input(value=self.book.get('format_type', ''), id="inp_format", placeholder="Formato (NOVEL, MANGA...)")
            yield Input(value=self.book.get('publisher', ''), id="inp_publisher", placeholder="Editorial")
            with Horizontal(classes="form_buttons"):
                yield Button("Guardar", variant="success", id="btn_save")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            payload = {
                "title": self.query_one("#inp_title", Input).value,
                "author_input": self.query_one("#inp_author", Input).value,
                "format_type": self.query_one("#inp_format", Input).value,
                "publisher": self.query_one("#inp_publisher", Input).value,
            }
            self.dismiss(payload)
        else:
            self.dismiss(None)


# ==============================================================================
# 🏠 PANTALLA PRINCIPAL: EL INVENTARIO
# ==============================================================================
class NeoLibraryApp(App):

    CSS = """
    Screen { background: $surface-darken-1; }
    DataTable { height: 100%; margin: 1 2; }
    #details_container { margin: 2 4; padding: 1 2; border: heavy $accent; background: $surface; }
    
    /* Estilos de los Modales Flotantes */
    IsbnModal, QuickEditModal { align: center middle; }
    #isbn_dialog { width: 40; height: 15; padding: 1 2; border: heavy $accent; background: $surface; }
    #edit_dialog { width: 50; height: 23; padding: 1 2; border: heavy $warning; background: $surface; }
    .modal_title { text-style: bold; margin-bottom: 1; }
    .form_buttons { height: auto; margin-top: 1; align: center middle; }
    Button { margin: 0 1; }
    """

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("a", "add_book", "Añadir (ISBN)"),  # 🚀 NUEVO
        ("e", "edit_book", "Editar Ficha"),  # 🚀 NUEVO
        ("d", "show_details", "Ver Detalles"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id="books_table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.add_columns("ID", "Título", "Autor",
                          "Formato", "Editorial", "Estado")
        self.load_books()

    @work(thread=True)
    def load_books(self) -> None:
        try:
            resp = httpx.get(API_LIBRARY, timeout=5.0)
            books = resp.json()
            orphan_books = [b for b in books if b.get('directory') is None]
            self.call_from_thread(self.populate_table, orphan_books)
        except Exception:
            self.app.call_from_thread(
                self.notify, "Fallo al cargar la biblioteca.", severity="error")

    def populate_table(self, books: list) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for book in books:
            status = "✔ Leído" if book.get('is_read') else "✘ Pendiente"
            row_key = str(book.get('id'))
            table.add_row(
                str(book.get('id')), book.get('title', 'Sin título').upper(),
                book.get('author_name', 'Desconocido'), book.get(
                    'format_type', '-'),
                book.get('publisher') or '-', status, key=row_key
            )
        table.focus()

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        self.query_one(DataTable).sort(event.column_key)

    def action_show_details(self) -> None:
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(
                table.cursor_coordinate).row_key.value
            if row_key:
                self.push_screen(BookDetailsScreen(book_id=row_key))
        except Exception:
            pass

    # 🚀 ACCIÓN 'A': AÑADIR LIBRO
    def action_add_book(self) -> None:
        # Callback: Qué hacer cuando el modal se cierra
        def check_isbn(isbn: str | None) -> None:
            if isbn:
                self.notify(
                    f"Buscando oráculos globales para {isbn}...", title="Escáner")
                self.process_isbn_add(isbn)

        # Abre el modal flotante
        self.push_screen(IsbnModal(), check_isbn)

    @work(thread=True)
    def process_isbn_add(self, isbn: str) -> None:
        try:
            resp = httpx.post(API_SCAN, json={"isbn": isbn}, timeout=10.0)
            if resp.status_code in [200, 201]:
                self.app.call_from_thread(
                    self.notify, "¡Libro registrado exitosamente!", title="Éxito")
                self.app.call_from_thread(self.load_books)  # Refresca la tabla
            else:
                self.app.call_from_thread(
                    self.notify, f"Error: {resp.json().get('error', 'Desconocido')}", severity="error")
        except Exception as e:
            self.app.call_from_thread(
                self.notify, f"Error de red: {e}", severity="error")

    # 🚀 ACCIÓN 'E': EDITAR LIBRO
    def action_edit_book(self) -> None:
        table = self.query_one(DataTable)
        try:
            row_key = table.coordinate_to_cell_key(
                table.cursor_coordinate).row_key.value
            if row_key:
                self.notify("Descargando ficha de edición...", timeout=1)
                self.fetch_and_edit(row_key)
        except Exception:
            self.notify("Selecciona un libro en la tabla primero.",
                        severity="warning")

    @work(thread=True)
    def fetch_and_edit(self, book_id: str) -> None:
        try:
            resp = httpx.get(f"{API_LIBRARY}{book_id}/", timeout=5.0)
            if resp.status_code == 200:
                book = resp.json()
                self.app.call_from_thread(
                    self.open_edit_modal_sync, book, book_id)
        except Exception:
            self.app.call_from_thread(
                self.notify, "Error al obtener datos.", severity="error")

    def open_edit_modal_sync(self, book: dict, book_id: str) -> None:
        # Callback: Qué hacer cuando se presiona "Guardar" en el Modal
        def save_changes(payload: dict | None) -> None:
            if payload:
                self.notify("Guardando cambios en el servidor...")
                self.process_edit(book_id, payload)
        self.push_screen(QuickEditModal(book), save_changes)

    @work(thread=True)
    def process_edit(self, book_id: str, payload: dict) -> None:
        try:
            resp = httpx.patch(f"{API_LIBRARY}{book_id}/",
                               json=payload, timeout=5.0)
            if resp.status_code == 200:
                self.app.call_from_thread(
                    self.notify, "¡Ficha actualizada!", title="Éxito")
                self.app.call_from_thread(self.load_books)
            else:
                self.app.call_from_thread(
                    self.notify, "Error al actualizar.", severity="error")
        except Exception:
            self.app.call_from_thread(
                self.notify, "Error de red.", severity="error")
