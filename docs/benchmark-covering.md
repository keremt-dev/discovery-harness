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

## 3. Sonuçlar (2026-08-13; koşu süresi 297 dk, 116/116 koşu tamam)

Ortam kaydı: arka plan yükü %26-41 dalgalı (docker backend, parsec,
claude oturumları — kayıt koşu öncesi alındı); solver'lar sıralı, tek
süreç. Genom SHA'ları: thinking620 = `evolve/artifacts/
best_v32_thinking_620_20260811.py` (commit 6198ebd), tohum =
`problems/covering/seed_solver.py`.

| Hücre | Rol | Arşiv | Tohum | thinking620 (3 seed) | Durum |
|---|---|---|---|---|---|
| C(7,3,2) | BEKÇİ | 7 | 7 | 7 | **EŞİT** |
| C(13,3,2) | BEKÇİ | 26 | 26 | 26 | **EŞİT** |
| C(32,8,4) | EĞİTİM | 620 | 1258 | 620 | **EŞİT** |
| C(8,4,3) | AFİN-H | 14 | 14 | 14 | **EŞİT** |
| C(9,3,2) | AFİN-H | 12 | 12 | 12 | **EŞİT** |
| C(16,4,3) | AFİN-H | 140 | 154 | 140 | **EŞİT** |
| C(16,8,4) | AFİN-H | 30 | 54 | 30 | **EŞİT** |
| C(25,5,2) | AFİN-H | 30 | 38 | 30 | **EŞİT** |
| C(27,3,2) | AFİN-H | 117 | 118 | 117 | **EŞİT** |
| C(27,9,3) | AFİN-H | 39 | 80 | 39 | **EŞİT** |
| C(32,4,3) | AFİN-H | 1240 | 1450 | 1240 | **EŞİT** |
| C(32,16,5) | AFİN-H | 62 | 219 | 62 | **EŞİT** |
| C(32,17,5) | AFİN-H | 62 | 156 | 62 | **EŞİT** |
| C(49,7,2) | AFİN-H | 56 | 91 | 56 | **EŞİT** |
| C(49,8,2) | AFİN-H | 49 | 72 | 49 | **EŞİT** |
| C(64,4,3) | AFİN-H | 10416 | 12986 | 10416 | **EŞİT** |
| C(81,3,2) | AFİN-H | 1080 | 1152 | 1080 | **EŞİT** |
| C(81,9,3) | AFİN-H | 1170 | 2504 | 1170 | **EŞİT** |
| C(27,10,3) | AFİN-SINIR | 35 | 59 | 36 | +1 |
| C(32,18,5) | AFİN-SINIR | 56 | 119 | 99-100 | +43 |
| C(24,6,4) | PP-DIŞI | 784 | 1171 | 1047-1049 | +263 |
| C(28,9,3) | PP-DIŞI | 56 | 90 | 58-70 | +2 |
| C(21,10,3) | PP-DIŞI | 18 | 25 | 18 | **EŞİT** |
| C(20,12,4) | PP-DIŞI | 20 | 29 | 20 | **EŞİT** |
| C(23,10,3) | PP-DIŞI | 24 | 34 | 24 | **EŞİT** |
| C(25,16,4) | PP-DIŞI | 17 | 24 | 17 | **EŞİT** |
| C(30,12,3) | PP-DIŞI | 30 | 51 | 31 | +1 |
| C(30,9,3) | PP-DIŞI | 66 | 113 | 91 | +25 |
| C(22,15,5) | PP-DIŞI | 22 | 35 | 29-30 | +7 |

**Özet:** 22/29 hücrede bilinen-en-iyi EŞİTLENDİ (rekor yok); tohum
baseline 29 hücrenin 27'sinde thinking620'nin gerisinde (2 küçük
hücrede eşit). 22 eşitlemenin 22'si bağımsız stdlib doğrulayıcıdan
geçti. Seed kararlılığı: 29 hücrenin 25'inde üç seed ÖZDEŞ sonuç
verdi (iş-sayaçlı determinizm sözleşmesinin ampirik karşılığı);
varyans görülen 4 hücrede bant dar (99-100, 1047-1049, 29-30) —
tek istisna C(28,9,3) 58-70.

**Protokol-altı yeni kazanım:** C(23,10,3)=24 — afin uygulanamayan
hücrede, önceki tüm koşularımızın kaçırdığı değer (en iyimiz 25 idi;
CLAUDE.md'de "kalan tek küçük av" diye kayıtlıydı) genel genom
tarafından 120 sn'de eşitlendi. PP-DIŞI kolundaki 4 eşitleme
(21/20/23/25 evrenleri) afin konstrüksiyonsuz, evrilmiş greedy+yerel
arama makinesiyle geldi — genelleme iddiasının afin ailesi dışına
taştığının kanıtı.

## 4. Negatif bulgular

- **C(32,18,5): +43 (99-100 vs 56).** Dolgulu afin yolu (16-flat + 2
  dolgu) bu hücrede yapısal olarak verimsiz; arşivin konstrüksiyonu
  farklı bir ailede. Genomun en zayıf hücresi.
- **C(24,6,4): +263.** Büyük PP-DIŞI hücrede yerel arama arşiv
  kalitesine yaklaşamıyor (arşiv 784, 1996 "Known design") —
  v32'nin afin çözümü gibi yapısal bir konstrüksiyon gerekir.
- **C(30,9,3): +25, C(22,15,5): +7.** Aynı desen: orta-büyük PP-DIŞI
  hücrelerde arama-temelli yaklaşım arşivin gerisinde.
- **C(27,10,3): +1 ve C(30,12,3): +1.** Kıl payı; daha uzun bütçe /
  odaklı evrim dilimi kapatabilir (C(28,9,3)=56 emsali: odaklı dilim
  gerekmişti).
- **EĞİTİM hücresi uyarısı:** C(32,8,4) satırı genelleme kanıtı
  DEĞİLDİR (döngü bu hücrede eğitildi); tabloda şeffaflık için durur.
- v=64 t=5 hücreleri sete alınmadı (bellek); boşluk açık.
