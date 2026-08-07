# GÖREV: P4.4 öncesi düzeltmeler (kod incelemesi bulguları, 2026-08-06)

Bu dosya tek başına yeterli bir görev listesidir. `problems/capset/CLAUDE.md`
sözleşmesi aynen geçerli; özellikle: **`harness/` ve `problems/kofn/`
dosyalarına dokunma**, `C:\kt\tcdd\cvrp-discovery` salt-okunur, web araştırması
yalnız WebFetch/WebSearch (Browser pane YOK), rekor değerler solver'a/prompt'a
sızdırılmaz. Görevleri SIRAYLA yap; **her görevden sonra**
`python -m pytest tests/ -q` yeşil olmadan sonrakine geçme. Bittikçe buradaki
kutuları işaretle.

Bağlam: P4.0–P4.3 teslimi iki bağımsız incelemeden geçti. Kritik hata yok;
evaluator doğrulandı (FunSearch 512-kümesi + bağımsız kontrol + fuzz). Aşağıdaki
maddeler P4.4 (evolve döngüsü) başlamadan kapanmalı.

---

## Görev 1 — Tohumun anytime yazımı gerçekten "anytime" olsun

**Sorun:** `seed_solver.py` `main()` (satır ~224-232) ilk atomik yazımı
`_swap_hillclimb` döndükten SONRA yapıyor; n≥6'da hill-climb kendi deadline'ına
kadar koştuğundan çıktı dosyası bütçenin neredeyse tamamı boyunca hiç var
olmuyor. Runner timeout'u (`DISCOVERY_SOLVER_TIMEOUT_S`) tohum bütçesinin
(`CAPSET_SEED_TIME_S`) altına düşerse sonuç: boş çözüm → fitness 0. Evrimde
LLM bütçe satırını mutasyona uğrattığı anda bu bir tuzak. Ayrıca `main()`
hill-climb'e tüm deadline'ı verirken `solve()` kalan sürenin ~%30'unu veriyor —
testlerin sınadığı yol ile gerçek koşu yolu farklı.

**Yapılacak:**
- [ ] `main()` akışını değiştir: her restart'ta `greedy_construct + extend`
      biter bitmez (hill-climb'den ÖNCE) iyileşme varsa atomik yaz; hill-climb
      sonrası tekrar kontrol et ve iyileşme varsa yine yaz. İlk yazım ilk
      restart'ın greedy'sinden hemen sonra gerçekleşmeli (< 1-2 sn).
- [ ] `main()` ile `solve()` arasındaki kod tekrarını kaldır: `solve()`'a
      opsiyonel bir `on_improve(cap)` callback parametresi ekle; `main()`
      callback'te atomik yazsın. Hill-climb bütçesi tek yerde (%30 kuralı).
- [ ] Test ekle (`tests/test_capset_seed.py`): kısa bütçeyle (env
      `CAPSET_SEED_TIME_S=2`, gerçekten `env=` ile geçir!) CLI koş; çıktı
      dosyası VAR, feasible ve |S| ≥ 1 olsun. Ek olarak: bütçenin ilk
      yarısında dosyanın oluştuğunu sına (ör. subprocess'i 2 sn bütçeyle
      başlat, ~1 sn sonra dosyanın varlığını kontrol eden bir polling testi —
      flake'e karşı toleranslı yaz).

## Görev 2 — Test zafiyetleri

- [ ] `tests/test_capset_seed.py:111-116`: `env_time` değişkeni tanımlanmış ama
      `subprocess.run`'a geçilmemiş → süre bütçesi testi hiçbir şey sınamıyor
      ve test 10 sn sürüyor. Düzelt: `env=dict(os.environ,
      CAPSET_SEED_TIME_S="2")` geç; duvar saati < 8 sn assert et.
- [ ] `tests/test_capset_seed.py:53-59`: determinizm testi duvar saatine bağlı
      (yüklü makinede flake). Değiştir: determinizmi saf fonksiyonlar
      üzerinden sına — aynı `seed` ile üretilmiş aynı `order` için
      `_greedy_construct + _extend` çıktısı birebir eşit (zaman yok). `solve()`
      düzeyinde ise n=2'de bol bütçeyle `len == 4` (doygunluk; optimuma
      doyduğundan restart sayısından bağımsız, flake'siz).
- [ ] `tests/test_capset_enumerate.py`: (a) n=2 ve n=3 için
      `r["proven"] is True` assert'i ekle (P4.2'nin asıl iddiası şu an hiç
      test edilmiyor); (b) n=4 + `time_limit_s=0.01` için
      `r["proven"] is False` ve `r["size"] >= 1` assert'i ekle; (c) satır
      29'daki ölü `inst = ... if False else None` satırını sil; (d)
      `NamedTemporaryFile(delete=False)` yerine pytest `tmp_path` fixture
      kullan (temp dosya birikintisi kalmasın).
- [ ] `tests/test_capset_objective.py:177`: `or v["fitness"] <= -1.0`
      disjunct'ını kaldır; doğru assert: `-2.0 <= f < -1.0` (bad_vector'da
      tam -2.0 dahil). -50 gibi bir değer bu testi GEÇMEMELİ.
- [ ] `tests/test_capset_objective.py:135-141`: yorum "None / sayı / liste"
      diyor ama yalnız `None` test ediliyor; `evaluate_text(inst, 42)` ve
      `evaluate_text(inst, ["012"])` fuzz vakalarını ekle (raise etmemeli).

## Görev 3 — objective/enumerate küçük davranış düzeltmeleri

- [ ] `objective.py:142`: `reported_size_matches` ham satır sayısıyla değil
      TEKİL vektör sayısıyla (`len(set(vecs))`) karşılaştırsın — duplicate'li
      çıktıda dürüstlük sensörü yanıltıcı. İlgili testi güncelle
      (`# size 3` + {00,00,01} → matches **False** olmalı).
- [ ] `enumerate.py` docstring'i: "leksikografik en küçük cap" vaadini gerçeğe
      uydur — kod ilk bulunan max-size cap'i tutuyor (greedy başlangıç eşitlik
      halinde korunur); garanti edilen DETERMİNİZM'dir, leks-minimallik değil.
      (Davranışı değiştirme; yalnız dokümantasyonu düzelt.)

## Görev 4 — Doküman/veri tutarlılığı

- [ ] **n=9 iddiası:** `docs/p4-problem-tanimi.md` (satır ~70) "çarpım
      sınırını eşitledi" ifadesi YANLIŞ (dokümanın kendi değerleriyle en iyi
      çarpım 2·512 = 1024 ≠ 1082; ayrıca çarpım konstrüksiyonu ALT sınır
      verir, "üst sınır" ifadesi de hatalı). Doğru kaynak: **Tyrrell 2022,
      "New lower bounds for cap sets", arXiv:2209.10045 → a(9) ≥ 1082.**
      WebFetch ile makaleyi teyit et; sonra üç yeri tutarlı düzelt:
      `docs/p4-problem-tanimi.md`, `docs/p4-baseline.md` kaynak sütunu,
      `problems/capset/baseline.py` `KNOWN[9]` (kaynak "Tyrrell 2022").
      FunSearch notebook'unun aynı değere ulaştığı notu kalabilir (ikincil).
      Spec (`problems/capset/CLAUDE.md` §2) ile dokümandaki ✅/⚠ çelişkisini
      de gider: teyitten sonra ikisi de ✅, teyit edilemezse ikisi de ⚠.
- [ ] **Kürasyon planı çelişkisi:** `problems/capset/CLAUDE.md` P4.4 satırı
      "n=6 bekçi" derken `docs/p4-baseline.md` "n=3 bekçi" diyor; n=6'da tohum
      77/112 (bol headroom) olduğundan bekçi olamaz. KARAR (uygula, tartışma):
      **bekçi = n=4** (tohum kanıtlı optimumda: 20), **gradyan = n=7 + n=8**,
      **holdout = n=6 ve n=9** (koşuya girmez; genelleme ölçümü). İki dokümanı
      ve CLAUDE.md P4.4 satırındaki `DISCOVERY_INSTANCE` örneğini buna göre
      düzelt (`capset-n7.cap;capset-n8.cap;capset-n4.cap`).
- [ ] **§4 plan/gerçek uyuşmazlığı:** `docs/p4-problem-tanimi.md` §4 ürün
      konstrüksiyonunu tohuma eklemeyi "zorunlu" ilan ediyor; P4.3 bilinçli
      olarak eklemedi (gerekçe CLAUDE.md P4.3'te). Dokümanı gerçeğe uydur:
      "zorunlu" ifadesini kaldır, verilen kararı ve gerekçesini yaz. Not:
      ürün konstrüksiyonu orta-n OPTİMAL kümeleri zaten üretemez
      (a(2)·a(3)=36<45, a(3)²=81<112) — n=5/6/7 pozitif kontrol boşluğu ancak
      literatürden somut küme bulunursa kapanır. Bir tur daha ara (Edel'in cap
      sayfaları, Hill 45-cap, Potechin 112-cap eki); bulunursa
      `data/capset/reference/`'a indir + doğrula + pozitif kontrol testi ekle;
      bulunamazsa `data/capset/reference/README.md`'deki "seed'in ürettiği küme
      boyutu tablodaki değere ulaşıyor" vaadini sil (yanlış vaat) ve boşluğu
      açıkça belgele.
- [ ] **`data/capset/reference/verify_capsets.py`:** (a) docstring'deki bozuk
      cümleleri düzelt ("makine-tarafli kani didn't", "baaimsiz"); (b)
      `.txt` ile `.pylist`'in AYNI küme olduğunu (küme eşitliği) kontrol eden
      adım ekle — README bunu iddia ediyor ama script sınamıyor.
- [ ] **`baseline.py` KNOWN tablosu:** rekor değerleri
      `data/capset/reference/known_values.csv`'ye taşı (kolonlar:
      n,value,status,source); `baseline.py` oradan okusun. Gerekçe: §0.5
      ruhu — referans değerlerin evi `data/*/reference/`. (Adaptör/solver bu
      dosyayı OKUMAZ; yalnız insan raporlama aracı okur.)
- [ ] Yazım hataları: `docs/p4-problem-tanimi.md` "atıfluyor"(58),
      "özgu"(140), "ürettpi"(166), "ewrilenebilirliği"(168); kaynakçada
      Pellegrino 1971 başlığı altında Hill'in makalesi gösterilmiş — doğru
      atıfı koy (bulamazsan "Pellegrino 1971, aktaran: Hill" biçiminde
      dürüst göster). §4 tablosunda n=7 satırı "a(n)" kolonunda 236
      gösteriyor — kolonu "bilinen en iyi (alt sınır)" diye yeniden adlandır
      ya da satırı `≥236` yap. `docs/p4-baseline.md:3` "n=3 optimuma ulasir"
      → "n=2/3/4 optimumda".
- [ ] Görev 1 tohum davranışını değiştirdiği için baseline tablosunu yeniden
      üret: `python -m problems.capset.baseline docs/p4-baseline.md`
      (değerler değişebilir; kürasyon notunu yeni plana göre yaz).

## Görev 5 — P4.4 hazırlığı (koşuyu BAŞLATMA)

- [ ] `problems/capset/prompt.md` yaz: evolve system_message metni.
      Şablon: `evolve/config.yaml`'daki kofn system_message'ının yapısı
      (Contract / Feasibility / Determinism / Resources / Goal başlıkları),
      içerik capset sözleşmesi: CLI `python solver.py <instance.cap>
      <output.txt>`; girdi `dimension n`; çıktı formatı (her satır bitişik n
      adet {0,1,2}; `# size K` beyanı yok sayılır ama loglanır; duplicate =
      ihlal); **anytime + atomik yazım zorunlu** (erken yaz, iyileştikçe yaz —
      Görev 1'deki desen); infeasible her feasible'ın altında puanlanır;
      ~50 sn duvar saati, tek process, stdlib(+numpy); ağ yok. **Bilinen
      rekor/hedef değer YAZMA** (§0.5). Amaç: MAXIMIZE |S|, S cap set.
- [ ] `evolve/config.capset.yaml` oluştur: `evolve/config.yaml` kopyası +
      system_message → prompt.md içeriği + `api_base:
      http://localhost:8318/v1` + model `glm-5` (Claude kotası korunuyor;
      8317/Opus'a dokunma) + `diff_based_evolution: false` (GLM'de diff %64
      kayıpla elenmişti — config.yaml notu). kofn config'ine DOKUNMA.
- [ ] `evolve/run.ps1`'in config yolunu nasıl seçtiğini oku. `-ConfigPath`
      benzeri bir parametre yoksa geriye-dönük uyumlu şekilde ekle (varsayılan
      mevcut `config.yaml` kalsın; kofn davranışı değişmesin). Bu, `harness/`
      yasağının DIŞINDA — evolve/ betiği eklenti değil, ama minimal dokun.
- [ ] Koşu öncesi kontrol listesini `problems/capset/CLAUDE.md` §7'ye ekle
      (yalnız fiilen doğruladığın komutlarla): pytest yeşil; `curl -s
      http://localhost:8318/v1/models` içinde `glm-5`; adaptör duman komutu
      (aşağıda); `CAPSET_SEED_TIME_S=50` env'inin koşu ortamında set edilmesi
      (runner 55 sn'de öldürür; 5 sn tampon).
      Adaptör duman: `DISCOVERY_PROBLEM=capset DISCOVERY_INSTANCE=
      "data/capset/instances/capset-n7.cap;data/capset/instances/capset-n8.cap;
      data/capset/instances/capset-n4.cap" DISCOVERY_SOLVER_TIMEOUT_S=55
      python harness/evolve_evaluator.py problems/capset/seed_solver.py`
- [ ] **DUR.** 5-iterasyonluk duman testini ve uzun koşuyu SEN BAŞLATMA —
      GLM Coding Plan kredisi pacing kararı insana ait. "P4.4 hazır" raporu
      ver: değişen dosyalar, yeni baseline tablosu, koşu komutu.

## Opsiyonel (zorunlu değil; süre kalırsa)

- [ ] `objective.py` doğrulayıcısını hızlandır: vektörleri tamsayıya kodla
      (base-3), çift döngüsünde tuple üretimini kaldır — 512-küme ~204 ms →
      hedef <50 ms (n=9'da ~1 sn → ~100 ms). Saf tamsayı kuralı korunur;
      önce mevcut testler yeşil kalmalı, sonra 512-küme süresini ölçüp
      CLAUDE.md §6 notunu güncelle.

## Bitiş kriteri

1. `python -m pytest tests/ -q` yeşil (tüm depo).
2. `python data/capset/reference/verify_capsets.py` yeşil (yeni küme-eşitliği
   kontrolü dahil).
3. Görev 5'teki adaptör duman komutu feasible skor üretiyor.
4. Bu dosyadaki tüm zorunlu kutular işaretli; `problems/capset/CLAUDE.md`
   faz listesine "P4.3b — inceleme düzeltmeleri ✓ (tarih)" satırı eklenmiş.
5. Evolve koşusu BAŞLATILMAMIŞ; hazır raporu verilmiş.
