"""Cozum arsivleme kancasi testleri (DISCOVERY_ARCHIVE_DIR).

2026-08-10 dersi: v28 rekor kosusunda evaluator'un gordugu cost=56
cozumu tempdir'le birlikte kayboldu. Kanca: feasible cozumler kalici
dizine <stem>-cost<X>-<sha1_8>.txt olarak kopyalanir; BELOW/ABOVE
esikleri filtre; arsivleme hatasi degerlendirmeyi asla bozmaz.
"""

import textwrap
from pathlib import Path

import pytest

from harness.evolve_evaluator import evaluate

FANO = "1 2 4\\n1 3 5\\n2 3 6\\n1 6 7\\n2 5 7\\n3 4 7\\n4 5 6\\n"


@pytest.fixture
def covering_env(monkeypatch, tmp_path):
    inst = tmp_path / "cover-v7-k3-t2.cover"
    inst.write_text("v 7\nk 3\nt 2\n", encoding="utf-8")
    monkeypatch.setenv("DISCOVERY_PROBLEM", "covering")
    monkeypatch.setenv("DISCOVERY_INSTANCE", str(inst))
    monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "20")
    return tmp_path


def fano_program(tmp_path):
    f = tmp_path / "cand.py"
    f.write_text(textwrap.dedent(f"""\
        import sys
        with open(sys.argv[2], "w") as out:
            out.write("{FANO}")
    """), encoding="utf-8")
    return f


def test_archives_feasible_solution(covering_env, monkeypatch):
    arch = covering_env / "arsiv"
    monkeypatch.setenv("DISCOVERY_ARCHIVE_DIR", str(arch))
    evaluate(fano_program(covering_env))
    files = list(arch.glob("cover-v7-k3-t2-cost7-*.txt"))
    assert len(files) == 1
    assert "1 2 4" in files[0].read_text(encoding="utf-8")


def test_below_threshold_filters(covering_env, monkeypatch):
    arch = covering_env / "arsiv"
    monkeypatch.setenv("DISCOVERY_ARCHIVE_DIR", str(arch))
    monkeypatch.setenv("DISCOVERY_ARCHIVE_BELOW", "6")  # cost 7 > 6 -> yok
    evaluate(fano_program(covering_env))
    assert not list(arch.glob("*.txt"))


def test_below_threshold_passes(covering_env, monkeypatch):
    arch = covering_env / "arsiv"
    monkeypatch.setenv("DISCOVERY_ARCHIVE_DIR", str(arch))
    monkeypatch.setenv("DISCOVERY_ARCHIVE_BELOW", "7")  # cost 7 <= 7 -> var
    evaluate(fano_program(covering_env))
    assert len(list(arch.glob("*.txt"))) == 1


def test_idempotent_same_content(covering_env, monkeypatch):
    arch = covering_env / "arsiv"
    monkeypatch.setenv("DISCOVERY_ARCHIVE_DIR", str(arch))
    prog = fano_program(covering_env)
    evaluate(prog)
    evaluate(prog)  # ayni cozum -> ayni sha1 -> tek dosya
    assert len(list(arch.glob("*.txt"))) == 1


def test_no_env_no_archive(covering_env):
    evaluate(fano_program(covering_env))  # DISCOVERY_ARCHIVE_DIR yok
    assert not list(covering_env.glob("arsiv/*.txt"))


def test_infeasible_not_archived(covering_env, monkeypatch, tmp_path):
    arch = covering_env / "arsiv"
    monkeypatch.setenv("DISCOVERY_ARCHIVE_DIR", str(arch))
    bad = covering_env / "bad.py"
    bad.write_text(textwrap.dedent("""\
        import sys
        with open(sys.argv[2], "w") as out:
            out.write("1 2 4\\n")
    """), encoding="utf-8")
    evaluate(bad)
    assert not list(arch.glob("*.txt"))