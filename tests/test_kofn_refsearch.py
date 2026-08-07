"""Headroom turnusolu (problems/kofn/refsearch.py) testleri.

Amac: "tohumun ustunde ulasilabilir alan var mi?" sorusunu optimum
bilmeden olcmek. Referans arama = cok baslangic + cok birimli transfer
hamleleri; DETERMINISTIK (kurasyon tekrarlanabilir olmali). Optimum
iddiasi yok — yalnizca alt sinir.

Kritik test: 'plato instance'i' — oran-greedy tohumun R=0'a saplandigi
ama cok-birimli hamlenin kurtardigi el yapimi ornek. Evrim hedefi
kurasyonunun varlik sebebi tam olarak bu fark.
"""

from pathlib import Path

import pytest

from problems.kofn.enumerate import enumerate_optimum
from problems.kofn.io import parse_instance
from problems.kofn.refsearch import reference_search

REPO = Path(__file__).resolve().parent.parent
ROUTER = REPO / "data" / "kofn" / "instances" / "router-n10-k20.kofn"

# Plato instance'i: oranlar A'yi (w=1) tercih ettirir -> (4,0) -> R=0;
# tekil takas yolu boyunca R=0 (gradyan yok). (0,4) ise R=0.9477.
PLATEAU = """\
NAME plato
M 2
N 4
K 9
BUDGET 16
TYPE 1 1 1 0.9
TYPE 2 3 4 0.9
"""


@pytest.fixture
def plateau_inst(tmp_path):
    f = tmp_path / "plato.kofn"
    f.write_text(PLATEAU, encoding="utf-8")
    return parse_instance(f)


class TestReferenceSearch:
    def test_finds_optimum_on_router(self):
        inst = parse_instance(ROUTER)
        r = reference_search(inst)
        assert round(r["reliability"], 8) == 0.99985291  # kanitli optimum

    def test_escapes_zero_plateau(self, plateau_inst):
        # Tekil-takas hill-climb (4,0)'da R=0'a saplanir; referans arama
        # cok-birimli transferle (0,4) ~ 0.9477'yi bulmali.
        r = reference_search(plateau_inst)
        assert r["reliability"] > 0.9
        # enumeration ile capraz: kucuk instance'ta ref = kanitli optimum
        opt = float(enumerate_optimum(plateau_inst)["reliability"])
        assert r["reliability"] == pytest.approx(opt, abs=1e-9)

    def test_deterministic(self, plateau_inst):
        a = reference_search(plateau_inst)
        b = reference_search(plateau_inst)
        assert a["alloc"] == b["alloc"]
        assert a["reliability"] == b["reliability"]

    def test_matches_enumeration_on_small_generated(self, tmp_path):
        from problems.kofn.generate import generate_instance
        f = tmp_path / "g.kofn"
        f.write_text(generate_instance(12, 3, 7), encoding="utf-8")
        inst = parse_instance(f)
        opt = float(enumerate_optimum(inst)["reliability"])
        r = reference_search(inst)
        assert r["reliability"] == pytest.approx(opt, abs=1e-9)

    def test_respects_feasibility(self, plateau_inst):
        r = reference_search(plateau_inst)
        alloc = r["alloc"]
        assert sum(alloc) == plateau_inst.n_total
        money = sum(float(c) * x
                    for c, x in zip(plateau_inst.costs, alloc))
        assert money <= float(plateau_inst.budget) + 1e-9
