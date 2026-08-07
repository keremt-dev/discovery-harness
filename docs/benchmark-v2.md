# Benchmark v2 — Büyük-n Evrim Dilimi ve Holdout Sonucu

Tarih: 2026-08-05. Amaç: benchmark v1'in dürüst negatif bulgusunu
(docs/benchmark-v1.md, okuma 3 — router-n500 genelleme açığı: evrilen
0.652 < tohum 0.962) evrim fitness setine büyük-n instance'ları katarak
kapatmak. Kullanıcı kararı: "2'yi deneyelim" (2026-08-05).

## Eğitim tasarımı (holdout disiplini)

- **Eğitim seti benchmark v1'den AYRIK tohumlarla** üretildi (v1: s1/s2;
  eğitim: s7/s10/s14). v1 ailesi bu dilim için gerçek holdout'tur.
- Üç instance, iki rol:
  - `train-router-n500-m12-s7` — **tek gradyan kaynağı** (turnusol:
    evrilen-v1 0.3320 < tohum 0.4068 → regresyon rejimi tekrar etti,
    kanıtlı headroom ≥ +0.075).
  - `train-enerji-n300-m10-s14` (evrilen-v1 1.000, tohum 0.784) ve
    `train-router-n20-m4-s10` (ikisi de kanıtlı opt 0.6633'te) —
    **regresyon bekçileri**: kazanılmış yetenek kaybedilirse set
    ortalaması düşer.
- **Başlangıç genomu = evrilen-v1** (`evolve/artifacts/best_20260805.py`),
  tohum değil: evrimden yalnızca büyük-n açığını kapatması istendi
  (`run.ps1 -InitialProgram`).

### Kürasyon bulgusu: dejenere instance sınıfı

enerji-n300'ün s8 ve s15 tohumlarında üretecin bütçe tabanı
(`n × min_maliyet`) bütçeye eşit çıktı → fiilen tek fizibil tahsis,
R sabit (bütün yapısal denemeler birebir 0.244416; 120 sn bütçe de
kıpırdatmadı). **v2 kürasyon kuralı: bütçe boşluğu
`budget/(n·min_cost) > 1` şart** — instance kabulünden önce kontrol
edilir. (s12 ve s14 ise evrilen-v1 tarafından doyuruldu → gradyan hedefi
olamaz, bekçi olabilir; turnusol kuralının v2 hali.)

## Koşu

- Opus 5 (8317), full-rewrite, 50 iterasyon, `runs/evolve/bench-v2-dilim1`.
- Duman testi 5/5 yeşil; başlangıç set skoru 0.6651 (turnusol öngörüsüyle
  birebir: (0.6633+1.000+0.332)/3).
- Sonuç: set skoru 0.6651 → **0.6900** (iter 2'de bulundu, 50 iterasyonda
  aşılamadı). Ayrıştırma: bekçiler tavanda tutuldu, router-n500-s7 slotu
  0.332 → 0.4067 ≈ tohum seviyesi (0.4068). Eğitim hedefinde regresyon
  kapandı; s7'nin tohum-üstü bölgesine geçilemedi.
- Evrilen program **yapısal olarak farklı**: güvenilirlik hesabı K'da
  kesilmiş absorbing konvolüsyon DP (O(K), toplam ağırlıktan bağımsız),
  bütçeye dayanıklı kurulum (en-ucuz-fizibil + marjinal-kazanç
  yükseltme), kalan süreye göre boyutlanan çoklu-birim takas + ILS.
- Dondurulmuş artefakt: `evolve/artifacts/best_v2_20260805.py`.

## Holdout sonucu (benchmark v1 ailesi, 16 instance, 2026-08-05)

Tam tablo: `runs/benchmark-v2-holdout.md`. Özet:

| kriter | v1 | v2 |
|---|---|---|
| küçük katman kanıtlı optimum | 8/8 | **8/8 (korundu)** |
| gen-router-n500-m12-s1 | 0.651619 (< tohum 0.9738) | **1.000000** |
| gen-enerji-n300-m10-s1 | 0.769271 | 0.769271 (korundu) |
| gen-enerji-n500-m12-s1 | 1.000000 | 0.999999 (~eşit) |
| gen-router-n300-m10-s1 | 0.990361 | 0.984587 (−0.0058) |

Okuma:

1. **Genelleme açığı kapandı:** v2, eğitimde hiç görmediği
   router-n500-s1'de v1'in 0.652'lik çöküşünü 1.000000'a çevirdi ve
   tohumu da geçti. Büyük-n fitness seti + ölçek-rejimi prompt notu
   yeterli oldu; tek gradyan instance'ı yetti.
2. **Bekçi tasarımı işledi:** küçük katman optimumları ve enerji-ölçek
   kazanımları birebir korundu — v1'deki "portföy yöntemi" ihtiyacı
   fiilen kalktı (v2, 16 satırın 15'inde v1'e eşit ya da üstün).
3. **Dürüst not:** router-n300'de v2 hem v1'in (−0.0058) hem tohumun
   (−0.0008) hafif altında. Mertebe küçük ama sıfır değil; çoklu re-run
   protokolünde izlenir.
4. **Eğitim/holdout ayrışması:** v2 eğitim instance'ı s7'de yalnız tohum
   seviyesine çıkabilirken holdout s1'de doygunluğa ulaştı — s7, K
   yerleşimi gereği daha sert bir rejim (tohum 0.41'de). s7'nin
   tohum-üstü bölgesi (varsa) gelecek dilimin hedefi olabilir; önce
   headroom kanıtı gerekir (turnusol kuralı).

## Sınırlar

- Tek makine, tek koşu; yayın öncesi çoklu bağımsız re-run protokolü
  (docs/bilimsel-iddia-plani.md §7) uygulanır.
- Büyük katmanda optimum bilinmiyor; "1.000000" 6 haneye yuvarlanmış
  doygunluktur, optimallik iddiası değildir.
- benchmark v1 tablosuyla tohum kolonundaki küçük farklar (ör.
  router-n500-s1: 0.9619 vs 0.9738) anytime çözücünün makine yüküne
  duyarlılığındandır; iddia öncesi sakin-makine re-run kuralı geçerli.

## Yeniden üretim

```bash
python -m problems.kofn.benchmark_eval rapor.md
```

(CLI varsayılanı artık üç kolon: tohum / evrilen-v1 / evrilen-v2.)
Evrim dilimi komutu: `evolve/run.ps1` başlık yorumunda.
