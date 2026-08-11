# P1 (kofn) keşif döngüsünü başlatır (Faz E).
# Kullanım (repo kökünden, GECE KOŞUSU BİTTİKTEN SONRA):
#   .\evolve\run.ps1 -GeceKosusuBitti -Iterations 5     # duman testi
#   .\evolve\run.ps1 -GeceKosusuBitti                   # uzun koşu (2000 iter)
#   .\evolve\run.ps1 -GeceKosusuBitti -Instance data\kofn\instances\gen-n200-m8-s3.kofn
# Benchmark-v2 dilimi (2026-08-05; buyuk-n fitness, evrilen genomdan devam):
#   .\evolve\run.ps1 -GeceKosusuBitti -Iterations 50 `
#     -InitialProgram "evolve\artifacts\best_20260805.py" `
#     -Instance ("data\kofn\instances\train-router-n500-m12-s7.kofn;" +
#                "data\kofn\instances\train-enerji-n300-m10-s14.kofn;" +
#                "data\kofn\instances\train-router-n20-m4-s10.kofn") `
#     -OutDir "runs\evolve\bench-v2-dilim1"
param(
    [string]$Problem = "kofn",
    # ';' ayracli liste = coklu-instance fitness (ortalama). Varsayilan:
    # DILIM-1 uzun kosu seti (docs/faz-e-gradyan.md, 2026-08-05):
    #   n25-m5-s3  -> enumere edilebilir capa (kanitli opt 0.7657)
    #   n60-m10-s4 -> ref plato 0.7371 (dogunluktan uzak, m=10)
    #   n100-m6-s4 -> derinlik sinyalli, ref64 0.6339
    # Tohum uclunun hepsinde 0.000; yenilecek baseline seti ort. ~0.712.
    [string]$Instance = ("data\kofn\instances\gen-sert-n25-m5-s3.kofn;" +
                         "data\kofn\instances\gen-sert-n60-m10-s4.kofn;" +
                         "data\kofn\instances\gen-sert-n100-m6-s4.kofn"),
    [int]$Iterations = 2000,
    [string]$OutDir = "",
    [string]$Checkpoint = "",
    # Baslangic genomu. Benchmark-v2 dilimi (2026-08-05) icin evrilen
    # artefakttan devam edilir: evolve\artifacts\best_20260805.py
    # (dosya salt okunur kullanilir; OpenEvolve kopyasini evriltir).
    [string]$InitialProgram = "problems\kofn\seed_solver.py",
    # OpenEvolve config dosyasi (Görev 5c). Varsayilan: kofn config.yaml
    # (mevcut davranis korunsun). capset icin: evolve\config.capset.yaml.
    [string]$ConfigPath = "evolve\config.yaml",
    # cli-proxy-api config dosyasi (API key kaynagi). Varsayilan: config.yaml
    # (Claude OAuth, 8317). GLM (8318) icin: config.glm.yaml.
    [string]$ProxyConfig = "config.yaml",
    # Runner'in aday programa verdigi duvar saati (instance BASINA, sn).
    # Cozucunun sure butcesi (or. COVERING_SEED_TIME_S) bunun ALTINDA
    # kalmali; or. butce 70 icin 80 ver (covering v28 rekor dilimi).
    [string]$SolverTimeoutS = "55",
    [switch]$GeceKosusuBitti
)
$ErrorActionPreference = "Stop"

# §0 guard'ı: cvrp-discovery gece koşusu aynı makinede CPU + LLM proxy
# paylaşıyor. Bilinçli onay olmadan döngü başlamaz.
if (-not $GeceKosusuBitti) {
    throw ("CLAUDE.md §0: cvrp-discovery gece kosusu bitmeden evolve dongusu " +
           "baslatilmaz. Bittiyse -GeceKosusuBitti anahtariyla calistir.")
}

# API key'i cli-proxy-api config'inden oku (repo'ya key yazmamak için).
# Varsayilan: config.yaml (Claude OAuth, 8317). GLM (8318) icin -ProxyConfig
# config.glm.yaml. Iki container ayni imaj (eceasy/cli-proxy-api), ayni key
# formati (kök CLAUDE.md §0).
$proxyCfgPath = Join-Path "C:\kt\upwork\cli-api" $ProxyConfig
$proxyCfg = Get-Content $proxyCfgPath -Raw
if ($proxyCfg -match '(?ms)api-keys:\s*\r?\n\s*-\s*"([^"]+)"') {
    $env:OPENAI_API_KEY = $Matches[1]
} else {
    throw "cli-proxy-api $ProxyConfig içinde api-keys bulunamadı"
}

# Ansambl icin ikinci anahtar: 8317 (Claude OAuth) config.yaml'dan.
# Yalniz ansambl configleri ${OPENAI_API_KEY_OPUS} kullanir; digerleri etkilenmez.
$opusCfgPath = Join-Path "C:\kt\upwork\cli-api" "config.yaml"
if (Test-Path $opusCfgPath) {
    $opusCfg = Get-Content $opusCfgPath -Raw
    if ($opusCfg -match '(?ms)api-keys:\s*\r?\n\s*-\s*"([^"]+)"') {
        $env:OPENAI_API_KEY_OPUS = $Matches[1]
    }
}

$instanceList = $Instance -split ';' | ForEach-Object { $_.Trim() } |
    Where-Object { $_ }
if (-not $OutDir) {
    $name = [IO.Path]::GetFileNameWithoutExtension($instanceList[0])
    if ($instanceList.Count -gt 1) { $name = "$name-mix$($instanceList.Count)" }
    $OutDir = "runs\evolve\$name"
}
$env:DISCOVERY_PROBLEM = $Problem
$env:DISCOVERY_INSTANCE = ($instanceList |
    ForEach-Object { (Resolve-Path $_).Path }) -join ';'
$env:DISCOVERY_SOLVER_TIMEOUT_S = $SolverTimeoutS

# Döngü öncesi enstrüman sağlığı: testler yeşil değilse başlama (guardrail)
# Arşiv env'leri pytest'e SIZMASIN: adaptör testleri gerçek arşiv dizinine
# çözüm yazar (2026-08-10'da yaşandı). Kapıdan önce kaldır, sonra geri koy.
$savedArch = $env:DISCOVERY_ARCHIVE_DIR
$savedBelow = $env:DISCOVERY_ARCHIVE_BELOW
$savedAbove = $env:DISCOVERY_ARCHIVE_ABOVE
Remove-Item Env:DISCOVERY_ARCHIVE_DIR -ErrorAction SilentlyContinue
Remove-Item Env:DISCOVERY_ARCHIVE_BELOW -ErrorAction SilentlyContinue
Remove-Item Env:DISCOVERY_ARCHIVE_ABOVE -ErrorAction SilentlyContinue
python -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) { throw "test suite kırmızı — döngü başlatılmadı" }
if ($savedArch) { $env:DISCOVERY_ARCHIVE_DIR = $savedArch }
if ($savedBelow) { $env:DISCOVERY_ARCHIVE_BELOW = $savedBelow }
if ($savedAbove) { $env:DISCOVERY_ARCHIVE_ABOVE = $savedAbove }

$args = @($InitialProgram, "harness\evolve_evaluator.py",
          "--config", $ConfigPath,
          "--output", $OutDir,
          "--iterations", $Iterations)
if ($Checkpoint) { $args += @("--checkpoint", $Checkpoint) }

openevolve-run @args
