# C(28,9,3) ≤ 56 — bilinen-en-iyi ile eşitleme sertifikası

**İddia:** ekteki `solution.txt`, 28 elemanlı evrende 56 adet 9'lu blokla
tüm C(28,3) = 3.276 üçlü altkümeyi kapsayan geçerli bir covering design'dır.
Bu, bilinen en iyi değerle **eşitliktir** (rekor değildir).

## Bağımsız doğrulama (hiçbir şeye güvenmeniz gerekmez)

```
python verify_cover.py 28 9 3 solution.txt
```

`verify_cover.py` yalnızca Python stdlib kullanır; kapsamayı saf sayımla
kontrol eder. Beklenen çıktı: `kapsanmayan: 0`, `SONUC: GECERLI COVERING`.

## Bağlam ve kaynak durumu (2026-08-10 itibarıyla)

- La Jolla Covering Repository (1 Mart 2026'da donduruldu):
  50 ≤ C(28,9,3) ≤ 56; üst sınır kaydı 14/11/1996 (JCD article).
- coveringrepository.com (canlı halef, 2026-08-10'da kontrol edildi):
  aynı değer — 56 blok, alt sınır 50, tarih 14/11/1996. Yani 56,
  ~30 yıldır iyileştirilmemiş güncel bilinen-en-iyidir.

## Üretim şekli

discovery-harness P5 hattı: OpenEvolve (LLM-evrimsel program arama;
GLM-5 + Claude Opus 5 dilimleri) + matematiksel kesin evaluator
(`problems/covering/`). Çözüm, evrilen çözücünün 70 sn bütçeli bir
koşusunda üretildi ve `harness/evolve_evaluator.py` arşivleme kancası
tarafından kalıcılaştırıldı (SHA: c155b2fe). Evrim hattının tam kaydı:
repo `CLAUDE.md` Faz P5 bölümü.

## Sınırlar

- Bu bir EŞİTLEMEDİR; rekor iddiası için ≤ 55 blok gerekir.
- Tek hücre odaklı üretim: çözücünün genelleme iddiası bu sertifikanın
  parçası değildir (genelleme kanıtı ayrı: holdout değerlendirmeleri,
  repo CLAUDE.md).
