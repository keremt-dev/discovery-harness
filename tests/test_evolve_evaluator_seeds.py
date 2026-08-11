"""DISCOVERY_EVAL_SEEDS coklu-seed ortalama testleri.

2026-08-10 56-piyango dersi: tek kosunun makine-ani sansini degil
PROGRAMI olcmek icin fitness = seed'ler uzerinden ortalama.
"""
import textwrap

import pytest

from harness.evolve_evaluator import evaluate


@pytest.fixture
def covering_env(monkeypatch, tmp_path):
    inst = tmp_path / "cover-v7-k3-t2.cover"
    inst.write_text("v 7\nk 3\nt 2\n", encoding="utf-8")
    monkeypatch.setenv("DISCOVERY_PROBLEM", "covering")
    monkeypatch.setenv("DISCOVERY_INSTANCE", str(inst))
    monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "20")
    # Dis ortamdan sizabilecek env'ler testi bozmasin / arsive yazmasin
    for var in ("DISCOVERY_EVAL_SEEDS", "DISCOVERY_ARCHIVE_DIR",
                "DISCOVERY_ARCHIVE_BELOW", "DISCOVERY_ARCHIVE_ABOVE"):
        monkeypatch.delenv(var, raising=False)
    return tmp_path


FANO = "1 2 4\\n1 3 5\\n2 3 6\\n1 6 7\\n2 5 7\\n3 4 7\\n4 5 6\\n"


def seed_sensitive_program(tmp_path):
    # seed 0 -> optimal 7 blok (fitness 1.0); baska seed -> 8 blok (7/8)
    f = tmp_path / "cand.py"
    f.write_text(textwrap.dedent(f"""\
        import sys
        seed = "0"
        if "--seed" in sys.argv:
            seed = sys.argv[sys.argv.index("--seed") + 1]
        sol = "{FANO}"
        if seed != "0":
            sol += "1 2 3\\n"
        with open(sys.argv[2], "w") as out:
            out.write(sol)
    """), encoding="utf-8")
    return f


def metrics_of(result):
    return result.metrics if hasattr(result, "metrics") else result


def test_mean_over_seeds(covering_env, monkeypatch):
    monkeypatch.setenv("DISCOVERY_EVAL_SEEDS", "0,1")
    m = metrics_of(evaluate(seed_sensitive_program(covering_env)))
    assert m["combined_score"] == pytest.approx((1.0 + 7 / 8) / 2)
    assert m["cost"] == 7.0          # en iyi kosunun cost'u
    assert m["feasible"] == 1.0


def test_no_env_single_run_no_args(covering_env):
    m = metrics_of(evaluate(seed_sensitive_program(covering_env)))
    assert m["combined_score"] == pytest.approx(1.0)  # arg'siz -> seed 0 yolu
