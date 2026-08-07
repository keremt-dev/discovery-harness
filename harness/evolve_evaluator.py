"""OpenEvolve evaluator adaptoru — probleme-agnostik.

Akis (cvrp-discovery faz3/evolve_evaluator.py deseninin cekirdege
tasinmis hali; bu dosyada hicbir problem adi GECMEZ):

- Problem ve instance env'den secilir; eklenti registry'den yuklenir.
- Aday program harness.runner ile ayri process'te, tempdir cwd'de,
  wall-clock timeout'la kosar; kismi cikti kurtarilir.
- Verdict, eklentinin evaluate_text'inden gelir (tam aritmetik; solver
  beyani yok sayilir). Solver'a referans/BKS degeri SIZDIRILMAZ.
- OpenEvolve MAKSIMIZE eder; isaret donusumu tek yerde:
  combined_score = harness.score.combined_score(fitness, SENSE).
- Hata ciktilari (stderr, violation ozeti) artifact olarak LLM'e geri
  doner — "neden kotuydu" bilgisi mutasyon kalitesini artiriyor.

Yapilandirma (env):
  DISCOVERY_PROBLEM          eklenti adi (problems/ altinda) — zorunlu
  DISCOVERY_INSTANCE         instance yolu; ';' ile AYRILMIS LISTE olabilir
                             (fitness = ortalama combined_score; feasible =
                             min — tek instance'a ezber olmasin, 2026-08-05)
  DISCOVERY_SOLVER_TIMEOUT_S solver sure limiti (instance BASINA), sn (55)
  DISCOVERY_PROBLEMS_ROOT    eklenti koku override (test icin)
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness.registry import load_problem  # noqa: E402
from harness.runner import run_candidate  # noqa: E402
from harness.score import combined_score  # noqa: E402

try:
    from openevolve.evaluation_result import EvaluationResult
except ImportError:  # test ortaminda openevolve yoksa dict'e dus
    EvaluationResult = None


def _result(metrics, artifacts):
    if EvaluationResult is not None:
        return EvaluationResult(metrics=metrics, artifacts=artifacts)
    return metrics


def _evaluate_one(problem, instance_path, program_path, timeout_s):
    """Tek instance icin (metrics, artifacts) dondurur."""
    # bozuk instance raise eder: enstruman hatasi, dongu durmali
    instance = problem.parse_instance(instance_path)
    rr = run_candidate(program_path, instance_path, timeout_s)

    artifacts = {}
    if rr.timed_out:
        artifacts["failure"] = f"timeout: {timeout_s:.0f} sn duvar saati asildi"
    elif rr.returncode != 0:
        artifacts["failure"] = f"solver exit code {rr.returncode}"
    if rr.stderr_tail:
        artifacts["stderr"] = rr.stderr_tail

    verdict = problem.evaluate_text(instance, rr.solution_text)
    if not verdict["feasible"]:
        artifacts["violations"] = json.dumps(verdict["violations"])

    metrics = {
        "combined_score": float(
            combined_score(verdict["fitness"], problem.sense)),
        "cost": float(verdict["cost"]),
        "feasible": 1.0 if verdict["feasible"] else 0.0,
        "solver_s": round(rr.wall_s, 3),
        "eval_ms": float(verdict["eval_ms"]),
    }
    return metrics, artifacts


def evaluate(program_path):
    problem_name = os.environ.get("DISCOVERY_PROBLEM")
    instance_env = os.environ.get("DISCOVERY_INSTANCE")
    if not problem_name or not instance_env:
        raise RuntimeError(
            "DISCOVERY_PROBLEM ve DISCOVERY_INSTANCE env degiskenleri zorunlu")
    # Runner tempdir cwd'de kosturur: goreli instance yollari burada,
    # cagiranin cwd'sinde MUTLAK'a cevrilir (cvrp deseni).
    instance_paths = [Path(p.strip()).resolve()
                      for p in instance_env.split(";") if p.strip()]
    timeout_s = float(os.environ.get("DISCOVERY_SOLVER_TIMEOUT_S", "55"))
    problems_root = os.environ.get("DISCOVERY_PROBLEMS_ROOT") or None

    problem = load_problem(problem_name, problems_root=problems_root)

    per_metrics, artifacts = [], {}
    for path in instance_paths:
        m, a = _evaluate_one(problem, path, program_path, timeout_s)
        per_metrics.append((path.stem, m))
        for key, val in a.items():  # instance adiyla onekle
            artifacts[f"{path.stem}:{key}" if len(instance_paths) > 1
                      else key] = val

    n = len(per_metrics)
    metrics = {
        "combined_score": sum(m["combined_score"]
                              for _, m in per_metrics) / n,
        "cost": sum(m["cost"] for _, m in per_metrics) / n,
        "feasible": min(m["feasible"] for _, m in per_metrics),
        "solver_s": round(sum(m["solver_s"] for _, m in per_metrics), 3),
        "eval_ms": sum(m["eval_ms"] for _, m in per_metrics),
    }
    if n > 1:
        artifacts["per_instance"] = json.dumps(
            {name: {"combined_score": m["combined_score"],
                    "feasible": m["feasible"]}
             for name, m in per_metrics})
    return _result(metrics, artifacts)


if __name__ == "__main__":
    r = evaluate(sys.argv[1])
    m = r.metrics if hasattr(r, "metrics") else r
    print(json.dumps(m, indent=1))
