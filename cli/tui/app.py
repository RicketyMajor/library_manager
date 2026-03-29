import httpx
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable
from textual import work

API_LIBRARY = "http://localhost:8000/api/books/library/"


class NeoLibraryApp(App):
    """El nuevo entorno inmersivo TUI de tu biblioteca (Estilo Neovim)."""

    # CSS básico integrado para dimensionar la tabla
    CSS = """
    Screen {
        background: $surface-darken-1;
    }
    DataTable {
        height: 100%;
        margin: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Salir de la Biblioteca"),
        # La tabla ya soporta j, k, flechas y PgUp/PgDown de forma nativa
    ]

    def compose(self) -> ComposeResult:
        """Dibuja los elementos principales de la interfaz."""
        yield Header(show_clock=True)
        # Añadimos la tabla con un ID para poder referenciarla luego
        yield DataTable(id="books_table")
        yield Footer()

    def on_mount(self) -> None:
        """Se ejecuta una única vez cuando la aplicación arranca."""
        table = self.query_one(DataTable)

        # Configuración al estilo Neovim
        table.cursor_type = "row"  # Selecciona toda la fila, no solo una celda
        table.zebra_stripes = True  # Filas intercaladas de color para mejor lectura

        # Definimos las columnas
        table.add_columns("ID", "Título", "Autor",
                          "Formato", "Editorial", "Estado")

        # Disparamos la carga de datos en segundo plano
        self.load_books()

    @work(thread=True)
    def load_books(self) -> None:
        """Consume la API en un hilo separado para no congelar la interfaz (Asincronía)."""
        try:
            resp = httpx.get(API_LIBRARY, timeout=5.0)
            books = resp.json()

            # Filtramos para mostrar solo la raíz (igual que el comando 'ls')
            orphan_books = [b for b in books if b.get('directory') is None]

            # El TUI se actualiza mediante call_from_thread para evitar choques de memoria
            self.call_from_thread(self.populate_table, orphan_books)

        except Exception as e:
            # Si falla la red, podríamos mostrar una notificación, pero por ahora lo dejamos limpio
            pass

    def populate_table(self, books: list) -> None:
        """Inyecta los datos en la interfaz de forma segura."""
        table = self.query_one(DataTable)
        table.clear()

        for book in books:
            status = "✔ Leído" if book.get('is_read') else "✘ Pendiente"

            # EL TRUCO MAESTRO: Guardamos el ID de la base de datos como llave de la fila
            # Esto será vital para la Fase 40 cuando presiones 'D' o 'E'
            row_key = str(book.get('id'))

            table.add_row(
                str(book.get('id')),
                book.get('title', 'Sin título').upper(),
                book.get('author_name', 'Desconocido'),
                book.get('format_type', '-'),
                book.get('publisher') or '-',
                status,
                key=row_key
            )

        # Le damos el foco a la tabla para que puedas usar el teclado de inmediato
        table.focus()

    # ORDENAMIENTO DINÁMICO
    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Se dispara al hacer clic en las cabeceras de las columnas para ordenar."""
        table = self.query_one(DataTable)
        # Ordena usando la columna clickeada (como texto)
        table.sort(event.column_key)
