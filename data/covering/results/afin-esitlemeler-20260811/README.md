# Afin genelleme taraması — 15 hücrede bilinen-en-iyi ile eşitleme (2026-08-11)

**İddia:** bu klasördeki her `C{v}-{k}-{t}-cost{N}.txt`, ilgili (v,k,t)
hücresi için N bloklu geçerli bir covering design'dır ve N, La Jolla /
coveringrepository arşivindeki bilinen-en-iyi değere **eşittir**
(rekor değildir). Tümü TEK bir evrilmiş programın (`evolve/artifacts/
best_v32_thinking_620_20260811.py`, C(32,8,4)=620'yi bulan genom)
seed=0 koşularıyla üretildi — hücre başına özel ayar YOK.

## Bağımsız doğrulama

```
python verify_cover.py <v> <k> <t> C<v>-<k>-<t>-cost<N>.txt
```

## Hücreler

| Hücre | Blok | Not |
|---|---|---|
| C(8,4,3) | 14 | AG(3,2) 2-flat'leri |
| C(9,3,2) | 12 | AG(2,3) doğruları |
| C(16,4,3) | 140 | AG(4,2) 2-flat'leri |
| C(16,8,4) | 30 | AG(4,2) 3-flat'leri |
| C(25,5,2) | 30 | AG(2,5) doğruları |
| C(27,3,2) | 117 | AG(3,3) doğruları |
| C(27,9,3) | 39 | AG(3,3) 2-flat'leri |
| C(32,16,5) | 62 | AG(5,2) 4-flat'leri |
| C(32,17,5) | 62 | 4-flat + 1 dolgu noktası |
| C(32,4,3) | 1240 | AG(5,2) 2-flat'leri |
| C(49,7,2) | 56 | AG(2,7) doğruları |
| **C(49,8,2)** | **49** | **saf afin 56 verir; evrilmiş yerel arama 56→49'a indirdi — eşitleme konstrüksiyondan değil ARAMADAN** |
| C(64,4,3) | 10416 | AG(6,2) 2-flat'leri |
| C(81,3,2) | 1080 | AG(4,3) doğruları |
| C(81,9,3) | 1170 | AG(4,3) 2-flat'leri |

Not: C(32,8,4)=620 eşitlemesi ayrı pakette (`../C32-8-4-cost620/`).

## Tarama bilançosu (dürüstlük kaydı)

- Analitik ön-tarama (8759 arşiv hücresi): saf afin d-flat sayısının
  arşivden KÜÇÜK olduğu hücre YOK — küratörler geometrik
  konstrüksiyonları biliyor; anında-rekor fırsatı bulunmadı.
- Koşulan 17 hücreden eşitlenemeyenler: C(27,10,3) bizde 36 (arşiv 35,
  1 blok fark) ve C(32,18,5) bizde 99 (arşiv 56 — dolgulu afin yolu bu
  hücrede verimsiz). v=64, t=5 hücreleri bellek riski nedeniyle
  koşulmadı (boşluk olarak not edilir).

## Üretim şekli

discovery-harness P5, thinking-açık Claude Opus 5 dilimi (Görev 7):
`affine_blocks` genel konstrüksiyonu (v=p^m tespiti + AG(m,p) öteleme
grubu + altuzay kapanışı + cosetler) + fazlalık ayıklama + yerel arama.
Doğrulayıcı zincir ve evrim kaydı: repo `CLAUDE.md` Faz P5.
