const axios = require('axios');
const cheerio = require('cheerio');

module.exports = {
    name: 'Buscalibre Chile',
    scrape: async function(keywords = []) {
        const releases = [];
        if (keywords.length === 0) return releases;

        for (const keyword of keywords) {
            const searchUrl = `https://www.buscalibre.cl/libros/search?q=${encodeURIComponent(keyword)}`;

            try {
                const response = await axios.get(searchUrl, {
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
                    }
                });

                const $ = cheerio.load(response.data);

                $('.producto').slice(0, 3).each((index, element) => {
                    const title = $(element).find('.nombre, h3').text().trim();
                    const link = $(element).find('a').attr('href');
                    
                    // 🥷 TÁCTICA NINJA: Búsqueda agresiva del precio
                    // 1. Capturamos todo el texto de cualquier elemento que huela a precio
                    let rawPrice = $(element).find('[class*="precio"], .p-precio').text().trim();
                    
                    // Si no encuentra nada, tomamos todo el texto de la tarjeta
                    if (!rawPrice) rawPrice = $(element).text();
                    
                    // 2. Usamos Expresiones Regulares (Regex) para cazar el patrón chileno: "$ 15.000" o "$15.000"
                    const priceMatch = rawPrice.match(/\$\s*[\d\.]+/);
                    const finalPrice = priceMatch ? priceMatch[0] : 'Precio no detectado';

                    if (title) {
                        releases.push({
                            title: title,
                            publisher: "Buscalibre",
                            price: finalPrice, // ¡Ahora inyectamos el precio cazado con Regex!
                            buy_url: link.startsWith('http') ? link : `https://www.buscalibre.cl${link}`,
                            cover_url: ""
                        });
                    }
                });

                await new Promise(resolve => setTimeout(resolve, 1500));

            } catch (error) {
                console.error(`   ❌ Error buscando '${keyword}' en Buscalibre: ${error.message}`);
            }
        }
        
        return releases;
    }
};