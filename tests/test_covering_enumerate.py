"""problems/covering enumerate testleri (P5 Faz C: kanitli optimum).

Uc kanit katmani:
  1. Enumerate, arsivin KANITLI (gap=0) kucuk hucre degerlerini bagimsiz
     bulur — evaluator dogrulugunun olcusu (skill Faz C).
  2. C(7,4,3)=12 > Schoenheim=11: basarisiz-derinlik yolu fiilen calisir
     (11'i curut, 12'de bul) — iterative deepening gercekten kanit uretiyor.
  3. Enumerate ciktisi evaluate_text'ten feasible + cost=opt doner
     ("evaluator optimumu = enumeration optimumu" caprazi).
"""

import pytest

from problems.covering.enumerate import (ENUM_CAP, enumerate_optimum,
                                         solution_text)
from problems.covering.io import parse_instance
from problems.covering.objective import evaluate_text
from problems.covering.spec import schoenheim


def inst_for(tmp_path, v, k, t):
    f = tmp_path / f"cover-v{v}-k{k}-t{t}.cover"
    f.write_text(f"v {v}\nk {k}\nt {t}\n", encoding="utf-8")
    return parse_instance(f)


# Arsivde gap=0 (kanitli) kucuk hucreler — enumerate ayni degeri bulmali.
PROVEN_CELLS = [
    (4, 3, 2, 3),
    (5, 3, 2, 4),
    (6, 3, 2, 6),
    (7, 3, 2, 7),    # Fano
    (9, 3, 2, 12),   # STS(9)
    (5, 4, 3, 4),
    (6, 4, 3, 6),
    (7, 4, 3, 12),   # Schoenheim=11 -> basarisiz derinlik + 1
    (8, 4, 3, 14),
]


class TestProvenOptima:
    @pytest.mark.parametrize("v,k,t,opt", PROVEN_CELLS)
    def test_matches_archive_proven_value(self, tmp_path, v, k, t, opt):
        r = enumerate_optimum(inst_for(tmp_path, v, k, t))
        assert r["proven"] is True
        assert r["size"] == opt
        assert len(r["blocks"]) == opt

    def test_failed_depth_path_c743(self, tmp_path):
        # C(7,4,3): Schoenheim 11 < optimum 12 -> DFS 11'i CURUTMUS olmali.
        inst = inst_for(tmp_path, 7, 4, 3)
        assert schoenheim(7, 4, 3) == 11
        r = enumerate_optimum(inst)
        assert r["lower_bound"] == 11
        assert r["size"] == 12
        assert r["proven"] is True

    @pytest.mark.parametrize("v,k,t,opt", PROVEN_CELLS)
    def test_cross_check_with_evaluator(self, tmp_path, v, k, t, opt):
        # Faz C asil iddiasi: evaluator optimumu = enumeration optimumu.
        inst = inst_for(tmp_path, v, k, t)
        r = enumerate_optimum(inst)
        verdict = evaluate_text(inst, solution_text(r))
        assert verdict["feasible"] is True
        assert verdict["cost"] == r["size"]
        # Schoenheim'in kesin oldugu hucrelerde fitness tavani 1.0
        if r["size"] == r["lower_bound"]:
            assert verdict["fitness"] == pytest.approx(1.0)


class TestDeterminism:
    def test_same_blocks_across_runs(self, tmp_path):
        # Tie-break: leksikografik-ilk cozum; iki kosu birebir ayni.
        inst = inst_for(tmp_path, 7, 3, 2)
        r1 = enumerate_optimum(inst)
        r2 = enumerate_optimum(inst)
        assert r1["blocks"] == r2["blocks"]

    def test_first_block_is_lexicographic_smallest(self, tmp_path):
        # Ilk kapsanmamis altkume (1,..,t) oldugu icin ilk blok (1..k)
        # olmak zorunda (leksikografik-ilk dallanmanin gorunur izi).
        inst = inst_for(tmp_path, 7, 3, 2)
        r = enumerate_optimum(inst)
        assert r["blocks"][0] == (1, 2, 3)


class TestScopeAndFallback:
    def test_out_of_scope_returns_no_proof(self, tmp_path):
        # Hedef hucre C(32,8,4): C(32,8) ~ 10.5M > ENUM_CAP -> kanit yok.
        inst = inst_for(tmp_path, 32, 8, 4)
        r = enumerate_optimum(inst)
        assert r["proven"] is False
        assert r["blocks"] is None
        assert r["size"] is None
        assert r["lower_bound"] == 532

    def test_time_limit_returns_greedy_upper_bound(self, tmp_path):
        # Cok kisa zaman siniri: kanit yok ama greedy feasible cozum var.
        inst = inst_for(tmp_path, 9, 3, 2)
        r = enumerate_optimum(inst, time_limit_s=0.0)
        assert r["proven"] is False
        assert r["blocks"] is not None
        verdict = evaluate_text(inst, solution_text(r))
        assert verdict["feasible"] is True
        assert verdict["cost"] == r["size"] >= 12

    def test_runs_fast_enough(self, tmp_path):
        # Faz C hucreleri ms-sn mertebesinde kalmali (CLAUDE.md §0 ruhu).
        import time
        t0 = time.perf_counter()
        for v, k, t, _ in PROVEN_CELLS:
            enumerate_optimum(inst_for(tmp_path, v, k, t))
        assert time.perf_counter() - t0 < 30.0
