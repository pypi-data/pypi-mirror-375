"""
scraper-bcv
-----------

Librería para obtener tasas oficiales del BCV de forma defensiva y trazable.
Cumple con la normativa venezolana: uso educativo y técnico.
"""

from .bcv_client import BCVClient, get_tasas_bcv

__all__ = ["BCVClient", "get_tasas_bcv"]
__version__ = "v0.1.1"
__author__ = "Francisco A Quivera G"
