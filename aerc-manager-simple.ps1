# AERC Project Manager - Windows PowerShell 版本
# 支援 Docker 和 Podman (當可用時)

param(
    [Parameter(Position = 0)]
    [string]$Command = "",
    
    [Parameter(Position = 1)]
    [string]$Parameter = ""
)

# 基本設定
$COMPOSE_FILE = "docker-compose.yml"

function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Warning { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host $msg -ForegroundColor Red }

function Test-ContainerTools {
    Write-Info "Checking available container tools..."
    
    # 檢查 Docker
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Success "[OK] Docker found: $dockerVersion"
            try {
                docker info 2>$null | Out-Null
                Write-Success "[OK] Docker daemon is running"
                $global:RUNTIME = "docker"
                return $true
            } catch {
                Write-Warning "[WARNING] Docker daemon not running"
            }
        }
    } catch {
        Write-Info "Docker not found"
    }
    
    # 檢查 Podman
    try {
        $podmanVersion = podman --version 2>$null
        if ($podmanVersion) {
            Write-Success "[OK] Podman found: $podmanVersion"
            $global:RUNTIME = "podman"
            Write-Warning "Note: Podman detected. Some docker-compose features may need adaptation."
            return $true
        }
    } catch {
        Write-Info "Podman not found"
    }
    
    Write-Error "[ERROR] No container runtime found. Please install Docker Desktop or Podman."
    return $false
}

function Test-Compose {
    if ($global:RUNTIME -eq "docker") {
        try {
            docker-compose version 2>$null | Out-Null
            $global:COMPOSE = "docker-compose"
            Write-Success "[OK] docker-compose available"
            return $true
        } catch {
            try {
                docker compose version 2>$null | Out-Null
                $global:COMPOSE = "docker compose"
                Write-Success "[OK] docker compose available"
                return $true
            } catch {
                Write-Error "[ERROR] Docker Compose not available"
                return $false
            }
        }
    } else {
        # 檢查 podman compose (內建功能)
        try {
            podman compose version 2>$null | Out-Null
            $global:COMPOSE = "podman compose"
            Write-Success "[OK] podman compose available"
            return $true
        } catch {
            # 檢查 podman-compose (外部工具)
            try {
                podman-compose --version 2>$null | Out-Null
                $global:COMPOSE = "podman-compose"
                Write-Success "[OK] podman-compose available"
                return $true
            } catch {
                Write-Warning "[WARNING] No compose tool found for Podman"
                Write-Info "Options:"
                Write-Info "1. Update Podman to 4.0+ for built-in compose support"
                Write-Info "2. Install podman-compose: pip install podman-compose"
                return $false
            }
        }
    }
}

function Read-EnvFile {
    param([string]$envPath = ".env")
    $envVars = @{}
    if (Test-Path $envPath) {
        Get-Content $envPath | Where-Object { $_ -match "=" } | ForEach-Object {
            $kv = $_ -split "=", 2
            $key = $kv[0].Trim()
            $val = $kv[1].Trim().Trim('"')
            $envVars[$key] = $val
        }
    }
    return $envVars
}

function Generate-SafePassword {
    $charset = @(
        'a','b','c','d','e','f','g','h','i','j','k','l','m',
        'n','o','p','q','r','s','t','u','v','w','x','y','z',
        'A','B','C','D','E','F','G','H','I','J','K','L','M',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        '0','1','2','3','4','5','6','7','8','9',
        '#','^','&','*','-','_','+'
    )
    return -join (1..20 | ForEach-Object { Get-Random -InputObject $charset })
}


function UrlEncode {
    param([string]$raw)
    return [System.Uri]::EscapeDataString($raw)
}

function Update-EnvPassword {
    $envPath = ".env"
    $envVars = Read-EnvFile $envPath
    if (-not $envVars.ContainsKey("POSTGRES_PASSWORD")) {
        Write-Warning "No POSTGRES_PASSWORD found in .env file. Generating secure password..."
        $newPassword = Generate-SafePassword
        $encoded = UrlEncode $newPassword

        # Update lines
        $newLines = @()
        foreach ($line in Get-Content $envPath) {
            if ($line -match "^POSTGRES_PASSWORD=") {
                continue
            } elseif ($line -match "^DATABASE_URL=") {
                $user = $envVars["POSTGRES_USER"]
                $dbhost = "db"
                $port = "5432"
                $dbname = $envVars["POSTGRES_DB"]
                $newUrl = "DATABASE_URL=postgres://${user}:${encoded}@${dbHost}:${port}/${dbname}"
                $newLines += $newUrl
                continue
            }
            $newLines += $line
        }

        # Add new password
        $newLines += "POSTGRES_PASSWORD=$newPassword"

        # 如果原本沒有 DATABASE_URL，也補上
        if (-not $envVars.ContainsKey("DATABASE_URL")) {
            $user = $envVars["POSTGRES_USER"]
            $dbhost = "db"
            $port = "5432"
            $dbname = $envVars["POSTGRES_DB"]
            $newLines += "DATABASE_URL=postgres://${user}:${encoded}@${dbhost}:${port}/${dbname}"
        }

        Set-Content $envPath $newLines

        Write-Success "Password has been updated in .env and DATABASE_URL has been regenerated."
        Write-Host "Generated password: " -NoNewline
        Write-Host "$newPassword" -ForegroundColor Yellow
    } else {
        Write-Info "Password already exists in .env. Skipping generation."
    }
}

Update-EnvPassword

function Rebuild-Services {
    Write-Info "Rebuilding AERC services..."
    if ($global:COMPOSE) {
        Write-Info "Stopping and removing existing containers..."
        if ($global:COMPOSE -eq "docker-compose") {
            docker-compose -f $COMPOSE_FILE down
            Write-Info "Rebuilding images..."
            docker-compose -f $COMPOSE_FILE build --no-cache
            Write-Info "Starting services with rebuilt images..."
            docker-compose -f $COMPOSE_FILE up -d
        } elseif ($global:COMPOSE -eq "docker compose") {
            docker compose -f $COMPOSE_FILE down
            Write-Info "Rebuilding images..."
            docker compose -f $COMPOSE_FILE build --no-cache
            Write-Info "Starting services with rebuilt images..."
            docker compose -f $COMPOSE_FILE up -d
        } elseif ($global:COMPOSE -eq "podman compose") {
            podman compose -f $COMPOSE_FILE down
            Write-Info "Rebuilding images..."
            podman compose -f $COMPOSE_FILE build --no-cache
            Write-Info "Starting services with rebuilt images..."
            podman compose -f $COMPOSE_FILE up -d
        } else {
            # podman-compose
            & $global:COMPOSE -f $COMPOSE_FILE down
            Write-Info "Rebuilding images..."
            & $global:COMPOSE -f $COMPOSE_FILE build --no-cache
            Write-Info "Starting services with rebuilt images..."
            & $global:COMPOSE -f $COMPOSE_FILE up -d
        }
        Write-Success "[OK] Services rebuilt and started"
    } else {
        Write-Warning "Compose not available. Use '$($global:RUNTIME) build' commands manually."
    }
}

function Start-Services {
    Write-Info "Starting AERC services..."
    if ($global:COMPOSE) {
        if ($global:COMPOSE -eq "docker-compose") {
            docker-compose -f $COMPOSE_FILE up -d
        } elseif ($global:COMPOSE -eq "docker compose") {
            docker compose -f $COMPOSE_FILE up -d
        } elseif ($global:COMPOSE -eq "podman compose") {
            podman compose -f $COMPOSE_FILE up -d
        } else {
            # podman-compose
            & $global:COMPOSE -f $COMPOSE_FILE up -d
        }
        Write-Success "[OK] Services started"
    } else {
        Write-Warning "Compose not available. Use '$($global:RUNTIME) run' commands manually."
    }
}

function Stop-Services {
    Write-Info "Stopping AERC services..."
    if ($global:COMPOSE) {
        if ($global:COMPOSE -eq "docker-compose") {
            docker-compose -f $COMPOSE_FILE down
        } elseif ($global:COMPOSE -eq "docker compose") {
            docker compose -f $COMPOSE_FILE down
        } elseif ($global:COMPOSE -eq "podman compose") {
            podman compose -f $COMPOSE_FILE down
        } else {
            # podman-compose
            & $global:COMPOSE -f $COMPOSE_FILE down
        }
        Write-Success "[OK] Services stopped"
    } else {
        Write-Warning "Compose not available. Use '$($global:RUNTIME) stop' commands manually."
    }
}

function Get-Status {
    Write-Info "AERC service status:"
    if ($global:COMPOSE) {
        if ($global:COMPOSE -eq "docker-compose") {
            docker-compose -f $COMPOSE_FILE ps
        } elseif ($global:COMPOSE -eq "docker compose") {
            docker compose -f $COMPOSE_FILE ps
        } elseif ($global:COMPOSE -eq "podman compose") {
            podman compose -f $COMPOSE_FILE ps
        } else {
            # podman-compose
            & $global:COMPOSE -f $COMPOSE_FILE ps
        }
    } else {
        Write-Info "Showing container status using $($global:RUNTIME):"
        if ($global:RUNTIME -eq "docker") {
            docker ps --filter "name=aerc"
        } else {
            podman ps --filter "name=aerc"
        }
    }
}

function Get-Logs {
    param($lines = "100")
    Write-Info "Service logs (last $lines lines):"
    if ($global:COMPOSE) {
        if ($global:COMPOSE -eq "docker-compose") {
            docker-compose -f $COMPOSE_FILE logs --tail=$lines
        } elseif ($global:COMPOSE -eq "docker compose") {
            docker compose -f $COMPOSE_FILE logs --tail=$lines
        } elseif ($global:COMPOSE -eq "podman compose") {
            podman compose -f $COMPOSE_FILE logs --tail=$lines
        } else {
            # podman-compose
            & $global:COMPOSE -f $COMPOSE_FILE logs --tail=$lines
        }
    } else {
        Write-Warning "Compose not available. Use '$($global:RUNTIME) logs <container>' manually."
    }
}

function Show-Help {
    Write-Info "===== AERC Project Manager ====="
    Write-Host ""
    Write-Host "Usage: .\aerc-manager-simple.ps1 [command]"
    Write-Host ""
    Write-Host "Available commands:"
    Write-Host "  start    - Start all services"
    Write-Host "  stop     - Stop all services"
    Write-Host "  rebuild  - Rebuild and restart all services"
    Write-Host "  status   - Show service status"
    Write-Host "  logs [n] - Show logs (default: 100 lines)"
    Write-Host "  help     - Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\aerc-manager-simple.ps1 start"
    Write-Host "  .\aerc-manager-simple.ps1 rebuild"
    Write-Host "  .\aerc-manager-simple.ps1 status"
    Write-Host "  .\aerc-manager-simple.ps1 logs 50"
}

# 主邏輯
if (-not (Test-ContainerTools)) {
    exit 1
}

$composeAvailable = Test-Compose

if (-not (Test-Path $COMPOSE_FILE)) {
    Write-Error "[ERROR] $COMPOSE_FILE not found in current directory"
    exit 1
}

switch ($Command) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "rebuild" { Rebuild-Services }
    "status" { Get-Status }
    "logs" { 
        if ($Parameter) {
            Get-Logs -lines $Parameter
        } else {
            Get-Logs
        }
    }
    "help" { Show-Help }
    "" { Show-Help }
    default {
        Write-Error "Unknown command: $Command"
        Show-Help
    }
}
