const axios = require('axios');
const cheerio = require('cheerio');

module.exports = {
    name: 'Blu-ray.com Global',
    scrape: async function(keywords = [], apiUrl) {
        const releases = [];
        if (keywords.length === 0) return releases;

        for (const keyword of keywords) {
            // URL de búsqueda directa en la base de datos de Blu-ray.com
            const searchUrl = `https://www.blu-ray.com/movies/search.php?keyword=${encodeURIComponent(keyword)}&action=search`;

            try {
                const response = await axios.get(searchUrl, {
                    headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36' }
                });

                const $ = cheerio.load(response.data);

                // Extrayendo los títulos de la tabla de resultados
                $('a.title').slice(0, 3).each((index, element) => {
                    const title = $(element).text().trim();
                    
                    // Si el título existe, lo prepara para el modelo de Django MovieWishlist
                    if (title) {
                        releases.push({
                            title: title,
                            director: keyword, // Usa la palabra clave vigilada como referencia
                            release_year: new Date().getFullYear().toString() // Asume lanzamiento reciente
                        });
                    }
                });

                await new Promise(resolve => setTimeout(resolve, 1500)); 
            } catch (error) {
                console.error(`   Error buscando '${keyword}' en Blu-ray.com: ${error.message}`);
            }
        }
        return releases;
    }
};