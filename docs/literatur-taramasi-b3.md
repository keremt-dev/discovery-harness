# B3 — Literatür Taraması (C1 makalesi novelty kontrolü)

Tarih: 2026-08-13. Yöntem: çok-açılı web taraması (arXiv, Semantic
Scholar, yayıncı siteleri) + anahtar makalelerin derin okuması.
UYARI: kanıt-yokluğu ≠ yokluk-kanıtı; gönderim öncesi son bir tur
tekrar taranmalı (alan hızlı hareket ediyor).

## Soru 1: "Covering design × LLM-evrim" emsali var mı? → BULUNAMADI

FunSearch/AlphaEvolve soyunun tüm bilinen problem listeleri tarandı:

| Sistem | Kombinatorik problemleri | Covering design? |
|---|---|---|
| AlphaEvolve (Novikov et al. 2025; 50+ problem) | Kakeya, Nikodym, Sidon setleri, cap set, kissing number, circle/hexagon packing, Ramsey (Nagda uzantısı) | **YOK** |
| Nagda et al. (Reinforced Generation…) | Ramsey sayıları, Zarankiewicz, karmaşıklık gadget'ları | **YOK** |
| ShinkaEvolve (Sakana 2025) | Circle packing, Heilbronn üçgenleri, otokorelasyon eşitsizlikleri, Dyck bijections | **YOK** |
| CodeEvolve, OpenEvolve-tabanlı çalışmalar (ör. bijection keşfi 2511.20987) | çeşitli | **YOK** |
| Klasik covering literatürü | GKP 1995 (greedy+geometri), Nurmela–Östergård SA (1993), çok-seviyeli tabu (2006) | LLM YOK |

Sonuç: covering design hücreleri bu soy tarafından hiç hedeflenmemiş
görünüyor; C1'in vaka çalışması bu boşluğa oturur.

## Soru 2: Evrimsel keşif döngüsünde kontrollü thinking ablasyonu? → BULUNAMADI

- AlphaEvolve: reasoning-modu ablasyonu raporlamıyor (Tao'nun kapsamlı
  blog analizi de teyit ediyor); model-boyu karşılaştırması var
  (Flash/Pro), thinking on/off yok.
- Zarankiewicz makalesi (2605.01120): Claude 3.7/Opus 4.6 + Gemini
  Flash kullanmış, ablasyon yok.
- Thinking on/off ablasyonları BAŞKA alanlarda var ve sonuçlar
  KARIŞIK/görev-bağımlı: el yazısı sentezinde faydalı (2606.18788),
  prompt-attack tespitinde faydasız (2603.25176), içerik
  moderasyonunda ZARARLI (2603.01724), bilgi-kontrol görevlerinde
  faydalı (2506.06589).

Sonuç: B1 deneyi (evrimsel keşif döngüsünde eşleştirilmiş thinking
on/off, kategorik kırılma farkı, 3/3 vs 0/3) bu literatürde ilk
görünüyor; "karışık sonuçlar" arka planı bulguyu daha da ilginç kılar
("keşif-tipi görevlerde belirleyici" tezi).

## Soru 3: "Eşitleme/rediscovery" raporlamanın meşruiyeti → GÜÇLÜ EMSAL

- AlphaEvolve'un kendi metriği: problemlerin %75'inde bilinen-en-iyi
  yeniden keşif, %20'sinde iyileştirme — rediscovery oranı bu
  literatürün kabul görmüş para birimi.
- Nagda Ramsey makalesi açıkça "kesin bilinen tüm Ramsey alt
  sınırlarını geri kazandık, çoğunda bilinen-en-iyiyle eşleştik" diye
  raporluyor.
- Negatif-sonuç yayını da emsalli: "Even with AI, Bijection Discovery
  is Still Hard" (OpenEvolve, 2511.20987).

Sonuç: 22/29 eşitleme + negatif satırlar + B1 nedensel deneyi, tür
olarak bu literatüre birebir oturuyor.

## Soru 4: Covering design'ı bugün kim iyileştiriyor? → DURGUN ALAN

Klasik hat: GKP 1995 (arşivin kurucu makalesi; AG(m,p) flat'leri
dahil), Nurmela–Östergård simulated annealing (1993+), kooperatif
çok-seviyeli tabu (2006). 2020'lerde LJCR hücrelerine dokunan yeni
yöntem dalgasına rastlanmadı (bizim hedef hücrelerin 15-30 yıl bayat
olması da bununla tutarlı).

## Venue çıkarımı

En yakın komşular (Zarankiewicz, Ramsey/Nagda, ShinkaEvolve,
CodeEvolve) HEPSİ arXiv-önce; hakemli çapa noktaları PPSN/GECCO/TELO
ekosistemi. Karar (2026-08-13 sohbeti): arXiv (cs.NE + cs.AI +
math.CO) → ACM TELO birincil; GECCO 2027 takvim uyarsa bildiri+dergi.

## C1 related-work çekirdek atıf listesi

- Romera-Paredes et al., FunSearch, Nature 2024.
- Novikov et al., AlphaEvolve, 2025 (arXiv:2506.13131).
- Nagda, Raghavan, Thakurta — Reinforced Generation of Combinatorial
  Structures: Ramsey Numbers (arXiv:2603.09172); Zarankiewicz
  (arXiv:2605.01120).
- ShinkaEvolve (arXiv:2509.19349); CodeEvolve (arXiv:2510.14150);
  OpenEvolve bijection çalışması (arXiv:2511.20987).
- PPSN 2024: Understanding the Importance of Evolutionary Search in
  Automated Heuristic Design with LLMs (arXiv:2407.10873).
- Thinking-ablasyon karışık-sonuç arka planı: 2606.18788, 2603.25176,
  2603.01724, 2506.06589.
- Covering klasikleri: Gordon–Kuperberg–Patashnik JCD 1995
  (arXiv:math/9502238); Nurmela–Östergård 1993; kooperatif tabu 2006;
  LJCR / coveringrepository.com (Zenodo DOI 10.5281/zenodo.10779736).
