const axios = require('axios');
const cheerio = require('cheerio');

module.exports = {
    name: 'Buscalibre USA (Películas)',
    scrape: async function(keywords = [], apiUrl) {
        const releases = [];
        if (keywords.length === 0) return releases;

        for (const keyword of keywords) {
            // URL apuntando a la versión US (.us) y a la categoría de películas
            const searchUrl = `https://www.buscalibre.us/peliculas/search?q=${encodeURIComponent(keyword)}&sst=novedades`;

            try {
                const response = await axios.get(searchUrl, {
                    headers: { 'User-Agent': 'Mozilla/5.0' }
                });

                const $ = cheerio.load(response.data);

                $('.producto').slice(0, 3).each((index, element) => {
                    const title = $(element).find('.nombre, h3').text().trim();
                    
                    if (title) {
                        releases.push({
                            title: title,
                            director: keyword,
                            release_year: new Date().getFullYear().toString()
                        });
                    }
                });

                await new Promise(resolve => setTimeout(resolve, 1500));
            } catch (error) {
                console.error(`   Error buscando '${keyword}' en Buscalibre USA: ${error.message}`);
            }
        }
        return releases;
    }
};