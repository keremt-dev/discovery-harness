# P1 Problem Tanımı — Weighted k-out-of-n:G (çok tipli)

Durum tarihi: 2026-08-03. Kaynak: üç paralel web-araştırma ajanı raporu +
yerel `fractions.Fraction` doğrulamaları. Bu doküman CLAUDE.md §4'teki
⚠ DOĞRULANACAK maddelerinin çözüm durumunu kayda geçirir.

Kanıt katmanları: **[A]** birincil kaynaktan birebir doğrulandı ·
**[B]** özet/önizlemeden çıkarım · **[C]** yakın literatürden çıkarım.
[C] olan hiçbir şey koda çevrilmez.

**Durum (2026-08-03 güncellemesi): tam metin elde edildi, formülasyon
doğrulandı → `objective.py` yazılabilir.** Aşağıdaki §1 tam metne göre
yeniden yazılmıştır.

---

## 1. Hedef makale: Ozkut & Tütüncü 2025 — TAM METİN ELDE, FORMÜLASYON [A]

Künye [A] (Crossref + DBLP + OpenAlex + İEU GCRIS uyumlu):

> Murat Ozkut, G. Yazgı Tutuncu, *"Reliability analysis and optimization
> problems for a weighted-k-out-of-n:G system with multiple types of
> components"*, **Computers & Industrial Engineering 210 (Aralık 2025),
> makale 111513**. DOI: `10.1016/j.cie.2025.111513`.
> ScienceDirect PII: S036083522500659X. Atıf sayısı (2026-08): 0.
> PDF: `data/kofn/reference/sources/ozkut_tutuncu_2025.pdf` (kullanıcı
> sağladı); çıkarılmış metin: aynı dizinde `.txt`.

**Model ve gösterim [A, tam metinden]:** n bileşen, **M ≥ 2 tip**. Tip j:
ζ_j adet bileşen, ağırlık ξ_j, güvenilirlik p_j (Σζ_j = n). N_j = tip j'nin
çalışan bileşen sayısı ~ Binom(ζ_j, p_j). Sistem, çalışan bileşenlerin
toplam ağırlığı ≥ k ise çalışır. **Ağırlıklar gerçel olabilir** (bağımlı
örnekte ξ = (2, 1.9, 2.1)).

**Teorem 1 (bağımsız durum, non-recursive) [A, birebir]:**

```
R = Σ_{ξ₁n₁+...+ξ_M n_M ≥ k, 0≤n_j≤ζ_j}  Π_j C(ζ_j, n_j) p_j^{n_j} (1-p_j)^{ζ_j-n_j}
```

Fraction ile tam hesaplanabilir (p_j ondalık → kesir). Dinamik uzantı:
p_j yerine F̄_j(t) konarak sağkalım fonksiyonu (Eq. 2), MTTF = ∫ (Eq. 3).

**Üç optimizasyon problemi [A — metin + Appendix A.7 Mathematica kodundan
çapraz doğrulanmış]:** karar değişkenleri tip adetleri (n₁..n_M), tamsayı.

1. **P-i, maliyet min:** `min Σ c_j·n_j  s.t.  R(n₁..n_M) ≥ r₀, Σ n_j = n`.
   Örnekte r₀ = 0.80.
2. **P-ii, güvenilirlik maks:** `max R  s.t.  Σ c_j·n_j ≤ C₀, Σ n_j = n`.
   Örnekte C₀ = 30. ⚠ Baskıdaki formülasyonda bir de "R ≥ r₀" satırı var
   ama kodda `r0 = 0` → fiilen pasif.
3. **P-iii, optimal değiştirme zamanı:** age replacement;
   `M(T) = (Σc_j n_j + c·(1−R(T))) / ∫₀ᵀ R(t)dt` minimize edilir
   (üstel ömürler; kodda FindMinimum). Baskıdaki Eq. (10) ile kod aynı
   (numeratör `(Σc_jn_j)·P{R>T} + (Σc_jn_j + c)·P{R≤T}` olarak parse edilir).

**⚠ Kritik: `Σ n_j = n` kısıtı baskıda görünmüyor** ("0 ≤ n_j ≤ n" yazıyor)
ama Mathematica kodunda kesin (`If[n1+n2+n3 == n, Sow[...]]`) ve 28 tablo
satırının tamamında Σ = n sağlanıyor. Toplam bileşen sayısı SABİT; arama
uzayı n'nin M parçaya kompozisyonları.

**Çözüm yöntemi [A]:** brute-force enumeration (Appendix A.3–A.5,
flowchart'lar; Mathematica kodu A.7). Makale kendisi bunu "benchmark for
future heuristic or metaheuristic solutions" diye konumluyor — evrilen
sezgiselin karşılaştırma zemini hazır.

**Bağımlı durum [A]:** ortak stres modeli (stress–strength: X_i = 1{η_i > β},
β ortak rastgele stres); R, tip-düzeyi binom çarpımlarının stres dağılımı
üzerinden integrali (Eq. 4–5). Örneklerde Lomax dağılımları; kodda integral
∞ yerine 0..20'ye kesilmiş (sayısal yaklaşım). **Fraction ile tam hesap
mümkün değil** → bağımlı alt-aile ancak kontrollü sayısal toleransla, ikinci
aşamada ele alınır.

### Sayısal tabloların bağımsız doğrulaması (verify_ozkut2025.py)

Tüm değerler Fraction ile yeniden hesaplandı
(`data/kofn/reference/verify_ozkut2025.py`, son koşu: 0 uyumsuzluk kendi
değerlerimize göre). Makaleye göre durum:

- **Tablo 5 (P-i ground truth): 13/14 birebir.** Tek fark: (0,8,2) k=10
  tam değer 0.92284670 → doğru baskı 0.9228; makale 0.9229 (son hane
  hatası).
- **Tablo 6 (P-ii ground truth): 12/14 birebir.** İki satır makale içi
  tutarsız (sayfa 7 görsel olarak da teyit edildi): (n=10,k=15) baskı
  "(5,5,0) C=25 R=1" — C=25'lik config aslında (5,0,5) ve R=0.99990;
  gerçek optimum (10,0,0) C=30 R=0.99999986. (n=15,k=15) baskı "(0,12,3)
  C=28 R=1" — o config'in R'si 0.94010; gerçek optimum (1,1,13) C=30
  R=0.99999961.
- **Tablo 1: k=10 satırları 4/4 birebir** → ξ=(3,1,2) ve "≥ k" semantiği
  kesinleşti. k=15/k=20 ve p-varyasyon satırları hiçbir makul parametre
  okumasıyla üretilemedi (ağırlık permütasyonu × eşik kayması taraması
  yapıldı; makale içi hata, kaynağı belirsiz — kalibrasyonda KULLANMA).
- Ders: makale tablolarında bile baskı hataları var — "beyana güvenme, ham
  veriden yeniden hesapla" ilkesi burada da doğrulandı. Kalibrasyon hedefi
  olarak yalnızca bizim Fraction değerlerimiz kullanılır.

**Instance tasarım dersi:** k, ulaşılabilir toplam ağırlığa göre düşükse
problem R≈1'de doyuma gidiyor ve optimumlar beraberliğe düşüyor (Tablo 6'da
dört satır "R=1") → üreteceğimiz benchmark ailesinde k doyumsuz bölgeden
seçilmeli (ör. maks ağırlığın %70–95'i) ve/veya r₀ agresif konmalı.

**Düzeltme — "2024 makalesi" hayalet çıktı [A-negatif]:** CLAUDE.md §7'de
anılan *"On weighted-k-out-of-n: G systems with multiple types of
components" (2024)* ayrı bir yayın olarak Crossref/DBLP/OpenAlex/İEU
deposunda YOK. Muhtemelen Google Scholar'ın 2025 makalesine ait hayalet
kaydı ya da şu farklı-yazarlı makaleyle karışma: Hamdan, Asadi, Tavangar,
*QTQM* 21(5):656-673, DOI `10.1080/16843703.2023.2238339` (survival
signature yaklaşımı — metodolojik akraba ama Tütüncü grubundan değil).

**Benchmark seti yayınlanmamış [A]** → CLAUDE.md'nin "headroom bizde"
varsayımı doğrulandı: instance ailesini biz üreteceğiz.

---

## 2. Pozitif kontrol seti: klasik RAP-33 — TAMAMEN DOĞRULANDI

**Önemli ayrım:** klasik set weighted k-out-of-n **değildir**. Fyffe–
Hines–Lee (1968) sistemi 14 alt-sistemli **seri-paralel RAP**'tır (her
alt-sistem 1-out-of-n:G, alt-sistem başına 3-4 bileşen seçeneği,
her seçenek r/c/w üçlüsü). Pozitif kontrol olarak kullanımı §4'teki
tasarım kararını gerektirir.

- **Veri:** [data/kofn/reference/verify_fyffe.py](../data/kofn/reference/verify_fyffe.py)
  — bileşen tablosu (Liang & Smith CEC 1999 Table 1'den) + Coit & Smith
  1996 Appendix'in 33 çözüm vektörü. Doğrulama: her vektör Fraction ile
  yeniden hesaplandı; R/maliyet/ağırlık **33/33 birebir** (0 uyumsuzluk).
  Tek rakam hatası en az bir satırı bozacağı için transkripsiyon hatası
  fiilen dışlanmıştır.
- **Instance şeması [A]** (iki makalede birebir aynı ifade): **C=130
  sabit; W ∈ {159..191}** (33 tamsayı değer). Orijinal FHL problemi
  W=170. k_i = 1 (∀i); amaç sistem güvenilirliği maksimizasyonu.
- **İki formülasyon çeşidi — sonuçlar karıştırılmaz:** (a) N&M 1981:
  alt-sistem içinde yalnız *özdeş* bileşen; (b) Coit & Smith 1996 ve
  sonrası: *karışık* bileşen, alt-sistem başına ≤ 8. Optimum etiketleri
  (b) uzayına aittir. N&M referans kolonunda infeasible/yakınsamamış
  değerler var (Coit & Smith'in uyarısı) — N&M kolonu hedef alınmaz.
- **İndeksleme tuzakları:** (a) yayınlanmış çözüm vektörleri bileşenleri
  **güvenilirliğe göre azalan** sırayla yeniden indeksler (ham tablo
  sırası değil; alt-sistem içi beraberlik yok, sıralama tekil);
  (b) instance numarası iki yönde de kullanılıyor — C&S: no.1=W191,
  Yeh: ID1=W159. **Daima W ile anahtarla, numarayla değil.**

---

## 3. Kanıtlanmış optimumlar (karışık-bileşen ≤8 uzayı)

- **Caserta & Voß düzeltmesi:** doğru künye **EJOR 244(1):110-116, 2015**
  (2016 değil), *"An exact algorithm for the reliability redundancy
  allocation problem"*, DOI `10.1016/j.ejor.2015.01.008`. RAP'ı multiple
  choice knapsack'e dönüştürüp branch-and-cut ile milisaniyeler içinde
  optimal çözüyor [A, RePEc özeti]. 2016 karışıklığı aynı ikilinin
  2015/2016 companion makalelerinden. **Kendi tablosu paywall'da —
  hiçbir açık kaynaktan erişilemedi (GAP).**
- **Açık sertifikasyon zinciri:** optimum değerler
  [data/kofn/reference/optima_rap33.csv](../data/kofn/reference/optima_rap33.csv)
  dosyasında. Kaynak: Yeh, arXiv:2204.04472, Table 6 (**BRB exact
  algoritması, 11 hane**; kaynak metin kopyası
  `data/kofn/reference/sources/bat_paper.txt`, değerler metinden grep ile
  teyitli). Bağımsız 6-hane çaprazı: Nahas & Nourelfath, IJMEMS 6(1),
  2021, Table 4 (GA/TS/ACO/HSA en iyileri; kopya `sources/ijmems.txt`) —
  **33/33 uyum, 0 çelişki**. Bilinen iki dizgi hatası (IJMEMS W=160 ACO
  kolonu, W=159 truncation) yayılmayacak.
- **Kendi bütünlük kontrolümüz** (scratchpad `diff_cs_vs_optima.py`,
  2026-08-03): exact-Fraction C&S değerleri hiçbir instance'ta sertifikalı
  optimumun üstünde değil (**0 alarm**). Maddi iyileşme (>1e-6) **25
  instance'ta**: W=159, 160, 162, 169 ve 171-191; kalan **8'inde C&S 1996
  optimumu zaten bulmuş** (W=161, 163-168, 170; fark ≤1e-8 = baskı
  hassasiyeti).
- **C&V'nin "21 yeni en iyi" iddiası:** cümle yalnız arama motoru
  snippet'inde görüldü, doğrudan doğrulanamadı; 21'in kimliği hiçbir açık
  kaynakta yok. Kendi diff'imiz "C&S'e göre 25" verdiği için "21"
  muhtemelen 2015'teki best-known tabanına (TS 2003 / ACO 2004 dahil)
  göredir. **GAP olarak kalır; rekor iddiamız için gerekli değil** —
  bizim hedef kolonumuz sertifikalı optimum kolonudur.
- **⚠ Konvansiyon şartı:** "optimum" etiketi **alt-sistem başına ≤8
  bileşen** varsayımına bağlıdır (Yeh, C&V dahil önceki exact yöntemlerde
  bu sınırın belirsizliğini açıkça eleştirir). `problems/*/spec.py`
  dosya formatı sözleşmesine bu sınır açıkça yazılacak.
- Zorluk kalibrasyonu notu: SSO (Yeh 2014) 33'ün 31'inde optimumu 6 haneye
  kadar bulmuştu; istisnalar **W=187** ve **W=190**. Evrimsel koşunun
  "kolay/zor" instance beklentisi buna göre kurulabilir.

---

## 4. Faz B tasarım kararları

**Öneri (karar kullanıcının):** iki ayrı problem eklentisi.

1. **`problems/rap33`** — pozitif kontrol enstrümanı: klasik seri-paralel
   RAP, veri ve optimumlar hazır (bkz. §2-3). Evaluator'ün doğruluğu
   33 bilinen optimumla bire bir ölçülür; ayrıca harness agnostikliği
   (Faz F sınavı) daha ilk problemde fiilen test edilmiş olur.
2. **`problems/kofn`** — ana hedef: 2025'in çok tipli weighted
   k-out-of-n:G modeli. Instance'ları biz üretiriz (M tip; p_i, w_i, c_i;
   k eşiği; bütçe); küçük n'de **exhaustive enumeration ground truth**
   (Faz C). Makale-birebir optimizasyon aynası, kısıt kümesi PDF'ten
   doğrulanınca ayrı alt-aile olarak eklenir.

Gerekçe: iki yapı matematiksel olarak farklı (seri-paralel ≠ tek katman
ağırlık eşiği); tek eklentiye sıkıştırmak evaluator'ü bulanıklaştırır.
Alternatif (tek `kofn` eklentisi, RAP-33'ü eklenti dışı kalibrasyon
script'i olarak tutmak) daha az iş ama Faz C kanıtı zayıflar.

Değişmeyen kurallar: doğrulama hesabı `fractions.Fraction` ile tam
rasyonel; karşılaştırma 6 haneye yuvarlama + 1e-9 tolerans; `fitness ≠
cost`; ceza ölçeği instance'tan türetilir; referans değerler sandbox'a
girmez.

**Kalan ⚠ listesi:**

| Madde | Durum | Blokladığı iş |
|---|---|---|
| 2025 makalesinin tam kısıt kümesi | **KAPANDI** (2026-08-03, PDF elde; formülasyon §1'de, tablolar verify_ozkut2025.py ile doğrulandı) | — (objective.py yazılabilir) |
| Bağımlı (ortak stres) alt-ailenin tam-aritmetik doğrulaması | AÇIK — Lomax integrali Fraction'a gelmez; kontrollü sayısal tolerans tasarlanacak | bağımlı alt-aile (ikinci aşama) |
| C&V 2015'in kendi baskı tablosu | AÇIK (opsiyonel) — Yeh+IJMEMS sertifikasyonu yeterli | — |
| "21 yeni en iyi"nin kimliği | AÇIK (opsiyonel, bilimsel merak) | — |
| RAP-33 verisi + optimumlar | **KAPANDI** | — |
| MMKP benchmark seti (P2) | AÇIK (CLAUDE.md §7, değişmedi) | Faz F |

---

## 5. Kaynaklar

- Ozkut & Tutuncu 2025: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S036083522500659X) · [Crossref](https://api.crossref.org/works/10.1016/j.cie.2025.111513) · [İEU GCRIS](https://gcris.ieu.edu.tr/handle/20.500.14365/6443)
- Caserta & Voß 2015: [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0377221715000284) · [RePEc özeti](https://ideas.repec.org/a/eee/ejores/v244y2015i1p110-116.html)
- Yeh BRB (sertifikalı optimumlar): [arXiv:2204.04472](https://arxiv.org/pdf/2204.04472)
- Nahas & Nourelfath 2021 (6-hane çapraz): [IJMEMS PDF](https://www.ijmems.in/volumes/volume6/number1/26-IJMEMS-SBS19-31-6-1-416-441-2021.pdf)
- Coit & Smith 1996 (veri + 33 çözüm): [compie.pdf](https://www.eng.auburn.edu/~smithae/files/compie.pdf)
- Liang & Smith 1999 (bileşen tablosu): [cec99yc.pdf](https://www.eng.auburn.edu/~smithae/files/cec99yc.pdf)
- Hamdan, Asadi & Tavangar (metodolojik akraba): [QTQM](https://www.tandfonline.com/doi/abs/10.1080/16843703.2023.2238339)
- Eryilmaz & Sarikaya 2014: [SAGE](https://journals.sagepub.com/doi/10.1177/1748006X13515647) · Eryilmaz & Ozkut 2020: DOI `10.1016/j.ress.2020.106911` · Franko, Tütüncü & Eryılmaz 2017: DOI `10.1080/03610918.2015.1096377`
