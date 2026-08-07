"""Kanonik hedef (TAM aritmetik) + feasibility + verdict.

Guvenilirlik, Ozkut & Tutuncu 2025 Teorem 1 ile fractions.Fraction
uzerinde TAM hesaplanir (float mesafe toplanmaz kuralinin P1 karsiligi).
Solver'in beyan ettigi deger ("R <float>" satiri) verdict'i ETKILEMEZ;
yalnizca info.reported_matches durustluk sensorune yazilir.

COZUM TARAFI ASLA RAISE ETMEZ: her girdi bir verdict'e cozumlenir.

Ceza gerekcesi (spec.penalty_scale ile birlikte): SENSE=max oldugu icin
ceza fitness'i asagi ceker. infeasible fitness = R_taban - scale*(1 + V);
V, ihlal buyukluklerinin normalize toplami (gradyan: daha az ihlal ->
daha az kotu fitness). scale=3 > sup(R)-inf(R)=1 oldugundan en umutsuz
feasible cozum (R=0) bile her infeasible'dan iyidir -> hicbir ihlal
karli olamaz.
"""

import time
from fractions import Fraction

from .spec import penalty_scale


def system_reliability(counts, instance) -> Fraction:
    """Teorem 1: R = P(Σ ξ_j·N_j >= k), N_j ~ Binom(n_j, p_j) bagimsiz.

    Hesap, toplam agirlik dagiliminin bilesen basina konvolusyonuyla (DP)
    yapilir: kompozisyon sayisi Π(n_j+1) ile patlayan naif toplamin aksine
    durum sayisi ayrik agirlik toplamlariyla sinirlidir (tamsayi
    agirliklarda <= N·w_max) — buyuk n'de de calisir. Sonuc naif toplamla
    birebir ayni Fraction'dir; makale tablolarina karsi dogrulanmistir
    (tests/test_kofn.py + data/kofn/reference/verify_ozkut2025.py).
    counts: tahsis (n_1..n_M), >= 0.
    """
    dist = {Fraction(0): Fraction(1)}  # toplam agirlik -> olasilik
    for j, nj in enumerate(counts):
        w, p = instance.weights[j], instance.reliabilities[j]
        q = 1 - p
        for _ in range(nj):
            new = {}
            for acc_w, acc_p in dist.items():
                new[acc_w] = new.get(acc_w, Fraction(0)) + acc_p * q
                wu = acc_w + w
                new[wu] = new.get(wu, Fraction(0)) + acc_p * p
            dist = new
    return sum(
        (pr for wt, pr in dist.items() if wt >= instance.k), Fraction(0))


def _parse_solution(instance, text):
    """(counts | None, reported | None) dondurur; asla raise etmez."""
    reported = None
    alloc_line = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if parts[0] == "R" and len(parts) == 2 and reported is None:
            try:
                reported = float(parts[1])
            except ValueError:
                pass  # bozuk beyan satiri: sessizce yok say (sensor bos kalir)
            continue
        if alloc_line is None:
            alloc_line = parts
    if alloc_line is None or len(alloc_line) != instance.m:
        return None, reported
    try:
        return tuple(int(tok) for tok in alloc_line), reported
    except ValueError:
        return None, reported


def evaluate_text(instance, text) -> dict:
    t0 = time.perf_counter()
    scale = penalty_scale(instance)
    violations = {}
    info = {}

    counts, reported = _parse_solution(instance, text if isinstance(text, str) else "")
    rel_violation = 0.0
    r = None  # Fraction | None

    if counts is None:
        violations["parse_error"] = {
            "detail": f"tam {instance.m} adet tamsayi tahsis satiri bekleniyor"}
        rel_violation += 1.0
    else:
        info["alloc"] = list(counts)
        negatives = [c for c in counts if c < 0]
        if negatives:
            violations["negative_count"] = {"count": len(negatives)}
            rel_violation += sum(-c for c in negatives) / instance.n_total
        total = sum(counts)
        if total != instance.n_total:
            violations["wrong_total"] = {
                "expected": instance.n_total, "got": total}
            rel_violation += abs(total - instance.n_total) / instance.n_total
        money = sum(c * n for c, n in zip(instance.costs, counts))
        info["money_cost"] = float(money)
        if money > instance.budget:
            overshoot = money - instance.budget
            violations["budget_exceeded"] = {
                "budget": float(instance.budget), "cost": float(money),
                "overshoot": float(overshoot)}
            rel_violation += float(overshoot / instance.budget)
        if not negatives:
            r = system_reliability(counts, instance)

    feasible = not violations
    cost = float(r) if r is not None else 0.0
    if feasible:
        fitness = cost
    else:
        fitness = cost - scale * (1.0 + rel_violation)

    info["reported_objective"] = reported
    if reported is None:
        info["reported_matches"] = None
    elif r is None:
        info["reported_matches"] = False
    else:
        # CLAUDE.md: 6 haneye yuvarlama + 1e-9 tolerans
        info["reported_matches"] = (
            abs(round(float(r), 6) - round(reported, 6)) < 1e-9)

    return {
        "feasible": feasible,
        "cost": cost,
        "violations": violations,
        "fitness": fitness,
        "eval_ms": int((time.perf_counter() - t0) * 1000),
        "info": info,
    }
