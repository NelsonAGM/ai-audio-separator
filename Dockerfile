# Etapa de build (Node)
FROM node:18-bullseye as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa final: Node + Python + dependencias
FROM node:18-bullseye

# Instala Python y utilidades necesarias
RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg libsndfile1 && \
    ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Copia dependencias y código
COPY --from=build-stage /app /app

# Instala dependencias de Node solo para producción
RUN npm ci --only=production

# Instala dependencias de Python
RUN pip install --no-cache-dir -r server/services/requirements.txt

EXPOSE 5000

CMD ["npm", "start"] 