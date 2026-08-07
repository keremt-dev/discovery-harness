"""Faz C: exhaustive enumeration ground truth araci testleri.

Kritik nokta: enumerator KENDI ciktisina degil, makalenin YAYINLANMIS P-ii
optimumlarina karsi test edilir (dongusellik yok). Deger kaynaklari:
Ozkut & Tutuncu 2025 Tablo 6'nin bozuk olmayan satirlari
(data/kofn/reference/verify_ozkut2025.py ile 8 haneye dogrulanmis).
"""

from fractions import Fraction

import pytest

from problems.kofn.enumerate import enumerate_optimum
from problems.kofn.io import parse_instance
from problems.kofn.objective import evaluate_text

BASE = """\
NAME {name}
M 3
N {n}
K {k}
BUDGET {budget}
TYPE 1 3 3 0.97
TYPE 2 1 1 0.92
TYPE 3 2 2 0.94
"""


def make_inst(tmp_path, n, k, budget=30, name=None):
    name = name or f"router-n{n}-k{k}"
    f = tmp_path / f"{name}.kofn"
    f.write_text(BASE.format(name=name, n=n, k=k, budget=budget),
                 encoding="utf-8")
    return parse_instance(f)


class TestPaperAnchors:
    """Yayinlanmis Tablo 6 optimumlari (doyumsuz satirlar) bire bir."""

    def test_n10_k20(self, tmp_path):
        r = enumerate_optimum(make_inst(tmp_path, 10, 20))
        # Makale: (10,0,0) C=30 R=0.9999 (bizim 8 hane: 0.99985291)
        assert r["alloc"] == (10, 0, 0)
        assert round(float(r["reliability"]), 8) == 0.99985291

    def test_n15_k30(self, tmp_path):
        r = enumerate_optimum(make_inst(tmp_path, 15, 30))
        # Makale: (7,7,1) C=30 R=0.42369 (bizim 8 hane: 0.42368665)
        assert round(float(r["reliability"]), 8) == 0.42368665
        assert r["money_cost"] <= 30

    def test_n20_k30(self, tmp_path):
        r = enumerate_optimum(make_inst(tmp_path, 20, 30))
        # Makale: (5,15,0) C=30 R=0.2459 (bizim 8 hane: 0.24585332)
        assert round(float(r["reliability"]), 8) == 0.24585332

    def test_n15_k25(self, tmp_path):
        r = enumerate_optimum(make_inst(tmp_path, 15, 25))
        # Makale: (7,7,1) C=30 R=0.9759 (bizim 8 hane: 0.97590373)
        assert round(float(r["reliability"]), 8) == 0.97590373

    def test_corrected_row_n15_k15(self, tmp_path):
        # Makalenin bozuk satiri (0,12,3); gercek optimum (1,1,13) C=30
        # (docs/p1-problem-tanimi.md §1'de karakterize edildi).
        r = enumerate_optimum(make_inst(tmp_path, 15, 15))
        assert round(float(r["reliability"]), 8) == 0.99999961
        assert r["money_cost"] == 30


class TestBudgetAndFeasibility:
    def test_budget_binds(self, tmp_path):
        free = enumerate_optimum(make_inst(tmp_path, 10, 20, budget=30))
        tight = enumerate_optimum(make_inst(tmp_path, 10, 20, budget=25))
        assert tight["money_cost"] <= 25
        assert tight["reliability"] < free["reliability"]

    def test_no_feasible_allocation_raises(self, tmp_path):
        # N=10 icin minimum maliyet 10*1=10 > BUDGET 5 -> fizibil yok.
        with pytest.raises(ValueError, match="[Ff]izibil"):
            enumerate_optimum(make_inst(tmp_path, 10, 20, budget=5))


class TestInstrumentConsistency:
    def test_enumerated_optimum_passes_evaluator(self, tmp_path):
        # Kapali dongu: enumeration'in optimumu, evaluator'den feasible +
        # ayni R ile gecmeli (enstrumanin ic tutarliligi).
        inst = make_inst(tmp_path, 15, 30)
        r = enumerate_optimum(inst)
        v = evaluate_text(inst, " ".join(map(str, r["alloc"])))
        assert v["feasible"] is True
        assert v["cost"] == float(r["reliability"])

    def test_reliability_is_exact_fraction(self, tmp_path):
        r = enumerate_optimum(make_inst(tmp_path, 10, 20))
        assert isinstance(r["reliability"], Fraction)


class TestTieBreak:
    def test_symmetric_types_deterministic(self, tmp_path):
        # Iki tip birebir ayni (w=1,c=1,p=0.9): tum tahsisler ayni R'yi
        # verir -> beraberlik. Kural: en dusuk maliyet, sonra leksikografik
        # en kucuk tahsis. Burada tum maliyetler esit -> (0,2) doner.
        f = tmp_path / "tie.kofn"
        f.write_text(
            "NAME tie\nM 2\nN 2\nK 1\nBUDGET 10\n"
            "TYPE 1 1 1 0.9\nTYPE 2 1 1 0.9\n", encoding="utf-8")
        r = enumerate_optimum(parse_instance(f))
        assert r["alloc"] == (0, 2)
        assert r["tie_count"] == 3  # (0,2), (1,1), (2,0)

    def test_feasible_count_reported(self, tmp_path):
        # N=2, M=2, genis butce: (0,2),(1,1),(2,0) -> 3 fizibil tahsis.
        f = tmp_path / "cnt.kofn"
        f.write_text(
            "NAME cnt\nM 2\nN 2\nK 1\nBUDGET 10\n"
            "TYPE 1 1 1 0.9\nTYPE 2 2 2 0.8\n", encoding="utf-8")
        r = enumerate_optimum(parse_instance(f))
        assert r["feasible_count"] == 3
