# tests/test_bcv_client.py
import subprocess
import sys
import pytest
from bs4 import BeautifulSoup
import logging
from src.scraper_bcv.bcv_client import BCVClient
from tests.fixtures.bcv_sample import BCV_SAMPLE_HTML
from tests.fixtures.bcv_sample_no_usd import BCV_SAMPLE_HTML_NO_USD

class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        pass


@pytest.fixture
def bcv_client(monkeypatch):
    """Cliente BCV con HTML completo."""
    client = BCVClient(log_level=0)
    client.fetch = lambda: BeautifulSoup(BCV_SAMPLE_HTML, 'html.parser')
    return client

@pytest.fixture
def bcv_client_no_usd(monkeypatch):
    """Cliente BCV con HTML sin USD."""
    client = BCVClient(log_level=logging.WARNING)  # permitir WARNING para capturar logs de prueba
    client.fetch = lambda: BeautifulSoup(BCV_SAMPLE_HTML_NO_USD, 'html.parser')
    return client

def test_get_all_rates(bcv_client):
    tasas = bcv_client.get_tasas()
    assert len(tasas) == 5
    assert tasas['USD']['valor'] == pytest.approx(151.7627, rel=1e-6)
    assert tasas['EUR']['valor_display'].startswith("177,0175")
    assert tasas['USD']['fecha_valor'] == "04/09/2025"

def test_get_single_rate(bcv_client):
    usd = bcv_client.get_tasas(moneda='USD')
    assert list(usd.keys()) == ['USD']
    assert usd['USD']['valor'] == pytest.approx(151.7627, rel=1e-6)

def test_invalid_currency(bcv_client):
    result = bcv_client.get_tasas(moneda='ABC')
    assert result == {}

def test_missing_usd_logs_warning_and_returns_others(bcv_client_no_usd, caplog):
    caplog.set_level("WARNING")

    tasas = bcv_client_no_usd.get_tasas()

    # Verifica que USD no está
    assert 'USD' not in tasas

    # Verifica que las demás monedas sí están
    for moneda in ['EUR', 'CNY', 'TRY', 'RUB']:
        assert moneda in tasas
        assert tasas[moneda]['valor'] is not None

    # Verifica que se logueó un warning sobre USD
    warnings = [rec.message for rec in caplog.records if rec.levelname == "WARNING"]
    assert any("USD" in w and "no encontrada" in w.lower() for w in warnings)

def test_invalid_value_logs_error(monkeypatch, caplog):
    """Simula valor no numérico para USD."""
    html_invalid = BCV_SAMPLE_HTML.replace("151,76270000", "VALOR_INVALIDO")
    client = BCVClient(log_level=0)
    client.fetch = lambda: BeautifulSoup(html_invalid, 'html.parser')

    caplog.set_level("ERROR")
    tasas = client.get_tasas()
    assert 'USD' not in tasas
    errors = [rec.message for rec in caplog.records if rec.levelname == "ERROR"]
    assert any("Valor inválido" in e for e in errors)

@pytest.mark.integration
def test_cli_with_python_m():
    """Ejecuta `python -m scraper_bcv` y verifica que no falle."""
    result = subprocess.run(
        [sys.executable, "-m", "scraper_bcv", "--log-level", "INFO"],
        capture_output=True,
        text=True
    )
    # Debe terminar con código 0
    assert result.returncode == 0, f"CLI falló: {result.stderr}"
    # Debe contener al menos una moneda en la salida (las monedas van a stderr por los logs INFO)
    assert any(moneda in result.stderr for moneda in ["USD", "EUR", "CNY", "TRY", "RUB"])

@pytest.mark.integration
def test_cli_as_installed_command():
    """Ejecuta el comando `scraper-bcv` y verifica que no falle."""
    result = subprocess.run(
        ["scraper-bcv", "--log-level", "INFO"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"CLI falló: {result.stderr}"
    assert any(moneda in result.stderr for moneda in ["USD", "EUR", "CNY", "TRY", "RUB"])
