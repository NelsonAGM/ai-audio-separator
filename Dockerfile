# Etapa 1: Build del frontend y backend desde la raíz
FROM node:18-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa 2: Backend y producción
FROM python:3.11-slim as python-base
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server/services/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY server/services/ ./services/

FROM node:18-alpine as node-base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY server/ ./server/
COPY shared/ ./shared/
# Copiar el backend compilado
COPY --from=build-stage /app/dist-server ./dist-server/
# Copiar el frontend generado
COPY --from=build-stage /app/dist ./client/dist/
EXPOSE 5000
CMD ["npm", "start"] 