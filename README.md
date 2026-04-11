# BUNKER (NeoLibrary 3.0)

Bunker es un Centro de Operaciones Multimedia operado 100% desde la terminal (TUI). Diseñado con una arquitectura de microservicios, permite gestionar tu biblioteca de libros y colección de películas físicas, apoyado por Scrapers que vigilan nuevos lanzamientos en segundo plano.

---

## Estructura del Proyecto

```
bunker/
├── bunker_core/                          # Configuración central de Django
│   ├── __init__.py
│   ├── asgi.py                           # Configuración ASGI para servidor
│   ├── settings.py                       # Configuración principal de Django
│   ├── urls.py                           # Rutas principales
│   ├── views.py                          # Vistas base
│   └── wsgi.py                           # Configuración WSGI para servidor
│
├── catalog/                              # App Django: Gestión de libros
│   ├── migrations/                       # Migraciones de BD (15 migraciones)
│   │   ├── 0001_initial.py
│   │   ├── 0002_remove_book_rating_...py
│   │   ├── 0003_friend_loan.py
│   │   ├── ... [12 más migraciones]
│   │   └── 0015_scaninbox.py
│   ├── templates/
│   │   └── catalog/
│   │       └── scanner.html              # Template para escaneo de códigos QR
│   ├── __init__.py
│   ├── admin.py                          # Configuración del panel admin
│   ├── apps.py
│   ├── models.py                         # Modelos de base de datos
│   ├── serializers.py                    # Serializadores DRF
│   ├── tests.py
│   ├── urls.py                           # Rutas de la app
│   └── views.py                          # Vistas de la app
│
├── movies/                               # App Django: Gestión de películas
│   ├── migrations/                       # Migraciones de BD (7 migraciones)
│   │   ├── 0001_initial.py
│   │   ├── 0002_moviewatcher_moviewishlist.py
│   │   ├── ... [5 más migraciones]
│   │   └── 0007_movie_production_company_movie_writers.py
│   ├── templates/
│   │   └── movies/
│   │       └── movie_scanner.html        # Template para escaneo de películas
│   ├── __init__.py
│   ├── admin.py                          # Configuración del panel admin
│   ├── apps.py
│   ├── commercial_oracle.py              # Integración con APIs comerciales
│   ├── models.py                         # Modelos de películas
│   ├── omdb_oracle.py                    # Integración OMDB
│   ├── serializers.py                    # Serializadores DRF
│   ├── tests.py
│   ├── tmdb_oracle.py                    # Integración TMDB
│   ├── urls.py                           # Rutas de la app
│   └── views.py                          # Vistas de la app
│
├── cli/                                  # Cliente Terminal (CLI/TUI)
│   ├── tui/                              # Interfaz de usuario textual
│   │   ├── __init__.py
│   │   ├── app.py                        # Aplicación Textual principal
│   │   ├── constants.py                  # Constantes de la TUI
│   │   ├── library_screen.py             # Pantalla de biblioteca
│   │   ├── movie_screens.py              # Pantallas de películas
│   │   ├── modals.py                     # Modales y diálogos
│   │   ├── screens.py                    # Pantallas adicionales
│   │   └── tabs.py                       # Gestión de pestañas
│   ├── __init__.py
│   ├── api.py                            # Cliente API (comunicación con backend)
│   ├── books.py                          # Comandos CLI para libros
│   ├── directories.py                    # Gestión de directorios
│   ├── loans.py                          # Gestión de préstamos
│   ├── main.py                           # Punto de entrada CLI
│   ├── tracker.py                        # Seguimiento de actividades
│   └── wishlist.py                       # Gestión de listas de deseos
│
├── scraper/                              # Scraper Node.js
│   ├── strategies/
│   │   ├── books/                        # Estrategias de scraping para libros
│   │   │   ├── alfaguara.js
│   │   │   ├── anagrama.js
│   │   │   ├── antartica.js
│   │   │   ├── buscalibre.js
│   │   │   ├── distrito_manga.js
│   │   │   ├── ecc.js
│   │   │   ├── ivrea.js
│   │   │   ├── minotauro.js
│   │   │   ├── norma.js
│   │   │   ├── panini.js
│   │   │   ├── penguin.js
│   │   │   └── planeta.js
│   │   └── movies/                       # Estrategias de scraping para películas
│   │       ├── amazon_usa.js
│   │       ├── bluray_com.js
│   │       └── buscalibre_usa.js
│   ├── Dockerfile                        # Imagen Docker del scraper
│   ├── book_radar.js                     # Scraper de libros
│   ├── movie_radar.js                    # Scraper de películas
│   ├── package.json                      # Dependencias Node.js
│   └── package-lock.json
│
├── library_cli.egg-info/                 # Metadatos del paquete Python
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── requires.txt
│   └── top_level.txt
│
├── docker-compose.yml                    # Orquestación de contenedores
├── Dockerfile                            # Imagen Docker del backend
├── .dockerignore                         # Archivos a ignorar en Docker
├── .gitignore                            # Archivos a ignorar en Git
├── .env                                  # Variables de entorno (local)
├── manage.py                             # Herramienta de administración Django
├── install.sh                            # Script de instalación
├── requirements.txt                      # Dependencias Python (pip)
├── pyproject.toml                        # Configuración del proyecto Python
├── package.json                          # Dependencias Node.js del proyecto
├── package-lock.json                     # Lock file de npm (árbol exacto de dependencias)
└── README.md                             # Este archivo
```

````

---

## Descripción por Módulo

### `bunker_core/` - Núcleo de Django
Contiene la configuración central de la aplicación Django, incluyendo rutas, configuraciones globales y vistas base.

### `catalog/` - Gestión de Libros
App Django que implementa todo el CRUD para la biblioteca de libros, incluyendo modelos, serializadores API y migraciones de BD.

### `movies/` - Gestión de Películas
App Django para gestionar la colección de películas con integración a APIs de TMDB y OMDB para obtener información de películas.

### `cli/` - Cliente de Terminal
Aplicación terminal interactiva construida con **Textual** y **Typer**, con una TUI multi-pestaña que permite navegar e interactuar con la biblioteca y colección de películas desde la terminal.

### `scraper/` - Scraper de Novedades
Servicio Node.js que scraatea múltiples editoriales y plataformas de películas en segundo plano para detectar nuevos lanzamientos, utilizando un sistema de estrategias extensible.

---

## Características Principales

- **Interfaz TUI:** Navegación por pestañas, modales flotantes, y un "Grid Cinematográfico" construidos con Textual y Typer.
- **Scraper (Node.js):** Un scraper asíncrono que busca novedades literarias en Google Books y estrenos cinematográficos en The Movie Database (TMDB).
- **Escáner Móvil:** Levanta un túnel SSH en background y renderiza un código QR en ASCII dentro de la terminal para escanear códigos de barras (ISBN/UPC) con la cámara de tu teléfono.
- Sincronización automática entre el registro de hábitos anuales y el inventario principal.

---

## Requisitos

Asegúrate de tener instalados los siguientes componentes en tu sistema operativo (Linux/macOS):

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/)
- `git`
- Una API Key gratuita de [The Movie Database (TMDB)](https://developer.themoviedb.org/docs/getting-started)

---

## Guía de Instalación

Sigue estos pasos en orden para desplegar la arquitectura completa en tu máquina local.

### 1. Clonar el Repositorio

```bash
git clone [https://github.com/RicketyMajor/library-manager.git](https://github.com/RicketyMajor/library-manager.git)
cd library-manager
````

### 2. Configurar Variables de Entorno

```bash
touch .env
```

```
TMDB_API_KEY=...
```

### 3. Levantar Docker

```bash
docker-compose up -d --build
```

### 4. Ejecutar Migraciones de Base de Datos

```bash
docker-compose exec web python manage.py migrate
```

### 5. Crear Superusuario

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Instalar el Cliente de Terminal

```bash
chmod +x install.sh
./install.sh
```
