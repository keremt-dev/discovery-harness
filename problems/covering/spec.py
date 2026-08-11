"""P5 sozlesmesi: SENSE, ceza olcegi, dosya format kontrati (covering design).

## Instance dosya formati (.cover)

Satir bazli; `#` ile baslayan kisim yorumdur. Zorunlu basliklar:

    v <int>   # evren buyuklugu
    k <int>   # blok buyuklugu
    t <int>   # kapsanacak altkume buyuklugu

Kisit: v > k > t >= 1. Bozuk instance InstanceFormatError raise EDER
(instance tarafinda hata serttir; kofn/capset deseni). Instance bilincli
olarak minimaldir — referans/rekor degerleri SIZDIRILMAZ (§0.5).

## Cozum metni formati

`#` yorumlari atilir. Her bos olmayan satir bir blok: tam k adet FARKLI
tamsayi (1..v), bosluk ayracli. Blok kume olarak yorumlanir (sira onemsiz;
kanonik form = sirali tuple). `# size K` solver beyani verdict'i ETKILEMEZ,
info.reported_size_matches durustluk sensorune yazilir.

## Problem

(v,k,t) covering design: [v]'nin her t-altkumesi en az bir blokta yer
alacak sekilde k-blok koleksiyonu; blok sayisi MINIMUM.

    min |B|  s.t.  her T in C([v],t) icin bir b in B ile T ⊆ b

## SENSE karari: min problem, "max" kalite fitness'i

Dogal yon MIN (blok sayisi). Fitness ise MONOTON donusumle kalite oranina
cevrilir:

    feasible fitness = schoenheim(v,k,t) / |B|   ∈ (0, 1]

Gerekce (capset [0,1) deseninin min karsiligi):
  - Instance'lar arasi olcek karsilastirilabilir -> coklu-instance fitness
    ortalamasi anlamli (DISCOVERY_INSTANCE `;` destegi icin sart).
  - fitness = 1.0 tavani "Schoenheim'a dokundu" demek; kanitli-optimal
    bekci instance'larda dogal hedef.
  - Sinirsiz kotu feasible (sisik blok listesi) fitness'i yalnizca 0'a
    yaklastirir; min-yonlu cezali maliyette gereken devasa ceza olcegi
    sorunu (C(v,k) mertebesi) hic dogmaz.
Blok sayisi (cost) iddia tarafinda MIN olarak raporlanmaya devam eder;
fitness != cost ayrimi aynen korunur. SENSE = "max": OpenEvolve
combined_score = +fitness (harness/score.py). Dokunma.

## Ceza olcegi

Infeasible fitness objective.py'de [-2,-1] bandina kilitlenir; her
infeasible < her feasible (> 0). penalty_scale bu eklentide normalizer
rolundedir (capset deseni): Schoenheim alt siniri. Bu bir TEOREM formulu
(Schoenheim 1964), referans tablosu DEGIL -> sızıntı yok.
"""

SENSE = "max"


def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def schoenheim(v: int, k: int, t: int) -> int:
    """L(v,k,t) = ceil(v/k * L(v-1,k-1,t-1)), L(v,k,1) = ceil(v/k).

    TAM tamsayi aritmetigi (float yok): carpim pay tarafinda tutulur,
    tek ceil bolme ile kapanir.
    """
    if t == 1:
        return _ceil_div(v, k)
    return _ceil_div(v * schoenheim(v - 1, k - 1, t - 1), k)


def penalty_scale(instance) -> float:
    """Normalizer: Schoenheim alt siniri (teorem; instance'tan turetilir).

    feasible fitness = penalty_scale / |B| ∈ (0,1]; |B| >= L oldugu icin
    (L gecerli bir alt sinir) 1.0 asilamamali — asilirsa bu enstruman
    alarmi demektir (objective.py info.instrument_alarm).
    """
    return float(schoenheim(instance.v, instance.k, instance.t))
