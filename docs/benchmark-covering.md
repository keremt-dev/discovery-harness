# Covering Benchmark — protokol ve sonuçlar (B2)

Tarih: 2026-08-13. Amaç: `docs/yayin-bulgu-ozeti-20260811.md` C1
makalesinin genelleme iddiasını taşıyan FORMAL ölçüm. Protokol bölümü
koşudan ÖNCE donduruldu (ön-kayıt disiplini); Sonuçlar bölümü koşu
bittikten sonra dolduruldu, protokol geriye dönük DEĞİŞTİRİLMEDİ.

## 1. İddia şablonu

> "Tek bir evrilmiş program (hücre başına ayar ve yeniden eğitim
> olmadan, sabit seed'lerle), aşağıda önceden ilan edilmiş hücre
> setinde şu sonuçları verdi; her değer kesin sayımla doğrulandı."

## 2. Protokol (DONDURULDU — 2026-08-13, koşu öncesi)

### Çözücüler
- **tohum**: `problems/covering/seed_solver.py` (evrim öncesi baseline;
  yalnız seed 0 — baseline için varyans bandı iddiası yok).
- **thinking620**: `evolve/artifacts/best_v32_thinking_620_20260811.py`
  (nihai evrilmiş genom; seed 0, 1, 2 — varyans ölçülür).

### Koşu koşulları
- CLI: `python <genom> <instance> <cikti> --seed N`;
  `COVERING_SEED_TIME_S` = hücre bütçesi; sıralı (tek solver süreci),
  sakin makine (başlangıçta CPU yükü kaydedilir).
- Doğrulama: `problems.covering.objective.evaluate_text` (kesin sayım);
  başlık satırları ayrıca stdlib `verify_cover.py` ile bağımsız.
- Ölçüt: feasible blok sayısı (cost); thinking620 için seed'ler üzerinden
  en iyi / en kötü (yayında ikisi de raporlanır).

### Hücre seti (29 hücre; arşiv = coveringrepository "size")
Roller: BEKÇİ = kanıtlı optimum (enstrüman sağlığı); EĞİTİM = evrim
döngüsünün fitness'ında GÖRÜLDÜ (açık beyan); AFİN-H = holdout,
asal-kuvvet (afin ailesi); AFİN-SINIR = holdout, afin uygulanır ama
arşiv saf afinden iyi; PP-DIŞI = holdout, afin uygulanamaz
(asal-kuvvet değil ya da d < t-1).

| Hücre | Arşiv | Rol | Bütçe (sn) |
|---|---|---|---|
| C(7,3,2) | 7* | BEKÇİ | 60 |
| C(13,3,2) | 26* | BEKÇİ | 60 |
| C(32,8,4) | 620 | EĞİTİM | 300 |
| C(8,4,3) | 14 | AFİN-H | 120 |
| C(9,3,2) | 12 | AFİN-H | 120 |
| C(16,4,3) | 140 | AFİN-H | 120 |
| C(16,8,4) | 30 | AFİN-H | 120 |
| C(25,5,2) | 30 | AFİN-H | 120 |
| C(27,3,2) | 117 | AFİN-H | 120 |
| C(27,9,3) | 39 | AFİN-H | 120 |
| C(32,4,3) | 1240 | AFİN-H | 120 |
| C(32,16,5) | 62 | AFİN-H | 120 |
| C(32,17,5) | 62 | AFİN-H | 120 |
| C(49,7,2) | 56 | AFİN-H | 120 |
| C(49,8,2) | 49 | AFİN-H | 120 |
| C(64,4,3) | 10416 | AFİN-H | 120 |
| C(81,3,2) | 1080 | AFİN-H | 120 |
| C(81,9,3) | 1170 | AFİN-H | 120 |
| C(27,10,3) | 35 | AFİN-SINIR | 300 |
| C(32,18,5) | 56 | AFİN-SINIR | 300 |
| C(24,6,4) | 784 | PP-DIŞI | 300 |
| C(28,9,3) | 56 | PP-DIŞI | 300 |
| C(21,10,3) | 18 | PP-DIŞI | 120 |
| C(20,12,4) | 20 | PP-DIŞI | 120 |
| C(23,10,3) | 24 | PP-DIŞI | 120 |
| C(25,16,4) | 17 | PP-DIŞI† | 120 |
| C(30,12,3) | 30 | PP-DIŞI | 120 |
| C(30,9,3) | 66 | PP-DIŞI | 300 |
| C(22,15,5) | 22 | PP-DIŞI | 120 |

\* BEKÇİ değerleri kendi enstrümanımızca kanıtlı optimum (enumerate).
† v=25 asal-kuvvet ama k=16,t=4 için afin d=1 < t-1 → afin uygulanamaz;
PP-DIŞI muamelesi görür.

### Dürüstlük kuralları
- EĞİTİM hücresi tabloda işaretli kalır; genelleme iddiası ondan
  türetilmez.
- Hiçbir hücrede parametre/varyant ayarı yok; genom dosyası sabit
  (git SHA ile kayıtlı).
- Negatif satırlar (arşivin gerisinde kalınan hücreler) tablodan
  ÇIKARILMAZ.
- v=64, t=5 hücreleri (2593-2604 bandı) bellek sınırı nedeniyle sete
  ALINMADI — boşluk beyanı, sonradan eklenebilir.
- Arşiv kıyası DAİMA `size` alanına (donmuş arşiv + canlı skorbord).

### Tekrarlama

```bash
python <surucu> --out runs/evolve/benchmark-covering
```

(sürücü: koşu bölümünde; instance dosyaları `v/k/t` başlıklı 3 satırlık
metin, sürücü tarafından deterministik üretilir)

## 3. Sonuçlar

(koşu sonrası doldurulacak)

## 4. Negatif bulgular

(koşu sonrası doldurulacak)
