"""Suit genelinde env hijyeni.

Koşu reçeteleri (evolve/run.ps1) DISCOVERY_* env'lerini set eder; pytest
aynı shell'den başlarsa bu değerler testlere SIZAR (2026-08-10: arşiv
env'i test çözümlerini gerçek arşive yazdı; 2026-08-11: EVAL_SEEDS
artifact anahtarlarını seed önekiyle değiştirip 3 testi kırdı).
Autouse fixture her testte bu env'leri temizler; env isteyen test kendi
monkeypatch.setenv'ini fixture'dan SONRA (test gövdesinde) yapar.
"""
import pytest


@pytest.fixture(autouse=True)
def _clean_discovery_env(monkeypatch):
    for var in ("DISCOVERY_EVAL_SEEDS", "DISCOVERY_ARCHIVE_DIR",
                "DISCOVERY_ARCHIVE_BELOW", "DISCOVERY_ARCHIVE_ABOVE"):
        monkeypatch.delenv(var, raising=False)
