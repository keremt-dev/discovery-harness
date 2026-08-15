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
   **Üçüncü proxy (2026-08-07):** **8319 / `config.kimi.yaml`** → Kimi/
   Moonshot PAYG ($15 bakiye; `docker compose -f docker-compose.kimi.yml
   up -d`). Doğrulandı: upstream modeller kimi-k2.6 / kimi-k2.7-code(-highspeed)
   / kimi-k3; alias `kimi`→kimi-k3, `kimi-code`→kimi-k2.7-code; duman çağrısı
   yeşil. ⚠ K3 reasoning modeli: küçük max_tokens'ta content boşalıyor
   (GLM hastalığının aynısı, ölçüldü); `thinking:{type:disabled}` Moonshot'ta
   çalışıyor (ölçüldü) — override AKTİF (2026-08-07: 20k bütçede bile
   content boşaldı; thinking-kapalı modda temperature=0.6 ZORUNLU, açıkken
   1.0). k2.7-code ELENDİ: thinking kapatılamıyor, 20k'nın 19.5k'sı
   reasoning'e gitti (ölçüldü). Gerçek tarife: K3 çıktı $15/M, k2.7-code
   $4/M — ama K3+thinking-off yalnız içeriğe ödediği için etkin maliyet
   daha düşük (~$0.10/çağrı, kampanya ~$200 mertebesi; eski "$80" notu
   yanlıştı). Amaç: ikinci motor + Kimi Ambassador başvurusuna somut
   entegrasyon kanıtı (`outreach/` notları; repo'ya girmez).
   **Duman testi YEŞİL (2026-08-07, `runs\evolve\capset-kimi-smoke4`):**
   5/5 iterasyon geçerli kod; iter 2'de yeni en-iyi 0.2996→0.3419 (+0.0432,
   ort. |S| 146→200); iterasyon ~200-245 sn (LLM ~60-90 sn); maliyet ~$0.5.
   Koşu reçetesi: `run.ps1 -ConfigPath evolve\config.capset.kimi.yaml
   -ProxyConfig config.kimi.yaml` + `CAPSET_SEED_TIME_S=50` (config'te
   temperature 0.6 ZORUNLU — thinking-off modunun kuralı).
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
   **Port tamiri (2026-08-14):** reboot sonrası host portu 51821,
   WinNAT hariç-tutma aralığına düştü (54545 vakasının aynısı) ve
   Docker konteynerin TÜM port forward'larını sessizce kurmadı —
   belirti: 8317 "connection refused" ama konteyner içi loglar
   sağlıklı; teşhis: `netstat`'ta 8317 dinleyicisi yok +
   `netsh int ipv4 show excludedportrange`. Düzeltme: compose'ta
   51821→41821 (yedek: `docker-compose.yml.bak-20260814`) +
   force-recreate. İKİ yan etki: (a) recreate `:latest` çekti (imaj
   2026-08-14) — claude yoluna güvenmeden önce §0'daki replika-istek
   kontrolünü tekrarla; (b) Claude OAuth refresh token invalid_grant
   veriyor → Opus/thinking (8317/8320, auths paylaşımlı) kullanılmadan
   önce `claude-login.ps1` + `docker restart cli-proxy-api` şart.
   GLM (8318) API-key'li, etkilenmez. **Tailscale erişimi (2026-08-14):**
   üç proxy portu uzak koşu makinesinden (100.73.210.41) host IP
   100.125.104.107 üzerinden uçtan uca doğrulandı — evolve döngüsü
   uzakta koşacaksa api_base bu IP'ye çevrilir
   (docs/uzak-kosu-kurulumu.md Faz 2).
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
  **GLM-5.3 güncellemesi (2026-08-14):** z.ai, Coding Plan'da glm-5.2
  isteklerini SESSİZCE glm-5.3'e yönlendirmeye başladı (yanıtta
  `"model":"glm-5.3"`) ve 5.3'te düşünme ZORUNLU:
  `thinking:{type:disabled}` artık yok sayılıyor,
  `enable_thinking:false` açık hata veriyor ("cannot be disabled;
  please use low, high, or max"). Eski override bu yüzden İŞLEMEZ
  oldu (GLM yolu fiilen kırılmıştı). Çalışan tek kapatma:
  **`reasoning_effort: "minimal"`** (empirik: reasoning=0,
  content dolu, finish=stop; "minimal" hata listesinde yazmasa da
  kabul ediliyor). `config.glm.yaml` payload.override buna çevrildi
  (yedekler: `config.glm.yaml.bak-20260814` = 5.3 alias öncesi,
  `bak2-20260814` = override değişikliği öncesi) + `glm-5.3` alias'ı
  eklendi (`glm-5` alias'ı provenans için upstream adı glm-5.2'de
  bırakıldı — zaten 5.3 servis ediliyor). Proxy'den iki alias da
  doğrulandı: reasoning≈0, content OK. Thinking-AÇIK GLM deneyi
  istenirse: override'a takılmayan ayrı bir alias + effort
  low/high/max + büyük max_tokens gerekir (yapılmadı).
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
- [ ] **Faz P5 — covering design (2026-08-09).** (v,k,t) covering: minimum
      blok sayısı; LJCR arşivi hedef tablosu (arşiv dondu 2026-03-01; canlı
      skorbord coveringrepository.com). **Faz B enstrümanı TAMAM:**
      `problems/covering/` — SENSE=max, feasible fitness =
      Schönheim(v,k,t)/|B| ∈ (0,1] (kanıtlı optimal ⇒ 1.0 tavan; teorem
      normalizer, sızıntı yok), infeasible [-2,-1] bandı (capset deseni);
      WORK_CAP/EXAMPLE_CAP ile evaluator hiçbir girdiyle takılmaz.
      50 covering testi + tam süit 239/239 yeşil; `harness/` içinde sıfır
      değişiklik (Faz F sınavı bir kez daha geçti). **Kürasyon:**
      `data/covering/reference/curate_targets.py` → `targets.csv`
      (8759 hücre; 4115 eligible; 1128 sweet). **Kalibrasyon:**
      `verify_ljcr.py` — I1 (Schönheim ≤ low_bd) + I2 (low_bd ≤ size) +
      T1 (Fort–Hedlund: 96/96 k=3,t=2 hücresi size=Schönheim) SERT temiz;
      196 I3 tarihçe-hijyen bulgusu (rekor kıyası DAİMA `size` alanına).
      Hedefler + iddia uyarıları: `data/covering/reference/hedef-notlari.md`
      (gradyan: C(32,8,4) 620/lb552, C(24,6,4) 784/lb720, C(28,9,3) 56/lb50 —
      üçü de 1996'dan beri dokunulmamış; bekçi: Fano, STS(13)).
      **Faz C TAMAM (2026-08-09):** `problems/covering/enumerate.py` —
      iterative deepening (Schönheim tabanı) + ilk-kapsanmamış-altküme
      dallanması + ceil(uncovered/C(k,t)) budağı; leksikografik-ilk çözüm
      deterministik; kapsam ENUM_CAP=1e5 (C(v,k), C(v,t)). Kanıtlar:
      9 arşiv-kanıtlı hücre birebir (Fano 28 düğüm; C(7,4,3): Schönheim
      11 fiilen çürütülüp 12 kanıtlandı, 450k düğüm/526ms; bekçi
      C(13,3,2)=26 kendi enstrümanımızca 14ms'de kanıtlı); evaluator
      çaprazı: enumerate çıktısı = evaluate_text feasible + tavan 1.0.
      24 enumerate testi; covering toplam 74 test yeşil.
      **Faz D TAMAM (2026-08-09):** `problems/covering/seed_solver.py` —
      greedy kurulum (SAMPLE_CANDIDATES=8 örneklenmiş aday paneli; tam
      max-gain taraması büyük hücrede Python'da onlarca sn sürer, bilinçli
      hız/kalite dengesi) + redundancy removal + ruin-and-recreate;
      anytime + atomik yazım, kısmi yazım PARTIAL_WRITE_EVERY=50 blokta
      (erken timeout'ta gradyanlı infeasible çıktı kalır);
      `COVERING_SEED_TIME_S` (default 10). `baseline.py` raporu
      (docs/faz-d-covering-baseline.md, 15 sn bütçe): bekçiler kanıtlı
      optimumda (7/7, 26/26 — tavan 1.0 çalışıyor); hedeflerde tohum
      arşivin ÇOK gerisinde: C(24,6,4) 1213/784 (+429), C(28,9,3) 91/56
      (+35), C(32,8,4) 1269/620 (+649). **Headroom KANITLI** — arşiv
      değeri ulaşılabilirlik sertifikası (o boyutta covering fiilen var).
      Covering test toplamı 85 yeşil. **Faz E başladı (2026-08-09):**
      motor = GLM 8318 (kullanıcı seçimi; Opus plato kartı olarak saklı),
      kapsam = duman 5 iter → kısa koşu 50 iter. Config:
      `evolve/config.covering.yaml` (diff true, GLM ölçümüne dayalı;
      system_message'ta arşiv değeri YOK). Fitness seti: v28+v32 (gradyan)
      + v13 (bekçi); **HOLDOUT: v24 + v7 — döngü asla görmez**, genelleme
      iddiası ancak holdout yeniden değerlendirmesiyle. Reçete:
      `$env:COVERING_SEED_TIME_S="50"` ŞART (genom bütçeyi env'den okur;
      set edilmezse 10 sn'de durur). LLM'siz adaptör kontrolü yeşil:
      set skoru 0.6324 (3 sn bütçeyle; yenilecek taban).
      **Duman testi YEŞİL (2026-08-09, runs\evolve\covering-glm-smoke1):**
      tohum (50 sn bütçe) 0.6366; iter 5'te yeni en iyi **0.6725**
      (+0.0359; ort. blok 460→404.7, 3/3 feasible). ⚠ diff kaybı 3/5
      ("No valid diffs") — capset ölçümü %16 idi; 50'lik koşu gerçek
      oranı ölçer, >%40 çıkarsa uzun koşuda full-rewrite'a dön.
      Tamamlanan iterasyon ~180-195 sn (solver 150 sn + LLM); başarısız
      diff iterasyonu ~12-60 sn.
      **Kısa koşu SONUÇ (2026-08-09, runs\evolve\covering-glm-50):**
      diff kaybı 7/50 = %14 (capset %16 ile tutarlı — duman 3/5 örneklem
      gürültüsüydü; diff modu KALIR). 43 iterasyon tamam, 4 yeni en iyi:
      0.6366 → **0.6798**. Per-instance (50 sn bütçe): v28 91→**82**,
      v32 ~1269→**1072**, v13 26 (bekçi tavanda). **HOLDOUT genelleme
      DOĞRULANDI:** v24 (döngü hiç görmedi) tohum 1198 → evrilen **1067**
      (−131 blok, skor 0.6010→0.6748); v7 ikisi de kanıtlı optimum 7.
      Arşive uzaklık (rekor hedefi): v28 82/56, v32 1072/620, v24
      1067/784 — 50 iterde açığın ~%15-20'si kapandı, rekor için uzun
      koşu + muhtemelen simetri/döngüsel konstrüksiyon sıçraması gerekir.
      Checkpoint: `runs\evolve\covering-glm-50\checkpoints\checkpoint_50`.
      **Dilim-2 SONUÇ (2026-08-09→10):** PLATO — 94 iter tamam, diff
      kaybı 6/100 (%6), SIFIR yeni en iyi; en iyi hâlâ iter-28 (0.6798),
      9 program aynı skora geri döndü (popülasyon yakınsamış). Genom
      analizi: evrim CYCLIC KONSTRÜKSİYONU KEŞFETTİ (_cyclic_blocks,
      _multi_cyclic_blocks, iki fazlı strateji, panel 8→24) ama SIĞ:
      MULTI_BASE_MAX=2 — v32'de 620 blok ~20 orbit ister, 2 tabanla
      imkânsız. Doğru fikir, yetersiz derinlik → yapısal sıçrama gerek.
      **Dilim-3 OPUS PLATO KARTI — BAŞARILI (2026-08-10):**
      checkpoint_150'den +25 iter, `evolve/config.covering.opus.yaml`
      (8317/claude-opus-5, full-rewrite). 25/25 geçerli kod (sıfır hata);
      plato kırıldı: 0.6798 → 0.7011 (iter ~155) → **0.7017** (iter 169).
      Yapısal sıçrama: genom 374→606 satır — delta-değerlendirmeli
      ELEMAN TAKASI yerel araması (_swap_ids/_delta/_apply + _random_kick),
      t-altküme indeks sınıfı, tam büyütmeli greedy; cyclic hâlâ sığ
      (MULTI_BASE_MAX=3). Per-instance (50 sn): v28 82→**74**, v32
      1072→**1055**, v24 HOLDOUT 1067→**1048**, bekçiler tavanda.
      Checkpoint: checkpoint_175. Gidişat: tohum→şimdi v28 91→74 (arşiv
      56), v32 1269→1055 (arşiv 620 — hâlâ büyük açık; çok-orbitli cyclic
      sıçraması gerekecek gibi), v24 1198→1048 (arşiv 784). Rekor eşiği
      geçilirse sakin-makine re-run + coveringrepository.com çaprazı
      olmadan iddia YAZILMAZ.
      **Dilim-4 OPUS +25 — İKİNCİ SIÇRAMA GELDİ (2026-08-10):**
      checkpoint_175'ten, prompt'a orbit aritmetiği vurgusuyla. 25/25
      geçerli; yeni en iyi 0.7017 → **0.7064** (iter 189, genom 724
      satır). Yapı: `orbit_skeleton` — orbit'leri kapsama/blok oranına
      göre SINIRSIZ yığar (ORBIT_CAND=24 aday taban/seçim), kazanç <1
      blok başına düşünce hedefli yama. Per-instance: v32 1055→**1016**
      (kazanç tam hedefte), v24 HOLDOUT 1048→**1040**, v28 74 sabit,
      bekçiler tavanda. Gidişat özeti (tohum→200. iter): v28 91→74
      (arşiv 56, kalan açık 18), v32 1269→1016 (arşiv 620, kalan 396),
      v24 1198→1040 (arşiv 784, kalan 256). Checkpoint: checkpoint_200.
      **Dilim-5 V28 REKOR DENEMESİ (2026-08-10, KULLANICI ONAYIYLA):**
      TEK hücre C(28,9,3) (arşiv 56, bizde 74); Opus 5, bütçe 70 sn
      (COVERING_SEED_TIME_S=70), runner 80 sn (`run.ps1`e -SolverTimeoutS
      parametresi EKLENDİ, default 55 korunur), 50 iter. TAZE koşu
      (checkpoint devri YOK — instance seti değişince eski DB skorları
      karşılaştırılamaz olur; kofn bench-v2 deseni): başlangıç genomu =
      `evolve/artifacts/best_covering_gen200_20260810.py` (gen-200 en
      iyisi). Config: `evolve/config.covering.v28.opus.yaml` (tek-hücre
      SCALE metni, evaluator timeout 150). Çıktı:
      `runs\evolve\covering-v28-opus-record`. NOT: tek-hücre odak =
      genelleme iddiası YOK, yalnız rekor avı; genel çözücü hattı
      checkpoint_200'de duruyor.
      **Dilim-5 SONUÇ: ARŞİVLE EŞİTLİK (2026-08-10).** 39 iter tamam,
      0 kod hatası; eğri 74→72→61→**56** (0.7857 = 44/56); koşuda 4 kez
      cost=56 görüldü. Donmuş arşiv sayfası teyit: 50 ≤ C(28,9,3) ≤ 56 —
      yani 30 yıllık bilinen-en-iyiye EŞİTLENDİ; rekor için ≤55 şart.
      ⚠ VARYANS BULGUSU: en iyi genom seed-deterministik AMA anytime faz
      bütçeleri duvar saatinden pay aldığı için makine yüküne duyarlı —
      sakin makinede seed-0 yeniden koşumu 73 verdi (56'lık çözüm
      evaluator tempdir'inde kaybolmuştu). DERS: cost=56 gören evaluator
      anında çözümü SAKLAMALIYDIK; bundan sonra rekor koşularında çözüm
      artifact'ı kalıcı dizine kopyalanır. Kurtarma: 12-seed'lik 70 sn
      tarama (`runs\...\solutions\`). Rekor iddiası için ≤55 + sertifika
      + coveringrepository.com çaprazı gerekmeye devam ediyor.
      **Kurtarma + kalıcı düzeltme (2026-08-10):** 12-seed 70sn tarama
      en iyi 59 verdi (bant 59-73; seed-0 iki koşuda 73 ve 63 — duvar-
      saatli faz bütçeleri aynı seed'de bile tekrarlanabilirliği bozuyor,
      ölçüldü). Derin probe (300 sn, seed 1/2/9/0) ayrıca koşuldu.
      **ÇÖZÜM ARŞİVLEME KANCASI eklendi** (`harness/evolve_evaluator.py`
      `_archive_solution`, probleme-agnostik, env-kapılı, asla raise
      etmez): `DISCOVERY_ARCHIVE_DIR` + opsiyonel `DISCOVERY_ARCHIVE_
      BELOW`/`ABOVE` eşikleri; feasible çözüm <stem>-cost<X>-<sha1_8>.txt
      olarak kalıcılaşır (idempotent). 6 yeni test; adaptör 16/16.
      BUNDAN SONRA her rekor koşusu ARCHIVE_DIR + BELOW eşiğiyle açılır.
      **Kurtarma bilançosu (2026-08-10):** derin probe (300 sn) en iyi
      **57** (v28-deep-s0.txt — ELDEKİ EN İYİ KALICI SERTİFİKA; arşiv
      56'nın 1 üstü). Paralel-yük taklidi (8 eşzamanlı) yardım etmedi
      (en iyi 61) — "yük hipotezi" çürüdü, varyans saf piyango.
      Checkpoint DB taraması: cost=56 skorlayan TEK program var
      (2d077b78, best'in kendisi); log'daki 4 görünüm aynı
      değerlendirmenin echo'ları. Yani 56 tek şanslı çekilişti ve
      çözümü kaybedildi (kanca o yüzden yazıldı). Sonraki dilim
      checkpoint_50'den (record koşusu) ARCHIVE_DIR + BELOW=56 ile.
      **Dilim-6 OPUS +50 KANCALI — SONUÇ (2026-08-10):** arşive ≤56
      DÜŞMEDİ (piyango tekrar vurmadı); yeni en iyi yok (0.7857/56
      sabit); 36 iter tamam, **14 iter (%28) kod-boyu 30k sınırına
      kurban** (KULLANICI max_code_length'i 35k'ya çektirdi — üç
      covering config'inde de uygulandı; bu koşu eski sınırla koştu).
      İki hijyen düzeltmesi: (1) pytest kapısı arşiv env'lerini miras
      alıp test çözümlerini gerçek arşive yazmıştı — `run.ps1`de kapı
      öncesi env temizle/sonra geri koy eklendi, sızan dosyalar silindi;
      (2) 35k artık aktif. DURUM: kalıcı en iyi sertifika 57 blok
      (arşiv 56, lb 50); 56 bir kez gözlendi, kaybedildi; sonraki dilim
      35k ile o %28'lik israfı geri kazanır.
      **Dilim-7 GLM PİYANGO +100 (2026-08-10, KULLANICI PLANI: "önce
      GLM, olmazsa Opus +50'ye dön" — fallback ÖN-ONAYLI):**
      checkpoint_100'den; `evolve/config.covering.v28.glm.yaml` (8318,
      diff true, 35k); env: SEED_TIME 70, ARCHIVE_DIR + BELOW=56;
      -SolverTimeoutS 80. Başarısızlıkta (arşiv boş + yeni en iyi yok)
      Opus +50 dilimi sorulmadan başlatılır (kullanıcı ön-onayı).
      **Dilim-7 SONUÇ — EŞİTLEME KALICI (2026-08-10):** kanca ≤56'yı
      YAKALADI: `cover-v28-k9-t3-cost56-c155b2fe.txt`. 96 iter, 3 diff
      kaybı, 1 kod-boyu hatası (35k çalışıyor). Kesin doğrulama:
      3276/3276 kapsama, 56 blok, 0 ihlal. **Canlı skorbord çaprazı
      (coveringrepository.com, browser pane ile):** C(28,9,3)=56, lb 50,
      tarih 14/11/1996 — ~30 yıldır iyileştirilmemiş; EŞİTLİK RESMİ.
      Sertifika paketi: `data/covering/results/C28-9-3-cost56/`
      (solution.txt + stdlib-only verify_cover.py + README). Fallback
      koşulu TETİKLENMEDİ (arşiv boş değil) → 55 avı kararı kullanıcıda.
      **Dilim-8 OPUS +50 — 55 AVI SONUÇ (2026-08-10):** 50/50 iter
      temiz (35k: sıfır kod-boyu hatası); arşive İKİ yeni farklı 56
      düştü (toplam 3 bağımsız 56-sertifikası — 56 tekrarlanabilir
      bölgede) ama **55 YOK**; en iyi 0.7857/56 sabit. Yorum: 56 güçlü
      çekim noktası; C(28,9,3)=56 gerçekten optimal olabilir (kanıt yok,
      lb 50). **REKOR TARAMASI (aynı gün, LLM'siz, 70 sn/hücre):**
      evrilmiş genel çözücü 8 bayat hücrede arşive karşı koşuldu —
      3 ANINDA EŞİTLİK: C(21,10,3)=18, C(20,12,4)=20, C(25,16,4)=17;
      kıl payı: C(23,10,3) 25/24, C(30,12,3) 32/30; zayıf: v29/v30-k9t3
      (80/59, 91/66 — genom v28 boyut rejimine ayarlı), C(22,15,5)
      30/22. **METODOLOJİK DERS (negatif bulgu):** "gap = size−low_bd"
      iyileştirilebilirlik sinyali olarak ZAYIF — küçük bayat hücreler
      çoğunlukla "bitmiş" oldukları için bayat; gerçek headroom
      (size−optimum) muhtemelen ~0. Kürasyon v2'de gap yerine "bizim
      ulaşabildiğimiz − arşiv" farkı kullanılmalı. **DERİN PROBE SONUÇ
      (300 sn × 2 seed):** C(30,12,3) 32→30 = DÖRDÜNCÜ EŞİTLİK; üç
      eşitlik iki seed'de de sabit (duvar görünümü); C(23,10,3) 25'te
      kaldı (arşiv 24). REKOR YOK. **P5 BİLANÇO (2026-08-10):** 5 hücrede
      30-yıllık bilinen-en-iyi EŞİTLENDİ — C(28,9,3)=56 (3 bağımsız
      sertifika), C(21,10,3)=18, C(20,12,4)=20, C(25,16,4)=17,
      C(30,12,3)=30; tümü bağımsız doğrulayıcıyla teyitli, paket:
      `data/covering/results/` (C28 ayrı + esitlemeler-20260810/).
      Ampirik yorum: küçük bayat hücrelerin arşiv değerleri büyük
      olasılıkla optimal(e yakın); gerçek açık alan büyük hücrelerde
      (v32: bizim 1016 / arşiv 620) — o da sprint değil maraton işi
      (daha uzun bütçeler + evrim). Kalan tek küçük av: C(23,10,3)
      24→23 (bizde 25; v28 emsali son bloğun 30 yıllık sertliğini
      söylüyor).
      **SIRADAKİ OTURUM İÇİN HAZIR PLAN (2026-08-10 akşamı yazıldı):**
      `docs/plans/2026-08-11-v32-maraton.md` — v32 rekor maratonu:
      çok-seed fitness (56-piyango tamiri), iş-sayaçlı determinizm
      sözleşmesi, GLM 0.8 + Opus 0.2 ansamblı, 300 sn bütçe, 300 iterlik
      gece koşusu, koşullu thinking-açık Opus kartı ve rekor prosedürü.
      Görev görev, kodlu, TDD'li — superpowers:executing-plans ya da
      subagent-driven-development ile uygulanır. Plana başlamadan önce
      bu Faz P5 bölümünü oku.
      **V32 maraton hazırlığı (2026-08-11, dal: faz-p5-v32-maraton):**
      plan Görev 1-4 TDD ile tamam. (1) `harness/runner.py`
      `run_candidate(..., extra_args=[...])` — aday argv[3:] ile ek
      arguman alır; (2) `harness/evolve_evaluator.py` `DISCOVERY_EVAL_
      SEEDS="0,1"` → seed başına `--seed N` koşusu, combined_score =
      seed ORTALAMASI, cost = en iyi koşu, feasible = min (56-piyango
      tamiri; boş env = eski davranış, arg'sız tek koşu); (3) `run.ps1`
      `OPENAI_API_KEY_OPUS` (8317 config.yaml'dan, ansambl için);
      (4) `evolve/config.covering.v32.yaml` — GLM 0.8 (8318) + Opus 0.2
      (8317) ansamblı, diff true, 300 sn bütçe metinleri, iş-sayaçlı
      determinizm maddesi, evaluator timeout 1400 / parallel 4.
      OpenEvolve 0.3.2 per-model api_base/api_key + `${VAR}` çözümü
      kaynak-doğrulandı (config.py `_resolve_env_var`, dacite
      `__post_init__`; env yoksa fail-fast). Testler: 280 → 283
      (test_extra_args, test_mean_over_seeds, test_no_env_single_run).
      **Başlangıç genomu bulgusu:** gen-200 artefaktı iç bütçeyi 50 sn'ye
      kırpıyor (`min(budget,50)`); 300 sn ölçümü için `_cap320` kopyası
      açıldı (orijinale dokunulmadı). LLM'siz 2-seed taban: kırpmalı
      0.5184/cost 1013, cap320 (600 sn fiili) 0.5176/cost 1016 — 6x süre
      kaliteye DÖNÜŞMÜYOR (duvar-saati-oranlı fazlar ölçeklenmiyor;
      maratonun varlık gerekçesi doğrulandı).
      **Hijyen tamiri:** duman kapısı 3 test kırdı — shell'deki
      `DISCOVERY_EVAL_SEEDS` pytest'e sızıp artifact anahtarlarını
      `seed0:` önekiyle değiştiriyor. Çift katman: run.ps1 kapı temizliği
      listesine EVAL_SEEDS eklendi + `tests/conftest.py` autouse fixture
      (suit dış env'den hermetik). Env-set'li regresyon senaryosu yeşil.
      **Duman testi YEŞİL (2026-08-11, 5 iter, 32 dk):** 5/5 geçerli kod,
      SIFIR diff kaybı; en iyi 0.5181 → **0.5423**, cost **978** (v32
      tüm-zaman en iyisi; önceki 1016). feasible hep 1.0, solver_s ~600
      (bütçe tam kullanılıyor). İterasyon duvarı 661-743 sn, 4 paralel
      örtüşmeyle efektif ~4.4 dk/iter.
      **Ansambl seed BULGUSU (önemli):** controller random_seed 42'den
      md5 ile llm_seed türetip TÜM model config'lerine yazıyor; her
      worker ensemble'ı AYNI seed'le kurup aynı çekiliş dizisini izliyor
      (`[1,1,0,1,0,0,0,1,...]`, 0=glm 1=opus). Duman'ın 5 çağrısının 5'i
      de bu yüzden Opus'a gitti (4 worker ilk çekiliş + bir ikinci) —
      proxy loglarıyla doğrulandı (8317: 5 POST, 8318: 0). 75 çekilişlik
      önekte Opus %21.3 → 300 iterlik koşuda karışım hedefe oturur; kısa
      koşularda Opus-ağır önek beklenir (kota planına dahil et). GLM
      bacağı worker-birebir OpenAILLM ile canlı test edildi (8318, 'OK',
      content dolu). Duman en iyisi: `evolve/artifacts/
      best_v32_smoke_20260811.py` (gece koşusu başlangıç adayı).
      **Gece koşusu BEKLEMEDE (2026-08-11, kullanıcı kararı):** her şey
      hazır, tek komutla başlar (repo kökünden; ~18-24 saat, ~237 GLM +
      ~63 Opus çağrısı):
      ```powershell
      $env:COVERING_SEED_TIME_S="300"
      $env:DISCOVERY_EVAL_SEEDS="0,1"
      $env:DISCOVERY_ARCHIVE_DIR="C:\kt\discovery-harness\runs\evolve\covering-v32-maraton\archive"
      $env:DISCOVERY_ARCHIVE_BELOW="700"
      .\evolve\run.ps1 -GeceKosusuBitti -Problem covering -Iterations 300 `
        -SolverTimeoutS 320 -ConfigPath evolve\config.covering.v32.yaml `
        -ProxyConfig config.glm.yaml `
        -InitialProgram evolve\artifacts\best_v32_smoke_20260811.py `
        -Instance "data\covering\instances\cover-v32-k8-t4.cover" `
        -OutDir runs\evolve\covering-v32-maraton
      ```
      Başlangıç genomu seçenekleri: duman en iyisi (0.5423/978, önerilen)
      ya da cap320 (0.5176/1016, planın harfiyen hali). Koşu sonrası:
      plan Görev 6 Step 2-3 (analiz; cost<620 ise Görev 8 rekor
      prosedürü, değilse Görev 7 thinking-açık Opus kartı kararı).
      **25-iter dilim SONUÇ (2026-08-11, kullanıcı kararıyla 300 yerine):**
      duman en iyisinden (0.5423/978), runs\evolve\covering-v32-iter25.
      SIFIR yeni en iyi (plato 0.5423/977 — 2-seed eval bir önceki 978'i
      977 olarak yeniden üretti, gürültü tabanı ~1 blok); **12/25 çağrı
      zayi (%48)**: 9 kod-boyu aşımı (35.4-38k > 35k — duman genomu
      29.5k'ya büyümüştü, additive diff'ler tavana çarpıyor; dilim-6
      dersinin tekrarı) + 3 diff kaybı (%12, GLM tarihçesiyle tutarlı).
      Ansambl karışımı öngörüyle birebir: 13 Opus / 12 GLM (kısa-koşu
      Opus-ağır önek). Checkpoint: covering-v32-iter25\checkpoints\
      checkpoint_25 (14 program). Sonraki dilim için öneri: max_code_
      length 35k→45k + system_message'a "dosyayı büyütme, ölü kodu buda"
      telkini; checkpoint_25'ten devam (popülasyon çeşitliliği korunur).
      **Dilim-2 SONUÇ (2026-08-11, +25 iter, 45k + budama telkini,
      checkpoint_25→50):** düzeltmeler DOĞRULANDI — zayiat %48 → **%8**
      (0 kod-boyu aşımı, 2 diff kaybı). AMA yine SIFIR yeni en iyi:
      plato 0.5423/977 artık enstrüman artefaktı değil, gerçek (50 iterde
      23 geçerli çocuk, hepsi 0.51-0.54 bandında). v28 emsali: bu noktada
      GLM-ağır diff evrimi platoya girmişti ve kırılma Opus full-rewrite
      "plato kartı" dilimiyle gelmişti (dilim-3: +25 iter, 0.6798→0.7017,
      yapısal sıçrama). Checkpoint: covering-v32-iter25\checkpoints\
      checkpoint_50.
      **Dilim-3 OPUS PLATO KARTI — KIRILMADI (2026-08-11):** checkpoint_
      50'den +25 Opus-only full-rewrite (config.covering.v32.opus.yaml).
      24/25 tamam (1 kayıp: Anthropic upstream Overloaded 502 ×4 retry),
      0 kod-boyu, 0 parse hatası — enstrüman tertemiz. SIFIR yeni en iyi;
      dahası çocuklar 977-980'e AŞIRI sıkı kümelendi (4 bağımsız rewrite
      tam 0.5423/977'ye geri döndü; kuyruk 0.53/990). Yorum: v28'deki
      "56 çekim noktası"nın v32 karşılığı — mevcut paradigma (greedy +
      orbit iskelet + yerel arama, 300 sn × 2 seed) ~977'de doyuyor;
      Opus'un yapısal denemeleri ya muhafazakâr kaldı ya daha kötü
      skorlandı. Arşiv açığı hâlâ büyük: 977 vs 620 (%36). 75 iter
      toplamda (50 ansambl + 25 Opus-FR) iyileşme yok. Checkpoint:
      checkpoint_75. Plan Görev 6 Step 3 gereği karar kullanıcıya
      sunuldu: Görev 7 (thinking-açık Opus, 8320) vs uzun koşu vs dur.
      **GÖREV 7 THINKING-AÇIK OPUS — KIRILMA + EŞİTLEME (2026-08-11):**
      kurulum: `C:\kt\upwork\cli-api\config.thinking.yaml` (config.yaml
      eksi thinking-disabled override; context_management filtresi +
      disable-cooling korundu) + `docker-compose.thinking.yml` (8320,
      auths PAYLAŞILIR, pull_policy: never — :latest sürprizine karşı).
      Replika ölçümü: 64k max_tokens'ta thinking ~42k token yiyor,
      content 20.3k karakter TAM geliyor (finish=stop), süre 564 sn →
      config timeout 900. `evolve/config.covering.v32.thinking.yaml`
      (8320, 64k, checkpoint_interval 5 — koşu SONUNDA checkpoint
      kaydı yok, 85 interval'e denk gelsin diye). 10 iter,
      checkpoint_75'ten: 10/10 iterasyon tamam, content-boş 0, 1 çökük
      çocuk (-2). **İLK thinking iterasyonu 75-iterlik 977 platosunu
      kırdı: cost 620 = LJCR ARŞİV DEĞERİYLE EŞİTLEME** (0.5423→0.8581;
      5 çocuk 620'de). Yapısal içerik: `affine_blocks` — v=p^m tespiti,
      AG(m,p) öteleme grubu, altuzay kapanışı, cosetler; v=32=2⁵ için
      tüm 3-flat'ler = 4·[5 seç 3]₂ = tam 620 blok, her 4 nokta ≤3-dim
      afin altuzayda ⇒ kapsama teorem gereği. HARDCODE YOK (muayene
      edildi; tek yoğun literal asal listesi). Doğrulama zinciri:
      bağımsız verify_cover.py (35960/35960, 0 ihlal) + canlı skorbord
      çaprazı (coveringrepository.com, browser pane: 620/lb 552,
      14/11/1996 — ~30 yıl dokunulmamış). Arşiv kancası 3 bağımsız
      620 kopyası yakaladı. Sertifika paketi:
      `data/covering/results/C32-8-4-cost620/`. Maliyet: ~10 thinking
      çağrısı ≈ ~480k output token (Opus OAuth). checkpoint_85 devam
      noktası. DERS: plato "fikir tükendi" değildi — thinking'siz Opus
      75 iterde bulamadığı sonlu-geometri paradigmasını thinking'li
      ilk denemede kurdu; Görev 7 kartı kesin sonuç verdi.
      **AFİN GENELLEME TARAMASI (2026-08-11, LLM'siz):** analitik
      ön-tarama (8759 hücre, kapalı formül p^(m−d)·[m seç d]_p): saf
      afin sayısı arşivden küçük hücre YOK (anında-rekor fırsatı yok;
      küratörler geometriyi biliyor); 17 hücrede arşiv = afin birebir.
      Kazanan genom 17 hücrede koşuldu (3 rekor-şanslı 300 sn + 14
      eşitleme-adayı 120 sn, seed 0): **15 EŞİTLEME** — en önemlisi
      C(49,8,2)=49: saf afin 56 verir, evrilmiş yerel arama 56→49'a
      indirdi (eşitleme ARAMADAN, konstrüksiyondan değil). Kaçanlar:
      C(27,10,3) 36/arşiv 35 (1 blok; uzun-probe adayı), C(32,18,5)
      99/56 (dolgulu afin verimsiz). v=64 t=5 bellek riskiyle atlandı.
      15/15 bağımsız doğrulayıcıdan geçti; paket:
      `data/covering/results/afin-esitlemeler-20260811/`. P5 bilançosu
      artık: **21 hücrede bilinen-en-iyi eşitlendi** (5 eski + 620 +
      15 tarama), tek genelleştirilmiş programla.
      **REGRESYON BEKÇİSİ YEŞİL (2026-08-11, genelleme 4. ayak):**
      thinking620 vs cap320, aynı bütçe (300/300/60/60 sn, seed 0),
      asal-kuvvet OLMAYAN hücreler: v28-k9-t3 70 vs 73 (yeni genom 3
      blok İYİ; arşiv 56), v24-k6-t4 (eski holdout) 1048 vs 1042
      (+6, tek-seed anytime gürültü bandında), bekçiler v13=26 / v7=7
      (ikisi de kanıtlı optimumda). Sonuç: afin sıçraması eski
      yetenekleri BOZMADI. Kapsamlı-sınırlı genelleme iddiasının dört
      ayağı tamam (holdout + sıfır-ayar + kesin doğrulama + regresyon);
      formal iddia için kalan iş mekanik: covering benchmark dokümanı
      (sabit set, asal-kuvvet dışı hücreler dahil, sakin-makine
      çok-seed protokol, tohum/arşiv kolonları). Ham veri:
      runs\evolve\regresyon-20260811\results.csv.
      **B1 THINKING TEKRAR DENEYİ (2026-08-12→13, yayın özeti B1):**
      tasarım: checkpoint_75'ten, ON (8320/64k/900) vs OFF (8317/20k,
      dilim-3 config'i), k=3 tekrar × 10 iter, dönüşümlü sıra, seed
      43/44/45 eşleştirilmiş, hepsi Opus full-rewrite. SONUÇ:
      **ON 3/3 KIRILMA — üçü de tam 620'ye ulaştı** (afin konstrüksiyon
      her tekrarda yeniden keşfedildi); OFF r1 978 (skor kıpırtısı,
      kırılma değil), r2 977 (hiç yeni-en-iyi), **r3 GEÇERSİZ: Claude
      kota 429'ları (48 hata, 2/10 iter)** — o dilim koşulamadı.
      **off-r3b TAMAM (2026-08-13, kota yenilenince):** 10/10 iter,
      kırılma yok (977 bandı) → **NİHAİ: ON 3/3 (üçü de 620) vs OFF
      0/3; Fisher tek-yönlü p = 0.05**; etki büyüklüğü her başarıda
      −357 blok (%36). Destekleyici: orijinal r0 ON=620 (dahil edilirse
      4/4 vs 0/3, p≈0.029) + checkpoint_50'de tarihsel OFF 0/25.
      Yorum: kırılma şans değil — thinking, afin paradigmasını
      TEKRARLANABİLİR şekilde kuruyor. C1 makalesinin başlık deneyi
      istatistiksel olarak yerinde. Ham loglar: runs\evolve\b1\*.log.
      NOT (pwsh tuzağı): retry script'i Windows PowerShell 5.1 ile
      koşturulamaz — EAP=Stop, openevolve'un stderr log satırını
      NativeCommandError'a çevirip koşuyu düşürüyor; pwsh 7 şart.
      **B2 BENCHMARK TAMAM (2026-08-13, docs/benchmark-covering.md):**
      protokol koşu ÖNCESİ donduruldu (07e3920); 29 hücre × (thinking620
      × 3 seed + tohum × 1), 297 dk, 116/116 koşu. SONUÇ: **22/29
      eşitleme** (22/22 bağımsız doğrulama); seed kararlılığı 25/29
      hücrede özdeş üçlü. YENİ kazanım: **C(23,10,3)=24** (önceki en
      iyimiz 25, "kalan av" kapandı) + PP-DIŞI kolda 4 eşitleme
      (21/20/23/25 evrenleri — afin konstrüksiyonsuz, evrilmiş arama
      makinesiyle; genelleme afin ailesi dışına taştı). Negatifler
      dokümanda: C(32,18,5) +43, C(24,6,4) +263, C(30,9,3) +25,
      C(22,15,5) +7, kıl payı C(27,10,3)/C(30,12,3) +1. Toplam eşitleme
      bilançosu artık 22 hücre (tek protokol altında). Yayın özeti B2
      kapandı.
      **REKOR-AVI TARAMASI (2026-08-14, docs/headroom-taramasi-20260814.md):**
      `python data/covering/reference/record_scan.py` → katmanlı headroom
      taraması (207 aday) + canlı skorbord çaprazı (14 aile sayfası).
      ⚠ Canlı çapraz Browser pane ile YAPILMAZ: Cloudflare challenge'ın
      WebGPU fingerprint'i GPU sürecini 0x60C201E ile çökertiyor (2. vaka
      2026-08-13 20:53, Desktop komple kapandı; 1. vaka ResearchGate
      2026-08-03) — gerçek Chrome (claude-in-chrome) kullan, challenge
      kendiliğinden geçiyor. Bulgular: hedef hücrelerin TÜMÜ canlıda
      donmuş arşivle aynı; tek sapma k=18,t=5 ailesi (canlı 55/105/122/
      147/182 < donmuş — aile aktif, hedeften düşürüldü; donmuş döküm
      canlının mükemmel aynası değil, rekor kıyası DAİMA canlıya).
      Kısa liste — Track A ucuz av: C(20,12,4) 20/lb15, C(30,12,3)
      30/lb25, C(25,16,4) 17/lb13, C(28,9,3) 56→55 avı, C(23,10,3)
      24/lb21 (+SEARCH bandı gap-2 ~15 hücre); Track B prestij:
      C(81,9,3)=1170/lb1080 (saf afini yen; yan ödül C(80,9,3)),
      ikincil C(32,17,5)=62/lb53; Track C konstrüksiyon: C(v,6,4) —
      önce v=24'te 784'ü yeniden keşfet (+263 açığımız var), sonra
      v=23 (716/625), v=26 (1152/1040), v=29 (1802/1653).
      **Track A bandı kuruldu (2026-08-14):** `python -m
      problems.covering.record_band --out runs/probes/track-a-20260814`
      — 21 hücre, ~10,5 saat, sakin makinede gece koşusu; kesin
      doğrulama + ADAY paketleme + idempotent devam. Duman testi ve
      pytest (283/283) yeşil. Aday çıkarsa iddia protokolü
      (headroom-taramasi §5-6) elle yürütülür.
      **TRACK A+B SONUÇLARI (2026-08-15, headroom-taramasi §5):**
      Tur-1 (uzak, 49/49): aday yok; 8 YENİ eşitleme (SEARCH bandı) →
      bilanço 30 hücre; genomda gizli `min(budget,305)` tavanı bulundu
      → cap7200 kopyası. Tur-2 (tavansız × 1200 sn, 21/21): aday yok;
      C(30,12,3)=30 ve C(28,9,3)=56 uzun bütçeyle eşitlendi. DESEN:
      arama arşivi yakalıyor, GEÇEMİYOR. Track B / C(81,9,3): dilim-1
      altyapı arızası (adaptive/high thinking 64k VE 100k'yı tamamen
      düşünmeye harcıyor, content 0 → tamir: OpenEvolve model-config
      `reasoning_effort: medium` + max_tokens 100000; proxy
      payload.override claude yolunda İŞLEMİYOR, apply.go "no config
      found"); dilim-2 TEMİZ NEGATİF: 10/10 geçerli tam yeniden yazım,
      hepsi 1170 — saf afin, medium-thinking için çekim noktası.
      Asimetri bulgusu kayıtlı: sınıra ULAŞMAK (v32 977→620, ilk
      iterasyon) vs sınırı AŞMAK (b81, 10 iterde gelmedi) + sınırsız
      düşünme sarmalı. Sıradaki: Track C — C(24,6,4)=784 yeniden
      keşif dilimi (+263 açık = gradyan var; başarılırsa v=23/26/29
      gap 91/112/149 av alanı).
      **Uzak koşu makinesi (2026-08-14, docs/uzak-kosu-kurulumu.md):**
      DESKTOP-M070IQB (Ryzen 5 5600, 16 GB), Tailscale 100.73.210.41,
      ssh host `kt-uzak`, repo `F:\kt\discovery-harness`, daima
      `py -3.14` (PATH'te eski Python var). Kurulum tuzakları (ssh
      ACL, ssh-keygen -N tırnak tuzağı, boş parola ağ oturumu,
      ssh→cmd tırnak, schtasks yeniden-tetik) dokümanda. Track A
      bandı ORADA koşuyor (schtasks `kt-track-a`, 2026-08-14 13:45,
      beklenen bitiş ~00:15); covering testleri uzakta yeşil, bilinen
      kırmızılar dokümanda kayıtlı.
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

Kimi/Moonshot container'ı (8319; key `config.kimi.yaml`'da dolu, 2026-08-07
doğrulandı — alias `kimi`→kimi-k3, `kimi-code`→kimi-k2.7-code):

```bash
docker compose -f docker-compose.kimi.yml up -d
```

```bash
curl -s -H "Authorization: Bearer $(grep -A1 'api-keys:' /c/kt/upwork/cli-api/config.kimi.yaml | grep -o '"[^"]*"' | tr -d '"')" http://localhost:8319/v1/models
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

Covering (P5) kürasyon + kalibrasyon (LJCR arşivi; kaynak:
`data/covering/reference/sources/coverdata.json`, dmgordo/LJCR):

```bash
python data/covering/reference/curate_targets.py
```

```bash
python data/covering/reference/verify_ljcr.py
```

Covering kanıtlı optimum (küçük hücre; büyük hücrede "kapsam dışı" der):

```bash
python -m problems.covering.enumerate data/covering/instances/cover-v7-k3-t2.cover
```

Covering tohum + baseline raporu (bütçe sn/instance; rapor docs/ altına):

```bash
python -m problems.covering.baseline docs/faz-d-covering-baseline.md 15
```

Covering Faz E döngüsü (GLM 8318; COVERING_SEED_TIME_S env ŞART;
duman için -Iterations 5, kısa koşu 50; PowerShell):

```bash
powershell -Command "Set-Location C:\kt\discovery-harness; \$env:COVERING_SEED_TIME_S='50'; .\evolve\run.ps1 -GeceKosusuBitti -Problem covering -Iterations 5 -ConfigPath evolve\config.covering.yaml -ProxyConfig config.glm.yaml -InitialProgram problems\covering\seed_solver.py -Instance 'data\covering\instances\cover-v28-k9-t3.cover;data\covering\instances\cover-v32-k8-t4.cover;data\covering\instances\cover-v13-k3-t2.cover' -OutDir runs\evolve\covering-glm-smoke1"
```

LLM'siz adaptör kontrolü (covering; kredi yakmadan boru hattı testi):

```bash
DISCOVERY_PROBLEM=covering COVERING_SEED_TIME_S=3 DISCOVERY_SOLVER_TIMEOUT_S=25 DISCOVERY_INSTANCE="data/covering/instances/cover-v28-k9-t3.cover;data/covering/instances/cover-v32-k8-t4.cover;data/covering/instances/cover-v13-k3-t2.cover" python harness/evolve_evaluator.py problems/covering/seed_solver.py
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
