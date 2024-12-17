import logging
import os
import json
from datetime import datetime
import google.generativeai as genai
import dspy
from dotenv import load_dotenv
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

# Cargar variables de entorno
load_dotenv()

# Configurar logging
os.makedirs('output', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurar Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Por favor configura GOOGLE_API_KEY en el archivo .env")

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro')

# Configurar DSPy con Gemini
lm = dspy.LM('gemini/gemini-1.5-pro', api_key=GOOGLE_API_KEY)
dspy.settings.configure(lm=lm)

class SAPTableAnalyzer:
    BASE_URL = "https://leanx.eu/en/sap/table/"
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Obtiene información de una tabla SAP específica"""
        try:
            url = f"{self.BASE_URL}{table_name.lower()}.html"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información de la tabla
            table_data = {
                "table_name": table_name,
                "description": self._get_description(soup),
                "fields": self._get_fields(soup)
            }
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error obteniendo información para tabla {table_name}: {str(e)}")
            return None
    
    def _get_description(self, soup: BeautifulSoup) -> str:
        """Extrae la descripción de la tabla"""
        try:
            return soup.find('h1').text.strip()
        except:
            return ""
    
    def _get_fields(self, soup: BeautifulSoup) -> List[Dict]:
        """Extrae información de los campos de la tabla"""
        fields = []
        try:
            table = soup.find('table')
            if not table:
                return fields
                
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 4:
                    field = {
                        "name": cols[0].text.strip(),
                        "data_element": cols[1].text.strip(),
                        "type": cols[3].text.strip(),
                        "length": cols[4].text.strip() if len(cols) > 4 else "",
                        "decimals": cols[5].text.strip() if len(cols) > 5 else "",
                    }
                    fields.append(field)
            
            return fields
        except Exception as e:
            logger.error(f"Error extrayendo campos: {str(e)}")
            return fields

class TableStructureGenerator(dspy.Signature):
    """Genera una estructura JSON para una tabla SAP"""
    table_info = dspy.InputField()
    structure = dspy.OutputField(desc="""Genera un JSON válido con esta estructura exacta:
    {
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
    }""")

    def validate_structure(self, value):
        """Asegura que la salida sea JSON válido"""
        try:
            if isinstance(value, str):
                json.loads(value)
            return True
        except:
            return False

generator = dspy.Predict(TableStructureGenerator)

def process_tables(table_names: List[str]) -> Dict:
    """Procesa una lista de tablas SAP y genera sus estructuras"""
    analyzer = SAPTableAnalyzer()
    structures = {}
    
    for table_name in table_names:
        logger.info(f"Procesando tabla: {table_name}")
        
        # Obtener información de la tabla
        table_info = analyzer.get_table_info(table_name)
        if not table_info:
            logger.info(f"No se encontró información para la tabla {table_name}, continuando con la siguiente...")
            continue
            
        # Verificar si la tabla tiene campos
        if not table_info.get("fields"):
            logger.info(f"La tabla {table_name} no tiene campos definidos, continuando con la siguiente...")
            continue
            
        # Usar DSPy para generar la estructura
        try:
            result = generator(table_info=table_info)
            try:
                json_structure = json.loads(result.structure)
            except:
                # Si falla, crear una estructura JSON básica
                json_structure = {
                    "name": table_info["table_name"],
                    "description": table_info["description"],
                    "fields": table_info["fields"]
                }
            
            # Verificar que la estructura tenga campos antes de guardarla
            if json_structure.get("fields"):
                structures[table_name] = json_structure
                logger.info(f"Estructura generada para tabla {table_name}")
                
                # Guardar el progreso después de cada tabla exitosa
                output_file = "output/sap_tables_structure.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(structures, f, indent=2, ensure_ascii=False)
            else:
                logger.info(f"La tabla {table_name} no generó campos válidos, continuando con la siguiente...")
                
        except Exception as e:
            logger.error(f"Error generando estructura para {table_name}: {str(e)}")
            continue
    
    return structures

def main():
    logger.info("Iniciando análisis de tablas SAP")
    
    try:
        # PASO 1: Prueba inicial con TCURR
        logger.info("\n=== INICIANDO PRUEBA CON TABLA TCURR ===")
        test_table = "TCURR"
        
        # Crear analizador para la prueba
        analyzer = SAPTableAnalyzer()
        logger.info(f"Obteniendo información de tabla de prueba: {test_table}")
        
        # Obtener información de TCURR
        table_info = analyzer.get_table_info(test_table)
        if table_info:
            try:
                result = generator(table_info=table_info)
                # Intentar parsear el JSON o usar un JSON por defecto
                try:
                    json_structure = json.loads(result.structure)
                except:
                    # Si falla, crear una estructura JSON básica
                    json_structure = {
                        "name": table_info["table_name"],
                        "description": table_info["description"],
                        "fields": table_info["fields"]
                    }
                
                test_structure = {test_table: json_structure}
                
                # Guardar resultado de la prueba
                test_output_file = "output/tcurr_structure.json"
                with open(test_output_file, "w", encoding="utf-8") as f:
                    json.dump(test_structure, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Prueba completada - Estructura de TCURR guardada en {test_output_file}")
            except Exception as e:
                logger.error(f"Error en prueba con TCURR: {str(e)}")
                return  # Si falla la prueba, no continuamos con el proceso completo
        else:
            logger.error("No se pudo obtener información de TCURR")
            return
            
        logger.info("=== FIN DE PRUEBA CON TABLA TCURR ===\n")
        
        # Preguntar si continuar con el proceso completo
        logger.info("=== INICIANDO PROCESO COMPLETO ===")
        
        # Leer y limpiar nombres de tablas
        with open('sap_tables.csv', 'r') as f:
            tables = []
            for line in f:
                table_name = line.strip().strip('",').strip()
                if table_name and not table_name.startswith("table_name"):
                    tables.append(table_name)
        
        if not tables:
            logger.error("El archivo sap_tables.csv está vacío")
            return
            
        logger.info(f"Se encontraron {len(tables)} tablas para procesar")
        
        # Procesar tablas
        structures = process_tables(tables)
        
        # Guardar resultado
        output_file = "output/sap_tables_structure.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(structures, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Estructuras guardadas en {output_file}")
        logger.info("=== FIN DEL PROCESO COMPLETO ===")
        
    except FileNotFoundError:
        logger.error("No se encontró el archivo sap_tables.csv")
    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
    
    logger.info("Proceso finalizado")

if __name__ == "__main__":
    main()