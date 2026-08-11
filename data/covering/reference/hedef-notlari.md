# P5 covering — hedef hücre kürasyonu notları (2026-08-09)

Kaynak: `sources/coverdata.json` (dmgordo/LJCR; arşiv donduruldu 2026-03-01).
Kürasyon scripti: `curate_targets.py` → `targets.csv`. Kalibrasyon:
`verify_ljcr.py` (I1/I2/T1 sert invariantlar 0 ihlal; Fort–Hedlund 96/96).

## Sayım özeti

| küme | adet |
|---|---|
| toplam hücre | 8 759 |
| kanıtlı optimal (gap=0) | 1 927 |
| eligible (gap≥1, C(v,t)≤1e7, size≤2000) | 4 115 |
| sweet band (3≤t≤5, 20≤v≤60, ≥10 yıl dokunulmamış) | 1 128 |

## Seçilen gradyan hedefleri (instances/ altında)

| instance | arşiv size | low_bd | Schönheim | gap | son iyileştirme |
|---|---|---|---|---|---|
| `cover-v32-k8-t4` | 620 | 552 | 532 | 68 | 1996-11-14 (hiç) |
| `cover-v24-k6-t4` | 784 | 720 | 720 | 64 | 1996-11-14 (hiç) |
| `cover-v28-k9-t3` | 56 | 50 | 44 | 6 | 1996-11-14 (hiç) |

Seçim gerekçesi: en büyük mutlak gap × 29+ yıl eskilik × ucuz kesin
doğrulama (C(v,t) ≤ 36k). v28 hücresi küçük blok sayısıyla (56) hızlı
iterasyon/duman testi hedefi; v32/v24 asıl keşif alanı.

## Bekçiler (kanıtlı optimal — fitness tavanı 1.0)

`cover-v7-k3-t2` (Fano, 7) ve `cover-v13-k3-t2` (STS(13), 26).
Kürasyon kuralı gereği evrim hedefi OLAMAZLAR (headroom=0); çoklu-instance
fitness setinde regresyon bekçisi olarak kullanılacaklar.

## Açık uyarılar (iddia diline geçmeden önce)

1. **gap>0 ≠ garanti headroom.** Alt sınır zayıf olabilir; 620'nin
   gerçek optimuma yakın olması mümkün. Faz D'de tohum + refsearch
   probuyla fiili headroom ölçülmeden hedef kesinleşmez (skill §3.1).
2. **"Rekor" tanımı arşive göredir.** 1 Mart 2026 sonrası literatür/
   coveringrepository.com kontrolü yapılmadan "bilinen en iyiyi aştı"
   iddiası YAZILMAZ. Canlı skorbord: coveringrepository.com (Acerbi);
   LJCR verisinden daha güncel iyileştirmeler içerebilir — iddia öncesi
   hedef hücreler orada da kontrol edilir.
3. **I3 hijyen bulguları (196):** arşivin imps tarihçesi yer yer monoton
   değil (aynı gün artan boyutlar, son imp ≠ güncel size). Rekor
   karşılaştırması DAİMA `size` alanına (güncel en iyi) yapılır,
   tarihçeye değil.
4. 1996 kayıtları DB'nin ilk yüklemesidir (Gordon'un tabloları);
   "hiç iyileştirilmemiş" = "depo ömrü boyunca kimse dokunmamış" demek,
   "kimse denememiş" demek değil. Yine de 68 bloklu gap + sıfır girişim,
   eldeki en iyi ihmal sinyalidir.
