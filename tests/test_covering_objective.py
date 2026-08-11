"""problems/covering objective testleri (evaluate_text + schoenheim).

Pozitif kontroller elle kurulabilen KANITLI optimal tasarimlar:
  - C(4,3,2)=3 (sayma argumani)
  - C(7,3,2)=7 Fano duzlemi (21 ikili / blok basi 3)
  - C(9,3,2)=12 STS(9) (afin duzlem AG(2,3))
Ucunde de Schoenheim siniri kesin -> feasible fitness tam 1.0 beklenir.
Cozum tarafi ASLA raise etmez; her ihlal dogru violation koduyla doner;
her infeasible fitness < her feasible fitness.
"""

import pytest

from problems.covering.io import parse_instance
from problems.covering.objective import evaluate_text
from problems.covering.spec import penalty_scale, schoenheim

FANO = "1 2 4\n1 3 5\n2 3 6\n1 6 7\n2 5 7\n3 4 7\n4 5 6\n"
STS9 = ("1 2 3\n4 5 6\n7 8 9\n1 4 7\n2 5 8\n3 6 9\n"
        "1 5 9\n2 6 7\n3 4 8\n1 6 8\n2 4 9\n3 5 7\n")
C432 = "1 2 3\n1 2 4\n1 3 4\n"


def inst_for(tmp_path, v, k, t):
    f = tmp_path / f"cover-v{v}-k{k}-t{t}.cover"
    f.write_text(f"v {v}\nk {k}\nt {t}\n", encoding="utf-8")
    return parse_instance(f)


class TestSchoenheim:
    @pytest.mark.parametrize("v,k,t,expected", [
        (7, 3, 2, 7),      # Fano — kesin
        (4, 3, 2, 3),      # kesin
        (9, 3, 2, 12),     # STS(9) — kesin
        (13, 3, 2, 26),    # STS(13) — kesin
        (32, 8, 4, 532),   # kurasyon ciktisiyla regresyon
        (12, 4, 1, 3),     # taban durum: ceil(12/4)
    ])
    def test_known_values(self, v, k, t, expected):
        assert schoenheim(v, k, t) == expected

    def test_penalty_scale_is_schoenheim(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        assert penalty_scale(inst) == 7.0
        assert isinstance(penalty_scale(inst), float)


class TestFeasible:
    @pytest.mark.parametrize("v,k,t,text,size", [
        (7, 3, 2, FANO, 7),
        (9, 3, 2, STS9, 12),
        (4, 3, 2, C432, 3),
    ])
    def test_proven_optimal_hits_ceiling(self, tmp_path, v, k, t, text, size):
        inst = inst_for(tmp_path, v, k, t)
        verdict = evaluate_text(inst, text)
        assert verdict["feasible"] is True
        assert verdict["violations"] == {}
        assert verdict["cost"] == size
        assert verdict["fitness"] == pytest.approx(1.0)
        assert "instrument_alarm" not in verdict["info"]
        assert isinstance(verdict["eval_ms"], int)

    def test_suboptimal_feasible_below_ceiling(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, FANO + "1 2 3\n")
        assert verdict["feasible"] is True
        assert verdict["cost"] == 8
        assert verdict["fitness"] == pytest.approx(7 / 8)

    def test_block_order_and_whitespace_irrelevant(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        shuffled = "4 2 1\n5\t3 1\n6 3 2\n7 6 1\n7 5 2\n7 4 3\n6 5 4\n"
        verdict = evaluate_text(inst, shuffled)
        assert verdict["feasible"] is True
        assert verdict["cost"] == 7

    def test_comments_ignored(self, tmp_path):
        inst = inst_for(tmp_path, 4, 3, 2)
        verdict = evaluate_text(inst, "# baslik\n" + C432 + "# son\n")
        assert verdict["feasible"] is True


class TestInfeasible:
    def test_empty_solution_floor(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, "# bos\n")
        assert verdict["feasible"] is False
        assert verdict["violations"]["uncovered"]["count"] == 21
        assert verdict["fitness"] == pytest.approx(-2.0)

    def test_partial_coverage_gradient(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        # (4,5,6) blogu eksik -> yalniz onun kapsadigi 3 ikili acikta
        verdict = evaluate_text(
            inst, "1 2 4\n1 3 5\n2 3 6\n1 6 7\n2 5 7\n3 4 7\n")
        assert verdict["feasible"] is False
        assert verdict["violations"]["uncovered"]["count"] == 3
        assert verdict["fitness"] == pytest.approx(-1.0 - 3 / 21)
        assert verdict["info"]["example_uncovered"] == [4, 5]

    def test_gradient_monotone_in_coverage(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        worse = evaluate_text(inst, "1 2 4\n")
        better = evaluate_text(inst, "1 2 4\n1 3 5\n2 3 6\n1 6 7\n2 5 7\n")
        assert worse["fitness"] < better["fitness"] < -1.0

    @pytest.mark.parametrize("bad_line", [
        "1 2",        # eksik eleman
        "1 2 3 4",    # fazla eleman
        "1 2 8",      # aralik disi (v=7)
        "1 2 2",      # blok icinde tekrar
        "1 2 x",      # tamsayi degil
        "0 1 2",      # 0 gecersiz (1..v)
    ])
    def test_bad_block(self, tmp_path, bad_line):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, FANO + bad_line + "\n")
        assert verdict["feasible"] is False
        assert "bad_block" in verdict["violations"]
        assert verdict["fitness"] == pytest.approx(-2.0)
        assert verdict["cost"] == 0

    def test_duplicate_block_as_set(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, FANO + "4 2 1\n")  # (1,2,4) tekrari
        assert verdict["feasible"] is False
        assert verdict["violations"]["duplicate_block"]["count"] == 1
        assert -2.0 <= verdict["fitness"] < -1.0

    @pytest.mark.parametrize("garbage", [None, 42, ["1 2 3"], b"1 2 3"])
    def test_non_str_never_raises(self, tmp_path, garbage):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, garbage)
        assert verdict["feasible"] is False
        assert verdict["violations"]["uncovered"]["count"] == 21


class TestHonestySensor:
    def test_matching_report(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, "# size 7\n" + FANO)
        assert verdict["info"]["reported_size_matches"] is True

    def test_wrong_report(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        verdict = evaluate_text(inst, "# size 5\n" + FANO)
        assert verdict["info"]["reported_size_matches"] is False

    def test_no_report(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        assert evaluate_text(inst, FANO)["info"]["reported_size_matches"] is None

    def test_report_does_not_affect_verdict(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        a = evaluate_text(inst, FANO)
        b = evaluate_text(inst, "# size 999\n" + FANO)
        assert a["feasible"] == b["feasible"] and a["cost"] == b["cost"]


class TestOrdering:
    def test_every_infeasible_below_every_feasible(self, tmp_path):
        inst = inst_for(tmp_path, 7, 3, 2)
        feasibles = [
            evaluate_text(inst, FANO),
            evaluate_text(inst, FANO + "1 2 3\n"),
            evaluate_text(inst, FANO + "1 2 3\n1 2 5\n1 2 6\n"),
        ]
        infeasibles = [
            evaluate_text(inst, ""),
            evaluate_text(inst, "1 2 4\n"),
            evaluate_text(inst, FANO[:-6]),          # son blok eksik
            evaluate_text(inst, FANO + "1 2\n"),     # bad_block
            evaluate_text(inst, FANO + "4 2 1\n"),   # duplicate
        ]
        worst_feasible = min(x["fitness"] for x in feasibles)
        best_infeasible = max(x["fitness"] for x in infeasibles)
        assert best_infeasible < 0.0 < worst_feasible
