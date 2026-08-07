# Ozkut & Tutuncu 2025 (C&IE 210, 111513) sayisal orneklerinin dogrulamasi.
#
# Teorem 1 (bagimsiz durum) fractions.Fraction ile TAM hesaplanir ve makalenin
# Tablo 1 / 5 / 6 satirlariyla karsilastirilir. Regresyon hedefi BIZIM tam
# degerlerimizdir (CALC kolonu); makale degerleri bilgi amaclidir, cunku
# 2026-08-03 dogrulamasinda makalede su hatalar tespit edildi:
#
#   * Tablo 1: k=10'daki 4 satir birebir uyuyor -> xi=(3,1,2) ve ">= k"
#     semantigi kesinlesti. k=15/k=20 ve p-varyasyon satirlari hicbir makul
#     parametre okumasiyla uretilemiyor (kaynagi belirsiz makale ici hata).
#   * Tablo 5: 13/14 satir birebir. (0,8,2) k=10 tam deger 0.92284670 ->
#     dogru baski 0.9228 olmali; makale 0.9229 basmis (son hane hatasi).
#   * Tablo 6: 12/14 satir birebir. Iki satir ic tutarsiz (config/C/R
#     uyusmuyor; sayfa 7 gorsel olarak da teyit edildi, ekstraksiyon degil):
#       - n=10,k=15: baski (5,5,0) C=25 R=1. C=25'lik config (5,0,5)'tir ve
#         R=0.99990407 (4 hanede 0.9999, 1 degil). Gercek optimum:
#         (10,0,0) C=30 R=0.99999986.
#       - n=15,k=15: baski (0,12,3) C=28 R=1. (0,12,3) icin R=0.94010.
#         C=28 & R~1 ile tutarli adaylar (4,6,5) R=0.99999685 ve (6,8,1)
#         R=0.99999708. Gercek optimum: (1,1,13) C=30 R=0.99999961.
#
# Tasarim dersi: k, ulasilabilir toplam agirliga gore dusukse problem R~1'de
# doyuma gidiyor ve optimumlar beraberlige dusuyor -> uretecegimiz benchmark
# instance'larinda k yuksek secilmeli (doyumsuz bolge).
from fractions import Fraction as F
from math import comb

XI = (3, 1, 2)
COST = (3, 1, 2)
P_T1 = (0.95, 0.97, 0.93)
P_OPT = (0.97, 0.92, 0.94)


def reliability(zeta, xi, p, k):
    """Teorem 1: R = P(sum xi_j * N_j >= k), N_j ~ Binom(zeta_j, p_j), tam."""
    total = F(0)
    p = [F(str(x)) for x in p]

    def rec(j, acc_w, acc_p):
        nonlocal total
        if j == len(zeta):
            if acc_w >= k:
                total += acc_p
            return
        for i in range(zeta[j] + 1):
            rec(j + 1, acc_w + xi[j] * i,
                acc_p * comb(zeta[j], i) * p[j] ** i * (1 - p[j]) ** (zeta[j] - i))

    rec(0, 0, F(1))
    return total


# (tablo, config, k, beklenen_tam_deger_8dp, makale_R, not)
ROWS = [
    ("T1", (3, 2, 5), 10, 0.99996943, 0.99997, ""),
    ("T1", (3, 2, 4), 10, 0.99975762, 0.99976, ""),
    ("T1", (3, 1, 5), 10, 0.99991621, 0.99992, ""),
    ("T1", (2, 2, 5), 10, 0.99955165, 0.99955, ""),
    ("T5", (0, 8, 2), 10, 0.92284670, 0.9229, "makale son hane hatali"),
    ("T5", (3, 7, 0), 15, 0.81903768, 0.8190, ""),
    ("T5", (2, 0, 8), 20, 0.86641665, 0.8664, ""),
    ("T5", (8, 0, 2), 25, 0.95226596, 0.9523, ""),
    ("T5", (0, 15, 0), 10, 0.99930480, 0.9993, ""),
    ("T5", (0, 13, 2), 15, 0.85117748, 0.8512, ""),
    ("T5", (2, 10, 3), 20, 0.81518316, 0.8152, ""),
    ("T5", (6, 9, 0), 25, 0.80815511, 0.8082, ""),
    ("T5", (3, 0, 12), 30, 0.80736202, 0.8074, ""),
    ("T5", (0, 20, 0), 10, 0.99999993, 1.0, ""),
    ("T5", (0, 20, 0), 15, 0.99620051, 0.9962, ""),
    ("T5", (0, 17, 3), 20, 0.89127653, 0.8913, ""),
    ("T5", (0, 12, 8), 25, 0.83610920, 0.8361, ""),
    ("T5", (2, 9, 9), 30, 0.81355296, 0.8136, ""),
    ("T6", (5, 0, 5), 10, 0.99999985, 1.0, ""),
    ("T6", (5, 0, 5), 15, 0.99990407, 1.0, "baski (5,5,0) C=25 R=1 tutarsiz"),
    ("T6", (10, 0, 0), 20, 0.99985291, 0.9999, ""),
    ("T6", (10, 0, 0), 25, 0.96549344, 0.9655, ""),
    ("T6", (0, 10, 5), 10, 0.99999594, 1.0, ""),
    ("T6", (1, 1, 13), 15, 0.99999961, 1.0, "baski (0,12,3) C=28 tutarsiz; gercek optimum bu"),
    ("T6", (6, 6, 3), 20, 0.99980315, 0.9998, ""),
    ("T6", (7, 7, 1), 25, 0.97590373, 0.9759, ""),
    ("T6", (7, 7, 1), 30, 0.42368665, 0.42369, ""),
    ("T6", (0, 20, 0), 10, 0.99999993, 1.0, ""),
    ("T6", (0, 13, 7), 15, 0.99999758, 1.0, ""),
    ("T6", (5, 15, 0), 20, 0.99986792, 0.9999, ""),
    ("T6", (5, 15, 0), 25, 0.97592987, 0.9759, ""),
    ("T6", (5, 15, 0), 30, 0.24585332, 0.2459, ""),
]


def enumerate_max_r(n, k, budget, xi=XI, cost=COST, p=P_OPT):
    """Makaledeki brute-force: Σn_j = n, maliyet <= budget, R maksimize."""
    best = None
    for n1 in range(n + 1):
        for n2 in range(n + 1 - n1):
            n3 = n - n1 - n2
            c = sum(ci * ni for ci, ni in zip(cost, (n1, n2, n3)))
            if c > budget:
                continue
            r = reliability((n1, n2, n3), xi, p, k)
            if best is None or r > best[0]:
                best = (r, (n1, n2, n3), c)
    return best


if __name__ == "__main__":
    bad = 0
    for tbl, cfg, k, expect, paper, note in ROWS:
        p = P_T1 if tbl == "T1" else P_OPT
        r = float(reliability(cfg, XI, p, k))
        ok = abs(round(r, 8) - expect) < 1e-9
        if not ok:
            bad += 1
        extra = f"  [{note}]" if note else ""
        print(f"{'OK ' if ok else 'FAIL'} {tbl} cfg={cfg} k={k} "
              f"calc={r:.8f} makale={paper}{extra}")
    print("MISMATCHES (bizim tam degerlere gore):", bad)
