from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Button, Label
from textual.containers import Vertical, Horizontal


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
