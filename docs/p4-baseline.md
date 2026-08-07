# P4.3 Baseline — tohum solver vs bilinen deger

Tohum: `problems/capset/seed_solver.py` (rastgele-greedy + extend + swap hill-climb + random-restart, anytime). Strawman DEGIL — meşru saf greedy gucu. n=2/3/4 optimumda (4/9/20); n=6/8'de gradyan bol (evrim baslangici icin ideal). n>=4 optimallik literature aittir.

| instance | n | tohum \|S\| | bilinen | durum | kaynak | gap % | sure s |
|---|---|---|---|---|---|---|---|
| capset-n2 | 2 | 4 | 4 | kanitli | trivial | 0.0 | 5.2 |
| capset-n3 | 3 | 9 | 9 | kanitli | klasik | 0.0 | 5.2 |
| capset-n4 | 4 | 20 | 20 | kanitli | Pellegrino 1971 | 0.0 | 5.1 |
| capset-n5 | 5 | 40 | 45 | kanitli | Edel-Ferret-Landjev-Storme 2002 | 11.1 | 5.1 |
| capset-n6 | 6 | 77 | 112 | kanitli | Potechin 2008 | 31.2 | 5.2 |
| capset-n7 | 7 | 142 | 236 | alt sinir (acik) | Calderbank-Fishburn / Edel | 39.8 | 5.2 |
| capset-n8 | 8 | 266 | 512 | alt sinir (acik) | FunSearch / Nature 2024 | 48.0 | 5.4 |
| capset-n9 | 9 | 487 | 1082 | alt sinir (acik) | Edel urun-konstr. / FunSearch teyidi | 55.0 | 5.5 |

**Kürasyon notu (P4.4, Görev 4b kararı):** bekçi = n=4 (tohum kanıtlı optimumda: 20 → gerileme hemen görünür); gradyan kaynağı = n=7 + n=8 (tohum 144/263 vs bilinen 236/512 → bol headroom); holdout = n=6 + n=9 (koşuya GİRMEZ, genelleme ölçümü). n=2/3 de tavanda (optimum) ama çok küçük (ayrım gücü yok). Headroom turnusolu: tohumun zaten tavana vurduğu instance (n=2/3/4) evrim hedefi olamaz.
