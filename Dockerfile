# Usa una imagen oficial de Python como imagen base
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo pyproject.toml y poetry.lock (si existe) para instalar las dependencias
COPY pyproject.toml poetry.lock* /app/

# Instala Poetry
RUN pip install poetry

# Instala las dependencias del proyecto sin usar el entorno virtual de Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copia el contenido del directorio actual en el contenedor en /app
COPY . /app

# Expone el puerto 5000 al mundo exterior
EXPOSE 5000

# Ejecuta la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
