from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label, Checkbox
from textual.containers import Vertical, Horizontal, VerticalScroll


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
            self.dismiss(val)
        else:
            self.dismiss(None)


class FullEditModal(ModalScreen[dict]):
    """Ventana flotante con Scroll para editar toda la ficha."""

    def __init__(self, book: dict, **kwargs):
        super().__init__(**kwargs)
        self.book = book

    def compose(self) -> ComposeResult:
        with Vertical(id="full_edit_dialog"):
            yield Label(f"✏️ Editando: {self.book.get('title')}", classes="modal_title")
            with VerticalScroll():
                yield Input(value=self.book.get('title', ''), id="inp_title", placeholder="Título")
                yield Input(value=self.book.get('subtitle', ''), id="inp_sub", placeholder="Subtítulo")
                yield Input(value=self.book.get('author_name', ''), id="inp_author", placeholder="Autor")
                yield Input(value=self.book.get('format_type', ''), id="inp_format", placeholder="Formato (NOVEL, MANGA...)")
                yield Input(value=self.book.get('publisher', ''), id="inp_publisher", placeholder="Editorial")
                generos_str = ", ".join(self.book.get(
                    'genre_list', [])) if self.book.get('genre_list') else ""
                yield Input(value=generos_str, id="inp_genres", placeholder="Géneros (separados por coma)")
                yield Input(value=str(self.book.get('page_count', '')), id="inp_pages", placeholder="Páginas")
                yield Checkbox("✔ Libro Completado/Leído", value=self.book.get('is_read', False), id="chk_read")

            with Horizontal(classes="form_buttons"):
                yield Button("Guardar Cambios", variant="success", id="btn_save")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            pages_val = self.query_one("#inp_pages", Input).value
            payload = {
                "title": self.query_one("#inp_title", Input).value,
                "subtitle": self.query_one("#inp_sub", Input).value,
                "author_input": self.query_one("#inp_author", Input).value,
                "format_type": self.query_one("#inp_format", Input).value,
                "publisher": self.query_one("#inp_publisher", Input).value,
                "genre_input": self.query_one("#inp_genres", Input).value,
                "is_read": self.query_one("#chk_read", Checkbox).value,
            }
            if pages_val.isdigit():
                payload["page_count"] = int(pages_val)
            self.dismiss(payload)
        else:
            self.dismiss(None)


class LendModal(ModalScreen[str]):
    """Pequeño diálogo para preguntar el nombre del amigo."""

    def compose(self) -> ComposeResult:
        with Vertical(id="lend_dialog"):
            yield Label("🤝 Prestar Ejemplar", classes="modal_title")
            yield Input(placeholder="Nombre de tu amigo...", id="inp_friend")
            with Horizontal(classes="form_buttons"):
                yield Button("Prestar", variant="success", id="btn_lend")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_lend":
            self.dismiss(self.query_one("#inp_friend", Input).value)
        else:
            self.dismiss(None)


class DirModal(ModalScreen[dict]):
    """Pequeño diálogo para crear un Directorio."""

    def compose(self) -> ComposeResult:
        with Vertical(id="dir_dialog"):
            yield Label("📁 Nuevo Universo/Directorio", classes="modal_title")
            yield Input(placeholder="Nombre (Ej: DC Comics)", id="inp_dirname")
            yield Input(placeholder="Color (red, cyan, green...)", value="cyan", id="inp_dircolor")
            with Horizontal(classes="form_buttons"):
                yield Button("Crear", variant="success", id="btn_save")
                yield Button("Cancelar", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            self.dismiss({
                "name": self.query_one("#inp_dirname", Input).value,
                "color_hex": self.query_one("#inp_dircolor", Input).value
            })
        else:
            self.dismiss(None)
