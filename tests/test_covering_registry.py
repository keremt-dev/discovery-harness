"""covering eklentisi harness/registry uzerinden yuklenir — Faz F sinavi:
harness/ icinde TEK SATIR degisiklik olmadan yeni problem calisiyor mu?
"""

from harness.registry import load_problem
from harness.score import combined_score

FANO = "1 2 4\n1 3 5\n2 3 6\n1 6 7\n2 5 7\n3 4 7\n4 5 6\n"


def make_instance_file(tmp_path):
    f = tmp_path / "cover-v7-k3-t2.cover"
    f.write_text("v 7\nk 3\nt 2\n", encoding="utf-8")
    return f


def test_load_contract():
    problem = load_problem("covering")
    assert problem.sense == "max"
    assert callable(problem.parse_instance)
    assert callable(problem.evaluate_text)
    assert callable(problem.penalty_scale)


def test_end_to_end_through_registry(tmp_path):
    problem = load_problem("covering")
    inst = problem.parse_instance(make_instance_file(tmp_path))
    verdict = problem.evaluate_text(inst, FANO)
    assert verdict["feasible"] is True
    assert verdict["cost"] == 7
    # SENSE=max -> combined_score fitness'i aynen gecirir; kanitli
    # optimumda tavan 1.0 (OpenEvolve bunu maksimize edecek).
    assert combined_score(verdict["fitness"], problem.sense) == verdict["fitness"]
    assert verdict["fitness"] == 1.0


def test_infeasible_score_below_feasible_through_registry(tmp_path):
    problem = load_problem("covering")
    inst = problem.parse_instance(make_instance_file(tmp_path))
    good = combined_score(
        problem.evaluate_text(inst, FANO)["fitness"], problem.sense)
    bad = combined_score(
        problem.evaluate_text(inst, "1 2 4\n")["fitness"], problem.sense)
    assert bad < good
