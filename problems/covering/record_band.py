"""Track A gece probu bandi — rekor avi (docs/headroom-taramasi-20260814.md §3).

FRONTIER/NEAR/SEARCH hucrelerinde thinking620 genomunu uzun butceyle
SIRALI (tek solver sureci) kosturur; her kosu kesin sayimla dogrulanir;
arsiv-alti deger cikarsa REKOR-ADAYI olarak paketlenir. Aday != iddia:
iddia protokolu (sakin-makine re-run + bagimsiz verify + canli skorbord
ayni-gun kontrolu + kullanici onayi) elle yurutulur.

Tasarim kurallari (devralinan disiplin):
- Arsiv degeri SOLVER'A SIZMAZ — ne argv ne env; yalniz kosu SONRASI
  runner tarafinda kiyaslanir.
- Genom anytime (her iyilestirmeyi atomik yazar) → Ctrl-C/elektrik
  kesintisi guvenli; subprocess timeout = butce + tampon.
- Artimli ve idempotent: biten kosular results.csv'den okunur ve
  atlanir → band kaldiği yerden devam eder.
- Solver'in yazdigi degere GUVENILMEZ: cikti dosyasi
  problems.covering.objective.evaluate_text ile yeniden sayilir.

Kullanim:
    python -m problems.covering.record_band --out runs/probes/track-a-20260814
    python -m problems.covering.record_band --out ... --smoke   # tesisat testi
Secenekler: --tier core|search|all (vars. all), --budget-scale F (vars. 1.0),
            --solver PATH (vars. thinking620 genomu).
"""

import argparse
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

from problems.covering.io import parse_instance
from problems.covering.objective import evaluate_text

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SOLVER = REPO / "evolve" / "artifacts" / "best_v32_thinking_620_20260811.py"

# (v, k, t, canli_arsiv, butce_s, seeds) — arsiv degerleri 2026-08-14'te
# coveringrepository.com'da tek tek teyit edildi (headroom-taramasi §2).
# Oncelik sirasi = liste sirasi (gece erken biterse onemliler bitmis olur).
CORE = [
    (20, 12, 4, 20, 1200, (0, 1, 2)),
    (25, 16, 4, 17, 1200, (0, 1, 2)),
    (30, 12, 3, 30, 1200, (0, 1, 2)),
    (28,  9, 3, 56, 1200, (0, 1, 2)),
    (23, 10, 3, 24, 1200, (0, 1, 2)),
    (21, 10, 3, 18, 1200, (0, 1, 2)),
    (22, 10, 3, 19, 1200, (0, 1, 2)),
]
SEARCH = [
    (25, 10, 3, 30, 450, (0, 1)),
    (28, 10, 3, 36, 450, (0, 1)),
    (24, 11, 3, 20, 450, (0, 1)),
    (26, 11, 3, 26, 450, (0, 1)),
    (27, 11, 3, 27, 450, (0, 1)),
    (31, 11, 3, 39, 450, (0, 1)),
    (32, 11, 3, 40, 450, (0, 1)),
    (25, 12, 3, 17, 450, (0, 1)),
    (29, 12, 3, 27, 450, (0, 1)),
    (34, 12, 3, 39, 450, (0, 1)),
    (35, 12, 3, 40, 450, (0, 1)),
    (22,  8, 3, 38, 450, (0, 1)),
    (23,  8, 3, 40, 450, (0, 1)),
    (20,  7, 3, 45, 450, (0, 1)),
]

FIELDS = ["v", "k", "t", "tier", "arsiv", "butce_s", "seed",
          "feasible", "cost", "fark", "sure_s", "cikti"]


def ensure_instance(inst_dir: Path, v: int, k: int, t: int) -> Path:
    path = inst_dir / f"cover-v{v}-k{k}-t{t}.cover"
    if not path.exists():
        path.write_text(f"v {v}\nk {k}\nt {t}\n", encoding="utf-8")
    return path


def done_keys(csv_path: Path) -> set:
    if not csv_path.exists():
        return set()
    with csv_path.open(encoding="utf-8") as fh:
        return {(int(r["v"]), int(r["k"]), int(r["t"]), int(r["seed"]),
                 int(r["butce_s"])) for r in csv.DictReader(fh)}


def append_row(csv_path: Path, row: dict) -> None:
    new = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


def run_cell(solver, inst_path, out_path, seed, budget_s):
    """Tek kosu; anytime cikti sayesinde timeout'ta da dosya okunur."""
    import os
    env = dict(os.environ)
    env["COVERING_SEED_TIME_S"] = str(budget_s)
    # Arsiv degeri env'e/argv'ye BILEREK konmuyor.
    t0 = time.time()
    try:
        subprocess.run(
            [sys.executable, str(solver), str(inst_path), str(out_path),
             "--seed", str(seed)],
            env=env, timeout=budget_s + 120,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        pass  # anytime: o ana kadarki en iyi cikti diskte
    return time.time() - t0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--tier", choices=["core", "search", "all"], default="all")
    ap.add_argument("--budget-scale", type=float, default=1.0)
    ap.add_argument("--solver", default=str(DEFAULT_SOLVER))
    ap.add_argument("--smoke", action="store_true",
                    help="tesisat testi: ilk 3 hucre, seed 0, 5 sn butce")
    args = ap.parse_args()

    out_dir = Path(args.out)
    inst_dir = out_dir / "instances"
    sol_dir = out_dir / "solutions"
    for d in (inst_dir, sol_dir):
        d.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "results.csv"
    solver = Path(args.solver)
    if not solver.exists():
        print(f"HATA: solver yok: {solver}")
        return 2

    plan = []
    if args.tier in ("core", "all"):
        plan += [(c, "CORE") for c in CORE]
    if args.tier in ("search", "all"):
        plan += [(c, "SEARCH") for c in SEARCH]
    if args.smoke:
        plan = [(list(c[:4]) + [5, (0,)], tier) for c, tier in plan[:3]]

    total_s = sum(c[4] * args.budget_scale * len(c[5]) for c, _ in plan)
    done = done_keys(csv_path)
    print(f"band: {len(plan)} hucre, toplam butce ~{total_s/3600:.1f} saat "
          f"(bitmis {len(done)} kosu atlanacak); cikti: {out_dir}")

    candidates = []
    for (v, k, t, archive, base_budget, seeds), tier in plan:
        budget = max(5, int(base_budget * args.budget_scale))
        inst_path = ensure_instance(inst_dir, v, k, t)
        instance = parse_instance(inst_path)
        for seed in seeds:
            key = (v, k, t, seed, budget)
            if key in done:
                continue
            out_path = sol_dir / f"C{v}-{k}-{t}-seed{seed}.txt"
            elapsed = run_cell(solver, inst_path, out_path, seed, budget)
            feasible, cost = False, ""
            if out_path.exists():
                verdict = evaluate_text(
                    instance, out_path.read_text(encoding="utf-8"))
                feasible = bool(verdict["feasible"])
                cost = verdict["cost"] if feasible else ""
            diff = (cost - archive) if feasible else ""
            append_row(csv_path, {
                "v": v, "k": k, "t": t, "tier": tier, "arsiv": archive,
                "butce_s": budget, "seed": seed, "feasible": int(feasible),
                "cost": cost, "fark": diff, "sure_s": round(elapsed, 1),
                "cikti": out_path.name,
            })
            tag = ""
            if feasible and cost < archive:
                cand = out_dir / f"ADAY-C{v}-{k}-{t}-cost{cost}-seed{seed}.txt"
                shutil.copyfile(out_path, cand)
                candidates.append(str(cand))
                tag = "  *** REKOR-ADAYI ***"
            print(f"C({v},{k},{t}) seed{seed} butce {budget}s -> "
                  f"cost={cost if feasible else 'INFEASIBLE'} "
                  f"(arsiv {archive}, fark {diff}){tag}", flush=True)

    print("\n=== band bitti ===")
    if candidates:
        print("REKOR ADAYLARI (iddia DEGIL — protokol §4 elle yurutulur):")
        for c in candidates:
            print(f"  {c}")
    else:
        print("arsiv-alti deger yok (esitlemeler results.csv'de).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
