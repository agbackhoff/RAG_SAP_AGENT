FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar archivos necesarios
COPY src/hello.py .
COPY sap_tables.csv .

# Crear el directorio de output
RUN mkdir output

CMD ["python", "hello.py"]