# data/kofn/reference — SANDBOX'A GİRMEZ

Bu dizindeki hiçbir şey solver sandbox'ına ya da LLM prompt'una taşınmaz
(CLAUDE.md §3). Yalnızca insanın raporlama/kalibrasyon adımında kullanılır.

## verify_fyffe.py

Fyffe–Hines–Lee (1968) 14 alt-sistemli bileşen tablosunun (Liang & Smith
CEC 1999, Table 1'den transkript) ve Coit & Smith (C&IE 1996) Appendix'indeki
33 en-iyi-bilinen çözüm vektörünün makine-okunur hali + doğrulama script'i.

Doğrulama: her çözüm vektörü `fractions.Fraction` ile tam aritmetikte yeniden
hesaplanır; güvenilirlik / maliyet / ağırlık, yayınlanan değerlerle bire bir
karşılaştırılır. Son koşu sonucu: **33/33 OK, 0 uyumsuzluk** (2026-08-03).

```bash
python data/kofn/reference/verify_fyffe.py
```

## optima_rap33.csv

33 instance'ın **sertifikalı optimum** güvenilirlik değerleri (W ile
anahtarlı). Kaynak: Yeh, arXiv:2204.04472, Table 6 (BRB exact, 11 hane;
alt-sistem başına ≤8 bileşen varsayımıyla). Bağımsız 6-hane çaprazı:
Nahas & Nourelfath, IJMEMS 6(1) 2021, Table 4 — 33/33 uyum. Kaynak
metinlerin kopyaları `sources/` altında (bat_paper.txt, ijmems.txt).

Exact-Fraction C&S değerleriyle diff (2026-08-03): 0 tutarsızlık alarmı;
25 instance'ta optimum > C&S (W=159,160,162,169,171-191), 8'inde C&S
zaten optimal (W=161,163-168,170).

## verify_ozkut2025.py

Ozkut & Tütüncü 2025 (C&IE 210, 111513) makalesinin Tablo 1/5/6
örneklerinin Fraction'la tam doğrulaması. Regresyon hedefi bizim tam
değerlerimizdir; makaleyle farklar (3 baskı hatası + Tablo 1'in
üretilemeyen satırları) script başındaki yorumda karakterize edilmiştir.
`sources/ozkut_tutuncu_2025.pdf` tam metin (yeniden dağıtılmaz),
`sources/ozkut_tutuncu_2025.txt` çıkarılmış metin.

```bash
python data/kofn/reference/verify_ozkut2025.py
```

Dikkat:
- Instance şeması: C=130 sabit, W = 191..159 (33 tamsayı değer);
  orijinal FHL problemi W=170 (instance no. 22).
- Çözüm vektörleri bileşenleri **güvenilirliğe göre azalan sırada yeniden
  indeksler** (1 = en güvenilir); ham tablo sırası değil. Script bu
  yeniden sıralamayı yapıyor — yayınlanmış vektör okuyan herkes yapmalı.
- Buradaki 33 değer Coit & Smith'in *bulduğu en iyiler*; **kanıtlanmış
  optimum etiketleri** Caserta & Voß (EJOR 2016) tablosundan gelmeli
  (henüz doğrulanmadı — bkz. docs/p1-problem-tanimi.md).
