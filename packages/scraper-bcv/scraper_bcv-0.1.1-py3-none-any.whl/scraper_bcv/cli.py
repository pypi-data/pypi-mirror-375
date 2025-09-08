import argparse
import logging
from .bcv_client import get_tasas_bcv, setup_logger

def main():
    parser = argparse.ArgumentParser(
        description="Obtiene las tasas de referencia del BCV."
    )
    parser.add_argument(
        "-m", "--moneda",
        help="Código de la moneda (ej: USD, EUR). Si no se indica, muestra todas."
    )
    parser.add_argument(
        "-l", "--log-file",
        help="Ruta del archivo de log (opcional)."
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Nivel de logging (por defecto: INFO)."
    )

    args = parser.parse_args()

    logger = setup_logger(args.log_file, getattr(logging, args.log_level.upper()))

    tasas = get_tasas_bcv(
        moneda=args.moneda,
        log_file=args.log_file,
        log_level=getattr(logging, args.log_level.upper())
    )

    if tasas:
        for codigo, datos in tasas.items():
            logger.info(f"{codigo}: {datos['valor_display']} Bs.S - Fecha: {datos['fecha_valor']}")
    else:
        logger.warning("No se obtuvieron tasas.")
