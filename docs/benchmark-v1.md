# Benchmark v1 — Çok Tipli Weighted k-out-of-n:G, Ölçekli Değerlendirme

Tarih: 2026-08-05. Amaç (İz-2, Tütüncü hattı): Ozkut & Tutuncu 2025'in
kendi ilan ettiği boşluğu doldurmak — *"yöntemlerimiz brute-force, büyük
sistemlerde pahalı; sonuçlarımız gelecekteki sezgisel yöntemler için
benchmark'tır"*. Bu doküman alanın ilk ölçekli benchmark ailesini ve
üzerindeki ilk sezgisel değerlendirmesini kaydeder.

## Kurulum

- **Instance ailesi:** 2 gerçekçi profil (makalenin uygulama senaryolarından:
  `router`, `enerji`) × 3 katman — küçük (n=12-20; exhaustive enumeration ile
  KANITLI optimum), orta (n=60-100; 32-start refsearch kolonu), büyük
  (n=300-500). Üreteç deterministik (`generate.py`, profil+seed); K
  kuantil-yerleşimli (doyumsuzluk). Aldatmalı yapı YOK (sert profilin aksine).
- **Çözücüler:** `tohum` (oran-greedy + tekil-takas, 45 sn bütçe) ve
  `evrilen` (dondurulmuş artefakt `evolve/artifacts/best_20260805.py`;
  GLM+Opus evriminin ürünü). Gerçek sözleşme: ayrı process, dosya I/O.
- **Doğrulama:** her değer ham instance'tan `fractions.Fraction` ile yeniden
  hesaplandı. Kritik ölçüm: tam-aritmetik tek-tahsis doğrulaması n=500,
  m=12'de ≤ 2.7 sn — **kesin yöntemin imkânsızlaştığı ölçekte sertifikalı
  değerlendirme mümkün** (verifier asimetrisi).

## Sonuç tablosu (2026-08-05 koşusu, tek çekirdek, sakin makine)

| instance | n | M | tohum R (s) | evrilen R (s) | refsearch R | kanıtlı opt |
|---|---|---|---|---|---|---|
| gen-router-n12-m3-s1 | 12 | 3 | 0.490768 (0s) | 0.490768 (40s) | 0.490768 | 0.490768 |
| gen-router-n16-m4-s1 | 16 | 4 | 0.440127 (0s) | **0.557485** (40s) | 0.557485 | 0.557485 |
| gen-router-n20-m3-s2 | 20 | 3 | 0.552691 (0s) | 0.552691 (40s) | 0.552691 | 0.552691 |
| gen-router-n20-m4-s1 | 20 | 4 | 0.358486 (0s) | **0.467310** (40s) | 0.462475 | 0.467310 |
| gen-router-n60-m6-s1 | 60 | 6 | 1.000000 (0s) | 1.000000 (40s) | 1.000000 | — |
| gen-router-n100-m8-s1 | 100 | 8 | 0.717417 (0s) | 0.717417 (40s) | 0.717417 | — |
| gen-router-n300-m10-s1 | 300 | 10 | 0.985426 (27s) | **0.990361** (41s) | — | — |
| gen-router-n500-m12-s1 | 500 | 12 | **0.961920** (45s) | 0.651619 (40s) | — | — |
| gen-enerji-n12-m3-s1 | 12 | 3 | 0.593963 (0s) | 0.593963 (40s) | 0.593963 | 0.593963 |
| gen-enerji-n16-m4-s1 | 16 | 4 | 0.648203 (0s) | **0.797250** (40s) | 0.797250 | 0.797250 |
| gen-enerji-n20-m3-s2 | 20 | 3 | 0.498569 (0s) | 0.498569 (40s) | 0.498569 | 0.498569 |
| gen-enerji-n20-m4-s1 | 20 | 4 | 0.828495 (0s) | 0.828495 (40s) | 0.828495 | 0.828495 |
| gen-enerji-n60-m6-s1 | 60 | 6 | 0.990564 (6s) | 0.990902 (40s) | 0.990902 | — |
| gen-enerji-n100-m8-s1 | 100 | 8 | 0.944696 (17s) | **0.969432** (40s) | 0.969432 | — |
| gen-enerji-n300-m10-s1 | 300 | 10 | 0.440189 (50s) | **0.769271** (40s) | — | — |
| gen-enerji-n500-m12-s1 | 500 | 12 | 0.693517 (52s) | 1.000000* (40s) | — | — |

## Okuma

1. **Güven zinciri kuruldu:** evrilen çözücü, enumere edilebilir 8
   instance'ın **8'inde kanıtlı optimumu** buldu (tohum 5/8). Bir
   instance'ta (router-n20-m4) 32-start refsearch'ün bile kaçırdığı
   optimumu yakaladı. Küçük boyutta kesin yöntemle bire bir eşleşme =
   makale hattının istediği güven kanıtı.
2. **Ölçekte katkı:** kesin yöntemin imkânsız olduğu bölgede (n=300-500)
   evrilen çözücü 3/4 instance'ta tohuma eşit ya da belirgin üstün —
   en çarpıcısı enerji-n300: 0.44 → 0.77 (+0.33). Tüm değerler ≤2.7 sn'de
   tam aritmetikle sertifikalı.
3. **Dürüst negatif bulgu — genelleme açığı:** router-n500'de evrilen
   çözücü tohumun ALTINDA kaldı (0.652 < 0.962). Evrim n≤100 sert
   instance'larla yapılmıştı; en büyük router rejiminde kurulum sezgiseli
   yanlış yöne gidiyor ve süre bütçesi toparlamaya yetmiyor. Pratik
   sonuç: **portföy yöntemi** (tohum ∪ evrilen; her instance'ta iyisi) +
   gelecek iş: büyük-n instance'ları evrim fitness setine katmak.
4. **Benchmark tasarım notu:** enerji-n500 satırında evrilen R ≈ 1.0
   (6 haneye yuvarlanmış doygunluk) — kuantil-K kurulum tahsisine göre
   yerleştiği için güçlü çözücüler büyük n'de doyurabiliyor. v2'de büyük
   katman kabulü "en iyi bilinen çözücü R < 0.99" kuralıyla yapılmalı
   (kürasyon baseline'ı artık evrilen çözücüdür).

## Sınırlar (rapora aynen girer)

- Objective, tanımlı matematiksel R'dir (Goodhart notu: bakım/tedarik/
  korelasyon modellenmiyor; makaleyle aynı çerçeve).
- Büyük katmanda optimum bilinmiyor; iddialar karşılaştırmalıdır
  (tohum/refsearch'e göre), mutlak değildir.
- Bağımlı-bileşen senaryosu (makale senaryo 2) kapsam dışı (tam aritmetik
  integrale gelmez; ikinci aşama).
- Tek makine, tek koşu; yayın öncesi çoklu bağımsız re-run protokolü
  (bilimsel-iddia-plani.md §7) uygulanır.

## Yeniden üretim

```bash
python -m problems.kofn.benchmark_eval rapor.md
```

(instance listesi verilmezse data/kofn/instances/gen-{router,enerji}-* taranır)
