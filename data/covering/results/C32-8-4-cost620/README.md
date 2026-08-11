# C(32,8,4) ≤ 620 — bilinen-en-iyi ile eşitleme sertifikası

**İddia:** ekteki `solution.txt`, 32 elemanlı evrende 620 adet 8'li blokla
tüm C(32,4) = 35.960 dörtlü altkümeyi kapsayan geçerli bir covering
design'dır. Bu, bilinen en iyi değerle **eşitliktir** (rekor değildir).

## Bağımsız doğrulama (hiçbir şeye güvenmeniz gerekmez)

```
python verify_cover.py 32 8 4 solution.txt
```

`verify_cover.py` yalnızca Python stdlib kullanır; kapsamayı saf sayımla
kontrol eder. Beklenen çıktı: `kapsanmayan: 0`, `SONUC: GECERLI COVERING`.

## Bağlam ve kaynak durumu (2026-08-11 itibarıyla)

- La Jolla Covering Repository (1 Mart 2026'da donduruldu):
  552 ≤ C(32,8,4) ≤ 620.
- coveringrepository.com (canlı halef): kontrol kaydı bu paketle aynı
  gün — bkz. repo CLAUDE.md Faz P5 (canlı değer hâlâ 620 ise eşitleme,
  değilse bu README güncellenmelidir).

## Üretim şekli ve yapısal içerik

discovery-harness P5 hattı: OpenEvolve (LLM-evrimsel program arama) +
matematiksel kesin evaluator (`problems/covering/`). Kırılma,
**thinking-açık Claude Opus 5** deney dilimlerinde geldi (Görev 7,
2026-08-11): 75 iterasyonluk plato (977 blok) sonrasında ilk thinking
iterasyonu **afin geometri konstrüksiyonunu** kurdu — v=32=2⁵ için
AG(5,2)'nin tüm 3-flat'leri (4 · [5 seç 3]₂ = 620 coset) covering'i
verir; her 4 nokta ≤3 boyutlu bir afin altuzayda yatar. Evrilen kod
(`affine_blocks`) hardcode içermez: konstrüksiyon her v=p^m için
genel türetilir (öteleme grubu + altuzay kapanışı + cosetler).
Çözüm, 300 sn bütçeli 2-seed değerlendirmede üretildi ve
`harness/evolve_evaluator.py` arşivleme kancasıyla kalıcılaştırıldı
(SHA: 4e58fb94; iki bağımsız eş kopya daha arşivde). Evrim hattının
tam kaydı: repo `CLAUDE.md` Faz P5 bölümü.

## Sınırlar

- Bu bir EŞİTLEMEDİR; rekor iddiası için ≤ 619 blok gerekir
  (alt sınır 552 — arada geniş, 30 yıldır kapanmamış bir boşluk var).
- Konstrüksiyon klasik sonlu-geometri bilgisidir (620 değerinin 1996
  kaynağının da bu aile olması kuvvetle muhtemel); iddia "yeni
  konstrüksiyon" değil, "LLM-evrim hattı doğru paradigmayı kendi
  buldu ve kanıtlı çözüm üretti"dir.
- Tek hücre odaklı üretim: çözücünün genelleme iddiası bu sertifikanın
  parçası değildir.
