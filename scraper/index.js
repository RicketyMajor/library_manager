const axios = require('axios');
const fs = require('fs');
const path = require('path');
const Fuse = require('fuse.js'); // El motor de coincidencias difusas

// Módulo Literario
const API_BOOKS_WATCHERS = 'http://web:8000/api/books/watchers/';
const API_BOOKS_WISHLIST = 'http://web:8000/api/books/wishlist/add/';

// Módulo Cinematográfico
const API_MOVIES_WATCHERS = 'http://web:8000/api/movies/watchers/';
const API_MOVIES_WISHLIST = 'http://web:8000/api/movies/wishlist/';
const API_BASE = 'http://web:8000/api'; // La IP interna de Docker
const TMDB_API_KEY = process.env.TMDB_API_KEY;


async function getWatchers(url) {
    try {
        const response = await axios.get(url);
        return response.data.keywords || []; // En el futuro, ajusta según el JSON del Videoclub
    } catch (error) {
        console.error(`Error conectando con ${url}:`, error.message);
        return [];
    }
}
async function sendToWishlist(item, targetUrl) {
    try {
        const response = await axios.post(targetUrl, item);
        if (response.status === 201) {
            console.log(`   > Guardado en Tablón: ${item.title}`);
        }
    } catch (error) {
        console.error(`   Error enviando '${item.title}':`, error.response?.data || error.message);
    }
}

/**
 * Consulta a Google Books para descartar reposiciones
 */
async function verifyNewRelease(title) {
    try {
        const searchUrl = `https://www.googleapis.com/books/v1/volumes?q=intitle:${encodeURIComponent(title)}&maxResults=1`;
        const response = await axios.get(searchUrl);

        if (response.data.items && response.data.items.length > 0) {
            const pubDate = response.data.items[0].volumeInfo.publishedDate; // Ej: "2011", "2023-11-08"
            if (pubDate) {
                const pubYear = parseInt(pubDate.substring(0, 4));
                const currentYear = new Date().getFullYear();

                if (currentYear - pubYear > 2) {
                    return { isNew: false, year: pubYear };
                }
            }
        }
        // Si no lo encuentra o es reciente, le da el beneficio de la duda
        return { isNew: true, year: "Reciente/Desconocido" }; 
    } catch (error) {
        return { isNew: true, year: "Error API" }; // No bloquea si falla la red
    }
}

async function syncMovies() {
    console.log("[MOVIE RADAR] Iniciando barrido en The Movie Database...");
    
    if (!TMDB_API_KEY || TMDB_API_KEY === 'tu_clave_de_tmdb_aqui') {
        console.error("[MOVIE RADAR] Falta la TMDB_API_KEY válida en el entorno.");
        return;
    }

    try {
        // Obtiene a quién vigila
        const watchersRes = await axios.get(`${API_BASE}/movies/watchers/`);
        const watchers = watchersRes.data.filter(w => w.is_active);
        
        if (watchers.length === 0) {
            console.log("[MOVIE RADAR] No hay directores ni sagas en la lista de vigilancia.");
            return;
        }

        // Obtiene Wishlist actual para no guardar duplicados
        const wishlistRes = await axios.get(`${API_BASE}/movies/wishlist/`);
        const existingIds = wishlistRes.data.map(w => w.tmdb_id);
        
        // Define umbral de "Novedad" 
        const currentYear = new Date().getFullYear();
        const thresholdYear = currentYear - 1;

        for (const watcher of watchers) {
            console.log(`\n[MOVIE RADAR] Escaneando frecuencia: "${watcher.keyword}"`);
            
            // Busca la palabra clave en TMDB
            const searchUrl = `https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(watcher.keyword)}&language=es-ES`;
            const response = await axios.get(searchUrl);
            const movies = response.data.results;

            let foundNew = false;

            for (const movie of movies) {
                const releaseYear = movie.release_date ? parseInt(movie.release_date.substring(0, 4)) : 9999; // 9999 = TBA (To Be Announced)
                
                // Solo películas recientes/futuras y que no estén ya en la wishlist
                if (releaseYear >= thresholdYear && !existingIds.includes(movie.id)) {
                    console.log(`[MOVIE RADAR] ¡Impacto detectado! -> ${movie.title} (${releaseYear === 9999 ? 'TBA' : releaseYear})`);
                    
                    // Inyecta el hallazgo al Bunker
                    await axios.post(`${API_BASE}/movies/wishlist/`, {
                        title: movie.title,
                        release_year: releaseYear === 9999 ? 'TBA' : releaseYear.toString(),
                        tmdb_id: movie.id,
                        is_rejected: false
                    });
                    
                    // Actualiza memoria local
                    existingIds.push(movie.id);
                    foundNew = true;
                }
            }
            if (!foundNew) console.log(`   [MOVIE RADAR] Sin novedades para "${watcher.keyword}".`);
        }
        
        console.log("\n[MOVIE RADAR] Barrido cinematográfico completado exitosamente.");

    } catch (error) {
        console.error("[MOVIE RADAR] Error de conexión con el satélite:", error.message);
    }
}

/**
 * Carga dinámicamente todas las estrategias de scraping
 */
function loadStrategies() {
    const strategies = [];
    const strategiesPath = path.join(__dirname, 'strategies');
    
    // Lee todos los archivos dentro de la carpeta 'strategies'
    if (fs.existsSync(strategiesPath)) {
        const files = fs.readdirSync(strategiesPath);
        for (const file of files) {
            if (file.endsWith('.js')) {
                const strategy = require(path.join(strategiesPath, file));
                // Solo cargamos si el archivo tiene el formato correcto
                if (strategy.name && typeof strategy.scrape === 'function') {
                    strategies.push(strategy);
                }
            }
        }
    }
    return strategies;
}

/**
 * Extrae, consolida y aplica Inteligencia Artificial
 */
async function runScrapers(keywords) {
    if (keywords.length === 0) {
        console.log("No hay palabras clave para vigilar. Abortando.");
        return;
    }

    console.log(`Iniciando vigilancia para: [ ${keywords.join(', ')} ]`);
    const strategies = loadStrategies();
    let allReleases = []; 

    // Recolecta lanzamientos de todas las editoriales (El Multiverso)
    for (const strategy of strategies) {
        console.log(`\nConsultando a: ${strategy.name}...`);
        try {
            // pasa las palabras clave a la estrategia
            const releases = await strategy.scrape(keywords); 
            allReleases = allReleases.concat(releases);
            console.log(`   ${releases.length} lanzamientos obtenidos de ${strategy.name}`);
        } catch (error) {
            console.error(`   Error crítico en ${strategy.name}:`, error.message);
        }
    }

    // Motor Fuzzy Matching
    console.log(`\nAnalizando ${allReleases.length} libros encontrados en total...`);
    
    // fuse.js perdona errores ortográficos, símbolos extra (como "Vol. 13") y mayúsculas
    const fuseOptions = {
        keys: ['title'],
        threshold: 0.3, // 0.0 es idéntico, 1.0 empareja cualquier cosa. 0.3 es el punto para mangas/libros.
        ignoreLocation: true
    };
    const fuse = new Fuse(allReleases, fuseOptions);

    // Evalua cada palabra clave contra el universo de lanzamientos
    for (const keyword of keywords) {
        const results = fuse.search(keyword);
        
        if (results.length > 0) {
            console.log(`\n¡MATCH PARA '${keyword}'! Analizando ${results.length} coincidencias...`);
            
            for (const result of results) {
                const item = result.item;
                
                const verification = await verifyNewRelease(item.title);

                if (!verification.isNew) {
                    console.log(`    Descartado por Reposición: '${item.title}' (Publicado originalmente en ${verification.year})`);
                    continue; 
                }

                item.author_string = keyword;
                await sendToWishlist(item, API_BOOKS_WISHLIST);
            }
        }
    }
}

async function runAllRadars() {
    console.log("==================================================");
    console.log("INICIANDO SISTEMAS DE RASTREO DEL BUNKER");
    console.log("==================================================");
    
    // 1. Radar Literario
    console.log("[RADAR] Escaneando novedades literarias...");
    const bookKeywords = await getWatchers(API_BOOKS_WATCHERS);
    await runScrapers(bookKeywords); 
    
    console.log("--------------------------------------------------");
    
    // 2. Radar Cinematográfico
    console.log("[RADAR] Consultando el oráculo de TMDB...");
    const movieKeywords = await getWatchers(API_MOVIES_WATCHERS);
    await syncMovies(movieKeywords, API_MOVIES_WISHLIST); 
    
    console.log("==================================================");
    console.log("Radares en reposo. Esperando próxima ventana...");
}

console.log("[SISTEMA] Esperando 15 segundos a que el Bunker (Django) esté en línea...");

setTimeout(async () => {
    // 2. Ejecuta el primer barrido
    await runAllRadars();
    
    // 3. ejecutándose cada 12 horas
    const DOCE_HORAS = 1000 * 60 * 60 * 12;
    setInterval(runAllRadars, DOCE_HORAS);
    
}, 15000);
