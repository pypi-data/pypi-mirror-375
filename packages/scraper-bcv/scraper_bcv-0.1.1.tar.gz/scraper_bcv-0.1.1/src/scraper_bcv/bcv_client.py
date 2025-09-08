# src/bcv_client.py
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import urllib3

import requests
from bs4 import BeautifulSoup

def setup_logger(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """Configura y devuelve un logger nombrado 'get_dolar'.
    Si se pasa log_file, se escribe también en ese archivo.
    """
    logger = logging.getLogger('get_dolar')
    logger.setLevel(level)

    # Evitar añadir handlers duplicados si ya fue configurado
    if logger.handlers:
        return logger

    fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Handler de consola (INFO)
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # Handler de archivo si se especifica
    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


class BCVClient:
    """
    Cliente para obtener tasas de referencia del Banco Central de Venezuela (BCV).
    """
    
    def __init__(self, log_file: Optional[str] = None, log_level: int = logging.INFO):
        self.logger = setup_logger(log_file, log_level)
        self.url = 'https://www.bcv.org.ve/'
        self.logger.info("Conectando con el Banco Central de Venezuela...")
        # Desactivar warnings de urllib3 (si aún usas verify=False en entornos de desarrollo)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session = requests.Session()
        self.session.verify = False

    # Helpers como métodos
    def _iso_to_ddmmyyyy(self, iso_str: str) -> str:
        try:
            dt = datetime.fromisoformat(iso_str)
            return dt.strftime('%d/%m/%Y')
        except Exception:
            return iso_str

    def _parse_currency_value(self, val: str) -> float | None:
        if not val:
            return None
        s = val.strip().replace('\xa0', '').replace(' ', '')
        try:
            if '.' in s and ',' in s:
                s = s.replace('.', '').replace(',', '.')
            elif ',' in s and '.' not in s:
                s = s.replace(',', '.')
            return float(s)
        except Exception:
            return None

    def _format_currency_ve(self, value: float | None, decimals: int = 4, thousands: bool = True) -> str | None:
        if value is None:
            return None
        fmt = f"{{:,.{decimals}f}}"
        s = fmt.format(value)
        s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
        if not thousands:
            parts = s.split(',')
            if len(parts) > 1:
                integer = parts[0].replace('.', '')
                s = integer + ',' + parts[1]
        return s

    def fetch(self) -> BeautifulSoup:
        resp = self.session.get(self.url, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, 'html.parser')

    def get_tasas(self, moneda: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene las tasas del BCV de forma dinámica.
        Si 'moneda' es None, devuelve todas las encontradas.
        Si 'moneda' es un código (ej: 'USD'), devuelve solo esa.
        """
        try:
            soup = self.fetch()

            # === Fecha única ===
            fecha_actualizacion = None
            fecha_span = soup.select_one('div.pull-right.dinpro.center span.date-display-single')
            if fecha_span and fecha_span.get('content'):
                raw_iso = fecha_span.get('content').strip()
                fecha_actualizacion = self._iso_to_ddmmyyyy(raw_iso)
            else:
                self.logger.warning("No se encontró la fecha de actualización.")

            results: Dict[str, Dict[str, Any]] = {}

            # === Buscar todos los divs que contengan una tasa ===
            contenedores = soup.select('div.view-content div[id]')

            for cont in contenedores:
                # Buscar el código de la moneda en el <span>
                span = cont.find('span')
                strong = cont.find('strong')

                if not span or not strong:
                    continue  # No es un bloque de tasa válido

                codigo = span.get_text(strip=True).upper()
                valor_str = strong.get_text(strip=True)

                # Validar que el código sea alfabético y el valor numérico
                if not codigo.isalpha():
                    continue

                valor_num = self._parse_currency_value(valor_str)
                if valor_num is None:
                    self.logger.error(f"Valor inválido para {codigo}: '{valor_str}'")
                    continue

                valor_display = self._format_currency_ve(valor_num)
                results[codigo] = {
                    'valor': valor_num,
                    'valor_display': valor_display,
                    'fecha_valor': fecha_actualizacion
                }

            # === Verificar si USD está presente (siempre esperado) ===
            if not moneda and 'USD' not in results:
                self.logger.warning("USD no encontrada en la página del BCV")
            
            # === Filtro opcional ===
            if moneda:
                moneda = moneda.upper()
                if moneda in results:
                    return {moneda: results[moneda]}
                else:
                    self.logger.warning(f"Moneda solicitada '{moneda}' no encontrada en la página.")
                    return {}

            return results

        except requests.exceptions.RequestException as e:
            self.logger.exception(f"Error de conexión: {e}")
            return {}
        except Exception as e:
            self.logger.exception(f"Ocurrió un error inesperado: {e}")
            return {}



def get_tasas_bcv(moneda: Optional[str] = None,
                  log_file: Optional[str] = None,
                  log_level: int = logging.INFO) -> Dict[str, Dict[str, Any]]:
    """Función de compatibilidad: instancia BCVClient y retorna las tasas."""
    client = BCVClient(log_file=log_file, log_level=log_level)
    return client.get_tasas(moneda=moneda)
