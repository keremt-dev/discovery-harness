# Faz D — Tohum Solver Baseline Raporu

Tarih: 2026-08-03. Üretim komutları en altta; tüm değerler tam aritmetikli
evaluator'den (solver beyanı değil).

## Kurulum

- **Tohum solver** (`problems/kofn/seed_solver.py`): maliyet/fayda oranına
  (w·p/c) göre greedy kurulum + tek birimlik takas hill-climb; 5 sn yumuşak
  süre bütçesi (anytime). Bilerek naif — iyileştirme evrimin işi.
- **Kanıtlı optimum**: exhaustive enumeration (`problems/kofn/enumerate.py`),
  yalnızca kompozisyon sayısı ≤ 200.000 olan instance'larda.
- Koşu: sakin makinede, tek çekirdek, ayrı process sözleşmesiyle.

## Sonuç tablosu

| instance | n | M | K | bütçe | tohum R | tohum s | kanıtlı opt R | gap % |
|---|---|---|---|---|---|---|---|---|
| gen-n10-m3-s1 | 10 | 3 | 26 | 29 | 0.656450 | 0.1 | 0.656450 | 0.000 |
| gen-n10-m3-s2 | 10 | 3 | 17 | 18 | 0.545675 | 0.1 | 0.545675 | 0.000 |
| gen-n12-m4-s1 | 12 | 4 | 44 | 38 | 0.898180 | 0.1 | 0.898180 | 0.000 |
| gen-n12-m4-s2 | 12 | 4 | 24 | 22 | 0.366874 | 0.1 | 0.366874 | 0.000 |
| gen-n15-m3-s1 | 15 | 3 | 40 | 43 | 0.497404 | 0.1 | 0.497404 | 0.000 |
| gen-n15-m3-s2 | 15 | 3 | 28 | 27 | 0.592285 | 0.1 | 0.592285 | 0.000 |
| gen-n16-m4-s1 | 16 | 4 | 56 | 51 | 0.965779 | 0.1 | 0.965779 | 0.000 |
| gen-n16-m4-s2 | 16 | 4 | 31 | 29 | 0.499857 | 0.1 | 0.499857 | 0.000 |
| gen-n20-m3-s1 | 20 | 3 | 54 | 57 | 0.565020 | 0.1 | 0.565020 | 0.000 |
| gen-n20-m3-s2 | 20 | 3 | 35 | 37 | 0.587572 | 0.1 | 0.587572 | 0.000 |
| router-n10-k20 | 10 | 3 | 20 | 30 | 0.999853 | 0.1 | 0.999853 | 0.000 |
| gen-n60-m5-s2 | 60 | 5 | 215 | 196 | 0.502014 | 0.1 | — (enum. dışı) | — |
| gen-n120-m6-s2 | 120 | 6 | 473 | 425 | 0.391144 | 0.1 | — (enum. dışı) | — |
| gen-n200-m8-s3 | 200 | 8 | 1216 | 827 | 0.538603 | 0.6 | — (enum. dışı) | — |

## Okuma

1. **Küçük katman (n ≤ 20, enumere edilebilir): tohum 11/11 instance'ta
   kanıtlı optimumu buluyor.** Fizibil tahsis sayısı küçük (14-329) olduğu
   için oran-greedy + hill-climb uzayı fiilen tarıyor. Sonuç: bu katmanda
   evrimin görevi *iyileştirme değil eşleşme* (regresyon bekçisi);
   keşif alanı büyük katmandadır. Bilimsel iddia planındaki Katman 1
   ölçümü bu tabloyla kuruldu.
2. **Büyük katman (n = 60-200, enumeration imkânsız): tohum R ≈ 0.39-0.54.**
   Optimum bilinmiyor; evrimin başarı kriteri bu değerleri sakin-makine
   yeniden koşusuyla doğrulanmış şekilde anlamlı aşmak
   (docs/bilimsel-iddia-plani.md §7). Doğrulama maliyeti düşük kalıyor:
   n=200'de tek tahsisin tam-aritmetik R'si ~1 sn.

## Tasarım dersleri (instance ailesi bunlarla şekillendi)

- **Plato dersi:** "hepsi-en-ucuz" başlangıçlı hill-climb, K yüksekken
  R=0 platosuna saplanıyor (hiçbir tekil takas eşiği geçemiyor → gradyan
  yok); ilk baseline'da 11 instance'ın 8'i R=0'dı. Oran-greedy kurulum
  bunu çözdü. Bu plato, evrilen sezgisellerin de karşılaşacağı gerçek
  bir arama-uzayı özelliği — benchmark'ın ayırt ediciliğine katkı.
- **Doygunluk dersi:** K'yı ulaşılabilir maks ağırlığın sabit oranı
  (%70-95) olarak seçmek büyük n'de çöker (büyük sayılar yasası →
  R_opt ≈ 1, beraberlik çöplüğü). Çözüm: K, oran-greedy kurulumun ağırlık
  dağılımının sağkalım eğrisinde q ~ U(0.25, 0.75) kuantiline yerleştirilir
  (`generate.py:_quantile_k`).
- **Küratörlü büyük katman:** kuantil yerleşimi kurulum tahsisini bantta
  tutar ama bütçe boşluğu varsa hill-climb yine doyurabilir. Optimum
  bilinemediğinden yapısal garanti yok; büyük katman adayları tohum-R
  kabul bandıyla (0.05 < R < 0.99) elenir. Kabul kayıtları:
  (60,5,seed=2) [s1: 0.9983 red], (120,6,seed=2) [s1: 1.0000 red],
  (200,8,seed=3) [s1: 0.999997 red; s2: 0.9963 red]. Bu eleme benchmark
  tasarım kuralıdır ve yayında açıkça belgelenir.

## Yeniden üretim

```bash
python -m problems.kofn.generate <n> <m> <seed> data/kofn/instances/gen-n<n>-m<m>-s<seed>.kofn
```

```bash
python -m problems.kofn.baseline docs/faz-d-baseline-tablo.md
```

(Tablo bu dokümana elle taşındı; solver süreleri makine yüküne göre oynar.)
