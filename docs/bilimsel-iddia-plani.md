# P1 Bilimsel İddia Planı — harness bu makaleyle nasıl bulgu üretecek

Tarih: 2026-08-03. Bağlam: `docs/p1-problem-tanimi.md` (formülasyon),
CLAUDE.md §1-2 (problem seçimi). Bu doküman "ne bulacağız ve iddiayı nasıl
savunacağız" sorusunun cevabıdır.

## 1. İddia şablonu

Harness'ın ürettiği her bilimsel iddia şu kalıptadır:

> "Bir LLM'in evrimsel döngüde yazdığı sezgisel çözücü, **hakemli
> literatürden alınmış tanımlı bir problemde**, **ölçülebilir şu sonucu**
> verdi — ve bu sonuç çözücünün beyanına değil, **matematiksel olarak kesin
> bir değerlendiricinin ham veriden yeniden hesabına** dayanıyor."

cvrp-discovery'de bu "BKS'ye %1,5 gap" biçimini aldı. P1'de daha güçlü bir
biçim mümkün, çünkü küçük boyutta **gerçek optimum kanıtlanabiliyor**
(exhaustive enumeration) — CVRP'de BKS'nin optimum olduğu bilinmiyordu.

## 2. Ozkut & Tütüncü 2025'in dört rolü

Makale hedef değil, altyapı taşıdır:

1. **Kanonik problem tanımı.** İddia uydurma bir problem üzerine kurulamaz.
   Weighted k-out-of-n:G (çok tipli) tanımı, Teorem 1 ve üç optimizasyon
   probleminin kısıt kümeleri makaleden birebir alındı ve doğrulandı.
2. **Enstrüman kalibrasyonu.** Evaluator'ümüz makalenin kendi sayısal
   tablolarına karşı test edildi (29/32 birebir; sapmaların makale baskı
   hatası olduğu kanıtlandı — `data/kofn/reference/verify_ozkut2025.py`).
   "Ölçüm aletimiz doğru" iddiasının kanıtı budur.
3. **Headroom tanımı.** Makale üç problemi de brute-force enumeration ile
   çözüyor, bunun büyük sistemlerde pahalı olduğunu kendisi söylüyor ve
   sonuçlarını "gelecekteki sezgisel/metasezgisel yöntemler için benchmark"
   diye konumluyor. Yayınlanmış benchmark seti YOK, yayınlanmış sezgisel
   YOK (atıf 0). Boşluk tam olarak burası.
4. **Bağımsız doğrulama muhatabı.** Yazarlar (İEU) iddia öncesi doğal
   hakem. Elimizdeki üç tablo hatası + iki gerçek optimum, temas için somut
   açılış.

## 3. Üç katmanlı iddia

- **Katman 1 — kanıtlanmış doğruluk (küçük n, M).** Enumeration'ın
  eriştiği her instance'ta optimum KANITLI. Evrilen sezgiselin bu bölgedeki
  başarısı kesin ölçülür: "enumere edilebilir K instance'ın X'inde kanıtlı
  optimumu buldu, kalanında ortalama gap %y."
- **Katman 2 — ölçek sınırının ötesi (büyük n, M).** Verifier asimetrisi:
  aday ÜRETMEK kombinatoryal patlar (n'nin M parçaya kompozisyonları), ama
  TEK adayın R'sini doğrulamak ucuz ve kesin kalır (tamsayı ağırlıkta
  ağırlık-DP; rasyonel aritmetik). n=500, M=15'te enumeration imkânsızken
  evrilen çözümün kalitesi yine tam olarak ölçülür. İddia: "exact yöntemin
  öldüğü bölgede doğrulanabilir kalitede çözüm üreten ilk yöntem."
- **Katman 3 — benchmark katkısı.** Alanın benchmark seti yok. Ürettiğimiz
  instance ailesi (küçük boyutta kanıtlı optimumlarıyla) kendi başına
  katkıdır; sonraki yöntemler buna karşı ölçülür.

## 4. Savunulabilirlik (reward hacking'e kapalılık)

- Evrilen çözücünün tek çıktısı bir tamsayı vektörü (n₁..n_M). R, maliyet
  ve fizibilite yalnızca evaluator tarafından ham instance'tan Fraction ile
  yeniden hesaplanır; çözücünün beyanı yok sayılır (ama
  `info.reported_matches` dürüstlük sensörü olarak kaydedilir).
- Çıktı formatı CVRP rotalarından bile küçük → hile yüzeyi dar.
- Ceza ölçeği instance'tan türetilir; hiçbir ihlal kârlı olamaz
  (infeasible fitness < her feasible fitness, kanıtı spec.py'de).
- İddia öncesi DAİMA sakin makinede bağımsız re-run + evaluator doğrulaması
  (CLAUDE.md §8).

## 5. Dürüst sınırlar (rapora aynen girecek)

- **Makalenin örnekleri evrim için fazla kolay** (M=3, n≤20; Tablo 6'da
  dört satır R≈1'de doymuş). Bunlar kalibrasyon içindir. Gerçek zorluk:
  M ve n büyük, k doyumsuz bölgede (maks ağırlığın ~%70-95'i), çoklu kısıt
  (maliyet + tip başına sınır). Instance ailesi bu "enumeration ölür,
  doğrulama yaşar" bölgesinde tasarlanır (Faz D).
- **Goodhart:** maksimize edilen tanımlı matematiksel R'dir; bakım
  maliyeti, tedarik gerçekliği, arıza korelasyonu değil. İddia daima "bu
  benchmark objective'inde" diye çerçevelenir.
- **Bağımlı (ortak stres) varyant** Fraction'a gelmez (Lomax integrali) →
  ancak kontrollü sayısal toleransla, ikinci aşamada.
- **Negatif sonuç da bulgudur:** evrim baseline'ı geçemezse "LLM-evrimi bu
  problem sınıfında şu koşullarda işe yaramadı" raporlanır; enstrüman ve
  benchmark katkısı yine geçerli kalır.

## 6. Çıktı paketi

1. **Gap tablosu** (Faz D→E): baseline greedy vs evrilen sezgisel vs
   kanıtlı optimum (küçük boyut) / enumeration-üstü boyutta mutlak R.
2. **Benchmark seti**: instance üreteci + dosyalar + küçük boyut kanıtlı
   optimumları + üretim kuralları (tohum, parametre dağılımları).
3. **Yöntem raporu**: harness mimarisi, kalibrasyon kanıtları (RAP-33
   33/33; Ozkut-Tütüncü tabloları + errata), evrim ayarları, dürüst
   sınırlar.
4. **Uzman doğrulaması**: Özkut/Tütüncü'ye benchmark + sonuç paketi;
   önerilen ilk temas içeriği `docs/ozkut-eposta-bilgi-notu.md` (artık ek
   olarak: tablo erratası + iki gerçek optimum bulgumuz).

## 7. Başarı kriterleri

| Seviye | Kriter |
|---|---|
| Enstrüman (Faz B-C) | Evaluator, kanıtlı optimumları bire bir buluyor; negatif kontroller doğru kodla düşüyor |
| Baseline (Faz D) | Greedy tohum, küçük boyutta optimuma ortalama gap'i belgelenmiş |
| Keşif (Faz E) | Evrilen sezgisel: (a) enumere edilebilir sette optimum oranı > baseline, (b) büyük sette baseline'ı istatistiksel olarak anlamlı farkla geçiyor, (c) bağımsız re-run'da tekrarlanıyor |
| Yayınlanabilirlik | (a)+(b)+(c) ve benchmark seti + uzman geri bildirimi |
