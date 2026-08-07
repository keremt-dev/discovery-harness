"""P4 sozlesmesi: SENSE, ceza olcegi, dosya format kontrati (cap set).

## Instance dosya formati (.cap)

Satir bazli; `#` ile baslayan kisim yorumdur. Zorunlu baslik:

    dimension <n, >= 1 tamsayi>

Bozuk instance InstanceFormatError raise EDER (instance tarafinda hata
sert olmalidir; CLAUDE.md §0 ruhu). Capset instance'i bilincli olarak
minimaldir: solver bu dosyayi okur (kural §0.5 — referans/rekor
SIZDIRILMAZ).

## Cozum metni formati

`#` yorumlari atilir. Her bos olmayan satir: tam n adet {0,1,2}
karakteri, bitisik (`02110221`). `# size K` solver beyani degeri YOK
SAYILIR (verdict'i etkilemez) ama info.reported_size_matches sensorune
yazilir (kofn durustluk sensorunun karsiligi).

## Problem

Cap set: S alt kumesi F_3^n, oyle ki uc FARKLI x,y,z icin
x+y+z = 0 (mod 3, bilesen bilesen) OLMASIN. Amaç: |S| MAKSIMUM.

    max |S|  s.t.  S cap set (3-AP'siz)

SENSE = "max": OpenEvolve combined_score = +fitness (harness/score.py).
"""

SENSE = "max"


def penalty_scale(instance) -> float:
    """Ceza/olcekleme olcegi — Meshulam 1995 teorem siniri.

    penalty_scale = 2 * 3^n / n  (a(n) <= bu deger; teorem dayanagi).

    Bu bir TEOREM siniridir, referans/rekor tablosu DEGIL (§0.5: sızıntı
    yok). Fitness bununla normalize edilir: feasible fitness = |S|/scale
    -> [0,1), boylece farkli n'li instance'lar arasi ortalama alinabilir
    (DISCOVERY_INSTANCE coklu-instance destegi icin sart). Infeasible
    fitness [-2,-1] araliginda kalir (objective.py), yani her infeasible
    < her feasible (>= 0).
    """
    n = instance.dimension
    return 2.0 * (3 ** n) / n
