# TELO Gönderim Rehberi (ilk kez gönderenler için, adım adım)

Tarih: 2026-08-13. Durum notu: bib yazarları arXiv/DBLP'den doğrulandı;
e-posta main.tex'te 3kerem@gmail.com; PDF derlemesi temiz (15 sayfa,
0 çözümsüz atıf).

## Adım 0 — Hesaplar (bir kez, ~20 dk)
1. **ORCID** (orcid.org): ücretsiz kayıt, 3kerem@gmail.com ile.
   ACM gönderiminde yazar kimliği olarak istenir. Aldığın ORCID iD'yi
   not et (0000-XXXX-... biçiminde).
2. **ScholarOne hesabı**: gönderim sitesinin kendisinde açılır
   (Adım 4'teki adres, "Create an Account" — ORCID ile bağlanabilir).
   Ayrı bir ACM hesabı ŞART DEĞİL; ancak kabul aşamasında (eRights)
   ücretsiz **ACM Web Account** gerekir: **https://accounts.acm.org**
   (çoğul "accounts"; üyelik GEREKMEZ — "Professional Membership"
   formu paralı üyeliktir, onunla İLGİSİ YOK, doldurma).
3. Zenodo hesabın zaten var (✓).

## Adım 1 — Kod arşivi + DOI (Zenodo, ~15 dk)
1. zenodo.org → giriş → sağ üst menü → **GitHub**.
2. Listeden `keremt-dev/discovery-harness` repo'sunun anahtarını AÇ
   (toggle ON). (Repo listede yoksa "Sync now".)
3. GitHub'da release oluştur: repo sayfası → Releases → "Draft a new
   release" → tag: `v1.0-paper`, başlık: "C1 paper artifact" →
   Publish release.
4. Zenodo birkaç dakika içinde otomatik arşivler ve **DOI** üretir
   (zenodo.org → Uploads altında görünür).
5. DOI'yi bana söyle → makalenin "Reproducibility and Artifacts"
   bölümüne ve README'ye eklerim (ya da kendin: paper/main.tex'te
   ilgili paragrafa `DOI: 10.5281/zenodo.XXXXXXX`).

## Adım 2 — arXiv ön-baskı (önerilir; gönderimle aynı gün, ~30 dk)
1. arxiv.org hesabı aç (3kerem@gmail.com).
2. ⚠ İlk gönderimde cs.NE için **endorsement** istenebilir (arXiv'in
   yeni-yazar mekanizması). İstenirse: alanda yayını olan bir tanıdık
   arXiv'in verdiği endorsement kodunu onaylar; tanıdık yoksa arXiv
   bazen otomatik muaf tutar — formu doldurup görmek en hızlısı.
3. Yüklenecekler (LaTeX kaynak olarak): `paper/main.tex`,
   `paper/sections/*.tex`, `paper/references.bib` VE `paper/main.bbl`
   (arXiv bbl ister), `paper/figures/f2-campaign-timeline.pdf`,
   `paper/figures/f3-affine-blocks-listing.py`.
4. Kategori: cs.NE (birincil), çapraz liste: cs.AI, math.CO.
   Lisans: arXiv non-exclusive license (varsayılan) yeterli.
5. ACM telif politikası ön-baskıya izin verir; sorun yok.

## Adım 3 — Gönderim günü son rötuşlar (~1 saat, birlikte yaparız)
1. **Literatür tazeleme**: docs/literatur-taramasi-b3.md'deki taramayı
   tekrarla (alan hızlı; yeni emsal çıktıysa §2'ye eklenir).
2. **Anonimlik: ÇÖZÜLDÜ (2026-08-13)** — TELO çift-anonim (web
   aramasıyla teyit). İnceleme PDF'i hazır:
   `paper/telo-anon-review.pdf` (ANONYMOUS AUTHOR(S), acks çıkarıldı,
   repo/DOI linkleri "withheld for review" — tam halleri cover
   letter'da). ScholarOne'a ANA BELGE olarak BU yüklenir; kimlikli
   main.pdf YÜKLENMEZ.
3. Zenodo DOI'yi makleye işle (Adım 1.5), yeniden derle, push.

## Adım 4 — TELO'ya gönderim (ScholarOne, ~45 dk)
1. **mc.manuscriptcentral.com/telo** adresine git (ScholarOne /
   "Manuscript Central" — ACM dergilerinin gönderim sistemi). Adres
   404 verirse doğru bağlantı guidelines sayfasındaki "Submit"
   düğmesindedir (dl.acm.org/journal/telo/author-guidelines); genel
   portal mc.manuscriptcentral.com/acm da yönlendirir. "Create an
   Account" ile hesap aç, ORCID'ini bağla.
2. "Author" sekmesi → **Start New Submission**. Sırayla istenecekler:
   - **Type**: Research Article.
   - **Title / Abstract**: main.tex'ten kopyala.
   - **Keywords + CCS concepts**: main.tex'tekiler (Genetic
     programming; Natural language generation; Combinatorics).
   - **Authors**: tek yazar; affiliation "Independent Researcher,
     Türkiye"; ORCID bağla.
   - **Files**: main.pdf (ana dosya) + kaynak zip (main.tex,
     sections/, figures/, references.bib, main.bbl). PDF "main
     document" olarak işaretlenir.
   - **Suggested reviewers** (opsiyonel ama faydalı): LLM+EC
     kesişiminden 3-4 isim önerebilirsin (ör. PPSN-2024 makalesinin
     yazarları, ShinkaEvolve/CodeEvolve yazarları — çıkar çatışması
     olmayanlardan).
   - **Cover letter**: kısa; istersen taslağını ben yazarım
     (katkı özeti + "kod ve sertifikalar açık: GitHub + Zenodo DOI" +
     "arXiv ön-baskısı: XXXX.XXXXX" + çıkar çatışması yok beyanı).
3. Submit → onay e-postası gelir (manuscript ID'yi sakla).

## Adım 5 — Sonrası
- İlk karar tipik 2-4 ay; "major/minor revision" normaldir ve
  ret değildir — revizyon mektubunu birlikte hazırlarız.
- Kabul olursa: ACM eRights formu (telif; open-access seçenekleri —
  APC'li OA ya da geleneksel model, o gün karar verirsin) ve TAPS
  (camera-ready) süreci.

## Kalan iki küçük TODO (prova aşamasına kadar bekleyebilir)
- `nurmela1993upper` cilt/sayfa teyidi (Congressus Numerantium 96,
  93-111 olarak yazılı — standart alıntıyla uyumlu, orijinalden teyit
  prova aşamasında).
- `openevolve` için tercih edilen atıf biçimi (repo README'sinde
  "cite as" var mı bak).


## GÖNDERİLDİ ✅ (2026-08-13)
- **Manuscript ID: TELO-2026-65**; başlık ve tek yazar (Turkyilmaz,
  Kerem — Independent Researcher) onay ekranında doğrulandı.
- Gönderilen ana belge: `paper/telo-anon-review.pdf` (çift-anonim).
- Reproducibility rozet başvurusu: Artifacts Available + Evaluated
  (Functional); DOI alanı anonimlik için boş (revizyonda doldurulacak:
  10.5281/zenodo.21920942).
- Beklenen: onay e-postası (3kerem@gmail.com); ilk karar tipik 2-4 ay.
- Paralel açık iş: arXiv endorsement (kod 79GNDU e-postada; taslak:
  outreach/endorsement-rica-taslagi.md). Endorsement gelince arXiv
  ön-baskısı yüklenir ve revizyonda makaleye işlenir.
