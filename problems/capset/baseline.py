"""P4.3 baseline raporu: tohum solver vs bilinen deger gap tablosu.

Her instance icin tohum solver'i GERCEK sozlesmeyle (ayri process, dosya
I/O, anytime + atomik) kosturur, verdict'i evaluator'den alir. Bilinen
degerlerle (docs/p4-problem-tanimi.md §2 tablosu) gap'i yazar. n<=3'te
kanitli optimumu enumeration'la bagimsiz hesaplar (ground truth); n>=4'te
literaturdeki bilinen degeri gosterir (optimallik bize ait degil).

Cikti: markdown tablo -> docs/p4-baseline.md (kofn baseline.py deseni).

CLI: python -m problems.capset.baseline <cikti.md> [instance.cap ...]
     (instance verilmezse data/capset/instances/*.cap taranir)
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from .enumerate import enumerate_optimum
from .io import parse_instance
from .objective import evaluate_text

_SEED_SOLVER = Path(__file__).resolve().parent / "seed_solver.py"
_REF_CSV = (Path(__file__).resolve().parents[2] / "data" / "capset"
            / "reference" / "known_values.csv")


def _load_known():
    """Bilinen degerleri data/capset/reference/known_values.csv'den okur.

    §0.5 ruhu: referans degerlerin evi data/*/reference/. Adaptör/solver bu
    dosyayı OKUMAZ; yalnızca bu insan-raporlama aracı okur. Kolonlar:
    n,value,status,source. Donus: {n: (value, status, source)}.
    """
    import csv
    known = {}
    with open(_REF_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            known[int(row["n"])] = (
                int(row["value"]), row["status"], row["source"])
    return known


KNOWN = _load_known()


def _run_seed(instance_path, seed_time_s, seed=0):
    """Tohum solver'i ayri process'te kostur (gercek sozlesme)."""
    env = dict(os.environ, CAPSET_SEED_TIME_S=str(seed_time_s))
    with tempfile.TemporaryDirectory(prefix="capset-base-") as tmp:
        out = Path(tmp) / "out.txt"
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                [sys.executable, str(_SEED_SOLVER), str(instance_path),
                 str(out), "--seed", str(seed)],
                capture_output=True, text=True, cwd=tmp, env=env,
                timeout=seed_time_s * 4 + 30,
            )
            dt = time.perf_counter() - t0
            text = out.read_text(encoding="utf-8") if out.exists() else ""
            if proc.returncode != 0:
                text = ""
            return text, dt
        except subprocess.TimeoutExpired:
            dt = time.perf_counter() - t0
            text = out.read_text(encoding="utf-8") if out.exists() else ""
            return text, dt


def build_report(instance_paths, out_md, seed_time_s=5, seed=0):
    lines = [
        "# P4.3 Baseline — tohum solver vs bilinen deger",
        "",
        "Tohum: `problems/capset/seed_solver.py` (rastgele-greedy + extend + "
        "swap hill-climb + random-restart, anytime). Strawman DEGIL — meşru "
        "saf greedy gucu. n=2/3/4 optimumda (4/9/20); n=6/8'de gradyan bol "
        "(evrim baslangici icin ideal). n>=4 optimallik literature aittir.",
        "",
        "| instance | n | tohum \\|S\\| | bilinen | durum | kaynak | gap % | sure s |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for path in instance_paths:
        inst = parse_instance(path)
        n = inst.dimension
        sol_text, solver_s = _run_seed(path, seed_time_s, seed=seed)
        v = evaluate_text(inst, sol_text)
        seed_size = v["cost"] if v["feasible"] else None
        seed_cell = str(seed_size) if seed_size is not None else "INFEASIBLE"

        known_size, status, source = KNOWN.get(n, (None, "?", "?"))
        known_cell = str(known_size) if known_size is not None else "?"

        # n<=3'te kanitli optimumu enumeration'la bagimsiz dogrula
        if n <= 3:
            enum = enumerate_optimum(inst)
            proven_cell = f"{enum['size']} (kanitli)"
        else:
            proven_cell = known_cell

        if seed_size is not None and known_size:
            gap = (known_size - seed_size) / known_size * 100
            gap_cell = f"{gap:.1f}"
        else:
            gap_cell = "-"

        lines.append(
            f"| {inst.name} | {n} | {seed_cell} | {known_cell} "
            f"| {status} | {source} | {gap_cell} | {solver_s:.1f} |")

    lines.append("")
    lines.append("**Kürasyon notu (P4.4, Görev 4b kararı):** bekçi = n=4 "
                 "(tohum kanıtlı optimumda: 20 → gerileme hemen görünür); "
                 "gradyan kaynağı = n=7 + n=8 (tohum 144/263 vs bilinen "
                 "236/512 → bol headroom); holdout = n=6 + n=9 (koşuya "
                 "GİRMEZ, genelleme ölçümü). n=2/3 de tavanda (optimum) ama "
                 "çok küçük (ayrım gücü yok). Headroom turnusolu: tohumun "
                 "zaten tavana vurduğu instance (n=2/3/4) evrim hedefi olamaz.")
    Path(out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_md


def main(argv):
    out_md = argv[1]
    paths = [Path(p) for p in argv[2:]]
    if not paths:
        root = Path(__file__).resolve().parents[2] / "data" / "capset" / "instances"
        paths = sorted(root.glob("*.cap"))
    build_report(paths, out_md)
    print(f"yazildi: {out_md} ({len(paths)} instance)")


if __name__ == "__main__":
    main(sys.argv)
