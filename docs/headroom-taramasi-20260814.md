# Rekor-avı headroom taraması ve canlı çapraz (2026-08-14)

Amaç: math.CO-tarafı **rekor denemesi** için hedef hücre seçimi. B2
benchmark'ı (docs/benchmark-covering.md) 22/29 eşitleme verdi; eşitleme
yeterli değil, rekor için arşivdeki bir değeri **düşürmek** gerekiyor.
Bu tarama "nerede düşürülebilir + makinemiz oraya yapıca yakın mı"
sorusunu cevaplar.

## 1. Yöntem

- Kaynak: `data/covering/reference/record_scan.py` → `record_targets.csv`
  (207 aday satır). Donmuş arşiv (sources/coverdata.json, 2026-03-01)
  üzerinde katmanlı tarama:
  - **FRONTIER** — B2'de eşitlediğimiz hücre + `gap = size − low_bd ≥ 1`:
    zaten bilinen-en-iyi seviyesindeyiz, **tek blok düşüş = rekor**.
  - **NEAR** — B2'de +1/+2 kaldığımız hücreler (önce eşitle, sonra it).
  - **CONSTR** — B2 negatif hücrelerinin (arşivin bizde olmayan
    konstrüksiyonu olduğu kanıtlı) aynı-(k,t) komşuları.
  - **SEARCH** — gap 1-2, küçük, arama-erimli hücreler
    (C(23,10,3)=24 emsali: konstrüksiyonsuz eşitlenmişti).
  - **AFFINE** — afin uygulanabilir, koşulmamış hücreler.
- Komut: `python data/covering/reference/record_scan.py`
- ⚠ Devralınan uyarı (hedef-notlari.md #1): **gap>0 ≠ garanti headroom**
  — alt sınır zayıf olabilir; sıralama üretir, iddia üretmez.

## 2. Canlı skorbord çaprazı (2026-08-14)

Donmuş arşiv 5,5 aylık; hedef seçmeden önce her aday aile canlı sitede
kontrol edildi (coveringrepository.com, 14 aile sayfası:
`systems.aspx?k=K&t=T&m=T`).

**Erişim yolu notu:** uygulama içi Browser pane KULLANILMADI — site
Cloudflare Turnstile arkasında ve challenge sayfasının WebGPU
fingerprint'i Browser pane'in GPU sürecini deterministik çökertiyor
(exit 0x60C201E; 2. vaka 2026-08-13 20:53, Claude Desktop komple
kapandı). Güvenli yol: kullanıcının gerçek Chrome'u (claude-in-chrome);
challenge kendiliğinden geçti, etkileşim gerekmedi.

**Sonuç: kısa listedeki TÜM hedef hücreler donmuş arşivle birebir aynı**
(size, lb ve tarih teyitli). Tek sapma k=18,t=5 ailesi — canlı değerler
donmuş dökümün ALTINDA:

| Hücre | Donmuş | Canlı | Canlı tarih |
|---|---|---|---|
| C(32,18,5) | 56 | **55** | 2024-06-16 |
| C(37,18,5) | 124 | **105** | 2024-09-25 |
| C(38,18,5) | 131 | **122** | 2024-09-23 |
| C(39,18,5) | 155 | **147** | 2026-02-28 |
| C(40,18,5) | 186 | **182** | 2026-02-28 |

Dersler:
1. dmgordo dökümü canlı DB'nin mükemmel aynası değil (hedef-notlari.md
   uyarı #2 fiilen doğrulandı) — **rekor kıyası DAİMA canlı siteye**.
2. k=18,t=5 ailesi aktif yarışılıyor → hedef listesinden DÜŞÜRÜLDÜ.
3. B2'nin C(32,18,5) negatif satırı canlıya göre +44-45 (56 değil 55'e
   karşı) — eşitleme iddialarını etkilemez (satır zaten negatifti),
   makale revizyonunda dipnot adayı.

2026-03-01 sonrası aile-içi diğer aktivite: k=9,t=3'te v≥74 bandı
(Bluskov–Sidorenko, Nis-May 2026) — bizim v'ler (27/28/30/81)
dokunulmamış; k=6,t=4'te v≥38; k=11/12,t=3-4'te v≥41. Hedef
hücrelerimizin hiçbirine değmemiş.

## 3. Kısa liste (öneri, öncelik sırasıyla)

### Track A — ucuz av (FRONTIER/NEAR; uzun bütçeli prob + odaklı dilim)

Her satırda zaten arşiv seviyesindeyiz (sertifika var) ya da +1
uzaktayız; tek blok düşüş rekor eder. Küçük hücreler → doğrulama ucuz,
koşu ucuz, gece bandında taranabilir.

| Hücre | Canlı size | lb | gap | Durumumuz |
|---|---|---|---|---|
| C(20,12,4) | 20 | 15 | 5 (%25) | eşitleme sertifikalı; 1996'dan beri sabit |
| C(30,12,3) | 30 | 25 | 5 | eşitleme sertifikalı |
| C(25,16,4) | 17 | 13 | 4 (%24) | eşitleme sertifikalı |
| C(28,9,3) | 56 | 50 | 6 | 56 sertifikamız var → 55 avı |
| C(23,10,3) | 24 | 21 | 3 | B2'de eşitlendi |
| C(21,10,3) | 18 | 16 | 2 | eşitleme sertifikalı |
| C(22,10,3) | 19 | 17 | 2 | SEARCH bandı (koşulmadı) |

Ek SEARCH bandı (gap 2, hepsi canlıda teyitli): C(25,10,3)=30,
C(28,10,3)=36, C(24,11,3)=20, C(26,11,3)=26, C(27,11,3)=27,
C(31,11,3)=39, C(32,11,3)=40, C(25,12,3)=17, C(29,12,3)=27,
C(34,12,3)=39, C(35,12,3)=40, C(22,8,3)=38, C(23,8,3)=40, C(20,7,3)=45.

### Track B — prestij hedefi (yapısal keşif, thinking-dilimi)

- **C(81,9,3) = 1170, lb 1080, gap 90.** Arşiv değeri = saf afin AG(4,3)
  2-flat konstrüksiyonu (bizim genom da aynı değeri buluyor). Kırmak,
  saf afini yenen bir hibrit/dolgu yapısı ister — tam olarak B1'de
  kanıtlanan thinking-dilimi mekanizmasının işi. Yan ödül: C(80,9,3)
  arşivi 1170 (81'den türetme, lb 1058) — 81 düşerse 80 otomatik düşer.
- İkincil: **C(32,17,5) = 62, lb 53, gap 9** (dolgulu-afin sınır
  hücresi, 2008'den beri sabit; B2'de eşitledik).
- Düşük öncelik: C(32,8,4)=620 (gap 68 ama 30 yıldır kırılamadı ve
  kendi makalemizin merkez değeri; ayrı bir motivasyon gerektirir).

### Track C — konstrüksiyon ailesi (önce yeniden keşif, sonra rekor)

**C(v,6,4) ailesi.** B2'de v=24'te +263 açığımız var → arşivin
konstrüksiyonu bizde yok; önce onu thinking-dilimiyle yeniden keşfet
(v=24, hedef 784), başarılırsa ailenin gap'li komşularına uygula:

| Hücre | Canlı size | lb | gap | Son iyileştirme |
|---|---|---|---|---|
| C(23,6,4) | 716 | 625 | 91 | 2016-11 |
| C(26,6,4) | 1152 | 1040 | 112 | 2021-03 |
| C(29,6,4) | 1802 | 1653 | 149 | 2008-07 |

### Düşürülenler (gerekçeli)

- **k=18,t=5 ailesi** — canlı değerler donmuş dökümün altında, aile
  aktif yarışılıyor (bkz. §2).
- **AFFINE katmanı** (C(64,16,4) gap 216, C(64,8,3) gap 124): arşiv saf
  afinin ÇOK altında (620 vs 2604; 916 vs 11160) — d > t−1 hücrelerinde
  afin savurgan, konstrüksiyon avantajımız yok.
- **C(49,8,2)** (gap 5): t=2 literatür-yoğun bant (Tao gözlemi:
  başarı literatür yoğunluğuyla ters).

## 4. Track A gece probu bandı (kuruldu 2026-08-14)

`problems/covering/record_band.py` — Track A + SEARCH hücrelerini
thinking620 genomuyla sıralı tarar (CORE 7 hücre × 3 seed × 1200 sn,
SEARCH 14 hücre × 2 seed × 450 sn ≈ **10,5 saat**). Her koşu
`evaluate_text` ile kesin doğrulanır; arşiv-altı değer `ADAY-*.txt`
olarak paketlenir ve bayraklanır. Arşiv değerleri solver'a sızmaz
(yalnız koşu sonrası kıyas). Anytime + idempotent: Ctrl-C güvenli,
aynı komut kaldığı yerden devam eder.

```bash
python -m problems.covering.record_band --out runs/probes/track-a-20260814
```

Duman testi 2026-08-14: 3 hücre × 5 sn tesisatı doğruladı (feasible,
doğru fark, ikinci çağrı koşuları atladı); pytest 283/283 yeşil.
Bandı **sakin makinede** başlat; sabah `results.csv` + varsa `ADAY-*`
dosyalarına bakılır.

**Tur 1 sonucu (uzak makine, 2026-08-14→15, 49/49 koşu):** rekor adayı
YOK; tüm `fark` ≥ 0. Kazanımlar: SEARCH bandından **8 YENİ eşitleme**
(B2 setinde olmayan hücreler, hepsi kesin doğrulamalı):
C(22,10,3)=19, C(24,11,3)=20, C(26,11,3)=26, C(31,11,3)=39,
C(25,12,3)=17, C(29,12,3)=27, C(22,8,3)=38, C(20,7,3)=45 → band
koşulları altında eşitleme bilançosu 22→30 hücre (B2 donmuş-protokol
sayımından AYRI tutulur). Negatif uçlar: C(32,11,3)=61 (+21),
C(34,12,3)=52 (+13), C(35,12,3)=64 (+24) — orta-v yüksek-k'da arama
zayıf. **Enstrüman bulgusu:** her koşu ~305 sn sürdü — genom bütçeyi
içeride `min(budget, 305)` ile tavanlıyormuş (gen200'ün `min(50)`
vakasının aynısı; "sessiz tavan yok" kuralı yine haklı çıktı). Yani
CORE'un 1200 sn'lik uzun-bütçe hipotezi tur 1'de TEST EDİLMEDİ.
Düzeltme: `best_v32_thinking_620_20260811_cap7200.py` (yalnız o satır;
≤305 sn davranış birebir aynı, duman testiyle doğrulandı). **Tur 2:**
CORE 7 hücre × 3 seed × 1200 sn (~7 saat) tavansız genomla uzakta
(`runs/probes/track-a2-uzun`, görev `kt-track-a2`).

## 5. Sonuçlar: Tur 2 + Track B dilimleri (2026-08-15)

**Tur 2 (tavansız genom × gerçek 1200 sn, uzak makine, 21/21):** rekor
adayı YOK. Kazanç: iki kıl-payı hücre uzun bütçeyle eşitlemeye döndü —
**C(30,12,3)=30** (seed2; önceki koşularda 31) ve **C(28,9,3)=56**
(seed2; B2'de 58-70). Kalan tüm hücreler eşitlemeyi korudu
(C(22,10,3)=19 dahil). Not: ilk gece koşusu makine uykusuyla öldü
(uzak-kosu-kurulumu.md tuzak 6); idempotent devam ile tamamlandı.
**Desen kesinleşti: arama-erimli hücrelerde arşiv YAKALANIYOR ama
GEÇİLEMİYOR** — Track A kapandı, rekor umudu yapısal keşifte.

**Track B / C(81,9,3) — iki dilim:**
- *Dilim-1 (altyapı arızası):* 10/10 iterasyon "No valid code" —
  adaptive/high thinking bu görevde 64k VE 100k tavanların tamamını
  düşünmeye harcayıp content üretmedi (ölçüm zinciri
  config.covering.b81.thinking.yaml başlığında). Tamir:
  `reasoning_effort: medium` + `max_tokens: 100000` (OpenEvolve
  model-config'i native gönderiyor; proxy payload.override claude
  yolunda İŞLEMİYOR).
- *Dilim-2 (temiz negatif):* 10/10 iterasyon GEÇERLİ tam yeniden
  yazım; hepsi cost=1170 / fitness 0.9231 — **saf afin AG(4,3)
  iskeleti, medium-thinking Opus için 10 iterasyonda aşılamayan bir
  çekim noktası.** Arşiv kancasında 1170-altı hiçbir çözüm yok.

**Yayın değeri olan asimetri bulgusu:** v32'de thinking-Opus, bilinen
sınıra ULAŞMAYI (977→620) ilk iyileşen iterasyonda başarmıştı; b81'de
bilinen sınırı AŞMA 10 iterasyonda gelmedi ve sınırsız (adaptive)
düşünme içerik üretimini süresiz erteleyen sarmala girdi. "Reaching
vs exceeding the frontier" asimetrisi + reasoning-derinliğinin görev
zorluğuna göre sarmal riski — makale revizyonu / C1 devam işi için
kayıt.

**Sıradaki öneri (Track C):** C(24,6,4)=784 yeniden keşif dilimi —
mekanizmaya en uygun hedef: mevcut durumumuz +263 AÇIK (gradyan var),
görev şekli v32/B1 ile birebir aynı ("bilinen sınıra ulaş"), başarılırsa
ailenin gap'li komşuları (v=23/26/29, gap 91/112/149) rekor av alanı.

**Track C dilim-1 sonucu (2026-08-15, runs/evolve/b24-dilim1):**
gradyan AKIYOR ama yapısal sıçrama henüz yok — 10/10 geçerli iterasyon
(medium/100k reçetesi ikinci dilimde de sıfır parse hatası), tohum
1054 → en iyi çocuk **993** (fitness 0.7144; ilk iyileşme daha 2.
iterasyonda). Arşiv kancasında 13 sertifika (1045→993 kademeli iniş).
Hedef 784'e kalan +209 — v32 deseninde kademeli iniş fazı yapısal
sıçramadan önce gelmişti (977 platosu ~75 iter sürmüştü); devam dilimi
checkpoint_10'dan başlar.

**Track C dilim-2 sonucu (2026-08-15, runs/evolve/b24-dilim2 —
GLM-5.3 thinking):** checkpoint_10'dan +25 iter, 25/25 geçerli
(sıfır parse hatası), ~50 dakikada bitti. En iyi: 993 → **926**
(fitness 0.7649; ara sertifikalar 988/981/980/978/957). Hedefe kalan
+142. Yol: 8318 + `glm5think` alias'ı (glm-* override'ına takılmayan
thinking-açık isim) + `reasoning_effort: high`. Modeller-arası ölçüm:
aynı tam-boy prompt'ta Opus-medium ~55k token düşünürken GLM-5.3
~1-3k token düşünüyor (high 3342 / max 1224 — z.ai dokümanına göre
seviyeler fiilen atla/high/max'a çöküyor, token eşlemesi belgesiz;
effort yükseltmek derinlik satın almıyor) ve iterasyonu dakikalar
mertebesinde tamamlıyor — kota verimi çarpıcı, sıçrama kapasitesi
henüz test aşamasında. Devam: checkpoint_35.

## 6. İddia protokolü (değişmedi, guardrail)

Bir prob/dilim arşiv altı değer üretirse: (1) sakin makinede bağımsız
re-run, (2) `evaluate_text` + stdlib `verify_cover.py` çifte doğrulama,
(3) canlı skorbordda AYNI GÜN yeniden kontrol (bu dosyanın §2 dersi),
(4) sertifika paketi `data/covering/results/` düzeninde, (5)
coveringrepository.com'a gönderim = dış paylaşım = **kullanıcı onayı
olmadan yapılmaz**.
