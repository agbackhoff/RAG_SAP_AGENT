# Analizador de Tablas SAP

Este proyecto es una herramienta para analizar y procesar tablas SAP utilizando modelos de lenguaje de última generación (LLMs).

## Descripción

El analizador utiliza Gemini 1.5 Pro de Google para procesar y generar estructuras de datos para tablas SAP. Integra las siguientes tecnologías:

- Google Gemini 1.5 Pro para procesamiento de lenguaje natural
- DSPy para interacción con LLMs
- Logging comprehensivo para seguimiento de operaciones
- Manejo de variables de entorno para configuración segura

## Proceso de Desarrollo

### 1. Configuración Inicial

1. Crear estructura básica del proyecto:
   - src/hello.py: Script principal
   - requirements.txt: Dependencias
   - Dockerfile: Configuración de contenedor
   - docker-compose.yml: Orquestación de servicios
   - .env: Variables de entorno

2. Configurar dependencias en requirements.txt:
   - google-generativeai>=0.3.0
   - dspy-ai>=2.0.0
   - python-dotenv==1.0.0
   - requests>=2.31.0
   - beautifulsoup4>=4.12.0

### 2. Implementación del Script Principal

1. Configuración de logging y variables de entorno:
   - Crear directorio output/
   - Configurar formato de logs
   - Cargar API key de Gemini

2. Implementación de clases principales:
   - SAPTableAnalyzer: Para extraer información de tablas
   - TableStructureGenerator: Para generar estructuras JSON

3. Implementación de funciones principales:
   - process_tables(): Procesa lotes de tablas
   - get_table_info(): Obtiene información de una tabla específica
   - _get_fields(): Extrae campos de una tabla

### 3. Proceso de Pruebas y Mejoras

1. Prueba inicial con tabla TCURR:
   - Verificar conexión con Gemini
   - Validar extracción de datos
   - Generar archivo tcurr_structure.json

2. Mejoras en manejo de errores:
   - Validación de campos existentes
   - Verificación de JSON válido
   - Logging detallado de errores

3. Implementación de guardado progresivo:
   - Guardar resultados después de cada tabla exitosa
   - Mantener progreso en caso de fallos

### 4. Uso del Sistema

1. Preparar archivo de entrada:
   - Crear sap_tables.csv con lista de tablas
   - Formato: Una tabla por línea
   - Eliminar encabezados y caracteres especiales

2. Configurar variables de entorno:
   ```
   GOOGLE_API_KEY=tu-api-key-aqui
   ```

3. Ejecutar con Docker:
   ```
   docker-compose up --build
   ```

4. Verificar resultados:
   - output/tcurr_structure.json: Resultado de prueba inicial
   - output/sap_tables_structure.json: Resultado completo
   - output/app.log: Registro de operaciones

### 5. Estructura de Salida

El sistema genera archivos JSON con la siguiente estructura:
```json
{
    "table_name": {
        "name": "nombre_tabla",
        "description": "descripción_tabla",
        "fields": [
            {
                "name": "nombre_campo",
                "data_element": "elemento_dato",
                "type": "tipo_dato",
                "length": "longitud",
                "decimals": "decimales"
            }
        ]
    }
}
```

### 6. Manejo de Errores

El sistema implementa varios niveles de manejo de errores:

1. Validación de entrada:
   - Verificación de archivo CSV
   - Validación de API key
   - Comprobación de nombres de tabla

2. Procesamiento de datos:
   - Verificación de campos existentes
   - Validación de JSON
   - Manejo de respuestas de API

3. Almacenamiento:
   - Guardado progresivo
   - Verificación de permisos de escritura
   - Manejo de errores de archivo

## Contribuir

1. Fork el proyecto
2. Crear rama feature
3. Commit cambios
4. Push a la rama
5. Crear Pull Request

## Licencia

MIT

## Autor

[Tu nombre]