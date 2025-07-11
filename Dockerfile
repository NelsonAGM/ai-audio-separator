# Multi-stage build para optimizar el tamaño
FROM python:3.11-slim as python-base

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements de Python
COPY server/services/requirements.txt ./requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de Python
COPY server/services/ ./services/

# Stage 2: Node.js para el servidor
FROM node:18-alpine as node-base

WORKDIR /app

# Copiar package.json
COPY package*.json ./

# Instalar dependencias de Node.js
RUN npm ci --only=production

# Copiar código del servidor
COPY server/ ./server/
COPY shared/ ./shared/

# Copiar cliente construido
COPY client/dist/ ./client/dist/

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["npm", "start"] 