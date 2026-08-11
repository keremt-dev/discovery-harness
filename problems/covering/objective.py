"""Kanonik covering dogrulayici + feasibility + verdict (saf tamsayi).

Dogrulama stratejisi: C(v,t) altkumelerini MATERYALIZE ETMEZ. Her blok
icin blogun C(k,t) t-altkumesi uretilir ve kapsanan kume olarak toplanir;
kapsanmayan sayisi = C(v,t) - |kapsanan|. Is yuku B*C(k,t) ile sinirli
(hedef hucrelerde ~10^4-10^5), C(v,t) ile DEGIL. Ornek kapsanmayan
altkume aramasi ayrica EXAMPLE_CAP adimla sinirlidir -> evaluator hicbir
girdiyle takilamaz.

SAF TAMSAYI aritmetigi — float yalniz fitness oraninda (deger tam
bolme sonucu; siralama icin yeterli). COZUM TARAFI ASLA RAISE ETMEZ:
her girdi bir verdict'e cozumlenir (kofn/capset deseni). Solver'in
"# size K" beyani verdict'i ETKILEMEZ; info.reported_size_matches
durustluk sensorune yazilir.

Fitness (gerekce spec.py'de):
  Feasible:   fitness = schoenheim(v,k,t) / |B| ∈ (0,1]; 1.0 = Schoenheim
              tavani. |B| < Schoenheim matematiksel olarak imkansiz;
              gorulurse info.instrument_alarm yazilir (enstruman bug'i,
              dongu DURUR — CLAUDE.md §8).
  Infeasible: fitness = -1 - min(1, ihlal_orani) ∈ [-2,-1] < her feasible.
              uncovered icin oran = kapsanmayan / C(v,t) -> kapsama
              ilerledikce -1'e yaklasir (gradyan). Yapisal ihlaller
              (bad_block, too_many_blocks) = -2 tabani.
Isaret donusumu SANA AIT DEGIL: harness/score.py SENSE="max" icin aynen
gecirir. Dokunma.
"""

import math
import time
from itertools import combinations

from .spec import penalty_scale, schoenheim

# B * C(k,t) is yuku bu esigi asarsa dogrulamaya hic girilmez ->
# too_many_blocks (infeasible). Hedef hucrelerde mesru cozumler ~10^4-10^5
# mertebesinde kalir; esik yalnizca spam/patolojik ciktiyi keser.
WORK_CAP = 20_000_000

# Kapsanmayan ORNEK arama sinnri (artifact niceligi; sayim bundan bagimsiz
# ve her zaman kesindir).
EXAMPLE_CAP = 2_000_000


def _parse_solution(instance, text):
    """(bloklar | None, reported_size | None) dondurur; asla raise etmez.

    Her bos olmayan satir: tam k adet FARKLI tamsayi (1..v). Kanonik form
    sirali tuple. Herhangi bir satir bozuksa -> (None, reported)
    (bad_block violation'a duser; capset bad_vector deseni).
    """
    k, v = instance.k, instance.v
    reported = None
    blocks = []
    saw_bad = False
    if not isinstance(text, str):
        return [], None  # non-str -> bos cozum gibi (never-raise)

    for raw in text.splitlines():
        hash_idx = raw.find("#")
        body = raw[:hash_idx] if hash_idx >= 0 else raw
        comment = raw[hash_idx + 1:] if hash_idx >= 0 else ""
        if "size" in comment.lower():
            toks = comment.split()
            si = next((i for i, tk in enumerate(toks)
                       if tk.lower() == "size"), None)
            if si is not None and si + 1 < len(toks):
                try:
                    reported = int(toks[si + 1])
                except ValueError:
                    pass
        line = body.strip()
        if not line:
            continue
        toks = line.split()
        try:
            nums = [int(x) for x in toks]
        except ValueError:
            saw_bad = True
            continue
        if len(nums) != k or len(set(nums)) != k or \
                any(not (1 <= x <= v) for x in nums):
            saw_bad = True
            continue
        blocks.append(tuple(sorted(nums)))

    if saw_bad:
        return None, reported
    return blocks, reported


def evaluate_text(instance, text) -> dict:
    t0 = time.perf_counter()
    v, k, t = instance.v, instance.k, instance.t
    scale = penalty_scale(instance)
    total_tsets = math.comb(v, t)
    per_block = math.comb(k, t)
    violations = {}
    info = {}
    uncovered = None

    blocks, reported = _parse_solution(instance, text)

    if blocks is None:
        violations["bad_block"] = {
            "detail": f"her satir tam {k} adet FARKLI tamsayi (1..{v}) olmali"}
    elif len(blocks) * per_block > WORK_CAP:
        violations["too_many_blocks"] = {
            "count": len(blocks),
            "detail": f"is yuku siniri asildi (B*C(k,t) > {WORK_CAP})"}
    else:
        if len(set(blocks)) != len(blocks):
            dup = len(blocks) - len(set(blocks))
            violations["duplicate_block"] = {"count": dup}

        covered = set()
        for b in blocks:
            covered.update(combinations(b, t))
        uncovered = total_tsets - len(covered)
        info["covered_tsets"] = len(covered)
        info["total_tsets"] = total_tsets

        if uncovered:
            violations["uncovered"] = {"count": uncovered}
            example = None
            for i, c in enumerate(combinations(range(1, v + 1), t)):
                if i >= EXAMPLE_CAP:
                    break
                if c not in covered:
                    example = list(c)
                    break
            if example is not None:
                info["example_uncovered"] = example

    feasible = not violations
    cost = len(blocks) if blocks is not None else 0

    if feasible:
        fitness = scale / cost  # cost >= 1: bos cozum uncovered'a duser
        if cost < schoenheim(v, k, t):
            # Matematiksel olarak imkansiz -> enstruman alarmi (§8: dongu durur)
            info["instrument_alarm"] = (
                f"|B|={cost} < Schoenheim={int(scale)}: evaluator bug suphesi")
    else:
        if blocks is None or "too_many_blocks" in violations:
            fitness = -2.0
        else:
            violation_count = uncovered if uncovered else 0
            if "duplicate_block" in violations:
                violation_count += violations["duplicate_block"]["count"]
            fitness = -1.0 - min(1.0, violation_count / total_tsets)

    info["reported_size"] = reported
    if reported is None:
        info["reported_size_matches"] = None
    elif blocks is None:
        info["reported_size_matches"] = False
    else:
        info["reported_size_matches"] = (reported == len(set(blocks)))

    return {
        "feasible": feasible,
        "cost": cost,
        "violations": violations,
        "fitness": fitness,
        "eval_ms": int((time.perf_counter() - t0) * 1000),
        "info": info,
    }
