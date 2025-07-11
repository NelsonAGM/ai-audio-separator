# Etapa de build (Node)
FROM node:18-slim as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa final: Node + Python + ffmpeg
FROM node:18-slim

# Instala Python, ffmpeg y dependencias mínimas
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg libsndfile1 && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia solo lo necesario
COPY --from=build-stage /app/dist-server ./dist-server
COPY --from=build-stage /app/dist/public ./client/dist
COPY --from=build-stage /app/server ./server
COPY --from=build-stage /app/shared ./shared
COPY --from=build-stage /app/package*.json ./
COPY --from=build-stage /app/server/services/requirements.txt ./server/services/requirements.txt

# Instala dependencias de Node solo para producción
RUN npm ci --only=production

# Instala dependencias de Python
RUN pip install --no-cache-dir --break-system-packages -r server/services/requirements.txt

EXPOSE 5000

CMD ["npm", "start"] 