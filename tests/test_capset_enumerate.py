"""problems/capset enumerate testleri (P4.2: kanitli optimum, n<=3).

enumerate_optimum: exhaustive branch-and-bound ile F_3^n'de MAKSIMUM cap
set'i bağımsız olarak bulur. Bu, evaluator (objective.py) ile cap-set
kontrolünün dogrulugu icin ground truth kanitidir (kofn'deki Faz C
karsiligi): kucuk n'de gercek optimum bilindiginden, enumerate onu
birebir bulmali.

n>=4 optimallik iddiasi BIZE AIT DEGIL (literature aittir). Bu nedenle
testler yalnizca n<=3'te "enumerate a(n)'yi bulur" der; n>=4 icin
"indirilen kume feasible + boyutu tabloyla esit" der (P4.0 verisi).
"""

import pytest

from problems.capset.enumerate import enumerate_optimum
from problems.capset.io import parse_instance
from problems.capset.objective import evaluate_text


def inst_for(tmp_path, n):
    f = tmp_path / f"capset-n{n}.cap"
    f.write_text(f"# n={n}\ndimension {n}\n", encoding="utf-8")
    return parse_instance(f)


def assert_is_cap(result, n, tmp_path):
    """Enumerate'in buldugu kume gercekten cap mi (objective ile capraz).

    tmp_path fixture'i kullanilir (temp dosya birikintisi kalmasin; Görev 2).
    """
    inst = inst_for(tmp_path, n)
    sol = "\n".join("".join(str(c) for c in v) for v in result["cap"])
    v = evaluate_text(inst, sol)
    assert v["feasible"] is True, "enumerate ciktisi cap degil!"
    assert v["cost"] == result["size"]


class TestEnumerateOptimum:
    def test_n2_finds_proven_optimum_4(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        r = enumerate_optimum(inst)
        assert r["size"] == 4  # a(2)=4, klasik/kanıtlanmış
        assert r["proven"] is True  # P4.2 asil iddia: n<=3'te KANITLI

    def test_n3_finds_proven_optimum_9(self, tmp_path):
        inst = inst_for(tmp_path, 3)
        r = enumerate_optimum(inst)
        assert r["size"] == 9  # a(3)=9, klasik/kanıtlanmış
        assert r["proven"] is True  # P4.2 asil iddia: n<=3'te KANITLI

    def test_n2_result_is_valid_cap(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        r = enumerate_optimum(inst)
        assert r["size"] == len(r["cap"])
        assert_is_cap(r, 2, tmp_path)

    def test_n3_result_is_valid_cap(self, tmp_path):
        inst = inst_for(tmp_path, 3)
        r = enumerate_optimum(inst)
        assert r["size"] == len(r["cap"])
        assert_is_cap(r, 3, tmp_path)

    def test_n1_trivial(self, tmp_path):
        # F_3^1 = {0,1,2}. Herhangi 2 nokta cap (3 nokta = butun uzay = bir line).
        # a(1)=2.
        inst = inst_for(tmp_path, 1)
        r = enumerate_optimum(inst)
        assert r["size"] == 2

    def test_deterministic_across_runs(self, tmp_path):
        # Ayni instance, iki koşu -> ayni cap (tie-break deterministik).
        inst = inst_for(tmp_path, 3)
        r1 = enumerate_optimum(inst)
        r2 = enumerate_optimum(inst)
        assert r1["size"] == r2["size"]
        assert sorted(r1["cap"]) == sorted(r2["cap"])

    @pytest.mark.parametrize("n,expected", [(2, 4), (3, 9)])
    def test_runs_fast_enough(self, tmp_path, n, expected):
        # CLAUDE.md §0.3: kanit aramasi tek cekirdekte, dakikalar mertebesini
        # asmamali. n=3 (27 nokta) saniyeler icinde bitmeli.
        import time
        inst = inst_for(tmp_path, n)
        t0 = time.perf_counter()
        r = enumerate_optimum(inst)
        elapsed = time.perf_counter() - t0
        assert r["size"] == expected
        assert elapsed < 30.0, f"n={n} {elapsed:.1f}s surdu (30s siniri asildi)"

    def test_result_has_metadata(self, tmp_path):
        inst = inst_for(tmp_path, 2)
        r = enumerate_optimum(inst)
        # kanit katmani: node_count (B&B dugum sayisi) ve time_ms raporlanmali
        assert "node_count" in r
        assert isinstance(r["node_count"], int)
        assert r["node_count"] > 0


class TestEnumerateLargerNFallback:
    """n>=4 optimallik iddiasi literatüre ait. Enumerate yalnizca alt sinir
    (feasible cap) uretir; optimum iddia ETMEZ. Bu testler bunu sabitler."""

    def test_n4_short_limit_unproven_nonempty(self, tmp_path):
        # n=4 B&B tam optimum dakikalar alir. COK kisa limit (0.01 sn) ile:
        # proven False (tamamlanmadi) ama yine de >=1 cap (greedy baslangic).
        inst = inst_for(tmp_path, 4)
        r = enumerate_optimum(inst, time_limit_s=0.01)
        assert r["proven"] is False
        assert r["size"] >= 1
        assert isinstance(r["cap"], list) and len(r["cap"]) == r["size"]
        assert_is_cap(r, 4, tmp_path)
