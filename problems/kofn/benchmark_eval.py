"""Benchmark v1 degerlendirme tablosu (Iz-2 yayin paketi, 2026-08-05).

Her instance icin: verilen cozuculeri GERCEK sozlesmeyle kosturur
(harness.runner: ayri process, timeout, kismi-cikti kurtarma), degerleri
TAM ARITMETIKLE yeniden hesaplar; kucuk katmanda kanitli optimum
(enumeration), orta katmanda refsearch kolonu ekler. Cikti: markdown.

Kolon anlamlari:
- cozucu kolonlari: exact R (feasible degilse INFEASIBLE) + duvar saati
- refsearch: cok-baslangicli referans arama (n <= refsearch_max_n)
- kanitli opt: exhaustive enumeration (kompozisyon <= enum_limit)

CLI: python -m problems.kofn.benchmark_eval <cikti.md> [instance...]
     (instance verilmezse data/kofn/instances/gen-{router,enerji}-*.kofn)
"""

import os
import sys
import time
from math import comb
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from harness.runner import run_candidate  # noqa: E402

from .enumerate import enumerate_optimum  # noqa: E402
from .io import parse_instance  # noqa: E402
from .objective import evaluate_text  # noqa: E402
from .refsearch import reference_search  # noqa: E402


def _run_solver(program, instance_path, seed_time_s, timeout_s):
    os.environ["KOFN_SEED_TIME_S"] = str(seed_time_s)
    t0 = time.perf_counter()
    rr = run_candidate(program, instance_path, timeout_s)
    return rr.solution_text, time.perf_counter() - t0


def build_report(instance_paths, out_md, solvers, refsearch_max_n=100,
                 enum_limit=200000, seed_time_s=45, timeout_s=90):
    labels = list(solvers)
    header = ("| instance | n | M | " +
              " | ".join(f"{l} R (s)" for l in labels) +
              " | refsearch R | kanıtlı opt |")
    sep = "|---" * (3 + len(labels) + 2) + "|"
    lines = [header, sep]

    for path in instance_paths:
        inst = parse_instance(path)
        cells = []
        for label in labels:
            text, wall = _run_solver(solvers[label], path, seed_time_s,
                                     timeout_s)
            v = evaluate_text(inst, text)
            cells.append(f"{v['cost']:.6f} ({wall:.0f}s)"
                         if v["feasible"] else f"INFEASIBLE ({wall:.0f}s)")

        if inst.n_total <= refsearch_max_n:
            ref = reference_search(inst, starts=32)
            ref_cell = f"{ref['reliability']:.6f}"
        else:
            ref_cell = "—"

        if comb(inst.n_total + inst.m - 1, inst.m - 1) <= enum_limit:
            opt = enumerate_optimum(inst)
            opt_cell = f"{float(opt['reliability']):.6f}"
        else:
            opt_cell = "—"

        lines.append(f"| {inst.name} | {inst.n_total} | {inst.m} | " +
                     " | ".join(cells) + f" | {ref_cell} | {opt_cell} |")
        print(f"tamam: {inst.name}", flush=True)

    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_md


def main(argv):
    out_md = argv[1]
    paths = [Path(p) for p in argv[2:]]
    if not paths:
        root = REPO / "data" / "kofn" / "instances"
        paths = sorted(root.glob("gen-router-*.kofn")) + sorted(
            root.glob("gen-enerji-*.kofn"))
    solvers = {
        "tohum": REPO / "problems" / "kofn" / "seed_solver.py",
        "evrilen-v1": REPO / "evolve" / "artifacts" / "best_20260805.py",
        "evrilen-v2": REPO / "evolve" / "artifacts" / "best_v2_20260805.py",
    }
    build_report(paths, out_md, solvers)
    print(f"yazildi: {out_md} ({len(paths)} instance)")


if __name__ == "__main__":
    main(sys.argv)
