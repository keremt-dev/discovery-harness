# Faz E Gradyan Tamiri — "50 iterasyonda iyileşme yok" vakası

Tarih: 2026-08-05. Teşhis, cvrp-discovery oturumunun analiziyle başladı;
buradaki araçlarla bağımsız doğrulandı ve tasarım düzeltmesine çevrildi.

## Teşhis (bağımsız doğrulanmış)

İlk GLM koşusu (50 iter, hedef `gen-n120-m6-s2`) skorda kıpırdamadı çünkü
**evrime çözülmüş bir instance verilmişti**: headroom turnusolu
(`python -m problems.kofn.refsearch <instance>`) tohumun tahsisiyle
referans aramanın tahsisinin AYNI olduğunu ölçtü —

    tohum R = ref R = 0.391144, alloc (0,0,101,19,0,0), headroom = 0.000000

Standart üreteç profili + oran-greedy tohum kombinasyonu, kuantil-K'ya
rağmen yerel aramanın tavanına ilk denemede oturuyor. Döngü, seçilim,
işaret dönüşümü, evaluator sağlamdı; keşfedilecek şey yoktu.

## Reddedilen öneri: tohumu zayıflatmak

"Naif tohum → erken gradyan" önerisi bilinçli olarak REDDEDİLDİ:
güdükleştirilmiş bir baseline'ı yenmek bilimsel iddia üretmez (strawman).
Tohum = güçlü oran-greedy olarak kalır; **gradyan instance tasarımından
gelir.** Evrimin ilk görünür adımı, tohumun yapamadığı çok-birimli/yapısal
hamleleri keşfetmektir — istenen de bu.

## Düzeltme 1: headroom turnusolu (kurasyon kuralı)

`problems/kofn/refsearch.py`:
- `idealized_seed` — süre limitsiz tohum (oran-greedy + tekil takas).
- `reference_search` — çok başlangıçlı (kurulum + tek-tip + rastgele
  fizibil) ve çok-birimli (1/2/4/8 transfer) deterministik arama.
- **Kural: headroom = ref_R − tohum_R ≈ 0 olan instance evrim hedefi
  OLAMAZ.** (Küçük n'de gerçek headroom = enum_opt − tohum ile ölçülür.)

## Düzeltme 2: "sert" üreteç profili

`generate.py profile="sert"` — plato oyuncağının ölçeklenmiş tarifi:
hafif tipler çok ucuz (w·p/c oranı en iyi → tohum bunları sever), ağır
tipler süper-lineer pahalı (c ∝ w^1.5) ama K'ya ulaşmak için şart; bütçe
dar (en-ucuz dolumun 1.2-1.8×); K, **maks-ağırlık tahsisinin** sağkalım
kuantilinde. Sonuç: oran-greedy'nin tahsisi R≈0 bölgesinde kalır ve tekil
takas yolu ölü bölgeden geçer.

Tarama (n∈{20,25,30}, m∈{4,5}, seed 1..10; gerçek headroom = enum_opt −
idealize tohum): 28 geçerli instance'ın 21'inde headroom > 0.02; en
iyiler 0.60-0.96 aralığında. Birkaçında **refsearch bile açığı tam
kapatamıyor** (0.016-0.043 kalıntı) — çok-birimli hill-climb ötesi
derinlik.

## Düzeltme 3: küratörlü evrim hedefi (çoklu-instance)

Seçilen set (üç farklı zorluk kipi; hepsi enumere edilebilir → gerçek
optimum raporlama için biliniyor, döngü asla görmüyor):

| instance | tohum R | kanıtlı opt | headroom | refsearch açığı |
|---|---|---|---|---|
| gen-sert-n20-m4-s1 | 0.0000 | 0.8816 | 0.8816 | 0 (ref çözüyor) |
| gen-sert-n25-m5-s3 | 0.0000 | 0.7657 | 0.7657 | 0.0434 |
| gen-sert-n30-m5-s6 | 0.4787 | 0.7837 | 0.3050 | 0 |

Adaptör artık `DISCOVERY_INSTANCE` içinde `;` ayraçlı liste kabul ediyor:
fitness = combined_score ortalaması, feasible = min, instance-başı kırılım
artifact'ta (`per_instance`). Tek instance'a ezber baskısı böyle kırılır.
Tohumun set ortalaması ≈ 0.160; evrim için görünür merdiven: çok-birimli
hamle keşfi (→ ~0.7+), refsearch-ötesi yapısal arama (→ 0.81+).

## Başarı okuma anahtarı (duman testi)

- İyileşme YOK + tüm adaylar ~0.16 → hâlâ sorun var (döngü/prompt).
- 0.16 → 0.5-0.7 bandına sıçrayanlar → gradyan geri geldi (beklenen).
- 0.78+ ortalama → evrim refsearch seviyesini de aştı (erken zafer,
  şüpheyle doğrula: bağımsız re-run + enumerate karşılaştırması).

## SONUÇ (2026-08-05, 20 iterasyon, GLM-5.2)

**Gradyan geri geldi ve tavana vurdu:** en iyi program (iterasyon 3)
combined = **0.8103** = üç kanıtlı optimumun ortalaması. Bağımsız re-run
(sakin makine, adaptör üzerinden, enumerate çaprazı): **üç instance'ta da
6 haneye kadar kanıtlı optimum** — 0.881601 / 0.765742 / 0.783694.
Dikkat çekici: `gen-sert-n25-m5-s3`'te refsearch 0.7223'te kalıyordu;
evrilen program 3 iterasyonda optimumu (0.7657) buldu — **bizim referans
aramamızı geçti.** Evrilen kod (220 satır): tip-bazlı binom dağılımı +
çapraz konvolüsyon (bizim birim-bazlı DP'den hızlı), çoklu-oran kurulum
portföyü, süre-bütçeli yerel arama.

Skor merdiveni sağlıklı: bozuk mutantlar −6/−1.45/−0.88 (doğru ceza),
orta adaylar 0.77x, tepe 0.8103.

**Açık sorun:** 20 iterasyonun 10'u "No valid diffs found" ile boşa gitti
(%50 diff-parse kaybı; GLM'in kendi 5-iter testinde %18'di). Kota başına
faydalı iterasyon maliyetini ikiye katlıyor — uzun koşudan önce ele
alınmalı (diff kapatmak full-rewrite ~15k token/çağrı demek; %50 kayıplı
diff hâlâ ~2×3.4k=6.8k ile daha ucuz ama duvar saati israfı var).

**Sonraki adım:** duman seti tasarımı gereği enumere edilebilirdi ve artık
çözüldü — uzun koşu hedefi, enumeration-dışı boyutta (n=60-150) refsearch
sertifikalı headroom'lu YENİ sert instance'lar olmalı; keşif iddiası
orada yaşar (bkz. bilimsel-iddia-plani.md Katman 2).

## DİLİM 1 hedef seti ve model planı (2026-08-05)

Tarama (n∈{60,100}, m∈{6,8,10}, seed 1..6; ucuz eleme:
headroom alt sınırı = R(maks-ağırlık tahsisi) − R(idealize tohum);
kısa liste refsearch + derinlik sondası starts 8→64, iki rng):

| hedef | tohum | ağır-tahsis (kanıtlı lb) | refsearch (yenilecek baseline) | not |
|---|---|---|---|---|
| gen-sert-n25-m5-s3 | 0.000 | — | **0.7657 = kanıtlı optimum** | enumere edilebilir çapa; duman koşusunda çözüldü |
| gen-sert-n60-m10-s4 | 0.000 | 0.5171 | **0.7371** (64 start'ta stabil) | doygunluktan uzak; m=10 kombinatorik boyut |
| gen-sert-n100-m6-s4 | 0.000 | 0.6278 | **0.6339** (derinlik sinyali: 8→64 start +0.006) | en büyük n; engebeli manzara işareti |

Merdiven: tohum 0.000 → ağır-tahsis keşfi ~0.4 → refsearch seviyesi
~0.712 (set ort.) → **üstü = keşif bölgesi**. İki büyük instance'ta
optimum bilinmiyor (enumeration imkânsız); "refsearch'ü geç" kriteri
docs/bilimsel-iddia-plani.md Katman 2'nin işlevsel hali.

Model/mod planı (kota gerekçeli, kullanıcı onaylı):
- **Dilim 1:** GLM + full-rewrite (diff kapalı — duman testinde %50 diff
  parse kaybı), 50 iterasyon.
- **Dilim 2:** checkpoint'ten diff'e geçiş; kayıp ilk 20 iterasyonda
  ölçülür, >%40 ise geri full.
- **Plato kartı:** ~100 iterasyon iyileşmesizlikte checkpoint'ten
  Opus 5 (8317) + full-rewrite kısa dilim; sonra GLM'e dönüş. Tohum
  zayıflatma önerisi reddedilmiş durumda (strawman).

## DİLİM 1 SONUCU (2026-08-05, 50 iterasyon, GLM full-rewrite)

En iyi program: combined = **0.7228** (set ort.; baseline seti ort.
0.712'nin üstünde). Bağımsız instance-başı doğrulama (sakin makine,
adaptör + tam aritmetik):

| hedef | baseline | evrilen | fark |
|---|---|---|---|
| gen-sert-n25-m5-s3 | 0.765742 (kanıtlı opt) | 0.765742 | **= optimum** (6 hane) |
| gen-sert-n60-m10-s4 | 0.7371 (refsearch) | 0.737075 | ≈ eşit |
| gen-sert-n100-m6-s4 | 0.6339 (refsearch64) | **0.665530** | **+0.0316 — refsearch GEÇİLDİ** |

**İlk keşif-bölgesi sonucu:** derinlik sinyali verdiğimiz n=100
instance'ında evrilen çözücü, elle yazılmış en güçlü aramamızın 3.2 puan
üstüne çıktı. (İddia dili dikkatli: refsearch bizim baseline'ımız,
yayınlanmış SOTA değil; rapor protokolü — çoklu bağımsız re-run,
Goodhart notları — Faz E kapanışında.)

Yan gözlem: bir aday R=1.0'lık infeasible aşırı-tedarik tahsisi denedi
→ ceza mekanizması doğru çalıştı (fitness −13.3, elendi). Evaluator'ün
"hiçbir ihlal kârlı olamaz" tasarımı sahada doğrulandı.

Sorunlar: (1) 19/50 iterasyon "No valid code found" — full-rewrite'ta
%38 kayıp; şüpheli mekanizma büyüyen programların (120+ sn'lik anytime
arama döngülü, yüzlerce satır) 20k max_tokens'a sığmaması. Diff modu
(küçük çıktı) bu kaybı azaltabilir — Dilim 2'nin ölçüm sorusu.
(2) 0.7228'e erken varış + uzun plato: popülasyon tek çözüm ailesine
yakınsadı; Dilim 2 düz kalırsa Opus kartı oynanır.

## OPUS KARTI SONUCU + TAVAN KANITI (2026-08-05 akşam)

Opus dilimi (checkpoint_75→105, 30 iterasyon, cli-proxy üçlü tamiri
sonrası — bkz. CLAUDE.md §0.3): **0 parse hatası (30/30 geçerli kod;
GLM full %62 idi)**. Sonuç: 28/30 aday tam olarak 0.7228'e yakınsadı —
plato kırılmadı.

Tavan kanıtı (LLM'siz): 512-start refsearch (2 rng) —
- n60-m10-s4: 0.737075 = evrilen değerle aynı nokta.
- n100-m6-s4: 0.633933 < evrilen 0.665530 — **512 start bile evrilen
  çözücünün +0.0316'lık avantajını kapatamıyor.**

Hüküm: bu üçlü set TÜKENDİ. 0.7228 ≈ setin fiilî tavanı; iki model
(~95 iterasyon) + ağır referans arama aynı noktada. Amiral gemisi bulgu
duruyor: n100'de evrilen sezgisel, en güçlü elle yazılmış aramanın
kalıcı olarak üstünde (Katman 2 tipi sonuç; iddia dili: "bizim
referans aramamıza karşı", yayınlanmış SOTA değil).

Sonraki adım seçenekleri: (a) benchmark'ı ölçekle — kürasyon baseline'ı
olarak artık EVRİLEN çözücüyü kullan (refsearch değil), onun da headroom
bıraktığı instance'lar üret → uzun koşu orada; (b) Faz E kapanış raporu
+ P2/MMKP'ye geçiş. Model notu: Opus %100 parse ile uzun koşu için de
tercih; kota planlamasına göre GLM keşif / Opus kırılım işbölümü.
