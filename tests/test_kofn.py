"""problems/kofn eklentisi (P1: weighted k-out-of-n:G, cok tipli) testleri.

Problem: P-ii (guvenilirlik maks): verilen (N, K, BUDGET, tipler) icin
cozum = (n_1..n_M) tahsisi; SENSE=max; R Fraction ile TAM hesaplanir.
Pozitif kontrol degerleri Ozkut & Tutuncu 2025 tablolarindan
(data/kofn/reference/verify_ozkut2025.py ile bagimsiz dogrulanmis).
"""

from fractions import Fraction

import pytest

from problems.kofn.io import InstanceFormatError, parse_instance
from problems.kofn.objective import evaluate_text, system_reliability
from problems.kofn.spec import SENSE, penalty_scale

# Makaledeki router ornegi (Tablo 6 taban parametreleri), K=20, C0=30.
ROUTER = """\
# Ozkut & Tutuncu 2025, Tablo 6 taban instance'i
NAME router-n10-k20
M 3
N 10
K 20
BUDGET 30
TYPE 1 3 3 0.97
TYPE 2 1 1 0.92
TYPE 3 2 2 0.94
"""

# Ayni tipler, K=10 (Tablo 5 ilk satiri icin), genis butce.
ROUTER_K10 = ROUTER.replace("K 20", "K 10").replace("NAME router-n10-k20",
                                                    "NAME router-n10-k10")
# Dar butce varyanti: (10,0,0) maliyeti 30 > 25 -> butce ihlali uretilebilir.
ROUTER_TIGHT = ROUTER.replace("BUDGET 30", "BUDGET 25")


@pytest.fixture
def inst(tmp_path):
    f = tmp_path / "router.kofn"
    f.write_text(ROUTER, encoding="utf-8")
    return parse_instance(f)


def make_inst(tmp_path, text, name="i.kofn"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return parse_instance(f)


class TestParseInstance:
    def test_valid_instance_fields(self, inst):
        assert inst.name == "router-n10-k20"
        assert inst.m == 3
        assert inst.n_total == 10
        assert inst.k == Fraction(20)
        assert inst.budget == Fraction(30)
        assert inst.weights == (Fraction(3), Fraction(1), Fraction(2))
        assert inst.costs == (Fraction(3), Fraction(1), Fraction(2))
        assert inst.reliabilities == (
            Fraction("0.97"), Fraction("0.92"), Fraction("0.94"))

    def test_missing_header_raises(self, tmp_path):
        text = ROUTER.replace("BUDGET 30\n", "")
        with pytest.raises(InstanceFormatError, match="BUDGET"):
            make_inst(tmp_path, text)

    def test_type_count_mismatch_raises(self, tmp_path):
        text = ROUTER.replace("TYPE 3 2 2 0.94\n", "")
        with pytest.raises(InstanceFormatError, match="TYPE"):
            make_inst(tmp_path, text)

    def test_reliability_out_of_range_raises(self, tmp_path):
        text = ROUTER.replace("0.97", "1.5")
        with pytest.raises(InstanceFormatError, match="[Gg]uvenilirlik|reliab"):
            make_inst(tmp_path, text)


class TestSystemReliability:
    def test_returns_exact_fraction(self, inst):
        r = system_reliability((10, 0, 0), inst)
        assert isinstance(r, Fraction)

    def test_table6_router_k20(self, inst):
        # verify_ozkut2025.py: T6 (10,0,0) k=20 -> 0.99985291 (8 hane)
        assert round(float(system_reliability((10, 0, 0), inst)), 8) == 0.99985291

    def test_table5_row_k10(self, tmp_path):
        # verify_ozkut2025.py: T5 (0,8,2) k=10 -> 0.92284670 (8 hane)
        i = make_inst(tmp_path, ROUTER_K10)
        assert round(float(system_reliability((0, 8, 2), i)), 8) == 0.92284670

    def test_unreachable_threshold_gives_zero(self, inst):
        # (0,10,0): maks agirlik 10 < K=20 -> R tam olarak 0
        assert system_reliability((0, 10, 0), inst) == 0


class TestEvaluateTextFeasible:
    def test_feasible_verdict(self, inst):
        v = evaluate_text(inst, "10 0 0")
        assert v["feasible"] is True
        assert v["violations"] == {}
        assert round(v["cost"], 8) == 0.99985291
        assert v["fitness"] == v["cost"]
        assert isinstance(v["eval_ms"], int)

    def test_comments_ignored(self, inst):
        v = evaluate_text(inst, "# yorum\n\n10 0 0\n# son")
        assert v["feasible"] is True

    def test_reported_objective_sensor(self, inst):
        v_match = evaluate_text(inst, "R 0.999853\n10 0 0")
        assert v_match["info"]["reported_objective"] == 0.999853
        assert v_match["info"]["reported_matches"] is True
        v_lie = evaluate_text(inst, "R 0.5\n10 0 0")
        assert v_lie["info"]["reported_matches"] is False
        # Beyan verdict'i DEGISTIRMEZ (guvenilmez), yalnizca sensor:
        assert v_lie["feasible"] is True
        assert round(v_lie["cost"], 8) == 0.99985291

    def test_feasible_but_hopeless_has_zero_fitness(self, inst):
        # (0,10,0) fizibil (maliyet 10 <= 30, toplam 10) ama R=0.
        v = evaluate_text(inst, "0 10 0")
        assert v["feasible"] is True
        assert v["cost"] == 0.0
        assert v["fitness"] == 0.0


class TestEvaluateTextViolations:
    def test_wrong_total(self, inst):
        v = evaluate_text(inst, "5 0 0")
        assert v["feasible"] is False
        assert "wrong_total" in v["violations"]
        assert v["fitness"] < 0

    def test_negative_count(self, inst):
        v = evaluate_text(inst, "11 -1 0")
        assert v["feasible"] is False
        assert "negative_count" in v["violations"]
        assert v["fitness"] < 0

    def test_budget_exceeded(self, tmp_path):
        i = make_inst(tmp_path, ROUTER_TIGHT)
        v = evaluate_text(i, "10 0 0")  # maliyet 30 > 25
        assert v["feasible"] is False
        assert "budget_exceeded" in v["violations"]
        assert v["fitness"] < 0

    @pytest.mark.parametrize("garbage", ["", "merhaba dunya", "1 2", "1 2 3 4",
                                         "1.5 2 6.5", "# sadece yorum"])
    def test_parse_error_never_raises(self, inst, garbage):
        v = evaluate_text(inst, garbage)  # ASLA raise etmez
        assert v["feasible"] is False
        assert "parse_error" in v["violations"]
        assert v["fitness"] < 0

    def test_every_infeasible_below_every_feasible(self, inst, tmp_path):
        # R=0'lik fizibil cozum bile her infeasible'dan iyi olmali.
        worst_feasible = evaluate_text(inst, "0 10 0")["fitness"]
        i_tight = make_inst(tmp_path, ROUTER_TIGHT)
        infeasibles = [
            evaluate_text(inst, "5 0 0")["fitness"],
            evaluate_text(inst, "11 -1 0")["fitness"],
            evaluate_text(i_tight, "10 0 0")["fitness"],
            evaluate_text(inst, "bozuk")["fitness"],
        ]
        assert all(f < worst_feasible for f in infeasibles)

    def test_graded_penalty_gives_gradient(self, tmp_path):
        # Daha az butce asimi -> daha yuksek (daha az kotu) fitness.
        i = make_inst(tmp_path, ROUTER_TIGHT)
        big = evaluate_text(i, "10 0 0")["fitness"]   # maliyet 30, asim 5
        small = evaluate_text(i, "9 1 0")["fitness"]  # maliyet 28, asim 3
        assert small > big


class TestSpec:
    def test_sense_is_max(self):
        assert SENSE == "max"

    def test_penalty_scale_positive_and_dominates_objective_span(self, inst):
        s = penalty_scale(inst)
        assert isinstance(s, float)
        assert s >= 2.0  # R araligi [0,1] -> hicbir ihlal karli olamaz


class TestRegistryIntegration:
    def test_loads_via_registry(self, tmp_path):
        from harness.registry import load_problem

        p = load_problem("kofn")  # gercek problems/ kokunden
        assert p.sense == "max"
        f = tmp_path / "r.kofn"
        f.write_text(ROUTER, encoding="utf-8")
        inst = p.parse_instance(f)
        v = p.evaluate_text(inst, "10 0 0")
        assert v["feasible"] is True
        assert p.penalty_scale(inst) >= 2.0
