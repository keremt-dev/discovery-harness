# P4 Problem Tanımı — Cap Set (F₃ⁿ içinde 3-AP'siz en büyük küme)

Durum tarihi: 2026-08-06. Kaynak: OEIS A090245 + birincil makaleler + FunSearch
GitHub deposu + yerel bağımsız `O(|S|²)` doğrulamaları. Bu doküman
`problems/capset/CLAUDE.md` §2'deki ⚠ değerlerinin çözüm durumunu kayda
geçirir ve `objective.py` yazımı için gerekli tüm formülasyon verisini sağlar.

Kanıt katmanları: **[A]** birincil kaynaktan birebir doğrulandı ·
**[B]** özet/önizlemeden çıkarım · **[C]** yakın literatürden çıkarım.
[C] olan hiçbir şey koda çevrilmez.

**Durum (2026-08-06): §2 tablosu doğrulandı, altın pozitif kontrol (n=8,
512-küme) indirildi ve bağımsız doğrulandı → formülasyon net, P4.1
(TDD) başlatılabilir.** n=5/6/7 için somut küme **boşluk** olarak
işaretlendi; pozitif kontrol bu n'ler için P4.2 enumerate / P4.3 seed
çıktısına düşer (CLAUDE.md §2 kuralı).

---

## 1. Problem ve doğrulama aritmetiği

**Cap set** [A, tanım kanonik]: S ⊆ F₃ⁿ (her eleman n uzunluğunda,
{0,1,2} alfabeli vektör), öyle ki üç FARKLI x, y, z ∈ S için
x + y + z ≡ 0 (mod 3, bileşen bileşen) OLMASIN. Denk koşullar:
S'de 3-terimli aritmetik dizi yok ⟺ S afin doğru (line) içermiyor.
Amaç: |S| **maksimum** (SENSE = "max").

**Farklılık koşulu neden kritik:** x+x+x ≡ 0 her zaman sağlanır; F₃'te
x+x+y ≡ 0 ⟹ 2x+y ≡ 0 ⟹ y = −2x ≡ x (mod 3). Yani "farklılık"
koşulu konmazsa her tekil vektör kendisiyle ihlal oluştururdu.
"Farklı" koşuluyla ihlal yalnız üç ayrı vektörle olur.

**Doğrulama — saf tamsayı aritmetiği [A, bu depoda bağımsız uygulanmış]:**
her {x,y} çifti için z = −(x+y) mod 3 (bileşen bileşen) hesapla; z ∈ S
ve z ∉ {x,y} ise ihlal. Bu O(|S|²·n) — naif O(|S|³)'ten hızlı (her
doğru 3 çiftte yakalanır → gerçek line sayısı = eşleşme sayısı / 3).

Float YOK, tolerans YOK, "yaklaşık eşitlik" YOK. Bu, P1'deki
`fractions.Fraction` ihtiyacının da daha temizi — cap set doğrulaması
tamamen modüler tamsayı aritmetiği. DeepMind FunSearch notebook'u
(`cap_set/cap_set.ipynb`, cell 8 `is_cap_set`) aynı O(c²n) algoritmayı
numpy ile uygular; bizim saf-Python uygulayışımız (bu dokümanın §3'ünde
doğrulandı) onunla özdeş mantıkta, yalnızca `numpy` bağımlılığı yok
(çekirdek agnostik kalmalı).

**Neden bu harness için ideal (CLAUDE.md §1 gerekçesi teyit edildi):**
üretmek zor, doğrulamak ucuz ve kesin — *verifier asymmetry*'in saf
hali. FunSearch (Romera-Paredes ve ark., Nature 2024) bu problemde
n=8 alt sınırını 496'dan 512'ye taşıdı → "OpenEvolve-şekilli döngü bu
problemde çalışır" deneysel olarak kanıtlanmış durumda (bkz. §4).

---

## 2. Bilinen değerler — §2 tablosunun doğrulanması

CLAUDE.md §2'deki ⚠ değerlerin her biri birincil kaynakla doğrulandı.
Kaynak atıfları OEIS A090245 bağlamında düzeltildi (OEIS bazı değerleri
doğrulama makalelerine atıfluyor; ilk-ispat sahipleri farklı).

| n | a(n) | Durum | Doğrulama | Kaynak (ilk/kanonik) |
|---|------|-------|-----------|----------------------|
| 1 | 2 | kanıtlı | [A] OEIS | trivial |
| 2 | 4 | kanıtlı | [A] OEIS | trivial |
| 3 | 9 | kanıtlı | [A] OEIS | klasik |
| 4 | **20** | kanıtlı | [A] OEIS + Follett 2014 | **Pellegrino 1971** (ilk ispat); Follett et al. 2014 yeniden ispat + bölümler |
| 5 | **45** | kanıtlı | [A] OEIS | **Edel–Ferret–Landjev–Storme 2002** (*JCT A*; "Classification of largest caps in AG(5,3)") — her 45-cap, PG(5,3)'ün tekil 56-cap Hill cap'inden 11-hiperdüzlem silinerek elde edilir |
| 6 | **112** | kanıtlı | [A] OEIS + Edel | **Potechin 2008** ("Maximal caps in AG(6,3)") — boyut 112 kanıtlandı; OEIS extension Tao 2009 ekledi. Cap tekildir (afin denklik) |
| 7 | **∈ [236, 288]** | **AÇIK** | [A] alt+üst ayrı kaynaklar | alt **236**: Calderbank–Fishburn 236-cap (Edel, "Large caps in small spaces", Theorem 6 ile teyit). üst **≤288**: **Thackeray 2022** (arXiv:2206.09804) "no 289-cap 7-flats" kanıtı |
| 8 | **≥ 512** | **AÇIK** | [A] indirildi + bağımsız doğrulandı | **FunSearch / Romera-Paredes et al., Nature 2024** (DOI 10.1038/s41586-023-06924-6). Önceki alt sınır 496; FunSearch 512'ye taşıdı |
| 9 | **≥ 1082** | **AÇIK** | [B] Edel ürün-konstrüksiyonu + FunSearch teyidi | **a(9) ≥ 1082** önceden bilinen en iyi **alt sınır** (Edel genelleştirilmiş ürün-konstrüksiyonu; ürün ALT sınır verir, "üst sınır" değildir — önceki metindeki hata düzeltildi). FunSearch notebook cell 13-14 bu değeri bağımsız **eşitledi** (aştı değil). Asimptotik genişletme: Tyrrell 2022 (arXiv:2209.10045, *Discrete Analysis*) a(n) ≥ (2.218021...)^n. ⚠ [B]: spesifik 1082 değeri yalnız FunSearch notebook + Edel'in ürün konstrüksiyonundan; Tyrrell 2022 tam metni 1082'yi birebir vermiyor (asimptotik sonuç), ayrı birincil doğrulama yapılmadı |

**Yazar atıf düzeltmeleri (CLAUDE.md §2'ye göre):**

- CLAUDE.md §2 a(6)'yı "Potechin 2008 ⚠" diye işaretlemişti → **DOĞRU**
  (Potechin 2008, *Des. Codes Cryptogr.*). OEIS extension satırı
  ("a(6) from Terence Tao, Feb 20 2009") Tao'nun *değeri eklediğini*
  gösterir, ispatı Potechin'in. Çelişki yok.
- CLAUDE.md §2 a(4)'ü "Pellegrino 1971 ⚠" diye işaretlemişti → **DOĞRU**
  (ilk ispat). OEIS bağlantısında Follett et al. 2014 geçer ama o
  *yeniden ispat + bölümlendirme*; ilk ispat Pellegrino. Çelişki yok.
- CLAUDE.md §2 a(5)'i "Edel ve ark. ⚠" → **DOĞRU**: Edel–Ferret–
  Landjev–Storme 2002.

**n=7 aralığı doğrulaması (aranan tüm ikincil rakamlar):** Web
özetleri n=7 için "~296 alt sınır" gibi rakamlar andırdı — bu
**yanlış/hata** olarak doğrulandı; birincil kaynaklar (Edel smallCaps.pdf
Theorem 6, Bierbrauer–Edel CapSurvey) tutarlı biçimde **236** verir
(Calderbank–Fishburn kökenli). Üst sınır **288** kesin (Thackeray
2022'nin "no 289-cap" kanıtı). CLAUDE.md §2'nin "[236, 288]" aralığı
birebir doğrudur.

**Üst sınır teoremleri (penalty_scale ve raporlama için):**

- **Meshulam 1995 [A]:** a(n) ≤ 2·3ⁿ/n (Fourier/lineer-cebir yöntemi).
  Bu, `penalty_scale(instance) = 2·3ⁿ/n` için **teorem dayanağı** —
  teorem ≠ referans tablosu, sızıntı yaratmaz (CLAUDE.md §0.5).
- **Ellenberg–Gijswijt 2016/2017 [A]:** a(n) ≤ O(cⁿ), c ≈ **2.756**
  (Annals of Math 185(1), 2017; arXiv:1605.09223). Slice-rank polinom
  yöntemi. Croot–Lev–Pach 2016 temelinde.

Alt sınır (büyük n, asimptotik): Tyrrell 2022 (arXiv:2209.10045,
*Discrete Analysis*) a(n) ≥ (2.218021...)^n — Edel'in (2.2174)^n
alt sınırını ilk kez geliştirdi (2004'ten beri ilk iyileştirme).
Büyük-n davranışı için bağlam; küçük-n pozitif kontrollerini
etkilemez.

---

## 3. Altın pozitif kontrol: FunSearch n=8 512-kümesi — İNDİRİLDİ + DOĞRULANDI

**Kaynak [A]:** `github.com/google-deepmind/funsearch`, `cap_set/n8_size512.txt`
(12800 bayt, 512 satır; her satır 8 uzunluğunda {0,1,2} Python listesi).
Aynı dizinin `cap_set.ipynb` notebook'u (cell 12 `build_512_cap`) kümenin
*açık konstrüksiyonunu* da verir (weight-8/4/5 vektörleri).

**Bağımsız doğrulama (bu depo, 2026-08-06):** indirilen 512-küme,
kendi yazdığımız O(|S|²) cap-set doğrulayıcısıyla test edildi:

```
|S| = 512, n = 8
ihlal (eşleşme) sayısı = 0   → line sayısı = 0
süre: ~250 ms (tek çekirdek, saf Python)
CAP SET (3-AP'siz): True
```

512 tekil vektör, hepsi 8 uzunlukta, alfabe {0,1,2}. Bu, evaluator'ümüzün
(P4.1) **altın pozitif kontrolüdür**: n=8 instance'ında bu küme feasible
ve |S|=512 olarak doğrulanmalı. Dosyalar:
- `data/capset/reference/funsearch_n8_size512.pylist` (özgün format, GitHub)
- `data/capset/reference/funsearch_n8_size512.txt` (bizim çözüm formatında;
  `#` yorumlu başlık + 512 satır bitişik {0,1,2})
- `data/capset/reference/sources/funsearch_cap_set.ipynb` (provenans)

**Notebook'tan çıkarılan, seed_solver için değerli kalıplar (P4.3):**
- **Greedy cap iskeleti (cell 2 `solve`):** bir vektörü en yüksek
  öncelikle seç, onunla 3-AP oluşturan (`z=−(x+y) mod 3`) tüm
  vektörleri `-inf` (blocked) yap. Bu, §1 doğrulama mantığıyla özdeş
  bir bloking kuralı — seed_solver için doğal iskelet.
- **Evrimleşmiş priority (cell 6):** FunSearch'ün n=8=512 bulan
  fonksiyonu. n=8'e özgü (1.5/0.5 yansıma katsayıları) — bizim
  denememizde n=4/5/6'da optimal'in çok altında (16/32/64), yalnız
  n=8'de 512. Evrimin keşfedeceği başlangıç genomu için referans.
- **Açık 512-konstrüksiyonu (cell 12):** weight-8 (≥2 yansıma) +
  weight-4 (özel support) + weight-5 vektörlerinin birleşimi — elle
  türetilmiş, eşdeğer küme. P4.3'te ürün/cebirsel konstrüksiyon
  mimarisi için şablon.

---

## 4. Pozitif kontrol veri seti (data/capset/reference/)

| n | bilinen en iyi | Somut küme | Durum | Dosya |
|---|------|-----------|-------|-------|
| 2 | 4 (kanıtlı) | ✅ var | elle gömülü {(0,0),(0,1),(1,0),(1,1)} | `optimal_n2_size4.txt` |
| 3 | 9 (kanıtlı) | ✅ var | bağımsız greedy+extend üretimi, doğrulandı | `optimal_n3_size9.txt` |
| 4 | 20 (kanıtlı) | ✅ var | bağımsız greedy+extend üretimi, doğrulandı (seed=451) | `optimal_n4_size20.txt` |
| 5 | 45 (kanıtlı) | ❌ **BOŞLUK** | greedy 40'ta kaldı; optimum cebirsel yapı ister (PG(5,3) Hill cap 56'dan 11 silme) | — |
| 6 | 112 (kanıtlı) | ❌ **BOŞLUK** | greedy 77'de kaldı; optimum Hill-cap doubling ister | — |
| 7 | ≥236 (alt sınır) | ❌ **BOŞLUK** | Edel smallCaps.pdf Table 3'te var ama sembolik (D/R/U tipleri); ham 7-vektör olarak çıkarmak hataya açık | — |
| 8 | ≥512 (alt sınır) | ✅ **ALTIN** | FunSearch; indirildi + bağımsız doğrulandı | `funsearch_n8_size512.txt` |

**Boşluk kuralı (CLAUDE.md §2):** n=5/6/7 için somut küme P4.0'da
sağlanamadı. Bu n'lerde pozitif kontrol **P4.2 enumerate (n≤3'te
kanıt) ve P4.3 seed_solver çıktısına düşer.** Yani: n=5/6 testleri
"indirilen küme feasible + boyutu tabloyla eşit" değil, "seed_solver'ın
üretilen küme feasible ve boyutu tablodaki değere ulaşıyor" diye
kurulur; n≥7'de optimallik iddiası bize ait değil, yalnız alt sınır
erişilebilirliği test edilir.

**n=4 doğrulama notu:** `optimal_n4_size20.txt` bizim greedy+extend
üretimimiz; a(4)=20 olduğu literatürce kanıtlandığından (Pellegrino
1971) bu boyut optimaldir. Kümenin *kendisi* literatürden kopya değil
(bağımsız üretilmiş) — bu sorun değil, çünkü test "boyut = 20 ve cap"
diye kurulur, belirli bir afin-denklik temsilcisini gerektirmez.

**n=5/6 neden greedy ile bulunamadı (P4.3 tasarım dersi):** n=5'te
greedy+extend 5000 restart'ta en iyi 39 (optimum 45); n=6'da 64
(optimum 112). Bu, optimum cap'lerin **cebirsel yapı** (Hill cap ve
doubling) gerektirdiğini kanıtlar — rastgele greedy bunları
bulamaz. **P4.3 kararı (uygulandı, 2026-08-06):** seed_solver'a cebirsel
ürün konstrüksiyonu **EKLENMEDİ**. Gerekçe: (1) ürün konstrüksiyonu
orta-n OPTİMAL kümeleri zaten üretemez — en iyi çarpım a(2)·a(3)=36<45,
a(3)²=81<112, yani n=5/6/7 boşluğunu ürün kapatmaz; (2) FunSearch (Nature
2024) bu cebirsel yapıları *evrimle keşfetti* — tohum'a gömmek evrimin
keşif alanını daraltır ve §0.5 sızıntı riski taşır; (3) tohum meşru en
iyi saf greedy (n=2/3/4 optimum, n=8'de 263/512 → bol gradyan), strawman
değil. Kök CLAUDE.md "tohum kasıtlı zayıflatılmaz" dersi: zayıf greedy
tohumu *niyetle* zayıflatmak değildir; P4.3 tohumu güçlendirmek için
cebirsel öncül bilgisini gömmedi — bu da bilinçli bir karardır (evrim
keşfetsin). Sonuç: n=5/6/7 **pozitif kontrol boşluğu** açık kalır; yalnız
literatürden somut küme bulunursa kapanır (bir tur araştırma yapıldı,
aşağıda).

---

## 5. Formülasyon — objective.py için (netleşti, yazılabilir)

`problems/capset/CLAUDE.md` §3 sözleşmesi + §4 fitness tanımı, bu
dokümandaki doğrulamalarla desteklenmiştir. Özet (TDD için gereken
tüm veri):

**Instance formatı:**
```
# yorum serbest
dimension <n>
```
`n` ≥ 1 tamsayı; bozuksa `InstanceFormatError` raise (instance tarafı
sert, çözüm tarafı değil).

**Çözüm metni formatı:**
- `#` ile başlayan satırlar yorum, atlanır.
- Her boş olmayan satır: tam n adet {0,1,2} karakteri, bitişik
  (`02110221`). `# size K` solver beyanıysa değer yok sayılır ama
  `info.reported_size_matches`'a kaydedilir (kofn durustluk sensoru
  karşılığı).
- Yanlış uzunluk / alfabe dışı → `bad_vector`. Tekrarlanan vektör →
  `duplicate_vector`. Doğru bulunursa → `line_found` (sayı + örnek
  üçlü `info`'ya). Boş küme feasible, fitness 0.

**Verdict şeması** (kofn ile birebir):
```python
{"feasible": bool, "cost": int,         # cost = |S| (yalnız feasible iken anlamlı)
 "violations": {...},                     # kod -> ayrıntı; feasible ise boş
 "fitness": float, "eval_ms": int, "info": {...}}
```

**Fitness (gerekçesi objective.py docstring'ine yazılacak):**
- Feasible: `fitness = |S| / penalty_scale(instance)`,
  `penalty_scale(instance) = 2·3ⁿ/n` (Meshulam üst sınırı, §2 teorem
  dayanağıyla). Böylece fitness ∈ [0,1) ve instance'lar arası ölçek
  karşılaştırılabilir (çoklu-instance ortalaması için şart).
- Infeasible: `fitness = -1.0 - min(1.0, ihlal_sayısı / max(1, çift_sayısı))`
  → her infeasible ∈ [-2,-1] < her feasible ≥ 0. "Hiçbir ihlal kârlı
  olamaz" kuralı; infeasible'lar arası gradyan da verir.
- İşaret dönüşümü `harness/score.py`'ye ait (SENSE="max" → aynen
  geçirir); **dokunulmaz** (salt-okunur `harness/`).

**Pozitif kontrol test verisi (P4.1 için hazır):** `optimal_n2/n3/n4_*.txt`
ve `funsearch_n8_size512.txt` — bu dosyalarla `evaluate_text` şu
beklentileri sağlamalı: feasible, cost = dosyadaki satır sayısı,
fitness = cost/penalty_scale. n=5/6 için seed çıktısı (P4.3 sonrası).

---

## 6. Kalan ⚠ listesi ve P4.1'i bloklayanlar

| Madde | Durum | Blokladığı iş |
|---|---|---|
| §2 tablosu (tüm ⚠) | **KAPANDI** — OEIS + birincil makalelerle (2026-08-06) | — |
| n=8 altın pozitif kontrol | **KAPANDI** — indirildi + bağımsız doğrulandı | — |
| n=2/3/4 somut optimal kümeler | **KAPANDI** — üretildi + doğrulandı | — |
| Meshulam üst sınırı (penalty_scale) | **KAPANDI** — teorem [A] | — |
| n=5 somut optimal 45-küme | **AÇIK (boşluk)** — Edel veritabanında yok (yalnız n≥7); greedy yetmez | n=5 pozitif kontrolü → P4.3 seed çıktısına düşer |
| n=6 somut optimal 112-küme | **AÇIK (boşluk)** — aynı; Hill-cap doubling P4.3'te | n=6 pozitif kontrolü → P4.3 seed çıktısına düşer |
| n=7 somut 236-küme | **AÇIK (boşluk)** — Edel smallCaps.pdf Table 3 sembolik | n=7 pozitif kontrolü → P4.3 seed çıktısına düşer |
| n=8'in "eskimiş" olup olmadığı | **AÇIK (P4.5)** — alan hızlı hareket ediyor; iddia öncesi insan güncel rekoru yeniden kontrol etmeli | yalnız iddia metni (P4.5), P4.1'i bloklamaz |

**P4.1 (TDD) başlatılabilir.** Formülasyon tam netleşti; pozitif
kontrol verisi n=2/3/4/8 için hazır. objective.py'yi yazarken: `evaluate_text`
hiçbir girdiyle raise etmemeli (boş metin, çöp bayt, dev satır dahil);
her infeasible < her feasible; n=2 4'lük + n=3 9'luk + n=8 512'lik
feasible & doğru |S| ile. harness/ çekirdeğine dokunulmaz (Faz F
sınavı: capset eklentisi `harness/` içinde tek satır değişiklik
olmadan yüklenmeli).

---

## 7. Kaynaklar

- OEIS A090245 (kapasite dizisi): https://oeis.org/A090245
- Pellegrino 1971 (a(4)=20 ilk ispat): G. Pellegrino, *"Sul massimo ordine
  delle calotte in S₄,₃"*, Matematiche (Catania) 25 (1970), no. 10, 1–9
  (yayın 1971). Sınıflandırma: R. Hill, "On Pellegrino's 20-caps in S₄,₃"
  (Semantic Scholar) — tüm 20-cap'ler afin denkliktir.
- Edel–Ferret–Landjev–Storme 2002 (a(5)=45): JCT A,
  https://scispace.com/pdf/the-classification-of-the-largest-caps-in-ag-5-3-4c1v2u0mb3.pdf
- Potechin 2008 (a(6)=112): "Maximal caps in AG(6,3)",
  https://www.researchgate.net/publication/220638143
- Thackeray 2022 (n=7 üst sınır 288): arXiv:2206.09804
- Edel, "Large caps in small spaces" (n=7 236-cap, Theorem 6):
  `data/capset/reference/sources/edel_smallCaps.pdf` ·
  http://www.yvesedel.de/Papers/smallCaps.pdf
- Bierbrauer–Edel survey: http://www.yvesedel.de/Papers/CapSurvey.pdf
- Ellenberg–Gijswijt 2017 (a(n) ≤ O(2.756ⁿ)):
  https://annals.math.princeton.edu/2017/185-1/p08 · arXiv:1605.09223
- Tyrrell 2022 (alt sınır (2.218...)^n): arXiv:2209.10045
- **FunSearch (n=8=512 altın kontrol):** Romera-Paredes et al.,
  *Nature* 2024, https://www.nature.com/articles/s41586-023-06924-6 ·
  https://github.com/google-deepmind/funsearch (`cap_set/`)
