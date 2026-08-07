"""Faz D baseline raporu: tohum solver vs kanitli optimum gap tablosu.

Her instance icin tohum solver'i GERCEK sozlesmeyle (ayri process, dosya
I/O) kosturur, verdict'i tam aritmetikli evaluator'den alir; kompozisyon
sayisi enum_limit altindaysa kanitli optimumu enumeration'la hesaplayip
gap'i yazar. Cikti: markdown tablo.

CLI: python -m problems.kofn.baseline <cikti.md> [instance.kofn ...]
     (instance verilmezse data/kofn/instances/*.kofn taranir)
"""

import os
import subprocess
import sys
import tempfile
import time
from math import comb
from pathlib import Path

from .enumerate import enumerate_optimum
from .io import parse_instance
from .objective import evaluate_text

_SEED_SOLVER = Path(__file__).resolve().parent / "seed_solver.py"


def _run_seed(instance_path, seed_time_s):
    env = dict(os.environ, KOFN_SEED_TIME_S=str(seed_time_s))
    with tempfile.TemporaryDirectory(prefix="kofn-base-") as tmp:
        out = Path(tmp) / "out.txt"
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(_SEED_SOLVER), str(instance_path), str(out)],
            capture_output=True, text=True, cwd=tmp, env=env,
            timeout=seed_time_s * 6 + 30,
        )
        dt = time.perf_counter() - t0
        text = out.read_text(encoding="utf-8") if out.exists() else ""
        if proc.returncode != 0:
            text = ""
        return text, dt


def build_report(instance_paths, out_md, enum_limit=200000, seed_time_s=5):
    lines = [
        "| instance | n | M | K | bütçe | tohum R | tohum s | kanıtlı opt R | gap % |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for path in instance_paths:
        inst = parse_instance(path)
        sol_text, solver_s = _run_seed(path, seed_time_s)
        v = evaluate_text(inst, sol_text)
        seed_r = v["cost"] if v["feasible"] else None
        seed_cell = f"{seed_r:.6f}" if seed_r is not None else "INFEASIBLE"

        compositions = comb(inst.n_total + inst.m - 1, inst.m - 1)
        if compositions <= enum_limit:
            opt = float(enumerate_optimum(inst)["reliability"])
            opt_cell = f"{opt:.6f}"
            gap_cell = (f"{(opt - seed_r) / opt * 100:.3f}"
                        if seed_r is not None else "-")
        else:
            opt_cell = f"- (>{enum_limit} kompozisyon)"
            gap_cell = "-"

        lines.append(
            f"| {inst.name} | {inst.n_total} | {inst.m} | {inst.k} "
            f"| {inst.budget} | {seed_cell} | {solver_s:.1f} "
            f"| {opt_cell} | {gap_cell} |")

    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_md


def main(argv):
    out_md = argv[1]
    paths = [Path(p) for p in argv[2:]]
    if not paths:
        root = Path(__file__).resolve().parents[2] / "data" / "kofn" / "instances"
        paths = sorted(root.glob("*.kofn"))
    build_report(paths, out_md)
    print(f"yazildi: {out_md} ({len(paths)} instance)")


if __name__ == "__main__":
    main(sys.argv)
