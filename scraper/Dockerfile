# Usa una imagen oficial y ultra ligera de Node.js
FROM node:20-alpine

# Instalar Chromium y dependencias para Puppeteer
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    nodejs \
    npm

# Puppeteer usa el Chrome instalado en el sistema
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el package.json para aprovechar la caché de Docker
COPY package.json ./

# Instala las dependencias
RUN npm install

# Copia el resto del código
COPY . .

# Comando para iniciar el servicio
CMD ["npm", "start"]