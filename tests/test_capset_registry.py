"""problems/capset registry entegrasyon testi (P4: cap set).

harness/registry.load_problem("capset") sozlesmeyi dogrulamali:
SENSE, parse_instance, evaluate_text, penalty_scale hepsi cagrilabilir
ve pozitif kontrol kumesiyle uçtan uca calismali. Bu, Faz F sinavinin
(P4 CLAUDE.md §0.1) capset on kosuludur: eklenti harness/ cekirdegine
DOKUNMADAN yuklenmelidir.
"""

from pathlib import Path

import pytest

from harness.registry import load_problem

REF = Path(__file__).resolve().parent.parent / "data" / "capset" / "reference"


def _n8_solution():
    lines = REF.joinpath("funsearch_n8_size512.txt").read_text(encoding="utf-8").splitlines()
    return "\n".join(l for l in lines if l.strip() and not l.strip().startswith("#"))


class TestRegistryIntegration:
    def test_loads_capset_with_contract(self):
        p = load_problem("capset")
        assert p.name == "capset"
        assert p.sense == "max"
        assert callable(p.parse_instance)
        assert callable(p.evaluate_text)
        assert callable(p.penalty_scale)

    def test_end_to_end_via_registry(self, tmp_path):
        # Faz F sinavi: capset eklentisi harness/ cekirdegiyle (o na dokunmadan)
        # uçtan uca calisiyor mu? Instance + cozum -> verdict.
        p = load_problem("capset")
        f = tmp_path / "capset-n8.cap"
        f.write_text("# cap set n=8\ndimension 8\n", encoding="utf-8")
        inst = p.parse_instance(f)
        v = p.evaluate_text(inst, _n8_solution())
        assert v["feasible"] is True
        assert v["cost"] == 512  # ALTIN pozitif kontrol
        assert p.penalty_scale(inst) == pytest.approx(2 * 3**8 / 8)

    def test_core_does_not_mention_capset(self):
        # harness/registry.py probleme-agnostik olmali: "capset" gecmemeli
        # (Faz F sinavi — cekirdek sizdirmiyor mu?).
        src = Path(__file__).resolve().parent.parent / "harness" / "registry.py"
        text = src.read_text(encoding="utf-8")
        assert "capset" not in text.lower()
