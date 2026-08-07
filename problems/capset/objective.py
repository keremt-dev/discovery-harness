"""Kanonik cap-set dogrulayici + feasibility + verdict (saf tamsayi).

Cap set: S alt kumesi F_3^n, oyle ki uc FARKLI x,y,z icin
x+y+z = 0 (mod 3, bilesen bilesen) OLMASIN. Dogrulama O(|S|^2):
her {x,y} cifti icin z = -(x+y) mod 3 hesapla; z in S ve z ∉ {x,y}
ise ihlal (her dogru 3 ciftte yakalanir -> line sayisi = eslesme/3).

SAF TAMSAYI aritmetigi — float YOK, tolerans YOK (docs/p4-problem-
tanimi.md §1; CVRP/P1'deki float sorunu burada en temiz haliyle yok).

COZUM TARAFI ASLA RAISE ETMEZ: her girdi bir verdict'e cozumlenir
(kofn objective.py deseni). Solver'in "# size K" beyani verdict'i
ETKILEMEZ; yalnizca info.reported_size_matches durustluk sensorune yazilir.

Fitness (gerekce spec.penalty_scale ile birlikte):
  Feasible:   fitness = |S| / penalty_scale(n),  penalty_scale = 2*3^n/n
              (Meshulam teorem siniri; teorem != referans tablosu -> sızıntı yok).
              fitness ∈ [0,1); instance'lar arasi olcek karsilastirilabilir.
  Infeasible: fitness = -1.0 - min(1.0, ihlal_sayisi / max(1, cift_sayisi))
              -> ∈ [-2,-1] < her feasible (>= 0). "Hicbir ihlal karli olamaz"
              kuralinin capset hali; infeasible'lar arasi gradyan da verir.
Isaret donusumu SANA AIT DEGIL: harness/score.py SENSE="max" icin aynen
gecirir. Dokunma.
"""

import time

from .spec import penalty_scale


def _parse_solution(instance, text):
    """(vektor_listesi | None, reported_size | None) dondurur; asla raise etmez.

    Her bos olmayan satir (yorum hariç): tam n adet {0,1,2}, bitisik.
    "# size K" yorum satiri reported_size sensorune yazilir.
    Bozuk vektor -> liste None olur (bad_vector violation'a duser).
    """
    n = instance.dimension
    reported = None
    vecs = []
    saw_bad = False
    if not isinstance(text, str):
        # Non-str guvenli bilgi -> bos kume gibi ele al (never-raise).
        return [], None

    for raw in text.splitlines():
        # once yorum kismindan "# size K" sensorunu yakala
        hash_idx = raw.find("#")
        body = raw[:hash_idx] if hash_idx >= 0 else raw
        comment = raw[hash_idx + 1:] if hash_idx >= 0 else ""
        if "size" in comment.lower():
            # "# size <int>" beklentisi; bozuksa sessizce yok say.
            toks = comment.split()
            si = next((k for k, t in enumerate(toks)
                       if t.lower() == "size"), None)
            if si is not None and si + 1 < len(toks):
                try:
                    reported = int(toks[si + 1])
                except ValueError:
                    pass
        line = body.strip()
        if not line:
            continue
        # vektor adayi: bitisik {0,1,2}
        if len(line) != n or any(c not in "012" for c in line):
            saw_bad = True
            vecs.append(line)  # ham haliyle tut (bad_vector info icin)
        else:
            vecs.append(tuple(int(c) for c in line))

    if saw_bad:
        return None, reported
    return vecs, reported


def evaluate_text(instance, text) -> dict:
    t0 = time.perf_counter()
    n = instance.dimension
    scale = penalty_scale(instance)
    violations = {}
    info = {}
    matches = 0  # 3-AP eslesme sayisi (her line 3 cipte yakalanir)

    vecs, reported = _parse_solution(instance, text)

    if vecs is None:
        violations["bad_vector"] = {
            "detail": f"her satir tam {n} adet {{0,1,2}} karakteri olmali (bitisik)"}
    else:
        # 1) bad vector zaten handle edildi (vecs None ise). Buraya gelenler duzgun.
        # 2) duplicate kontrolu
        if len(set(vecs)) != len(vecs):
            dup = len(vecs) - len(set(vecs))
            violations["duplicate_vector"] = {"count": dup}
        # 3) cap-set (3-AP) kontrolu: O(|S|^2)
        S = set(vecs)
        L = list(vecs)
        matches = 0  # her line 3 cipte yakalanir
        example = None
        for i in range(len(L)):
            x = L[i]
            for j in range(i + 1, len(L)):
                y = L[j]
                z = tuple((-(a + b)) % 3 for a, b in zip(x, y))
                if z in S and z != x and z != y:
                    matches += 1
                    if example is None:
                        example = [list(x), list(y), list(z)]
        if matches:
            line_count = matches // 3  # her dogru 3 cipte yakalanir
            violations["line_found"] = {"count": line_count}
            info["line_count"] = line_count
            info["example_line"] = example

    feasible = not violations
    cost = len(vecs) if (vecs is not None and feasible) else (
        len(vecs) if vecs is not None else 0)
    if feasible:
        fitness = cost / scale
    else:
        # CLAUDE.md §3 formulu: fitness = -1 - min(1, ihlal/cift).
        # ihlal_sayisi = eslesme sayisi (matches); her line 3 cipte yakalanir
        # ama gradyan icin eslesme yogunlugu (matches/cift) kullanilir.
        # Yapuisal ihlaller (bad_vector, duplicate_vector) icin de ihlal sayisi:
        # bad -> cozum cozulemedi (vecs None); duplicate -> tekrar sayisi.
        pair_count = max(1, len(vecs) * (len(vecs) - 1) // 2) if vecs is not None else 1
        violation_count = matches
        if "duplicate_vector" in violations:
            violation_count += violations["duplicate_vector"]["count"]
        if vecs is None:  # bad_vector: tum cozum hatali
            violation_count = max(violation_count, 1)
            pair_count = 1
        fitness = -1.0 - min(1.0, violation_count / pair_count)

    # reported size sensoru — TEKIL vektor sayisina gore (Görev 3: duplicate'li
    # ciktiya karsi durustluk; solver "# size 3" deyip 3 satir verdiyse ama 2
    # tekil vektor varsa sismis demek -> matches False).
    info["reported_size"] = reported
    if reported is None:
        info["reported_size_matches"] = None
    elif vecs is None:
        info["reported_size_matches"] = False
    else:
        info["reported_size_matches"] = (reported == len(set(vecs)))

    return {
        "feasible": feasible,
        "cost": cost,
        "violations": violations,
        "fitness": fitness,
        "eval_ms": int((time.perf_counter() - t0) * 1000),
        "info": info,
    }
