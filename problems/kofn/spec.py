"""P1 sozlesmesi: SENSE, ceza olcegi, dosya format kontrati.

## Instance dosya formati (.kofn)

Satir bazli; `#` ile baslayan kisim yorumdur. Zorunlu basliklar:

    NAME <ad>
    M <tip sayisi, >=2>
    N <toplam bilesen sayisi; cozumde Σn_j = N ZORUNLU>
    K <agirlik esigi, > 0>
    BUDGET <maliyet butcesi C0, > 0>
    TYPE <idx 1..M> <agirlik ξ_j> <maliyet c_j> <guvenilirlik p_j>

Tam M adet TYPE satiri, idx'ler 1..M. Sayilar Fraction'a cevrilir (ondalik
yazim tam kesir olarak okunur: 0.97 -> 97/100). Agirliklar > 0, maliyetler
>= 0, guvenilirlikler [0,1].

## Cozum metni formati

`#` yorumlari atilir. `R <float>` satiri solver'in BEYAN ettigi objective
(yalnizca durustluk sensoru; verdict'i etkilemez). Ilk diger icerik satiri
tam M adet tamsayi: tahsis (n_1 ... n_M).

## Problem (P-ii, Ozkut & Tutuncu 2025 §4.3.2)

    max R(n_1..n_M)  s.t.  Σ c_j·n_j <= BUDGET,  Σ n_j = N,  n_j >= 0 tamsayi

SENSE = "max": OpenEvolve icin combined_score = +fitness (harness/score.py).
"""

SENSE = "max"


def penalty_scale(instance) -> float:
    """Ceza olcegi — hicbir ihlal karli olamaz.

    Turetim: kanonik hedef R bir olasilik oldugundan araligi HER instance'ta
    [0,1]; span = 1. Olcek = 2*span + 1 taban = 3.0. Boylece infeasible
    fitness <= R - scale*(1 + ...) <= 1 - 3 < 0, feasible fitness = R >= 0;
    yani en umutsuz feasible cozum (R=0) bile her infeasible'dan iyidir.
    (CVRP'de span bbox koseganindan turetiliyordu; burada objective'in
    dogal araligi instance'tan bagimsiz sabit oldugu icin turetim sabite
    cikar — fiat degil, turetim sonucu.)
    """
    objective_span = 1.0  # R ∈ [0,1]
    return 2.0 * objective_span + 1.0
