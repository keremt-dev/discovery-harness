# Yayın Bulgu Özeti — 2026-08-11 itibarıyla

Bağlam: `docs/bilimsel-iddia-plani.md` (iddia şablonu ve katmanlar),
CLAUDE.md Faz P5 (olay kaydı). Bu doküman üç soruya cevaptır:
(A) bugün sunulabilir bulgular, (B) kapatılabilir eksikler,
(C) yayın adayları.

## A. Bugün sunulabilir bulgular (kanıt zinciri tamam)

### A1. Probleme-agnostik harness, üç problem sınıfında uçtan uca
kofn (P1) → capset (P4) → covering (P5), `harness/` çekirdeğinde tek
satır değişiklik olmadan. Kesin-aritmetik evaluator disiplini
(Fraction / tam sayım), ceza ölçeği instance'tan türetme, fitness≠cost
ayrımı, çözüm arşivleme kancası, çok-seed ortalamalı fitness.

### A2. P1 (kofn) — üç katmanlı sonuç (iddia planındaki şablon dolu)
- Enstrüman kalibrasyonu: Ozkut–Tütüncü 2025 tabloları 29/32 birebir;
  3 satırın baskı hatası olduğu KANITLI + iki satırın gerçek optimumu
  bulundu (**errata bulgusu — kendi başına yayın parçası**).
- Kanıtlı-optimum katmanı: enumere edilebilir instance'larda evrilen
  çözücü optimumda (benchmark-v2 sonrası 8/8 küçük katman).
- Ölçek katmanı: router-n500'de skor 1.000000 (tohum 0.9738'i geçti);
  genelleme açığı holdout'ta kapandı. Yapısal keşif: K-kesimli
  absorbing konvolüsyon DP (O(K)).
- Benchmark ailesi: üreteç + kanıtlı küçük-boyut optimumları
  (alanın yayınlanmış benchmark seti YOK — boşluk bizim).

### A3. P5 (covering) — 21 hücrede 30-yıllık bilinen-en-iyi eşitlendi
- C(28,9,3)=56 (3 bağımsız sertifika) + 4 eşitleme (2026-08-10) +
  **C(32,8,4)=620** + 15 afin-tarama eşitlemesi (2026-08-11). Tümü
  bağımsız stdlib doğrulayıcıdan geçti; canlı skorbord çaprazı yapıldı.
  Paketler: `data/covering/results/*`.
- **Başlık bulgusu (B1 deneyiyle İSTATİSTİKLEŞTİ, 2026-08-13):**
  75 iterasyonluk 977 platosu (50 ansambl + 25 thinking-KAPALI Opus
  full-rewrite, çocuklar 977-980'e sıkı kümeli), thinking-AÇIK Opus'un
  İLK iterasyonunda kırıldı: genel afin-geometri konstrüksiyonu
  (`affine_blocks`, hardcode yok, her v=p^m için türetiliyor) → 620.
  Aynı model, aynı prompt, aynı checkpoint; değişen tek şey thinking.
  Kontrollü tekrar (checkpoint_75'ten, k=3/kol, 10 iter/dilim,
  eşleştirilmiş seed, dönüşümlü sıra): **ON 3/3 kırılma — üçü de
  bağımsız olarak tam 620; OFF 0/3** (977-1011 bandı). Fisher
  tek-yönlü p = 0.05; etki −357 blok (%36). Destekleyici: orijinal
  r0 (dahilse 4/4 vs 0/3, p≈0.029) + tarihsel OFF 0/25 iterasyon.
- C(49,8,2)=49: saf konstrüksiyon 56 verir; evrilmiş yerel arama
  kapattı → eşitleme ezber değil ARAMA ürünü (kontaminasyon savunması).
- Genelleme dört ayaklı doğrulandı: holdout (17 tarama hücresi döngü
  dışı) + sıfır hücre-ayarı + kesin doğrulama + regresyon bekçisi
  (v28: yeni genom 3 blok İYİ; v24 gürültü bandında; v13/v7 optimumda).
- Literatür teyidi: eşitlenen değerlerin kaynağı GKP 1995 JCD
  (AG(m,p) flat'leri) — "yeniden keşif" çerçevesi doğru ve dürüst.

### A4. Metodolojik / negatif bulgular (rapor değeri yüksek)
- 56-piyango: tek-koşu fitness'ın makine-anı şansını ölçtüğü, çok-seed
  ortalamanın bunu düzelttiği (ölçülmüş varyans örnekleriyle).
- Duvar-saati-oranlı faz bütçeleri ölçeklenmiyor: 6× süre tek başına
  kaliteyi İYİLEŞTİRMEDİ (0.5184@50sn vs 0.5176@300sn) — kazanç
  evrimden geldi.
- "gap = size − lower_bound" iyileştirilebilirlik sinyali olarak ZAYIF;
  küçük bayat hücreler büyük olasılıkla optimalde.
- Kod-boyu tavanı dinamiği: genom büyüdükçe additive diff'ler tavana
  çarpıyor (%36 zayiat) → tavan + budama telkini ikilisi düzeltti (%8).
- OpenEvolve ansambl seed patolojisi: worker'lar aynı llm_seed'le
  kurulunca model seçimi worker-başına deterministik → kısa koşularda
  ağırlıklar fiilen çöküyor (5/5 Opus ölçüldü; 75 çekiliş önekinde
  %21.3'e oturuyor). Upstream'e raporlanabilir yazılım bulgusu.

## B. Eksik ama kapatılabilir

| # | Eksik | Neden önemli | Kapatma maliyeti |
|---|---|---|---|
| ~~B1~~ | ~~Thinking etkisi n=1~~ **KAPANDI (2026-08-12→13):** ON 3/3 (üçü de 620) vs OFF 0/3, Fisher tek-yönlü **p=0.05**, etki −357 blok/%36; destekleyici r0 (4/4, p≈0.029) + tarihsel OFF 0/25. A3'e taşındı. | — | — |
| ~~B2~~ | ~~Covering benchmark dokümanı~~ **KAPANDI (2026-08-13):** `docs/benchmark-covering.md` — dondurulmuş protokol, 29 hücre × 3 seed, 22/29 eşitleme (22/22 bağımsız doğrulama), C(23,10,3)=24 yeni, PP-DIŞI 4 eşitleme (genelleme afin dışına taştı), negatifler dahil. | — | — |
| ~~B3~~ | ~~Sistematik literatür taraması~~ **KAPANDI (2026-08-13):** `docs/literatur-taramasi-b3.md` — covering×LLM emsali YOK (AlphaEvolve/Nagda/Shinka/CodeEvolve listeleri tarandı); evrimsel döngüde thinking ablasyonu YOK (başka alanlarda karışık sonuçlu); rediscovery raporlama emsalli (AlphaEvolve %75). Gönderim öncesi tek tur tazeleme şart. | — | — |
| B4 | Kontaminasyon tartışması | Hakem "model 620'yi biliyordu" der | Kodda değer-yokluğu muayenesi (yapıldı) + C(49,8,2) arama kanıtı + aile-transferi; yazıma dönüştürülecek |
| B5 | kofn uzman teması | İddia planı §6.4; errata açılış kozu | `docs/ozkut-eposta-bilgi-notu.md` hazır; gönderim kullanıcı onayına bağlı |
| B6 | Capset (P4) bilançosu | Agnostiklik kanıtının üçüncü ayağı dağınık | Koşu kayıtlarından tek sayfalık özet; yarım oturum |
| B7 | kofn sakin-makine final re-run | İddia öncesi zorunlu (CLAUDE.md §8) | Benchmark-v2 tablosunun bağımsız tekrarı; yarım oturum |
| B8 | v64 t=5 boşluğu + C(27,10,3) 36→35 | Tarama tamlığı | Bellek-verimli TIndex + uzun probe; opsiyonel, 1 oturum |

## C. Yayın adayları

### C1. Yöntem/sistem makalesi (ana aday)
**"Problem-agnostic LLM-evolutionary discovery with exact verifiers:
verified rediscovery of optimal covering designs and the decisive role
of reasoning mode"** — FunSearch/AlphaEvolve çizgisi (hedef: arXiv
cs.NE + GECCO/ALIFE ya da ACM TELO / NeurIPS workshop).
Omurga: A1 + A3 + A4; şart: B1 (tekrar deneyi), B2, B3, B4.
Satış noktası: (i) tek harness üç problem sınıfı, (ii) 21 kesin-
doğrulanmış eşitleme, (iii) thinking on/off karşılaştırması (B1
sonrası), (iv) negatif bulgular ve reward-hacking savunma mimarisi.

### C2. kofn benchmark + errata makalesi (alan dergisi)
**"A verified benchmark family for weighted k-out-of-n:G design:
proven optima, an evolved heuristic, and errata for [OT2025]"** —
hedef: Computers & Industrial Engineering (aynı dergi) ya da
Reliability Engineering & System Safety. Omurga: A2; şart: B5, B7.
İddia planındaki üç katman + başarı kriterleri zaten karşılanmış
durumda; en olgun aday.

### C3. Kısa yazılım/mühendislik notları (düşük maliyet)
- OpenEvolve ansambl-seed patolojisi: upstream issue + kısa not
  (A4 son madde).
- Çok-seed fitness + arşivleme kancası + iş-sayaçlı determinizm
  sözleşmesi: C1'in yöntem bölümü ya da ayrı tool-paper.

### Yayın OLMAYACAK olanlar (dürüstlük)
- Eşitlemelerin kendisi matematik dergisine gitmez (yeni değer yok,
  yeni konstrüksiyon yok — JCD'ye "620'yi yine bulduk" yazılmaz).
- Rekor iddiası yok; metinlerde "tie/eşitleme" kalır.
