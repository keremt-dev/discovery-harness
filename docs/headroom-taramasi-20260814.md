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

## 4. İddia protokolü (değişmedi, guardrail)

Bir prob/dilim arşiv altı değer üretirse: (1) sakin makinede bağımsız
re-run, (2) `evaluate_text` + stdlib `verify_cover.py` çifte doğrulama,
(3) canlı skorbordda AYNI GÜN yeniden kontrol (bu dosyanın §2 dersi),
(4) sertifika paketi `data/covering/results/` düzeninde, (5)
coveringrepository.com'a gönderim = dış paylaşım = **kullanıcı onayı
olmadan yapılmaz**.
