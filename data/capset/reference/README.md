# data/capset/reference — SANDBOX'A GİRMEZ

Bu dizindeki hiçbir şey solver sandbox'ına ya da LLM prompt'una taşınmaz
(CLAUDE.md §3, problems/capset/CLAUDE.md §0.5). Yalnızca insanın
raporlama/kalibrasyon adımında ve **test doğrulaması** için kullanılır.
Ayrıntı: `docs/p4-problem-tanimi.md`.

⚠ **Sızıntı kuralı:** bilinen rekor değerleri solver'a SIZDIRILMAZ.
Bu dosyalar yalnızca (a) insanın raporlaması ve (b) `tests/` altında
evaluator'ün doğruluğunu ölçmek içindir. Instance dosyasına, seed
solver'a veya evolve prompt'una bilinen rekor YAZILMAZ. Evaluator'ün
Meshulam *teorem* sınırını (2·3ⁿ/n) normalizasyon için kullanması
serbesttir — teorem ≠ referans tablosu.

## Pozitif kontrol kümeleri (çözüm formatı: `#` yorum + bitişik {0,1,2})

| Dosya | n | \|S\| | Durum | Kaynak |
|---|---|---|---|---|
| `optimal_n2_size4.txt` | 2 | 4 | optimal (a(2)=4) | elle gömülü |
| `optimal_n3_size9.txt` | 3 | 9 | optimal (a(3)=9) | bağımsız greedy+extend |
| `optimal_n4_size20.txt` | 4 | 20 | optimal (a(4)=20, Pellegrino 1971) | bağımsız greedy+extend (seed=451) |
| `funsearch_n8_size512.txt` | 8 | 512 | alt sınır (AÇIK, en iyi bilinen) | **FunSearch / Nature 2024; indirildi + bağımsız O(\|S\|²) doğrulandı** |

## n=5/6/7 boşluk (açık — vaat DEĞİL)

n=5 (a(5)=45), n=6 (a(6)=112), n=7 (alt sınır 236) için **somut küme
sağlanamadı** (iki araştırma turu: 2026-08-06). Nedenleri:

- **Edel CAPs veritabanı** (yvesedel.de/Matrizen/CAPs) yalnız n≥7 projective
  cap'leri verir; n=4/5/6 yok.
- **n=5/6 optimum cap'leri cebirsel yapı ister:** 45-cap = Hill 56-cap PG(5,3)'ün
  11-hyperplane silinmesiyle; 112-cap = Hill cap doubling. PG↔AG dönüşümü ve
  hangi 11 noktanın silineceği hataya açık olduğundan güvenilir pozitif kontrol
  verisi bu yolla sağlanamadı.
- **Tohum (seed_solver) optimum'a ulaşamaz:** n=5'te 40/45, n=6'da 77/112.
  Bu nedenle "seed'in ürettiği küme tablodaki değere ulaşıyor" vaadi YANLIŞ
  olur — bu vaat kaldırıldı (2026-08-07, Görev 4c).

Bu n'lerde pozitif kontrol **bulunana kadar yoktur.** n=5/6/7 testleri
yalnızca şunu sınayabilir: tohum çıktısı feasible cap (boyutu bilinen değere
ulaşmıyor; gerçeğe uygun gap `docs/p4-baseline.md`'de). Ürün konstrüksiyonu da
kapatmaz (a(2)·a(3)=36<45, a(3)²=81<112).

## funsearch_n8_size512.pylist

FunSearch GitHub deposundan özgün format (Python listesi, her satır
8 uzunluğunda {0,1,2}). `funsearch_n8_size512.txt` aynı kümenin bizim
çözüm formatındaki (bitişik karakter) halidir. Bağımsız doğrulama
(2026-08-06): 512 tekil vektör, O(|S|²) cap-set kontrolü → 0 ihlal,
~250 ms. **Altın pozitif kontrol** — evaluator n=8'de bunu feasible +
|S|=512 olarak doğrulamalı.

## sources/

- `funsearch_cap_set.ipynb` — FunSearch cap set notebook (Apache 2.0 /
  CC-BY-4.0). Skeleton (greedy cap iskeleti), evrimleşmiş priority
  (n=8=512), açık 512-konstrüksiyonu (`build_512_cap`), `is_cap_set`
  (O(c²n) doğrulama) ve n=9=1082 priority'sini içerir. P4.3 seed_solver
  için değerli şablonlar. Yeniden dağıtılabilir (lisans uygun).
- `edel_smallCaps.pdf` — Edel & Bierbrauer, "Large caps in small spaces".
  AG(7,3) 236-cap Theorem 6 + Table 2/3 (sembolik D/R/U kodlama).
  Ham 7-vektör değil; çıkarmak hataya açık → n=7 boşluk olarak işaretli.
