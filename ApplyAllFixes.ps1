# ApplyAllFixes.ps1
# Wprowadza: PUBLIC_BASE_URL, CELERY_BROKER_URL, Nginx SSE, ESLint guard, statusy w docs, naprawa URL-i w RULES
# Działa na Windows/PowerShell. Robi backupy *.bak.YYYYMMDD-HHMMSS.

$ErrorActionPreference = "Stop"

function Backup-File($path) {
  if (Test-Path $path) {
    $ts = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item $path "$path.bak.$ts" -Force
    Write-Host "Backup: $path -> $path.bak.$ts" -ForegroundColor DarkGray
  }
}

function Replace-InFile($path, [string]$pattern, [string]$replacement, [switch]$Multiline) {
  if (-not (Test-Path $path)) { Write-Host "SKIP (brak pliku): $path" -ForegroundColor Yellow; return $false }
  $content = Get-Content -Raw -Encoding UTF8 $path
  $options = 'None'
  if ($Multiline) { $options = 'Multiline' }
  $new = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, $replacement, $options)
  if ($new -ne $content) {
    Backup-File $path
    $new | Set-Content -Encoding UTF8 $path
    Write-Host "OK: Zmieniono $path" -ForegroundColor Green
    return $true
  } else {
    Write-Host "INFO: Bez zmian (brak dopasowania) w $path" -ForegroundColor Yellow
    return $false
  }
}

function Ensure-Contains($path, [string]$marker, [string]$blockToAppend) {
  if (-not (Test-Path $path)) { Write-Host "SKIP (brak pliku): $path" -ForegroundColor Yellow; return }
  $content = Get-Content -Raw -Encoding UTF8 $path
  if ($content -notmatch [Regex]::Escape($marker)) {
    Backup-File $path
    ($content.TrimEnd() + "`r`n`r`n" + $blockToAppend.Trim() + "`r`n") | Set-Content -Encoding UTF8 $path
    Write-Host "OK: Dopisano blok do $path" -ForegroundColor Green
  } else {
    Write-Host "INFO: Blok już istnieje w $path (pomijam)" -ForegroundColor Yellow
  }
}

Write-Host "== START: ApplyAllFixes ==" -ForegroundColor Cyan

# 1) ARCHITECTURE.md
if (Test-Path "ARCHITECTURE.md") {
  # a) FRONT: NEXT_PUBLIC_API_URL
  Replace-InFile "ARCHITECTURE.md" `
    'NEXT_PUBLIC_API_URL\s*=\s*http://backend:8000' `
    'NEXT_PUBLIC_API_URL=${PUBLIC_BASE_URL}  # e.g., http://localhost or https://your.domain' | Out-Null

  # b) BACKEND & CELERY: CELERY_BROKER_URL po REDIS_URL w blokach env
  Replace-InFile "ARCHITECTURE.md" `
    '(?m)^(?<indent>\s*-\s*REDIS_URL=\$\{REDIS_URL\}\s*)$' `
    '${indent}' + "`r`n" + '      - CELERY_BROKER_URL=${CELERY_BROKER_URL}' -Multiline | Out-Null
} else {
  Write-Host "INFO: Brak ARCHITECTURE.md (pomijam)" -ForegroundColor Yellow
}

# 2) docker-compose.yml
if (Test-Path "docker-compose.yml") {
  # a) FRONT: NEXT_PUBLIC_API_URL -> PUBLIC_BASE_URL
  Replace-InFile "docker-compose.yml" `
    'NEXT_PUBLIC_API_URL\s*=\s*http://backend:8000' `
    'NEXT_PUBLIC_API_URL=${PUBLIC_BASE_URL}  # e.g., http://localhost or https://your.domain' | Out-Null

  # b) BACKEND & CELERY: CELERY_BROKER_URL po REDIS_URL
  Replace-InFile "docker-compose.yml" `
    '(?m)^(?<indent>\s*-\s*REDIS_URL=\$\{REDIS_URL\}\s*)$' `
    '${indent}' + "`r`n" + '      - CELERY_BROKER_URL=${CELERY_BROKER_URL}' -Multiline | Out-Null

  # c) NGINX volumes: upewnij się że mapujemy sse.conf (nie nadpisuj, tylko dopisz jeśli nie ma)
  $compose = Get-Content -Raw -Encoding UTF8 "docker-compose.yml"
  if ($compose -notmatch 'nginx\.conf:/etc/nginx/nginx\.conf') {
    Write-Host "INFO: Upewnij się, że nginx.conf jest zamapowany w docker-compose.yml (manual check)" -ForegroundColor Yellow
  }
  if ($compose -notmatch 'sse\.conf:/etc/nginx/sse\.conf') {
    Write-Host "INFO: Dodaj mapowanie ./nginx/sse.conf:/etc/nginx/sse.conf:ro w serwisie nginx (manual check)" -ForegroundColor Yellow
  }
} else {
  Write-Host "INFO: Brak docker-compose.yml (pomijam)" -ForegroundColor Yellow
}

# 3) RULES.md – zamień relatywne '/api' w przykładowych hookach
if (Test-Path "RULES.md") {
  # fetch('/api/...') -> fetch(`${base}/api/...`, credentials: 'include' jeśli nie ma
  Replace-InFile "RULES.md" `
    "fetch\('/api/" `
    'fetch(`${(process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "")}/api/' | Out-Null

  # new EventSource('/api/...') -> nowy absolutny
  Replace-InFile "RULES.md" `
    "new\s+EventSource\('/api/" `
    'new EventSource(`${(process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "")}/api/' | Out-Null

  # Dodatkowo spróbuj dodać credentials: 'include' tam gdzie jest login/logout/me
  Replace-InFile "RULES.md" `
    "(fetch\(`\$\{[^`]+\}/api/[^`]+`,\s*\{)([^}]*?)(\})" `
    '$1$2, credentials: ''include''$3' -Multiline | Out-Null
} else {
  Write-Host "INFO: Brak RULES.md (pomijam)" -ForegroundColor Yellow
}

# 4) CLAUDE.md – realny status + wzmianki o baseURL/SSE
if (Test-Path "CLAUDE.md") {
  Replace-InFile "CLAUDE.md" `
    '\*\*Current Status\*\:.*' `
    '**Current Status**: **MVP Complete – Pre-Production** – baseline test coverage 45% (target 80%); known ORM relation fix pending; readiness for UAT.' | Out-Null

  Ensure-Contains "CLAUDE.md" "SSE via Nginx" @'
#### Known Issues (Current Status) – additions
- **Frontend base URL**: Ensure `NEXT_PUBLIC_API_URL` points to the public entry (Nginx host), not the Docker service name (`backend`).
- **SSE via Nginx**: `proxy_buffering off; proxy_cache off;` and `text/event-stream` must be honored; use a dedicated `location` for `/api/v1/jobs/*/events`.
'@
} else {
  Write-Host "INFO: Brak CLAUDE.md (pomijam)" -ForegroundColor Yellow
}

# 5) PRD.md – status i luki znane
if (Test-Path "PRD.md") {
  Replace-InFile "PRD.md" `
    'Status\s+Draft\s*-\s*Ready\s*for\s*Review' `
    'Status	MVP ukończone – oczekuje na UAT' | Out-Null

  Ensure-Contains "PRD.md" "Luki znane (przed UAT)" @'
### Luki znane (przed UAT)
- Pokrycie testami: 45% (cel 80%) – skoncentrować się na warstwie services oraz testach SSE.
- ORM/Relacje: dodać `template_id` w `Report` i odblokować relację `ReportTemplate.generated_reports` + migracja.
- SSE przez Nginx: wyłączyć buforowanie (`proxy_buffering off`) i cache (`proxy_cache off`) dla ścieżek `/api/v1/jobs/*/events`.
'@
} else {
  Write-Host "INFO: Brak PRD.md (pomijam)" -ForegroundColor Yellow
}

# 6) ESLint guard (frontend/.eslintrc.cjs) – jeśli nie istnieje, utwórz
$eslintPath = "frontend\.eslintrc.cjs"
if (-not (Test-Path $eslintPath)) {
  New-Item -ItemType Directory -Force -Path "frontend" | Out-Null
  @'
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react'],
  extends: ['next/core-web-vitals', 'plugin:@typescript-eslint/recommended'],
  rules: {
    // Disallow relative API calls from the browser – must use absolute base URL
    'no-restricted-syntax': [
      'error',
      {
        selector: "CallExpression[callee.name='fetch'] Literal[value^='/api/']",
        message: 'Do not use relative /api URLs. Use NEXT_PUBLIC_API_URL (absolute) or ApiClient.'
      }
    ]
  }
}
'@ | Set-Content -Encoding UTF8 $eslintPath
  Write-Host "OK: utworzono $eslintPath" -ForegroundColor Green
} else {
  Write-Host "INFO: $eslintPath już istnieje (scal ręcznie jeśli chcesz dodać regułę)" -ForegroundColor Yellow
}

# 7) .env.example – dodaj brakujące
if (Test-Path ".env.example") {
  Ensure-Contains ".env.example" "PUBLIC_BASE_URL" @'
CELERY_BROKER_URL=redis://redis:6379/1
# Frontend public entry (what the BROWSER can reach)
PUBLIC_BASE_URL=http://localhost
'@
} else {
  # jeśli nie istnieje, utwórz nowy z sensownymi defaultami
  @'
DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/fro_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me
CELERY_BROKER_URL=redis://redis:6379/1
PUBLIC_BASE_URL=http://localhost
'@ | Set-Content -Encoding UTF8 ".env.example"
  Write-Host "OK: utworzono .env.example" -ForegroundColor Green
}

# 8) nginx/sse.conf – utwórz/odśwież
New-Item -ItemType Directory -Force -Path "nginx" | Out-Null
$SseConf = @'
# SSE-friendly locations (include this from nginx.conf http{} block)

location /api/ {
  proxy_pass         http://backend:8000/api/;
  proxy_set_header   Host $host;
  proxy_set_header   X-Real-IP $remote_addr;
  proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_http_version 1.1;
  proxy_set_header   Connection "";
}

location ~ ^/api/v1/jobs/.*/events$ {
  proxy_pass                 http://backend:8000;
  proxy_set_header           Host $host;
  proxy_http_version         1.1;
  proxy_set_header           Connection '';
  proxy_buffering            off;
  proxy_cache                off;
  chunked_transfer_encoding  on;
  add_header                 Cache-Control no-cache;
}
'@
Backup-File "nginx\sse.conf"
$SseConf | Set-Content -Encoding UTF8 "nginx\sse.conf"
Write-Host "OK: zapisano nginx\sse.conf" -ForegroundColor Green

Write-Host "== DONE: ApplyAllFixes ==" -ForegroundColor Cyan
