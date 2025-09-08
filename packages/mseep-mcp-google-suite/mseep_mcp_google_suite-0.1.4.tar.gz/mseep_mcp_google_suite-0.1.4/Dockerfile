FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv (gestor moderno de dependencias)
RUN pip install uv

# Copiar archivos requeridos
COPY . /app
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/
COPY .smithery.yaml .smithery.yaml
# Copia el archivo de definición de herramientas de Smithery

COPY .smithery.yaml /app/.smithery.yaml


# Instalar dependencias usando uv en el entorno global
RUN uv pip install --no-cache --system .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear usuario no root por buenas prácticas
RUN useradd -m -u 1000 mcp

# Cambiar permisos
RUN chown -R mcp:mcp /app

# Cambiar a usuario mcp
USER mcp

# Expone el puerto que Smithery necesita (ajústalo si usas otro)
EXPOSE 3001


# Definir el punto de entrada para ejecutar el módulo directamente
CMD ["python", "-m", "mcp_google_suite"]
