# P4 — Cap Set (F₃ⁿ içinde 3-AP'siz en büyük küme)

Bu dosya, bu klasördeki işi yürütecek ajan için **kendi başına yeterli**
talimattır. Bu iş **GLM ile** yürütülür (Claude kotası tasarrufu — 2026-08-06
kararı); ajan hangi model olursa olsun buradaki sözleşmeye uyar.

Depo kökündeki `CLAUDE.md` kuralları burada da geçerlidir; kritik olanlar
aşağıda tekrarlanmıştır ki bu dosya tek başına okunabilsin.

## 0. SERT KURALLAR (tartışmaya açık değil)

1. **`harness/` altında TEK SATIR bile değiştirilmez.** Bu problem aynı
   zamanda Faz F'nin sınavıdır: "yeni problem çekirdeğe dokunmadan
   eklenebiliyor mu?" Eklenemiyorsa çekirdek sızdırıyordur — o zaman DUR ve
   insana raporla; kendin harness'ı "düzeltme".
2. **`problems/kofn/` ve `C:\kt\tcdd\cvrp-discovery` salt-okunurdur.**
   Desen kopyalanır, dosyaya dokunulmaz.
3. **CPU disiplinli kullanılır.** Doğrulayıcı O(|S|²) ve ms mertebesinde
   kalmalı. `enumerate` tarzı kanıt araması tek çekirdekte, dakikalar
   mertebesini aşmamalı; aşıyorsa kapsamı daralt (küçük n). Paralel pytest,
   uzun benchmark yok.
4. **Web araştırması WebFetch/WebSearch ile yapılır; uygulama içi tarayıcı
   (Browser pane) KULLANILMAZ** — Claude Desktop'ta GPU çökmesine yol açtığı
   görüldü (kök CLAUDE.md §0.4). Erişilemeyen kaynak "boşluk" olarak
   raporlanır.
5. **Referans/rekor değerleri solver'a SIZDIRILMAZ.** `data/capset/reference/`
   yalnızca insan raporlaması ve test doğrulaması içindir; instance
   dosyasına, seed solver'a veya evolve prompt'una bilinen rekor yazılmaz.
   (Evaluator'ün Meshulam *teorem* sınırını normalizasyon için kullanması
   serbesttir — teorem ≠ referans tablosu.)
6. **Uydurma komut belgeleme.** Bu dosyanın §9'una yalnızca fiilen çalıştırıp
   yeşil gördüğün komutları yaz.
7. Kod içi yorum/docstring dili: mevcut depo gibi Türkçe (ASCII, aksansız —
   `cozum`, `kosturur` gibi).

## 1. Problem tanımı

**Cap set:** S ⊆ F₃ⁿ (her eleman n uzunluğunda, {0,1,2} alfabeli vektör),
öyle ki **üç FARKLI** x, y, z ∈ S için x + y + z ≡ 0 (mod 3, bileşen
bileşen) OLMASIN. Bu koşul şunlara denktir: S'de 3-terimli aritmetik dizi
yok ⟺ S afin doğru içermiyor. Amaç: |S| **maksimum** (SENSE = "max").

Dikkat: x+x+x ≡ 0 her zaman sağlanır; F₃'te x+x+y ≡ 0 ⟹ y = x. Yani
"farklılık" koşulu konunca ihlal ancak üç ayrı vektörle olur. Doğrulama
O(|S|²): her {x,y} çifti için z = −(x+y) mod 3 hesapla; z ∈ S ve
z ∉ {x,y} ise ihlal (her doğru 3 çiftte yakalanır → doğru sayısı = eşleşme/3).

**Neden bu harness için ideal:** doğrulama **saf tamsayı aritmetiği** —
P1'deki Fraction ihtiyacının bile daha temizi; float hiç yok. Üretmek zor,
doğrulamak ucuz ve kesin (verifier asymmetry, kök CLAUDE.md §1). Emsal:
DeepMind FunSearch bu problemde n=8 alt sınırını 496'dan 512'ye taşıdı
(Romera-Paredes ve ark., Nature 2024) — yani "OpenEvolve-şekilli döngü bu
problemde çalışır" kanıtlanmış durumda.

## 2. Bilinen değerler (✅ = web'den doğrulandı, P4.0, 2026-08-06)

Ayrıntılı doğrulama + yazar-atıf düzeltmeleri: `docs/p4-problem-tanimi.md` §2.

| n | a(n) | Durum | Kaynak (ilk/kanonik, doğrulanmış) |
|---|------|-------|--------|
| 1 | 2 | kanıtlı | trivial |
| 2 | 4 | kanıtlı | trivial |
| 3 | 9 | kanıtlı | klasik |
| 4 | 20 | kanıtlı ✅ | Pellegrino 1971 (ilk ispat); Follett et al. 2014 yeniden ispat |
| 5 | 45 | kanıtlı ✅ | Edel–Ferret–Landjev–Storme 2002 (JCT A) |
| 6 | 112 | kanıtlı ✅ | Potechin 2008 (Des. Codes Cryptogr.); OEIS extension Tao 2009 |
| 7 | ∈ [236, 288] ✅ | AÇIK | alt 236: Calderbank–Fishburn (Edel, smallCaps Theorem 6); üst ≤288: Thackeray 2022 (arXiv:2206.09804, "no 289-cap") |
| 8 | ≥ 512 ✅ | AÇIK | FunSearch / Romera-Paredes et al., Nature 2024 — küme İNDİRİLDİ + bağımsız doğrulandı (`data/capset/reference/funsearch_n8_size512.txt`) |
| 9 | ≥ 1082 ⚠ | AÇIK | Edel ürün-konstrüksiyonu (alt sınır) + FunSearch teyidi (eşitledi). ⚠ Tyrrell 2022 (arXiv:2209.10045) tam metni 1082'yi birebir vermiyor (asimptotik 2.218^n); ayrı birincil doğrulama yapılmadı |
| ≥10 | çarpım sınırları | AÇIK | a(m+n) ≥ a(m)·a(n) |

Üst sınır teoremleri: **Meshulam 1995: a(n) ≤ 2·3ⁿ/n** (normalizasyonda
kullanılacak olan bu); Ellenberg–Gijswijt 2017: a(n) ≤ O(2.756ⁿ).

Doğrulama kaynakları: OEIS **A090245**; `erdosproblems.com`; Tao'nun
kataloğu `teorth.github.io/optimizationproblems`; FunSearch makalesi ve
`github.com/google-deepmind/funsearch` (yayınlanmış 512'lik n=8 kümesi —
bulunursa **altın pozitif kontrol**: evaluator'ümüz onu feasible + |S|=512
olarak doğrulamalı); Yves Edel'in cap sayfaları (açık cap veritabanı —
n=4/5/6 optimal kümelerin somut kopyaları için).

Bulguları `docs/p4-problem-tanimi.md`'ye yaz (P1'deki
`docs/p1-problem-tanimi.md` deseni); tablo doğrulanmadan `objective.py`'nin
pozitif kontrol testlerini yazma. İndirilen somut kümeler
`data/capset/reference/` altına, kaynağıyla birlikte.

## 3. Eklenti sözleşmesi (registry'nin fiilen doğruladığı)

`harness/registry.py`, `problems/capset/__init__.py`'den şunları arar:

```python
SENSE = "max"
parse_instance(path) -> Instance      # bozuk instance InstanceFormatError raise EDER
evaluate_text(instance, text) -> dict # ÇÖZÜM TARAFI ASLA RAISE ETMEZ
penalty_scale(instance) -> float      # instance'tan türetilir, sabit değil
```

verdict şeması (kofn ile birebir aynı — araç zinciri değişmesin):

```python
{"feasible": bool, "cost": int,        # cost = |S| (yalnız feasible iken anlamlı)
 "violations": {...},                  # kod -> ayrıntı; feasible ise boş
 "fitness": float, "eval_ms": int, "info": {...}}
```

Kofn'daki `__init__.py` re-export deseni kopyalanır:
`from .io import ...`, `from .objective import ...`, `from .spec import ...`.

### Dosya formatları

**Instance** (`data/capset/instances/capset-n8.cap` gibi) — bilinçli olarak
minimal, çünkü solver bu dosyayı okur (kural §0.5):

```
# yorum satırı serbest
dimension 8
```

**Çözüm** (aday program `python <program> <instance> <çıktı>` ile çağrılır —
`harness/runner.py` sözleşmesi; timeout'ta çıktı dosyası KURTARILIR):

- Her boş olmayan satır: tam n adet {0,1,2} karakteri, bitişik (`02110221`).
- `#` ile başlayan satırlar yorumdur, atlanır. Solver `# size K` yazarsa
  değer YOK SAYILIR ama `info.reported_size_matches` olarak kaydedilir
  (kofn'daki sessiz dürüstlük sensörünün karşılığı).
- **Anytime deseni:** solver çıktıyı geçici dosyaya yazıp `os.replace` ile
  atomik değiştirir; böylece timeout anında yarım satır kalmaz. Bu,
  `prompt.md` sözleşme metnine de yazılır.

### Evaluator kuralları (paranoyak — kök CLAUDE.md §8 ruhu)

- Yanlış uzunluk / alfabe dışı karakter → `bad_vector`.
- Tekrarlanan vektör → `duplicate_vector` (şişirme hilesine karşı; küme
  tekilleştirilerek "affedilmez", ihlaldir).
- Doğru (line) bulunursa → `line_found` (sayı + örnek üçlü `info`'ya).
- Boş küme **feasible**'dır, fitness 0 — meşru taban.
- Hiçbir koşulda raise yok; her bozukluk violation koduyla verdict döner.

### Fitness (gerekçesini `objective.py` docstring'ine yaz)

- **Feasible:** `fitness = |S| / penalty_scale(instance)` ve
  `penalty_scale(instance) = 2·3ⁿ/n` (Meshulam üst sınırı). Böylece fitness
  ∈ [0,1), instance'lar arası ölçek karşılaştırılabilir (çoklu-instance
  ortalaması için şart — adaptör `DISCOVERY_INSTANCE`'ta `;` ayraçlı liste
  destekliyor, fitness = ortalama).
- **Infeasible:** `fitness = -1.0 - min(1.0, ihlal_sayısı / max(1, çift_sayısı))`
  → her infeasible ∈ [-2,-1] < her feasible ≥ 0. "Hiçbir ihlal kârlı olamaz"
  kuralının buradaki hali; infeasible'lar arasında gradyan da verir.
- İşaret dönüşümü SANA AİT DEĞİL: `harness/score.py` combined_score'u
  SENSE="max" için aynen geçirir. Dokunma.

## 4. Yapılacak dosyalar

```
problems/capset/
  __init__.py      # re-export (kofn deseni)
  spec.py          # SENSE, penalty_scale, format sabitleri
  io.py            # parse_instance (+ InstanceFormatError)
  objective.py     # evaluate_text — saf tamsayı doğrulayıcı
  seed_solver.py   # evrimin başlangıç genomu (tek dosya, anytime)
  enumerate.py     # n<=3 için kanıtlı optimum (B&B / tam arama)
  baseline.py      # tohum gap tablosu (Faz P4.3)
  prompt.md        # evolve system message (çözüm format sözleşmesi metni)
tests/test_capset_io.py, test_capset_objective.py, test_capset_seed.py ...
data/capset/instances/*.cap          # capset-n4 ... capset-n9
data/capset/reference/               # bilinen değerler + indirilen kümeler
docs/p4-problem-tanimi.md, docs/p4-baseline.md
```

## 5. Faz planı (sırayla; her faz sonunda `python -m pytest tests/ -q` YEŞİL)

- [x] **P4.0 — Literatür doğrulama.** ✅ (2026-08-06) §2 tablosu web'den
      doğrulandı (OEIS A090245 + birincil makaleler); FunSearch 512-kümesi
      indirildi + bağımsız `O(|S|²)` ile doğrulandı (`funsearch_n8_size512.txt`,
      altın pozitif kontrol); n=2/3/4 optimal kümeleri üretildi + doğrulandı;
      n=5/6/7 **boşluk** (Edel veritabanı yalnız n≥7 verir; greedy cebirsel
      cap'leri bulamaz → P4.3 seed/ürün-konstrüksiyon çıktısına düşer).
      Bulgular: `docs/p4-problem-tanimi.md`; veri: `data/capset/reference/`.
      Somut küme bulunamayanları "boşluk" olarak işaretlendi.
- [x] **P4.1 — Enstrüman (TDD).** ✅ (2026-08-06) Önce test, sonra kod
      (Red-Green-Refactor): `spec.py`, `io.py`, `objective.py`,
      `__init__.py`. Testler (44 yeni, `tests/test_capset_{io,objective,
      registry}.py`): (a) pozitif — n=2/3/4/8 indirilen kümeler feasible
      + doğru |S|; (b) negatif — bad_vector, duplicate_vector, line_found,
      bozuk instance → InstanceFormatError; (c) her infeasible < her
      feasible; (d) `evaluate_text` hiç girdiyle raise etmez (boş, çöp
      bayt, dev satır, non-str); (e) `load_problem("capset")` sözleşmeyi
      geçer + çekirdek agnostik (`registry.py`'de "capset" geçmez → Faz F
      sınavı). `pytest tests/ -q` → 161 passed. n=8 512-küme ~210 ms.
      Instance dosyaları `data/capset/instances/capset-n{2..9}.cap`.
- [x] **P4.2 — Kanıt katmanı.** ✅ (2026-08-06) `enumerate.py`: n≤3'te
      kanıtlanmış optimum (B&B; n=3, 27 nokta → ~0.5 sn, 647K düğüm).
      enumerate bağımsız olarak a(1)=2, a(2)=4, a(3)=9'u bulur (literatürle
      birebir). n≥4 için `time_limit` (default 10 sn) ile alt sınır; tam kanıt
      dakikalar alır — n=4'te 3 sn'de 20'ye ulaşır ama `proven=False`
      (optimallik literatüre ait). Testler (`tests/test_capset_enumerate.py`,
      10 yeni): n≤3 optimum + çıktı cap doğrulaması + determinizm + hız
      sınırı; n≥4 alt sınır fallback. `pytest tests/ -q` → 171 passed.
- [x] **P4.3 — Tohum + baseline.** ✅ (2026-08-06) `seed_solver.py`:
      rastgele-greedy kurulum + extend + swap hill-climb (1-çıkar/k-ekle)
      + random-restart (anytime), atomik yazım (`os.replace`), deterministik
      `--seed`. Cebirsel Hill cap doubling EKLENMEDİ (evrim keşfetsin; §0.5
      sızıntı riski). Tohum meşru saf greedy: n=2/3/4 **optimum** (4/9/20),
      n=6=77, n=8=263 (gap %31/%49 → bol gradyan). Strawman DEĞİL.
      `baseline.py` → `docs/p4-baseline.md` (8 instance, gap tablosu).
      Adaptör duman kontrolü yeşil (`combined_score` 0.494 n=4'te). Testler
      (`tests/test_capset_seed.py`, 10 yeni): determinizm, anytime, CLI,
      atomik yazım, eşikler. `pytest tests/ -q` → 181 passed.
- [x] **P4.3b — İnceleme düzeltmeleri** ✓ (2026-08-07). İki bağımsız
      kod incelemesinin bulguları kapatıldı: Görev 1 (anytime yazımı
      gerçekten anytime — `on_improve` callback, ilk yazım greedy'den hemen,
      hill-climb öncesi; kod tekrarı kalktı); Görev 2 (test zafiyetleri —
      env geçişi, determinizm flake'siz saf fonksiyonlar, enumerate `proven`
      assert, fitness aralığı, fuzz vekilleri); Görev 3 (reported_size tekil
      vektör sayısıyla, enumerate docstring); Görev 4 (n=9 ⚇ Tyrrell teyit
      yapılamadı, kürasyon planı bekçi=n4, §4 ürün dokümanı, verify_capsets
      küme-eşitliği, known_values.csv, yazım); Görev 5 (prompt.md,
      config.capset.yaml, run.ps1 `-ConfigPath`/`-ProxyConfig`, §7 koşu
      öncesi kontrol listesi). `pytest tests/ -q` → 189 passed; evolve koşusu
      BAŞLATILMADI (insan pacing kararı).
- [ ] **P4.4 — Döngü (evolve).** Kök CLAUDE.md §5 ayarları zaten
      `evolve/config.yaml`'da (GLM proxy 8318, timeout 600, max_tokens
      20000). Yeni koşu için env:
      `DISCOVERY_PROBLEM=capset`,
      `DISCOVERY_INSTANCE=capset-n7.cap;capset-n8.cap;capset-n4.cap` deseni.
      Kürasyon kuralı (**headroom turnusolu** — tohumun zaten tavana vurduğu
      instance evrim hedefi olamaz; kofn'daki düz-çizgi dersinin karşılığı):
      **bekçi = n=4** (tohum kanıtlı optimumda: 20 → gerileme hemen görünür),
      **gradyan kaynağı = n=7 + n=8** (tohum 144/263 vs bilinen 236/512 → bol
      headroom), **holdout = n=6 + n=9** (koşuya GİRMEZ; genelleme ölçümü).
      n=6 tohum 77/112 (headroom bol) olduğundan bekçi DEĞİL. Önce 5 iterasyonluk
      duman testi, sonra uzun koşu. GLM Coding Plan Lite haftalık kredisi
      sınırlı — pacing kararını insana bırak.
- [ ] **P4.5 — Rapor.** İddia metni yalnız şöyle kurulur: "n=7'de ≥237 /
      n=8'de ≥513 feasible küme bulundu; evaluator verdict'i + küme dosyası
      ektedir." İddia ÖNCESİ: sakin makinede bağımsız re-run + insanın
      güncel rekoru yeniden kontrolü (alan hızlı hareket ediyor — Mayıs
      2026'da unit distance düştü; 512 de eskimiş olabilir).

## 6. Kaçınılacaklar

- Rekoru instance'a/prompt'a yazmak (sızıntı, §0.5).
- Doğrulayıcıda float, "yaklaşık eşitlik", tolerans — hepsi tamsayı.
- Evaluator'ün çözümü "onarması" (duplicate silmek, kötü satırı atlamak).
  Onarım solver'ın işi; evaluator yalnız yargılar.
- Evaluator'de bug şüphesi varken döngü koşturmak — önce enstrüman düzelir
  (kök CLAUDE.md §8).
- n'i büyütüp doğrulamayı pahalılaştırmak: |S| birkaç bini, doğrulama
  ~100 ms'yi aşıyorsa insana danış.

## 7. Komutlar (yalnızca fiilen çalışanlar yazılır)

Depo kökünden:

```bash
python -m pytest tests/ -q
```

P4.0 pozitif kontrol doğrulaması (indirilen/üretilen cap kümelerinin
3-AP'siz olduğunun bağımsız O(|S|²) teyidi; FunSearch 512-kümesi dahil):

```bash
python data/capset/reference/verify_capsets.py
```

Kanıtlanmış optimum (n≤3; n≥4 alt sınır, `time_limit` ile):

```bash
python -m problems.capset.enumerate data/capset/instances/capset-n3.cap
```

Adaptör duman kontrolü (LLM'siz; instance dosyası oluştuktan sonra) —
✅ doğrulandı (2026-08-06, n=4 → combined_score 0.494). Çoklu-instance
varyantı (P4.4 kürasyonu; ✅ 2026-08-07, 3-instance ortalama → 0.295):

```bash
# tek instance
DISCOVERY_PROBLEM=capset DISCOVERY_INSTANCE=data/capset/instances/capset-n6.cap python harness/evolve_evaluator.py problems/capset/seed_solver.py

# P4.4 kürasyonu (bekçi=n4, gradyan=n7+n8); CAPSET_SEED_TIME_S koşu ortamında
DISCOVERY_PROBLEM=capset \
DISCOVERY_INSTANCE="data/capset/instances/capset-n7.cap;data/capset/instances/capset-n8.cap;data/capset/instances/capset-n4.cap" \
DISCOVERY_SOLVER_TIMEOUT_S=55 \
python harness/evolve_evaluator.py problems/capset/seed_solver.py
```

## P4.4 koşu öncesi kontrol listesi (her koşudan ÖNCE, insandan sonra)

1. **pytest yeşil:** `python -m pytest tests/ -q` (kırımızıysa DUR).
2. **GLM proxy ayakta + model alias:** `curl -s http://localhost:8318/v1/models`
   çıktısında `glm-5` (upstream `glm-5.2`) görünmeli. Görünmezse
   `C:\kt\upwork\cli-api` altında `docker compose -f docker-compose.glm.yml up -d`.
3. **CAPSET_SEED_TIME_S=50** koşu ortamında set edilmeli (runner 55 sn'de
   öldürür; 5 sn tampon). Evrilen solver da bu limite uyacak (prompt.md).
4. **Yukarıdaki çoklu-instance adaptör dumanı** feasible skor üretmeli
   (`feasible: 1.0`, `combined_score > 0`).
5. Koşu: `.\evolve\run.ps1 -GeceKosusuBitti -ConfigPath evolve\config.capset.yaml
   -Problem capset -Instance "data\capset\instances\capset-n7.cap;data\capset\instances\capset-n8.cap;data\capset\instances\capset-n4.cap"
   -InitialProgram problems\capset\seed_solver.py -ProxyConfig config.glm.yaml
   -Iterations 5` (önce duman), sonra uzun koşu (`-Iterations 2000`).

Tohum + baseline gap tablosu (her instance'ta tohum |S| vs bilinen değer;
çıktı `docs/p4-baseline.md`):

```bash
python -m problems.capset.baseline docs/p4-baseline.md
```

## 8. İlk oturum başlangıç komutu (insan bunu GLM'e verir)

"`problems/capset/CLAUDE.md`'yi oku ve uy. P4.0'dan başla: §2 tablosunu
web'den doğrula (WebFetch/WebSearch; Browser pane kullanma), FunSearch'ün
n=8 512'lik kümesini ve Edel'in n=4/5/6 optimal kümelerini
`data/capset/reference/` altına indir, `docs/p4-problem-tanimi.md`'yi yaz.
Formülasyon ve pozitif kontrol verisi netleşmeden `objective.py` yazma.
Sonra P4.1'i TDD ile yap. `harness/` ve `problems/kofn/` dosyalarına dokunma."
