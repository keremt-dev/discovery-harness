"""P5 Faz D baseline raporu: tohum vs ground truth / arsiv (insan tarafi).

Her data/covering/instances/*.cover icin tohumu kosar, evaluator'la
puanlar ve referansla karsilastirir:

  - Kucuk hucre (enumerate kapsaminda): KANITLI optimum (bagimsiz kanit).
  - Buyuk hucre: LJCR arsiv degeri (size) + low_bd — data/covering/
    reference/sources/coverdata.json. INSAN RAPORU icindir; adaptore/
    prompt'a girmez (§0.5 sizinti kurali burada gecerli DEGIL cunku bu
    modul evrim dongusunun parcasi degildir; yine de solver'a aktarilmaz).

Headroom turnusolu (skill §3.1): hedef hucrede tohum, arsivin ANLAMLI
gerisinde kalmali (gradyan kaynagi); bekci hucrede tavana yakin olmali.

CLI: python -m problems.covering.baseline <rapor.md> [butce_s]
"""

import json
import sys
import time
from pathlib import Path

from .enumerate import ENUM_CAP, enumerate_optimum
from .io import parse_instance
from .objective import evaluate_text
from .seed_solver import format_solution, solve
from .spec import schoenheim

ROOT = Path(__file__).resolve().parent.parent.parent
INSTANCES = ROOT / "data" / "covering" / "instances"
COVERDATA = (ROOT / "data" / "covering" / "reference" / "sources"
             / "coverdata.json")


def build_rows(instances_dir, budget_s, seed=0):
    coverdata = json.loads(COVERDATA.read_text(encoding="utf-8")) \
        if COVERDATA.exists() else {}
    rows = []
    for path in sorted(Path(instances_dir).glob("*.cover")):
        inst = parse_instance(path)
        v, k, t = inst.v, inst.k, inst.t
        t0 = time.perf_counter()
        blocks = solve(v, k, t, time_budget_s=budget_s, seed=seed)
        solve_s = time.perf_counter() - t0
        verdict = evaluate_text(inst, format_solution(blocks))

        import math
        in_scope = (math.comb(v, k) <= ENUM_CAP
                    and math.comb(v, t) <= ENUM_CAP)
        if in_scope:
            ref = enumerate_optimum(inst)
            ref_val, ref_kind = ref["size"], "kanitli-opt"
        else:
            cell = coverdata.get(f"C({v},{k},{t})")
            ref_val = cell["size"] if cell else None
            ref_kind = "arsiv" if cell else "yok"

        rows.append({
            "instance": inst.name, "v": v, "k": k, "t": t,
            "schoenheim": schoenheim(v, k, t),
            "seed_cost": verdict["cost"],
            "feasible": verdict["feasible"],
            "fitness": round(verdict["fitness"], 4),
            "ref": ref_val, "ref_kind": ref_kind,
            "gap": (verdict["cost"] - ref_val) if ref_val else None,
            "solve_s": round(solve_s, 1),
        })
    return rows


def write_report(rows, out_path, budget_s):
    lines = [
        "# P5 covering — Faz D baseline (tohum vs referans)",
        "",
        f"Tohum butcesi: {budget_s} sn/instance, seed=0. Referans turu: "
        "kanitli-opt = bagimsiz enumerate kaniti; arsiv = LJCR (donmus "
        "2026-03-01, insan-tarafi — sandbox'a girmez).",
        "",
        "| instance | (v,k,t) | Schönheim | tohum | referans | tur | gap | fitness | süre(s) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['instance']} | ({r['v']},{r['k']},{r['t']}) "
            f"| {r['schoenheim']} | {r['seed_cost']}"
            f"{'' if r['feasible'] else ' (INFEASIBLE!)'} "
            f"| {r['ref']} | {r['ref_kind']} | "
            f"{'+' + str(r['gap']) if r['gap'] and r['gap'] > 0 else r['gap']} "
            f"| {r['fitness']} | {r['solve_s']} |")
    lines += [
        "",
        "Okuma: hedef hucrede pozitif gap = evrim icin headroom (tohum",
        "arsivin gerisinde — gradyan kaynagi). Bekci hucrede gap 0/kucuk =",
        "tohum tavanda, bekci gorevi gorur. INFEASIBLE gorulurse enstruman",
        "ya tohum bug'i demektir — dongu KURULMAZ (CLAUDE.md §8).",
        "",
    ]
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main(argv):
    out = argv[1] if len(argv) > 1 else "docs/faz-d-covering-baseline.md"
    budget_s = float(argv[2]) if len(argv) > 2 else 10.0
    rows = build_rows(INSTANCES, budget_s)
    write_report(rows, out, budget_s)
    for r in rows:
        flag = "" if r["feasible"] else "  !! INFEASIBLE"
        print(f"{r['instance']:>22}: tohum {r['seed_cost']:>4} | "
              f"ref {str(r['ref']):>4} ({r['ref_kind']}) | "
              f"gap {str(r['gap']):>5} | {r['solve_s']}s{flag}")
    print(f"\nrapor: {out}")


if __name__ == "__main__":
    main(sys.argv)
