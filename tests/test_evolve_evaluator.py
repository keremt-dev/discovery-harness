"""harness/evolve_evaluator.py testleri — OpenEvolve adaptoru.

Adaptor probleme-agnostiktir: problem adi/instance yolu env'den gelir,
SENSE isareti harness.score.combined_score'dan. Solver'a referans deger
SIZDIRILMAZ; artifact'lar (stderr, violation ozeti) LLM'e geri doner.
"""

import textwrap
from pathlib import Path

import pytest

from harness.evolve_evaluator import evaluate

REPO = Path(__file__).resolve().parent.parent
ROUTER = REPO / "data" / "kofn" / "instances" / "router-n10-k20.kofn"


def write_program(tmp_path, body, name="cand.py"):
    f = tmp_path / name
    f.write_text(textwrap.dedent(body), encoding="utf-8")
    return f


@pytest.fixture
def kofn_env(monkeypatch):
    monkeypatch.setenv("DISCOVERY_PROBLEM", "kofn")
    monkeypatch.setenv("DISCOVERY_INSTANCE", str(ROUTER))
    monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "15")


def metrics_of(result):
    return result.metrics if hasattr(result, "metrics") else result


def artifacts_of(result):
    return result.artifacts if hasattr(result, "artifacts") else {}


class TestEvaluate:
    def test_good_candidate_scores_positive(self, tmp_path, kofn_env):
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write("10 0 0\\n")
        """)
        m = metrics_of(evaluate(prog))
        assert m["feasible"] == 1.0
        # SENSE=max -> combined_score = +fitness = R
        assert round(m["combined_score"], 8) == 0.99985291
        assert m["cost"] == m["combined_score"]
        assert m["solver_s"] >= 0

    def test_infeasible_candidate_scores_negative_with_artifacts(
            self, tmp_path, kofn_env):
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write("5 0 0\\n")
        """)
        r = evaluate(prog)
        m = metrics_of(r)
        assert m["feasible"] == 0.0
        assert m["combined_score"] < 0
        assert "wrong_total" in artifacts_of(r).get("violations", "")

    def test_timeout_gives_deterministic_bad_score(self, tmp_path,
                                                   kofn_env, monkeypatch):
        monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "1")
        prog = write_program(tmp_path, """\
            import time
            time.sleep(30)
        """)
        r = evaluate(prog)
        m = metrics_of(r)
        assert m["feasible"] == 0.0
        assert m["combined_score"] < 0
        assert "timeout" in artifacts_of(r).get("failure", "")

    def test_crashing_candidate_stderr_in_artifacts(self, tmp_path, kofn_env):
        prog = write_program(tmp_path, """\
            raise RuntimeError("bilerek patladim")
        """)
        r = evaluate(prog)
        assert metrics_of(r)["combined_score"] < 0
        assert "bilerek patladim" in artifacts_of(r).get("stderr", "")

    def test_sense_min_problem_negates_fitness(self, tmp_path, monkeypatch):
        # Agnostiklik + isaret: sahte min-problemde combined = -fitness.
        root = tmp_path / "problems_root"
        plugin = root / "sahtemin"
        plugin.mkdir(parents=True)
        (plugin / "__init__.py").write_text(textwrap.dedent("""\
            SENSE = "min"

            def parse_instance(path):
                return {"path": str(path)}

            def evaluate_text(instance, text):
                return {"feasible": True, "cost": 5.0, "violations": {},
                        "fitness": 5.0, "eval_ms": 0, "info": {}}

            def penalty_scale(instance):
                return 1.0
        """), encoding="utf-8")
        monkeypatch.setenv("DISCOVERY_PROBLEM", "sahtemin")
        monkeypatch.setenv("DISCOVERY_INSTANCE", str(ROUTER))
        monkeypatch.setenv("DISCOVERY_PROBLEMS_ROOT", str(root))
        monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "15")
        prog = write_program(tmp_path, """\
            import sys
            open(sys.argv[2], "w").write("x")
        """)
        m = metrics_of(evaluate(prog))
        assert m["combined_score"] == -5.0

    def test_relative_instance_path_resolved(self, tmp_path, monkeypatch):
        # Runner aday programi tempdir cwd'de kosturur; adapter goreli
        # instance yolunu evaluate aninda MUTLAK'a cevirmeli (cvrp deseni).
        monkeypatch.setenv("DISCOVERY_PROBLEM", "kofn")
        monkeypatch.setenv("DISCOVERY_INSTANCE",
                           "data/kofn/instances/router-n10-k20.kofn")
        monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "15")
        monkeypatch.chdir(REPO)
        prog = write_program(tmp_path, """\
            import sys
            # instance'i GERCEKTEN okuyabildigini kanitla
            open(sys.argv[1], encoding="utf-8").read()
            with open(sys.argv[2], "w") as f:
                f.write("10 0 0\\n")
        """)
        m = metrics_of(evaluate(prog))
        assert m["feasible"] == 1.0

    def test_missing_env_raises(self, tmp_path, monkeypatch):
        monkeypatch.delenv("DISCOVERY_PROBLEM", raising=False)
        monkeypatch.delenv("DISCOVERY_INSTANCE", raising=False)
        prog = write_program(tmp_path, "pass")
        with pytest.raises(RuntimeError, match="DISCOVERY_"):
            evaluate(prog)


class TestMultiInstance:
    """DISCOVERY_INSTANCE = ';' ayracli liste -> fitness ortalamasi.

    Varlik sebebi: tek instance'a evrim ezber yapabilir (2026-08-05
    gradyan tamiri); 2-3 instance ortalamasi genelleme baskisi kurar.
    """

    def _env(self, monkeypatch, paths):
        monkeypatch.setenv("DISCOVERY_PROBLEM", "kofn")
        monkeypatch.setenv("DISCOVERY_INSTANCE", ";".join(map(str, paths)))
        monkeypatch.setenv("DISCOVERY_SOLVER_TIMEOUT_S", "15")

    def test_mean_of_per_instance_scores(self, tmp_path, monkeypatch):
        # Ayni instance iki kez -> ortalama tekil skora esit olmali.
        self._env(monkeypatch, [ROUTER, ROUTER])
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write("10 0 0\\n")
        """)
        m = metrics_of(evaluate(prog))
        assert round(m["combined_score"], 8) == 0.99985291
        assert m["feasible"] == 1.0

    def test_one_infeasible_drops_feasible_flag(self, tmp_path, monkeypatch):
        gen = REPO / "data" / "kofn" / "instances" / "gen-sert-n20-m4-s1.kofn"
        # "10 0 0" router'da fizibil (M=3) ama sert instance'ta M=4 ->
        # parse_error -> infeasible. feasible = min, skor = ortalama.
        self._env(monkeypatch, [ROUTER, gen])
        prog = write_program(tmp_path, """\
            import sys
            with open(sys.argv[2], "w") as f:
                f.write("10 0 0\\n")
        """)
        r = evaluate(prog)
        m = metrics_of(r)
        assert m["feasible"] == 0.0
        # ortalama: (0.99985291 + negatif ceza) / 2 < 0.5
        assert m["combined_score"] < 0.5
        assert "per_instance" in artifacts_of(r)

    def test_instance_aware_solver_scores_on_both(self, tmp_path,
                                                  monkeypatch):
        gen = REPO / "data" / "kofn" / "instances" / "gen-sert-n20-m4-s1.kofn"
        # instance'i gercekten okuyan cozucu: M'e gore tahsis yazar
        # (en ucuz tipe tam dolum — fizibilite garantili).
        self._env(monkeypatch, [ROUTER, gen])
        prog = write_program(tmp_path, """\
            import sys
            headers, types = {}, {}
            for raw in open(sys.argv[1], encoding="utf-8"):
                line = raw.split("#", 1)[0].strip()
                if not line:
                    continue
                p = line.split()
                if p[0] == "TYPE":
                    types[int(p[1])] = float(p[3])
                else:
                    headers[p[0]] = p[1]
            m = int(headers["M"]); n = int(headers["N"])
            cheapest = min(types, key=types.get)
            alloc = [n if j == cheapest else 0 for j in range(1, m + 1)]
            with open(sys.argv[2], "w") as f:
                f.write(" ".join(map(str, alloc)) + "\\n")
        """)
        m = metrics_of(evaluate(prog))
        assert m["feasible"] == 1.0  # iki instance'ta da fizibil
