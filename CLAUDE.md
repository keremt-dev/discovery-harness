# CLAUDE.md

Bu dosya Claude Code'a (claude.ai/code) bu depoda çalışırken rehberlik eder.

# Proje: Probleme-Agnostik Keşif Harness'ı (Faz 5 devamı)

## 0. BU OTURUMDA ÖNCE OKU — makine paylaşımlı

`C:\kt\tcdd\cvrp-discovery` deposunda **gece boyu bir OpenEvolve koşusu
çalışıyor**. İki sert kural:

1. **`C:\kt\tcdd\cvrp-discovery` altında hiçbir dosya DEĞİŞTİRİLMEZ.** O depo
   bu proje için salt-okunur referanstır. Kod taşınacaksa **kopyalanır**,
   oradaki dosyaya dokunulmaz.
2. **Bu depoda CPU-yoğun hiçbir şey koşturulmaz** (evolve döngüsü, uzun solver
   benchmark'ı, paralel pytest yok). Gerekçe: cvrp-discovery'nin evrilen
   solver'ları **süre-bütçeli (anytime)**; aynı makinede CPU çalarsak gece
   koşusunun sonuçları bozulur ve rekor iddiası geçersizleşir. Bu oturumda
   yapılacak iş: **kod yazmak, test yazmak, tasarım kararı almak**. Ucuz
   birim testleri (ms-sn mertebesi) sorun değil.
3. Ek olarak: cli-proxy-api (localhost:8317) tek proxy; ikinci bir evolve
   döngüsü başlatmak gece koşusunun LLM çağrılarıyla yarışır. Bu depoda
   evolve döngüsü **ancak gece koşusu bittikten sonra** başlatılır.
   **Proxy katmanı (2026-08-04):** Faz E döngüsü Claude kotası bittiği için
   **GLM Coding Plan Lite (z.ai)**'a taşındı. Artık iki cli-proxy container'ı
   var (aynı `eceasy/cli-proxy-api` imajı, ayrı config/port):
   - **8317 / `config.yaml`** → Claude OAuth (mevcut, DOKUNULMAZ).
   - **8318 / `config.glm.yaml`** → GLM Coding Plan Lite, `openai-compatibility`
     bloğu (API key, OAuth değil). Kurulum: `C:\kt\upwork\cli-api` altında
     `docker compose -f docker-compose.glm.yml up -d`.
   Evolve döngüsü 8318'i kullanır (`evolve/config.yaml`, `evolve/run.ps1`).
   §0'daki "tek proxy" kuralı zayıfladı; gece koşusu bittiği için kabul
   edildi. Claude kotası dolunca geri 8317'ye dönülebilir (elle revert).
   **8317 tamiri (2026-08-05):** 04.08'deki `:latest` image güncellemesi
   claude executor'a `context_management` (clear_thinking_20251015)
   enjeksiyonu getirdi; Anthropic bunu thinking kapalıyken 400 ile
   reddediyor ve 8317'nin claude yolu komple kırılıyordu. Tamir:
   `config.yaml` sonuna `payload.filter` bloğu (claude-* / protocol
   claude → `context_management` alanını kaldır) + container restart.
   Yedek: `config.yaml.bak-20260805`. Image güncellerken bu davranışı
   yeniden kontrol et. **İkinci tamir (aynı gün):** upstream Overloaded
   başına 60 sn auth-cooldown, tek kimlikle blackout kaskadı yaratıyordu
   (koşuda 78 ardışık `auth_unavailable`); `disable-cooling: true` eklendi
   (yedek: `config.yaml.bak2-20260805`). Ayrıca `claude-login.ps1` login'i
   container restart'ından SONRA kaydettiği için sunucu yeni auth'u
   görmüyor — login sonrası elle `docker restart cli-proxy-api` gerekir.
   **Üçüncü tamir (aynı gün):** bu OAuth yolunun beta başlıklarıyla Opus,
   `thinking` alanı YOKKEN bile varsayılan adaptive thinking yapıyor ve
   büyük prompt'larda TÜM max_tokens bütçesini thinking'e harcayıp
   content'i boş bırakıyor (ölçüldü: completion 20000, content 0,
   finish=length → OpenEvolve "No valid code"). Alanı filtrelemek YETMEZ;
   GLM tamiriyle aynı desen gerekir: `payload.override` ile claude-* /
   protocol claude için `thinking: {type: disabled}` dayatıldı (yedek:
   `config.yaml.bak4-20260805`). Doğrulama: koşuyu birebir taklit eden
   replika istek (system + top_p + 51k karakter prompt) finish=stop,
   tam kod bloğu, 9k token content. NOT: 8317'yi kullanan diğer
   istemcilerde de claude thinking kapanır — istenirse blok silinip
   restart atılır.
4. **Subagent'lara uygulama içi tarayıcı YASAK** (Claude Desktop'ta
   çalışırken). 2026-08-03: araştırma ajanı ResearchGate'i Browser pane'de
   açınca GPU süreci çöktü (exit 0x60c201e, deterministik) ve Claude Desktop
   1.24012.9 tüm ajanlarla birlikte komple kapandı — iki kez. Web araştırması
   yapan her subagent prompt'una açıkça yaz: WebFetch/WebSearch/API kullan,
   `mcp__Claude_Browser__*` kullanma; tarayıcı gerektiren kaynağı boşluk
   olarak raporla.

## 1. Amaç

cvrp-discovery, "AI'a bilimsel keşif yaptırma" döngüsünün CVRP üzerinde
çalıştığını kanıtladı (tohum 44.486 → 33.991; BKS 33.503'e gap %1,5). Bu depo
o deponun **Faz 5** hedefini gerçekleştirir: harness'ı probleme-agnostik hale
getirip **yeni problem sınıflarına** taşımak.

Bilimsel iddianın tam çerçevesi (ne bulunacak, nasıl savunulacak):
`docs/bilimsel-iddia-plani.md`.

Problem seçimi, İzmir Ekonomi Üniversitesi'nden **G. Yazgı Tütüncü**'nün
araştırma profilinin taranmasıyla yapıldı (bkz. §7). Seçim kriteri değişmedi:
**verifier asymmetry** — üretmesi zor, doğrulaması ucuz ve *kesin* problemler.

## 2. Problem sırası (karar verilmiş, tartışma kapandı)

| # | Problem | Neden | Öncelik |
|---|---|---|---|
| **P1** | **Weighted k-out-of-n:G redundancy/component allocation** | Doğrulayıcı *tam* hesaplanabilir (signature / ağırlık üzerinden DP). Küçük n'de exhaustive enumeration ile **gerçek optimum** bilinir → evaluator'ün doğruluğu test edilmekle kalmaz, ÖLÇÜLÜR. CVRP'de yapamadığımız şey. | **ANA HEDEF** |
| **P2** | **MMKP** (multidimensional multiple-choice knapsack) | En ucuz "harness gerçekten agnostik mi?" sınavı. Objective = seçilen değerlerin toplamı (tamsayı), kısıt = m kaynak boyutu + grup başına tam bir seçim. Evaluator ~80 satır. | İkinci |
| **P3** | **HFFVRP-with-backhauls / MD-VRPB** (köprü) | cvrp-discovery evaluator'ünün %80'i yeniden kullanılır; hedef tablo doğrudan Tütüncü'nün EJOR 2010 + AOR 2021 sonuçları. | Gece koşusu bitince |

**P1 ile başla.** P3 cazip görünse de mevcut depoya bağımlı ve gece koşusu
bitene kadar kalibrasyonu güvenilir yapılamaz.

### Kaçınılacak alanlar (guardrail — tartışmaya açık değil)

Tütüncü profilindeki **fuzzy naive Bayes / qtQDA / RNA-Seq kovaryans /
portföy optimizasyonu** kümesi bu harness'a **UYGUN DEĞİL**. Gerekçe:
objective (accuracy, AUC, backtest getirisi) sonlu veriden hesaplanan
*gürültülü bir tahmin*. Evrilen program değerlendirme bölünmesine overfit
eder — reward hacking'in ders kitabı vakası; ayrıca plateau ile overfit
ayırt edilemez hale gelir. Biri ısrar ederse: nested CV + döngünün asla
görmediği mühürlü holdout şart, ve o zaman bile "rekor" iddiası edilemez.

## 3. Mimari — problem eklentisi (plugin) sözleşmesi

cvrp-discovery'de problem bilgisi evaluator'e gömülüydü. Burada ayrılıyor:

```
harness/            # probleme-agnostik çekirdek (problem adı GEÇMEZ)
  runner.py         # aday programı ayrı process'te koştur, timeout, artifact
  score.py          # sense'e göre fitness -> combined_score dönüşümü
  registry.py       # problems/ altındaki eklentileri yükler
problems/
  kofn/             # P1
    io.py           # instance parser -> Instance dataclass
    objective.py    # kanonik hedef (TAM aritmetik) + feasibility + violations
    seed_solver.py  # evrimin başlangıç genomu (kendi kendine yeten tek dosya)
    prompt.md       # LLM system_message (sözleşme metni)
    spec.py         # SENSE, penalty ölçeği, dosya formatı sözleşmesi
  mmkp/ ...         # P2
data/
  kofn/instances/   # instance dosyaları
  kofn/reference/   # yayınlanmış en iyi değerler — SANDBOX'A GİRMEZ
tests/              # her problem için pozitif + negatif kontroller
runs/               # koşu çıktıları (git'e girmez)
docs/
```

**Eklenti sözleşmesi** (her problem bunu sağlamak zorunda):

```python
SENSE: str            # "min" | "max"   <-- P1 MAX (güvenilirlik), CVRP MIN
parse_instance(path) -> Instance          # bozuksa InstanceFormatError raise
evaluate_text(instance, text) -> verdict  # ÇÖZÜM TARAFI ASLA RAISE ETMEZ
penalty_scale(instance) -> float          # instance'tan türetilir, sabit değil
```

`verdict` şeması cvrp-discovery ile aynı tutulur (araç zinciri değişmesin):

```python
{"feasible": bool, "cost": <int|float>, "violations": {...},
 "fitness": float, "eval_ms": int, "info": {...}}
```

### Taşınan tasarım kararları (cvrp-discovery'de bedeli ödenmiş)

- **`fitness` ≠ `cost`.** `fitness` evrim için (cezalı), `cost` rekor iddiası
  için (yalnızca `feasible=True` iken). Karıştırılmaz.
- **Solver'ın raporladığı değere GÜVENİLMEZ.** Her şey ham instance'tan
  yeniden hesaplanır. Solver "Cost 12345" yazarsa yok sayılır (ama
  `info.reported_cost_matches` olarak kaydedilir — sessiz bir dürüstlük
  sensörü, cvrp-discovery'de işe yaradı).
- **Ceza ölçeği instance'tan türetilir**, öyle ki *hiçbir ihlal kârlı
  olamaz*. CVRP'de bbox köşegeni kullanıldı. P1'de MAX yönlü olduğu için
  ceza fitness'ı **aşağı** çeker; ölçek: bütçe ihlali başına
  `2 * (R_max - R_min)` mertebesi + sabit taban → gerekçesini
  `objective.py` docstring'ine yaz (cvrp-discovery'deki gibi).
- **`SENSE` dönüşümü tek yerde.** OpenEvolve **maksimize eder**:
  `combined_score = -fitness` (min problem) / `+fitness` (max problem).
  Bu işaret hatası sessizce evrimi tersine çevirir → `harness/score.py`
  için ilk yazılacak test bu.
- **Referans/BKS değerleri solver'a SIZDIRILMAZ.** `data/*/reference/`
  adaptörden okunmaz; yalnızca insanın raporlama adımında kullanılır.

## 4. P1 — weighted k-out-of-n:G: bilinmesi gerekenler

**Problem:** n pozisyonlu sistem; her pozisyona bir bileşen *tipi* atanır
(farklı güvenilirlik / maliyet / ağırlık). Sistem, çalışan bileşenlerin
ağırlık toplamı ≥ k ise çalışır. Karar: hangi pozisyona hangi tip + kaç
yedek. Amaç: maliyet/ağırlık bütçesi altında sistem güvenilirliğini
**maksimize** etmek.

**Neden bu harness için ideal:** güvenilirlik hesabı ağırlıklar üzerinden
DP ile *kapalı formda ve kesin*. Yani evaluator matematiksel olarak
doğrulanabilir — CVRP'de mesafe toplamına güvenmek zorundaydık, burada
küçük n için **exhaustive enumeration ile ground truth optimum** var.

**Kritik enstrüman kararı:** güvenilirlik bir float. Kayan nokta
toplamı platform/derleyici duyarlı olabilir; literatür 6 hane veriyor.
Bu yüzden **doğrulama hesabı `fractions.Fraction` ile tam rasyonel
yapılır** (bileşen güvenilirlikleri 0.80, 0.85 gibi ondalıklar → tam
kesire çevrilebilir). Evrilen solver float kullanabilir; evaluator kesin
aritmetikle yeniden hesaplar. Karşılaştırma: 6 haneye yuvarlanmış değer
+ 1e-9 tolerans. **Bu, "float mesafe toplanmaz" kuralının P1 karşılığıdır.**

**Kalibrasyon (Faz 0 karşılığı, atlanmaz):**
- Klasik **Fyffe–Hines–Lee / Nakagawa-Miyazaki 33 instance** seti: exact
  optimumları artık **tamamen biliniyor** (Caserta & Voß, EJOR **2015**,
  DOI 10.1016/j.ejor.2015.01.008; açık sertifikasyon Yeh arXiv:2204.04472).
  Bu set **pozitif kontrol** görevi görür (cvrp-discovery'de X-n101-k25
  neyse o): headroom yok, ama evaluator'ün doğruluğunu bire bir kanıtlar.
  Dikkat: bu set seri-paralel RAP'tır, weighted k-out-of-n DEĞİL —
  eklenti ayrımı için bkz. `docs/p1-problem-tanimi.md` §4.
- **Headroom, Tütüncü'nün 2025 C&IE makalesindeki *çok tipli ağırlıklı*
  varyantta**: yayınlanmış benchmark seti YOK. Instance setini kendimiz
  üretiriz, küçük n'de enumeration ile optimum alırız, büyük n'de evrilen
  sezgiseli onun yayınladığı yönteme karşı raporlarız.
- ⚠ durumu (2026-08-03 araştırmasıyla; ayrıntı `docs/p1-problem-tanimi.md`):
  - **KAPANDI:** 33 instance verisi → `data/kofn/reference/verify_fyffe.py`
    (Fraction ile 33/33 doğrulandı); optimum değerler →
    `data/kofn/reference/optima_rap33.csv` (Yeh BRB 11 hane + IJMEMS 6 hane
    çaprazı, 0 çelişki). "Optimum" etiketi alt-sistem başına ≤8 bileşen
    konvansiyonuna bağlı — spec.py'ye yazılacak.
  - **KAPANDI (2026-08-03):** 2025 makalesinin tam kısıt kümesi — PDF elde
    edildi (`data/kofn/reference/sources/ozkut_tutuncu_2025.pdf`).
    Formülasyon `docs/p1-problem-tanimi.md` §1'de; sayısal tablolar
    `data/kofn/reference/verify_ozkut2025.py` ile Fraction'la doğrulandı
    (29/32 satır birebir; 3 satır + Tablo 1'in bir kısmı makale baskı
    hatası olarak karakterize edildi — kalibrasyon hedefi bizim tam
    değerlerimizdir). Kritik: `Σn_j = n` kısıtı baskıda görünmez ama
    koddan doğrulandı. `objective.py` yazılabilir.

**Rekor iddiasının anlamı P1'de farklı:** klasik RAP'te rekor kapalı
(optimumlar biliniyor) → iddia "CVRPLIB'e gönderim" değil, "**evrilen
sezgisel, yayınlanmış metodun sonucunu şu instance ailesinde şu kadar
aştı**" olur. Bu bilimsel olarak daha zayıf değil; sadece iddia metni
farklı. Ayrıca alan uzmanı (Tütüncü) bağımsız doğrulama için doğal muhatap.

## 5. Döngü tarafı — cvrp-discovery'den birebir taşınacak ayarlar

Bunlar **öğrenilmiş dersler**, yeniden keşfetmek zaman kaybı. Kaynak:
`C:\kt\tcdd\cvrp-discovery\faz3\config.yaml` (salt okuma ile kopyala):

- `diff_based_evolution` — **tarihçe ve güncel durum.** cvrp-discovery'de
  `false` idi: Opus + `max_tokens` 8192'de diff output'u kesiliyor → yarım
  SEARCH/REPLACE bloğu → "No valid diffs found" → iterasyon eleniyordu.
  **GLM-5.2 + max_tokens 20000'de bu geçersiz** (2026-08-04 testi): diff
  output'u ~3400 token, 4 geçerli blok, parent'ta tam eşleşme, **4-5x kota
  tasarrufu** (full rewrite ~15000 vs diff ~3400 token/call). Bu yüzden
  `evolve/config.yaml`'da `true`'ya çevrildi. Geri alma: `false` + thinking
  kontrolü aynı kalır.
- `llm.timeout: 600` — **şart**. Opus tam-dosya üretimi 3-10 dk; 180 sn'de
  kesmek retry fırtınası yaratıyordu.
- `llm.max_tokens: 20000`, `max_code_length: 30000`, `temperature: 0.8`.
- `llm.api_base: http://localhost:8317/v1`, model `claude-opus-5`,
  api_key env'den (`run.ps1` cli-proxy-api config'inden okuyor — **key repoya
  yazılmaz**).
  **GLM'e taşındı (2026-08-04):** Claude kotası bitti; Faz E döngüsü artık
  `http://localhost:8318/v1` + model `glm-5` (upstream `glm-5.2`, z.ai Coding
  Plan Lite). `run.ps1` `config.glm.yaml`'dan okuyor. Yukarıdaki diğer §5
  ayarları (timeout 600, max_tokens 20000, temperature 0.8,
  diff_based_evolution: false, population/archive/island) modele bağlı değil,
  aynen geçerli. Geri dönmek için: `evolve/config.yaml`'da api_base→8317,
  model→`claude-opus-5`; `run.ps1` path→`config.yaml`.
  **GLM thinking KAPALI (2026-08-04) — zorunlu:** GLM-5.2 OpenAI-tarzı
  reasoning modeli; `max_tokens` bütçesini `reasoning_tokens`'dan düşer.
  Zor promptta (kofn) TÜM bütçeyi thinking'e yiyip `content=""` üretir
  (`finish_reason: length`); OpenEvolve yalnız `message.content` okur
  (`openevolve/llm/openai.py:228`, `reasoning_content`'i yok sayar) →
  "No valid code found in response". Empirik testle doğrulandı: baseline
  `reasoning=8000, content_len=0` (147 s, bozuk) vs `thinking:{type:disabled}`
  `reasoning=0, content_len=6207` (22 s, çalışır). Düzeltme: cli-proxy
  `config.glm.yaml`'da `payload.override` (protocol `openai`, model `glm-*`,
  `thinking: {type: disabled}`) — OpenEvolve koduna dokunmadan proxy
  seviyesinde. Thinking açmak istenirse o blok silinir. Duman testi (5 iter)
  bu configle yeşil: 5/5 geçerli kod, MAP-Elites hücreler doluyor; ilk
  nesiller infeasible (normal), tohum skoru (0.3911) korundu.
- `prompt.include_artifacts: true` — stderr + violation özeti LLM'e döner;
  "neden kötüydü" bilgisi mutasyon kalitesini artırıyor.
- `database`: population 200, archive 50, 4 island, elite 0.1 / exploration
  0.2 / exploitation 0.7.
- `evaluator.timeout` solver limitinin üstünde tampon bırakır
  (CVRP'de 55 s solver / 90 s evaluator).
- `run.ps1` deseni: **döngüden önce `pytest` koşar, kırmızıysa başlatmaz.**
  Bu guardrail aynen korunur.
- Referans adaptör: `C:\kt\tcdd\cvrp-discovery\faz3\evolve_evaluator.py`
  (ayrı process, tempdir cwd, timeout → deterministik kötü skor,
  `combined_score = -fitness`, artifact geri besleme).

**Bilinen sınır (devralınıyor):** Windows'ta subprocess için ağ/bellek
izolasyonu OS düzeyinde zorlanmıyor. Tek kullanıcılı yerel makinede kabul
edilen risk; Docker'lı koşuma taşınabilir. Raporda not edilir.

## 6. Faz planı (bu depo)

- [x] **Faz A — İskelet + sözleşme testi.** `harness/score.py` +
      `registry.py`; ilk test `SENSE` işaret dönüşümü (min/max). ✓ 2026-08-03.
- [x] **Faz B — P1 enstrümanı (TDD).** `problems/kofn/`: parser (io.py),
      Fraction'lı Teorem 1 (objective.py), feasibility + ceza (spec.py).
      Pozitif kontrol: Ozkut-Tütüncü tablo değerleri (verify_ozkut2025.py
      ile çapraz doğrulanmış). Negatif kontroller: parse_error / wrong_total /
      negative_count / budget_exceeded → doğru violation koduyla;
      evaluate_text asla raise etmez; her infeasible < her feasible testi.
      ✓ 2026-08-03. (RAP-33 pozitif kontrol eklentisi ayrı karar —
      docs/p1-problem-tanimi.md §4.)
- [x] **Faz C — Ground truth ölçümü.** `problems/kofn/enumerate.py`:
      tüm tahsisleri sayarak kanıtlı optimum (deterministik tie-break).
      Kanıt kuruldu: enumerator, yayınlanmış Tablo 6 optimumlarını
      (doymamış satırlar dahil) bağımsız olarak yeniden buldu; makalenin
      iki bozuk satırının gerçek optimumları da testlerde sabitlendi.
      ✓ 2026-08-03.
- [x] **Faz D — Tohum solver + baseline.** `problems/kofn/seed_solver.py`
      (oran-greedy kurulum + hill-climb, anytime), `generate.py` (tohumlu
      üreteç, kuantil-K), `baseline.py` (gap tablosu). Sonuç:
      `docs/faz-d-baseline.md` — tohum, enumere edilebilir 11 instance'ın
      11'inde kanıtlı optimumda; büyük katmanda (n=60-200, küratörlü)
      R ≈ 0.39-0.54 → evrimin keşif alanı. ✓ 2026-08-03.
- [ ] **Faz E — Döngü.** §5 ayarlarıyla OpenEvolve. **Gece koşusu bittikten
      sonra.** Duman testi 5 iterasyon, sonra uzun koşu.
      **Hazırlık TAMAM (2026-08-03):** `harness/runner.py` (ayrı process,
      timeout, kısmi-çıktı kurtarma) + `harness/evolve_evaluator.py`
      (probleme-agnostik adaptör; problem/instance env'den:
      `DISCOVERY_PROBLEM`, `DISCOVERY_INSTANCE`, `DISCOVERY_SOLVER_TIMEOUT_S`)
      + `evolve/config.yaml` (§5 ayarları + kofn sözleşme prompt'u) +
      `evolve/run.ps1` (pytest gate + `-GeceKosusuBitti` guard'ı).
      Adaptör tohum solver'la uçtan uca doğrulandı (LLM'siz); openevolve
      0.3.2 kurulu. Duman testi: `.\evolve\run.ps1 -GeceKosusuBitti
      -Iterations 5`.
      **GLM'e taşındı (2026-08-04):** Claude kotası bitti → döngü artık
      8318/GLM Coding Plan Lite (z.ai). Önce ikinci cli-proxy container'ını
      ayağa kaldır (bkz. §0 / §5). **Açık doğrulama adımı:** döngüyü başlatmadan
      önce `curl -s http://localhost:8318/v1/models` ile `glm-5` alias'ını ve
      upstream model adını teyit et; Coding Plan'ın haftalık kredi limiti
      yoğun OpenEvolve çağrılarıyla hızlı tükenir (pacing kararı).
      **Gradyan tamiri (2026-08-05, docs/faz-e-gradyan.md):** ilk 50-iter
      koşu düz çizgiydi — hedef instance'ta headroom=0 (tohum zaten yerel
      tavandaydı). Düzeltme: headroom turnusolu (`refsearch.py`; kural:
      headroom≈0 instance evrim hedefi olamaz), "sert" üreteç profili
      (oran-aldatmalı plato yapısı) ve küratörlü 3-instance hedef seti +
      adaptörde `;` ayraçlı çoklu-instance fitness (ortalama). Tohum
      ZAYIFLATILMADI (strawman baseline reddedildi). Tohum set ortalaması
      0.160; kanıtlı optimumlar 0.88/0.77/0.78.
      **Benchmark-v2 dilimi (2026-08-05):** router-n500 genelleme açığı
      (docs/benchmark-v1.md bulgu 3) için büyük-n fitness seti. Eğitim
      instance'ları benchmark v1'den AYRIK tohumlarla (v1 holdout kalır):
      `train-router-n500-m12-s7` (tek gradyan kaynağı; evrilen 0.332 <
      tohum 0.407) + `train-enerji-n300-m10-s14` ve `train-router-n20-m4-s10`
      (regresyon bekçileri; evrilen tavanda: 1.000 / kanıtlı opt 0.6633).
      Başlangıç genomu = `evolve/artifacts/best_20260805.py`
      (`run.ps1 -InitialProgram`). Kürasyon bulgusu: üreteç bütçeyi tabana
      (n·min_cost) sabitleyebiliyor → tek fizibil tahsis, R sabit
      (enerji-n300 s8/s15 dejenere) — v2 kuralı: **bütçe boşluğu
      budget/(n·min_cost) > 1 şart**, instance kabulünden önce kontrol et.
      Duman testi 5/5 yeşil; başlangıç set skoru 0.6651 (öngörüyle birebir),
      iter 2'de +0.0249. 50-iter koşu: `runs\evolve\bench-v2-dilim1`.
      **SONUÇ (2026-08-05, docs/benchmark-v2.md):** set skoru 0.6900'de
      plato (n500-s7 slotu tohum seviyesine geldi); asıl kazanç holdout'ta —
      v1 ailesinde `evolve/artifacts/best_v2_20260805.py`: router-n500-s1
      0.652 → **1.000000** (tohum 0.9738'i de geçti), küçük katman 8/8
      kanıtlı optimum korundu, enerji kazanımları korundu; tek gerileme
      router-n300'de −0.0058. Genelleme açığı kapandı, portföy ihtiyacı
      kalktı. Yapısal fark: K-kesimli absorbing konvolüsyon DP (O(K)).
      `benchmark_eval` CLI varsayılanı artık 3 kolon (tohum/v1/v2).
- [ ] **Faz F — P2 (MMKP).** Harness'ın agnostikliğinin sınavı: yeni problem
      `harness/` içinde **tek satır değişiklik olmadan** eklenebilmeli.
      Eklenemiyorsa çekirdek sızdırıyor, düzelt.
- [ ] **Faz P4 — capset (GLM eliyle, 2026-08-06).** Ödüllü/açık matematik
      problemi denemesi: F₃ⁿ cap set (FunSearch emsali). Kendi başına
      yeterli talimat: `problems/capset/CLAUDE.md`. Claude kotası tasarrufu
      için bu faz GLM'e devredildi; F/G sırasını değiştirmez, `harness/`
      çekirdeğine dokunmama kuralı Faz F sınavı yerine de geçer.
- [ ] **Faz G — P3 (HFFVRP-B).** cvrp-discovery evaluator'ünü KOPYALA,
      heterojen filo (tip başına kapasite + sabit maliyet) ve backhaul
      öncelik kısıtını ekle. ⚠ **Yuvarlama sözleşmesi DOĞRULANACAK**:
      X-serisi NINT kullanıyordu, Taillard heterojen filo instance'ları
      büyük olasılıkla **gerçek değerli Öklid** kullanıyor. Referans çözümle
      kalibre etmeden tek satır yazma — bu, CVRP'de bire bir tutan kontrolün
      buradaki karşılığı.

## 7. Doğrulanmış profil bilgisi (yeniden taramaya gerek yok)

Kaynak: [Google Scholar profili](https://scholar.google.com/citations?user=1AsbPe4AAAAJ&hl=tr)
(CAPTCHA'yı insan geçti; 2010 öncesi kayıtlar [DBLP](https://dblp.org/search?q=Yazgi+Tutuncu)
ile tamamlandı). **G. Yazgı Tütüncü**, Matematik Bölümü, İzmir Ekonomi
Üniversitesi. 454 atıf, h-index 12, i10 12. Kendi etiketleri: heuristic
methods for optimization, fuzzy classification, reliability analysis,
real-life optimization. Eş yazarlar arasında **Said Salhi** (Kent, VRP),
**Serkan Eryılmaz** (güvenilirlik), Fatih Kocatürk, Alejandra Duenas,
Linda L. Zhang.

İlgili yayınlar:
- *Reliability analysis and optimization problems for a weighted-k-out-of-n:
  G system with multiple types of components* — Ozkut & Tutuncu, Computers &
  Industrial Engineering, 2025. ← **P1'in hedef makalesi**
- ~~*On weighted-k-out-of-n: G systems with multiple types of components*
  (2024)~~ ⚠ ayrı yayın olarak DOĞRULANAMADI (Crossref/DBLP/OpenAlex/İEU
  deposunda yok; muhtemelen Scholar hayaleti ya da Hamdan–Asadi–Tavangar
  QTQM 21(5) ile karışma — bkz. docs/p1-problem-tanimi.md §1)
- *Signature based reliability analysis of repairable weighted k-out-of-n: G
  systems* — IEEE Trans. Reliability 65(2), 2015 (42 atıf)
- *Reliability of weighted k-out-of-n: G systems … cold standby component* —
  Comm. Stat. Simul. Comp. 46(5), 2017 (21 atıf)
- *The multi-depot heterogeneous VRP with backhauls: … hybrid VNS with GRAMPS*
  — Annals of OR 307(1) 277-302, 2021 (19 atıf) ← **P3 hedef tablosu**
- *An interactive GRAMPS algorithm for the heterogeneous fixed fleet VRP with
  and without backhauls* — EJOR 201(2), 2010 ← **P3 hedef tablosu**
- *A multidimensional multiple-choice knapsack model … evolutionary
  algorithm* — APMS 2014 ← **P2 bağlantısı**

Benchmark kaynakları (başlangıç noktası; §4'teki ⚠ maddeleri hâlâ geçerli):
- RAP exact optimumlar: [Caserta & Voß, EJOR 2015](https://www.sciencedirect.com/science/article/abs/pii/S0377221715000284)
  (paywall; açık sertifikasyon [Yeh arXiv:2204.04472](https://arxiv.org/pdf/2204.04472)
  → `data/kofn/reference/optima_rap33.csv`)
- RAP 33 instance verisi + metasezgisel karşılaştırma:
  [Liang & Smith](https://www.eng.auburn.edu/~smithae/files/cec99yc.pdf),
  [Coit & Smith](https://www.eng.auburn.edu/~smithae/files/compie.pdf)
- Heterojen filo VRP derlemesi + instance geçmişi:
  [Koç & Bektaş, Thirty years of heterogeneous VRP](https://eprints.soton.ac.uk/378863/1/ThirtyYears.pdf)
- Taillard VRP instance'ları: `http://mistic.heig-vd.ch/taillard/problemes.dir/vrp.dir/vrp.html`
- ⚠ MMKP benchmark seti (Khan / Hifi instance'ları) **DOĞRULANMADI** — P2'ye
  geçmeden önce teyit et.

## 8. Guardrail'ler (cvrp-discovery'den devralındı, geçerliliğini korur)

- Reward hacking varsayılan tehdittir: evaluator paranoyak, solver yaratıcı.
- "Rekor"/"aştı" iddiası yalnızca cezasız, tam feasible, kanonik hedefle.
- Evaluator'de bug şüphesi → döngü durdurulur, önce enstrüman düzeltilir.
- Süre-bütçeli (anytime) solver'lar makine yüküne duyarlı: iddia öncesi
  **DAİMA sakin makinede bağımsız re-run + evaluator doğrulaması**.
- Goodhart notu: benchmark objective'i ≠ gerçek problem. P1'de "en yüksek
  güvenilirlik" ölçülüyor; bakım maliyeti, tedarik gerçekliği, arıza
  korelasyonu ölçülmüyor — objective'i yazan bunu belgelemek zorunda.
- **Bu dosyayı gerçek komutlar ve dizin yapısı oluştukça güncelle. Uydurma
  komut yazma; yalnızca fiilen çalışanı belgele.** (Aşağıdaki bölüm bu
  kuralın gereğidir.)

## 9. Komutlar

Depo kökünden (Python 3.14, pytest 9 ile doğrulandı):

```bash
python -m pytest tests/ -q
```

Mevcut kapsam: `harness/score.py` (SENSE işaret dönüşümü),
`harness/registry.py` (eklenti yükleme + sözleşme doğrulama) ve
`problems/kofn` (parser, Fraction'lı Teorem 1, verdict, negatif kontroller,
registry entegrasyonu) testleri. Referans doğrulamaları:

```bash
python data/kofn/reference/verify_fyffe.py
```

```bash
python data/kofn/reference/verify_ozkut2025.py
```

Kanıtlı optimum (küçük instance, exhaustive enumeration):

```bash
python -m problems.kofn.enumerate data/kofn/instances/router-n10-k20.kofn
```

Adaptör duman kontrolü (LLM'siz, döngüsüz; bash sözdizimi):

```bash
DISCOVERY_PROBLEM=kofn DISCOVERY_INSTANCE=data/kofn/instances/router-n10-k20.kofn python harness/evolve_evaluator.py problems/kofn/seed_solver.py
```

GLM cli-proxy container'ını ayağa kaldırma (Faz E döngüsü bunu kullanır;
`C:\kt\upwork\cli-api` altında, Claude OAuth container'ından ayrı):

```bash
# 1. config.glm.yaml içindeki iki placeholder'ı doldur:
#    - REPLACE_WITH_CLI_PROXY_CLIENT_KEY (istemci doğrulaması; run.ps1 okur)
#    - REPLACE_WITH_GLM_CODING_KEY       (z.ai Coding Plan API key)
# 2. Container'ı başlat:
docker compose -f docker-compose.glm.yml up -d
# 3. Model listesini doğrula (glm-5 alias görünmeli):
curl -s http://localhost:8318/v1/models
```

Instance üretimi (deterministik; son argüman profil: `standart`|`sert`)
ve baseline gap tablosu:

```bash
python -m problems.kofn.generate 15 3 1 data/kofn/instances/gen-n15-m3-s1.kofn
```

```bash
python -m problems.kofn.generate 20 4 1 data/kofn/instances/gen-sert-n20-m4-s1.kofn sert
```

Benchmark v1 değerlendirmesi (İz-2 yayın paketi; LLM'siz; sonuç:
docs/benchmark-v1.md):

```bash
python -m problems.kofn.benchmark_eval rapor.md
```

Headroom turnusolu (kurasyon kuralı: headroom≈0 → evrim hedefi olamaz):

```bash
python -m problems.kofn.refsearch data/kofn/instances/gen-sert-n20-m4-s1.kofn
```

```bash
python -m problems.kofn.baseline rapor.md
```

Referans olarak cvrp-discovery'de **fiilen çalışan** komutlar:

```bash
python -m pytest tests/ -q
```

```bash
python -m evaluator.evaluate <instance.vrp> <solution.sol>
```

## 10. İlk oturum için önerilen başlangıç komutu

"§0'ı oku ve uy: cvrp-discovery'ye dokunma, CPU-yoğun iş koşturma. Faz A'yı
yap: `harness/score.py` + `registry.py` iskeletini ve `SENSE` (min/max)
işaret dönüşümünün testini TDD ile yaz. Sonra Faz B için P1'in kısıt
kümesini netleştir: §4'teki ⚠ DOĞRULANACAK maddelerini (33 instance verisi,
Caserta & Voß tabloları, 2025 makalesinin formülasyonu) araştır ve bulgularını
`docs/p1-problem-tanimi.md` olarak yaz — formülasyon netleşmeden
`objective.py` yazma."
