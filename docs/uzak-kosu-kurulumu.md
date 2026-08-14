# Uzak koşu makinesi kurulumu (2026-08-14, fiilen çalışan hal)

Adanmış sakin koşu makinesi: **DESKTOP-M070IQB** (Ryzen 5 5600 6C,
16 GB RAM, RX 6700 XT — GPU kullanılmıyor). İddia protokolündeki
"sakin makine" şartını sağlar; ana makine gündüz işine serbest kalır.
16 GB sınırı: v64-t5 bellek boşluğu burada da kapsam DIŞI.

## Ağ ve erişim

- **Tailscale** iki makinede de kurulu (kullanıcı kurdu): uzak
  `100.73.210.41` (desktop-m070iqb), ana `100.125.104.107`.
- **OpenSSH Server** uzakta; 22/tcp güvenlik duvarında YALNIZCA
  Tailscale aralığına (100.64.0.0/10) açık, varsayılan açık kural
  devre dışı.
- Anahtar: ana makinede `~/.ssh/kt_uzak_ed25519` (adanmış, parolasız);
  uzakta `C:\ProgramData\ssh\administrators_authorized_keys`
  (+ `icacls /inheritance:r /grant "Administrators:F" /grant "SYSTEM:F"`).
- Ana makine `~/.ssh/config`:

```
Host kt-uzak
    HostName 100.73.210.41
    User Crossfire
    IdentityFile ~/.ssh/kt_uzak_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
```

- Repo klonu: **`F:\kt\discovery-harness`** (kullanıcı tercihi; C: değil).
- Python: **daima `py -3.14`** — PATH'te eski bir Python (3.10) öne
  çıkıyor, `python` komutuna güvenme.

## Yaşanmış tuzaklar (yeniden keşfetme)

1. **Windows ssh istemcisi ACL'e takılır:** `Bad owner or permissions
   on .ssh/config` → `icacls <dosya> /inheritance:r /grant "kerem:F"`
   (config + private key).
2. **PowerShell'de `ssh-keygen -N '""'` tuzağı:** parola "boş" değil,
   literal iki-tırnak karakteri olur. Belirti: `Server accepts key`
   ama `Permission denied` (istemci anahtarı sessizce açamaz).
   Düzeltme: `ssh-keygen -p -P '""' -N "" -f <key>`. PS'te doğrusu
   baştan `-N ""`.
3. **Boş parolalı Windows hesabı ağdan oturum AÇAMAZ** (anahtar kabul
   edilse bile; varsayılan LSA politikası). Düzeltme: hesaba parola
   koy (`net user <ad> *`); otomatik giriş isteniyorsa `netplwiz`.
4. **ssh → cmd iç içe tırnak kırılgandır:** `findstr "a b"` /
   `tasklist /FI "..."` gibi tırnaklı komutlar bozulur. Karmaşık işi
   `.cmd` sarmalayıcıya yaz, `scp` ile gönder, `schtasks /TR`'ye
   tırnak gerektirmeyen dosya yolunu ver.
5. **schtasks ONCE + gelecekteki /ST yeniden tetikler:** elle /Run
   sonrası ikinci kopyayı önlemek için `schtasks /Change /TN <ad>
   /DISABLE` (parola istemez; `/ST` değişikliği "run as" parolası
   İSTER, kullanma). Disable çalışan örneği durdurmaz.
6. **Taze klonda bilinen kırmızılar:** `test_verify_kofn_standalone`
   (gitignore'lu `outreach/ozkut-2026-08/verify_kofn.py`'ye bağımlı —
   düzeltme işi ayrıldı) ve `test_evolve_evaluator` 4 fail (adaptör;
   Faz 2'ye bakılacak). **Covering enstrümanının tüm testleri uzakta
   yeşil** — Track A bandının yolu temiz.

## İş başlatma (fiilen kullanılan)

Sarmalayıcı (`F:\kt\discovery-harness\runs\band-task.cmd`, CRLF):

```
@echo off
cd /d F:\kt\discovery-harness
if not exist runs\probes mkdir runs\probes
py -3.14 -m problems.covering.record_band --out runs/probes/track-a-uzak >> runs\probes\track-a-uzak.log 2>&1
```

```bash
scp band-task.cmd kt-uzak:F:/kt/discovery-harness/runs/band-task.cmd
```

```bash
ssh kt-uzak "schtasks /Create /F /TN kt-track-a /TR F:\kt\discovery-harness\runs\band-task.cmd /SC ONCE /ST 23:59 && schtasks /Run /TN kt-track-a && schtasks /Change /TN kt-track-a /DISABLE"
```

(SSH kopsa da koşu sürer; band idempotent — yeniden başlatma kaldığı
yerden devam eder.)

## İzleme / sonuç toplama

```bash
ssh kt-uzak "type F:\kt\discovery-harness\runs\probes\track-a-uzak\results.csv"
```

```bash
ssh kt-uzak "type F:\kt\discovery-harness\runs\probes\track-a-uzak.log"
```

```bash
scp -r kt-uzak:F:/kt/discovery-harness/runs/probes/track-a-uzak runs/probes/track-a-uzak-uzaktan
```

Durdurma: `ssh kt-uzak "schtasks /End /TN kt-track-a"` — ardından
`tasklist | findstr /i python` ile süreç ağacını DOĞRULA
(TaskStop zombi dersi geçerli).

## Aktif koşu kaydı

- **kt-track-a**: Track A bandı (21 hücre, ~10,5 saat) 2026-08-14
  ~13:45'te başladı; beklenen bitiş ~00:15. Çıktı:
  `runs/probes/track-a-uzak/` + `ADAY-*` (varsa).

## Faz 2 (evolve döngüsünü taşımadan önce)

- **Proxy erişimi ÇÖZÜLDÜ (2026-08-14):** üç port da uzaktan uçtan uca
  doğrulandı — `curl http://100.125.104.107:8317/v1/models` (ve 8318,
  8320) uzaktan `{"error":"Missing API key"}` dönüyor (= erişim var,
  anahtar kapısı aktif). Compose zaten 0.0.0.0'a yayınlıyor; ek
  güvenlik duvarı kuralı gerekmedi. Uzak evolve config'inde api_base
  `http://100.125.104.107:<port>/v1` olur.
- ⚠ 8317 o gün ölüydü: reboot sonrası 51821 portu WinNAT hariç-tutma
  aralığına düşünce Docker konteynerin TÜM forward'larını sessizce
  kurmamıştı → compose'ta 41821'e taşındı + force-recreate
  (ayrıntı: ana repo CLAUDE.md §0 "Port tamiri 2026-08-14").
- ⚠ Claude OAuth refresh invalid_grant — Opus/thinking yolu (8317/8320)
  kullanılmadan önce kullanıcı `claude-login.ps1` + container restart
  yapmalı. GLM (8318) API-key'li, hazır.
- KALAN: openevolve 0.3.2 kurulumu (`py -3.14 -m pip install --user
  openevolve==0.3.2`), pwsh 7, adaptör test faillerinin çözümü
  (4 fail), API anahtarının repo-dışı taşınması (env dosyası).
