# C1 Makale İskeleti

Hedef: ACM TELO (arXiv cs.NE ön-baskıyla). Dil: İngilizce.
Tarih: 2026-08-13. Kaynak dokümanlar bölüm başlarında işaretli.

**Başlık:** *Reasoning Mode Breaks the Plateau: Verified
LLM-Evolutionary Search Matches Three Decades of Best-Known
Covering Designs*

**Kapsam kararı:** birincil vaka = covering (P5). kofn (P1) ve capset
(P4) yalnız "harness genelliği" bölümünde kısa kanıt olarak geçer —
derin kofn anlatısı C2 makalesine saklanır (C1, B7'ye bloklanmaz).

---

## Abstract (taslak, ~200 kelime)

> LLM-driven evolutionary program search (FunSearch, AlphaEvolve) has
> produced new mathematical constructions, but little is known about
> WHICH model capabilities drive its breakthroughs. We present a
> problem-agnostic evolution harness built around mathematically exact
> verifiers, and use it to study covering designs C(v,k,t) — a domain
> untouched by this line of work. Starting from a generic greedy
> solver, our loop matched the 30-year-old best-known value C(32,8,4)
> = 620 by autonomously reconstructing the classical affine-geometry
> construction as general code. The decisive factor was the model's
> extended reasoning mode: in a controlled experiment from a frozen
> plateau state, reasoning-enabled slices broke the plateau 3/3 times
> (each reaching exactly 620) while reasoning-disabled slices with the
> same model failed 0/3 (p = 0.05, one-sided; effect −36%). Under a
> pre-registered 29-cell benchmark, the single evolved program matched
> best-known values in 22 cells (all independently verified), including
> four cells outside the affine family. Direct-recall probes show the
> model can neither recall the target value nor emit the artifact
> without code, dissociating retrieval from the reasoning-to-code
> pathway. We release all certificates, protocols, and negative
> results.

---

## 1. Introduction (~1.5 sayfa)
Kaynak: CLAUDE.md P5 anlatısı, yayin-bulgu-ozeti.
- Hook: 75 iterasyonluk plato → thinking açılınca ilk iterasyonda
  kırılma. "Ne zaman büyük model / ne zaman muhakeme?" sorusu
  AlphaEvolve-soyu sistemlerde açık.
- Katkı listesi (4):
  C1: Kontrollü reasoning-mode deneyi (evrimsel keşif döngüsünde ilk).
  C2: 22 kesin-doğrulanmış eşitleme; covering design bu soyda ilk kez.
  C3: Probleme-agnostik, kesin-doğrulayıcılı, reward-hacking'e
      dirençli harness tasarımı (+ negatif bulgular).
  C4: Kontaminasyon ayrışma metodolojisi (değer-hatırlama /
      artefakt-üretme / koda-dökme üçlü sondası).

## 2. Related Work (~1 sayfa)
Kaynak: docs/literatur-taramasi-b3.md (atıf listesi hazır).
- LLM-evrim soyu: FunSearch, AlphaEvolve, Nagda (Ramsey/Zarankiewicz),
  ShinkaEvolve, CodeEvolve, PPSN-2024 analizi.
- Thinking-ablasyon literatürü: karışık/görev-bağımlı sonuçlar
  (4 atıf) — bizim netliğimizin kontrastı.
- Covering design klasikleri: GKP 1995, Nurmela–Östergård, tabu;
  LJCR/coveringrepository.

## 3. The Discovery Harness (~2 sayfa)
Kaynak: harness/ kodu, CLAUDE.md §3, discovery-harness skill.
- Eklenti sözleşmesi (SENSE, parse, evaluate_text, penalty_scale);
  fitness ≠ cost; ceza ölçeği instance'tan.
- Kesin doğrulama ilkesi: solver beyanı yok sayılır; Fraction/tam
  sayım; "reported_matches" dürüstlük sensörü.
- Çok-seed ortalamalı fitness (56-piyango motivasyonu) + iş-sayaçlı
  determinizm sözleşmesi.
- Çözüm arşivleme kancası (kayıp-620 dersi).
- Genellik kanıtı (kısa): kofn, capset, covering — çekirdekte sıfır
  değişiklik. (kofn detayı C2'ye atıf.)

## 4. Case Study: Covering Designs (~1.5 sayfa)
Kaynak: problems/covering/, docs/faz-d-covering-baseline.md.
- Tanım, Schönheim normalizer (fitness ∈ (0,1], sızıntısız),
  infeasible bandı.
- Enstrüman kanıtları: enumerate ile kanıtlı optimumlar (C(7,4,3)=12
  Schönheim'ı çürüterek; bekçiler), LJCR kürasyonu (I1-I3 turnusolu).
- Tohum çözücü + başlangıç durumu.

## 5. The Evolution Campaign (~2 sayfa)
Kaynak: CLAUDE.md P5 dilim kayıtları.
- Zaman çizelgesi figürü: tohum 1258 → duman 978 → plato 977 (50
  ansambl + 25 Opus-FR; çocukların 977-980 kümelenmesi) → thinking
  620.
- Mühendislik bulguları (kısa, dürüst): kod-boyu zayiatı (%48→%8),
  diff kaybı oranları, OpenEvolve ansambl-seed patolojisi (worker
  başına özdeş çekiliş dizisi — upstream'e raporlandı/raporlanacak).
- Keşfedilen yapı: `affine_blocks` kod listesi (figür) + neden tam
  620 verdiğinin bir paragraflık matematiği.

## 6. Controlled Experiment: Reasoning Mode (~1.5 sayfa) — ANA BÖLÜM
Kaynak: CLAUDE.md B1 kaydı, runs/evolve/b1/.
- Tasarım: dondurulmuş checkpoint_75, eşleştirilmiş seed, dönüşümlü
  sıra, tek fark thinking (+ bütçe karıştırıcısının dürüst beyanı:
  64k/20k — thinking'in bütçe İHTİYACI tedavinin parçası).
- Sonuç tablosu: ON 3/3 → hepsi 620; OFF 0/3 (977-1011). Fisher
  p=0.05; destekleyici r0 (4/4, p≈0.029) + tarihsel 0/25.
- Yorum: retrieval ucuz olurdu → K5 ayrışması; token/maliyet analizi
  (thinking ~5x pahalı; "plato kartı" reçetesi).

## 7. Pre-registered Benchmark & Generalization (~2 sayfa)
Kaynak: docs/benchmark-covering.md.
- Protokol (dondurulmuş; roller: BEKÇİ/EĞİTİM/AFİN-H/AFİN-SINIR/
  PP-DIŞI), 29 hücre × 3 seed.
- Ana tablo (22/29 EŞİT; tohum kolonu; seed kararlılığı 25/29 özdeş).
- Dört-ayaklı genelleme: holdout + sıfır-ayar + bağımsız doğrulama +
  regresyon bekçisi (v28/v24/v13/v7 tablosu).
- Afin-dışı 4 eşitleme + C(23,10,3)=24 vurgusu.

## 8. Contamination Analysis (~1 sayfa)
Kaynak: docs/kontaminasyon-b4.md (bölüm neredeyse hazır).
- Tehdit modeli; K1-K6 kanıt hatları; S1/S2 sondaları; ayrışma
  tablosu; kalibre edilmiş iddia.

## 9. Negative Results and Limitations (~1 sayfa)
Kaynak: benchmark §4, CLAUDE.md dersleri.
- Arşivin gerisinde kalınan 7 hücre (tablodan çıkarılmadı);
  C(32,18,5) yapısal zayıflık; v64-t5 boşluğu.
- Rekor YOK — yalnız eşitleme; küçük bayat hücreler muhtemelen
  optimal(e yakın).
- k=3 örneklem küçüklüğü; tek model ailesi (Opus; GLM yalnız motor);
  tek problem sınıfında derinlik; wall-clock anytime varyansı.
- Goodhart notu; ortam kaydı (%26-41 arka plan yükü).

## 10. Conclusion (~0.5 sayfa)
- "Bilgi ağırlıklarda uyur; muhakeme+kod+kesin doğrulayıcı onu
  doğrulanmış artefakta çevirir" tezi.
- Gelecek: rekor avı için yeni konstrüksiyon aileleri; reasoning-mode
  çalışmasının başka problem sınıflarına taşınması; C2 (kofn) yolu.

## Reproducibility & Artifacts
- Repo (harness + problems + configs), sertifika paketleri
  (data/covering/results/*), dondurulmuş protokoller, ham loglar.
- Karar gerekli: repo kamuya açılacak mı / hangi lisans? (KULLANICI)

## Figür/Tablo planı
- F1 harness mimarisi; F2 kampanya zaman çizelgesi (skor eğrisi);
  F3 affine_blocks kod listesi; T1 B1 sonuçları; T2 benchmark (29
  satır); T3 kontaminasyon ayrışması; T4 regresyon bekçisi.

## Yazım sırası önerisi
1. §6 (B1) + §7 (B2) — veri hazır, en kolay.
2. §3-5 (sistem + kampanya) — CLAUDE.md'den destile.
3. §8 (B4 hazır), §2 (B3 hazır), §9.
4. §1 + Abstract en son.

## Açık kararlar (KULLANICI)
- Yazar listesi / sıra / affiliasyon (Intellica? bağımsız?).
- Repo açılması + lisans.
- Tütüncü/Özkut'a C1'de teşekkür-notu (acknowledgement) verilecek mi
  (problem seçimi profil taramasından çıktı) — C2 temasından bağımsız.
- GECCO 2027 deadline'ı kollanacak mı yoksa doğrudan TELO mu.
