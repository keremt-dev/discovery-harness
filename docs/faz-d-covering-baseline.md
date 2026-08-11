# P5 covering — Faz D baseline (tohum vs referans)

Tohum butcesi: 15.0 sn/instance, seed=0. Referans turu: kanitli-opt = bagimsiz enumerate kaniti; arsiv = LJCR (donmus 2026-03-01, insan-tarafi — sandbox'a girmez).

| instance | (v,k,t) | Schönheim | tohum | referans | tur | gap | fitness | süre(s) |
|---|---|---|---|---|---|---|---|---|
| cover-v13-k3-t2 | (13,3,2) | 26 | 26 | 26 | kanitli-opt | 0 | 1.0 | 15.0 |
| cover-v24-k6-t4 | (24,6,4) | 720 | 1213 | 784 | arsiv | +429 | 0.5936 | 15.0 |
| cover-v28-k9-t3 | (28,9,3) | 44 | 91 | 56 | arsiv | +35 | 0.4835 | 15.0 |
| cover-v32-k8-t4 | (32,8,4) | 532 | 1269 | 620 | arsiv | +649 | 0.4192 | 15.1 |
| cover-v7-k3-t2 | (7,3,2) | 7 | 7 | 7 | kanitli-opt | 0 | 1.0 | 15.0 |

Okuma: hedef hucrede pozitif gap = evrim icin headroom (tohum
arsivin gerisinde — gradyan kaynagi). Bekci hucrede gap 0/kucuk =
tohum tavanda, bekci gorevi gorur. INFEASIBLE gorulurse enstruman
ya tohum bug'i demektir — dongu KURULMAZ (CLAUDE.md §8).
