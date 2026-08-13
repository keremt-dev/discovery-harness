# B4 — Kontaminasyon Analizi ve Savunması (C1 makalesi bölüm taslağı)

Tarih: 2026-08-13. Tehdit modeli: "LLM, LJCR tablolarını ve/veya bilinen
çözümleri eğitim verisinden ezberledi; 'yeniden keşif' aslında geri
çağırma (retrieval), evrim hattının katkısı yok."

## 1. Kanıt hattı (altı bağımsız gözlem + iki sonda)

**K1 — Kod muayenesi (2026-08-11):** kazanan genomda blok listesi,
tablo değeri ya da hücreye özgü sabit YOK; tek yoğun sayı literali
asal listesi `(2,3,...,31)`. `affine_blocks` her v=p^m için genel
türetim yapar (öteleme grubu + altuzay kapanışı + cosetler).

**K2 — Sızıntı hijyeni:** arşiv değerleri hiçbir prompt'a/config'e
yazılmadı (grep kanıtları commit geçmişinde); `DISCOVERY_ARCHIVE_BELOW`
eşiği (700) solver'a gitmeyen env; 620 sayısı döngünün hiçbir
girdisinde geçmedi.

**K3 — Konstrüksiyon-ötesi arama:** C(49,8,2)'de saf afin 56 verir;
arşiv 49. Eşitleme, evrilmiş yerel aramanın 7 blok kırpmasıyla geldi —
ezbere değil aramaya işaret eder.

**K4 — Afin-dışı transfer (B2):** afin konstrüksiyonun UYGULANAMADIĞI
4 hücrede (C(21,10,3), C(20,12,4), C(23,10,3), C(25,16,4)) eşitleme,
evrilmiş genel arama makinesiyle geldi; C(23,10,3)=24 önceki tüm
koşularımızın üstünde. Ezber hipotezi bu deseni açıklamaz.

**K5 — Thinking on/off ayrışması (B1):** ezber geri-çağırma ucuz bir
işlemdir; thinking gerektirmez. Aynı model thinking KAPALIYKEN 55
full-rewrite denemesinde afin çözümü bir kez bile üretemedi; AÇIKKEN
3/3 üretti. Mekanizma retrieval olsaydı iki kolda da görünürdü.

**K6 — Doğrulama bağımsızlığı:** her çözüm ham instance'tan kesin
sayımla doğrulanır; iddia "üretilmiş-geçerli artefakt" üzerinedir,
modelin beyanı üzerine değil. Kontaminasyon YORUMU etkiler (keşif mi
yeniden-keşif mi), GEÇERLİLİĞİ etkileyemez — ve biz zaten yalnız
yeniden-keşif/eşitleme iddia ediyoruz.

**S1 — Değer-bilgisi sondası (2026-08-13, thinking OFF, temp 0):**
"C(32,8,4) bilinen-en-iyi kaç?" → model değeri BİLMEDİĞİNİ beyan etti
("tahmin etmektense bilmiyorum derim"). Güvenilir sayı-ezberi yok.

**S2 — Doğrudan-artefakt sondası (2026-08-13, thinking ON, 64k token,
temp 0):** "kod yazmadan, düz metin olarak covering'i üret" →
596 sn muhakeme, TÜM token bütçesi tükendi (finish=length),
**sıfır blok üretildi**. Model artefaktı bağlam içinde elle inşa
EDEMİYOR. Aynı model, döngüde konstrüksiyonu 30 satırlık genel kod
olarak yazıp saniyeler içinde kusursuz üretti (3/3).

## 2. Kalibre edilmiş iddia

Ayrışma tablosu:

| Yetenek | Kanıt | Sonuç |
|---|---|---|
| Değeri hatırlama | S1 | güvenilir DEĞİL |
| Artefaktı doğrudan üretme | S2 | YAPAMIYOR (64k thinking'le bile) |
| Paradigmayı seçip KODA dökme | B1 (3/3) | thinking ile GÜVENİLİR |

Dolayısıyla iddia şu şekilde kalibre edilir: modelin ağırlıklarındaki
matematik bilgisi (afin geometrilerin covering verdiği — ders kitabı
bilgisi) İZİN VERİLEN bir kaynaktır, insan uzmanın literatür bilgisi
gibi. Katkı, bu örtük bilginin **evrimsel baskı + kesin doğrulayıcı +
kod yürütme** hattıyla doğrulanmış artefakta dönüştürülmesidir; ve bu
dönüşümün anahtarının muhakeme modu olduğu kontrollü deneyle
gösterilmiştir. FunSearch/AlphaEvolve literatürünün "rediscovery
oranı" metriği de aynı çerçeveyi kullanır.

## 3. Dürüst sınırlar

- S1/S2 "ağırlıklarda yok" KANITLAMAZ (söylememesi ≠ bilmemesi);
  gösterdiği şey güvenilir doğrudan erişimin yokluğudur.
- S2'nin başarısızlık modu token tükenmesi — farklı prompt/effort ile
  model bir ŞEYLER üretebilirdi (büyük olasılıkla geçersiz); sonda
  tek konfigürasyonda koşuldu, makalede böyle raporlanacak.
- GKP 1995 makalesi (arXiv math/9502238) neredeyse kesin eğitim
  verisindedir; "modelin afin ailesini bilmesi" varsayılan durumdur
  ve iddiamız buna dayanmaz, bununla uyumludur.
- kofn tarafında kontaminasyon riski zaten düşük: hedef makale 2025,
  benchmark ailesi bizim üretimimiz, kanıtlı optimumlar kendi
  enumeration'ımızdan.
