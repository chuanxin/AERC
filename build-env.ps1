# PowerShell Docker Setup Script
# 執行注意事項：
# 1. 需要 PowerShell 7+ 版本以獲得最佳兼容性
#
# 2. 首次執行前需設定執行政策：
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#
# 3. 需安裝 OpenSSL (可通過 Chocolatey 或 Git for Windows 安裝)
# 4. 建議在 Windows Terminal 或 VS Code 中執行以獲得完整 ANSI 顏色支持
# 5. 文件路徑需保持 Unix 風格（與 Docker 兼容）
#
# 執行命令：
# pwsh -NoProfile -ExecutionPolicy Bypass -File build-env.ps1


# ANSI Color Codes
$ESC = [char]27
$GREEN = "$ESC[0;32m"
$BLUE = "$ESC[0;34m"
$YELLOW = "$ESC[1;33m"
$RED = "$ESC[0;31m"
$NC = "$ESC[0m"

# Check first run condition
$modelsDir = "api/migrations/models"
$certbotDir = "dry-farm/certbot"

$envExists = Test-Path .env
$modelsDirExists = Test-Path $modelsDir -PathType Container
$modelsDirEmpty = $modelsDirExists -and ((Get-ChildItem $modelsDir -Force | Measure-Object).Count -eq 0)
$FIRST_RUN = (-not $envExists) -or (-not $modelsDirExists) -or $modelsDirEmpty

# Check certbot directory
$certbotExists = Test-Path $certbotDir -PathType Container
$certbotValid = $certbotExists -and ((Get-ChildItem $certbotDir -Force | Measure-Object).Count -gt 0)
$CERTBOT_EXISTS = $certbotValid

# Generate new secret key
$NEW_SECRET_KEY = openssl rand -hex 32

# Database configuration
$DATABASE_URL = "postgres://hello_fastapi:hello_fastapi@db:5432/hello_fastapi_dev"
$POSTGRES_USER = "hello_fastapi"
$POSTGRES_PASSWORD = "hello_fastapi"
$POSTGRES_DB = "hello_fastapi_dev"

# API configuration
$FAST_API_BASE_URL = "/api"
$FAST_API_TARGET = "http://api:5000/"
$FAST_API_VERSION = "v1"

# Create .env file if not exists
if (-not (Test-Path .env)) {
    New-Item -ItemType File -Path .env | Out-Null
}

# Function to update or add environment variable
function Update-EnvVariable {
    param(
        [string]$pattern,
        [string]$newLine,
        [string]$comment = $null
    )
    
    $content = Get-Content .env -ErrorAction SilentlyContinue
    $found = $false
    $commentExists = $false

    foreach ($line in $content) {
        if ($line -match $pattern) {
            $found = $true
            break
        }
        if ($comment -and $line -eq $comment) {
            $commentExists = $true
        }
    }

    if ($found) {
        $content = $content -replace $pattern, $newLine
    }
    else {
        if ($comment) {
            if (-not $commentExists) {
                $content += $comment
            }
        }
        $content += $newLine
    }

    $content | Set-Content .env
}

# Update environment variables
Update-EnvVariable -pattern "^SECRET_KEY=.*" -newLine "SECRET_KEY=$NEW_SECRET_KEY" -comment "# api environment variables in docker-compose"
Update-EnvVariable -pattern "^DATABASE_URL=.*" -newLine "DATABASE_URL=$DATABASE_URL"
Update-EnvVariable -pattern "^POSTGRES_USER=.*" -newLine "POSTGRES_USER=$POSTGRES_USER" -comment "`n# postgres environment variables in docker-compose"
Update-EnvVariable -pattern "^POSTGRES_PASSWORD=.*" -newLine "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
Update-EnvVariable -pattern "^POSTGRES_DB=.*" -newLine "POSTGRES_DB=$POSTGRES_DB"
Update-EnvVariable -pattern "^FAST_API_BASE_URL=.*" -newLine "FAST_API_BASE_URL=$FAST_API_BASE_URL" -comment "`n# dry-farm environment variables in docker-compose"
Update-EnvVariable -pattern "^FAST_API_TARGET=.*" -newLine "FAST_API_TARGET=$FAST_API_TARGET"
Update-EnvVariable -pattern "^FAST_API_VERSION=.*" -newLine "FAST_API_VERSION=$FAST_API_VERSION"

# SSL certificate warning
if (-not $CERTBOT_EXISTS) {
    Write-Host "`n${RED}===== WARNING: SSL Certificates Missing =====${NC}"
    Write-Host "The ${YELLOW}dry-farm/certbot${NC} directory is missing or empty."
    Write-Host "If you're running on a production environment with port 443, SSL certificates are required."
    Write-Host "Please copy the certbot directory from your development environment:"
    Write-Host "   ${BLUE}scp -r your-dev-machine:path/to/AERC/dry-farm/certbot ./dry-farm/${NC}"
    Write-Host "Or press any key to continue without SSL (suitable for local development only)..."
    $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
}

# Build and start containers
Write-Host "`n${GREEN}===== Building Docker Containers =====${NC}"
docker-compose build --no-cache
docker-compose up -d

# Wait for containers to initialize
Start-Sleep -Seconds 3

# Display service information
Write-Host "`n${BLUE}===== Service Access Information =====${NC}"

# Get frontend port
$frontendPort = docker-compose port dry-farm 3000
if ($frontendPort) {
    $FRONTEND_PORT = $frontendPort.Split(':')[-1]
    Write-Host "Frontend service accessible at  ➜  ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
}

# Get API port
$apiPort = docker-compose port api 5000
if ($apiPort) {
    $API_PORT = $apiPort.Split(':')[-1]
    Write-Host "API service accessible at  ➜  ${YELLOW}http://localhost:${API_PORT}${NC}"
}

# Display first run instructions
if ($FIRST_RUN) {
    Write-Host "`n${YELLOW}===== First Time Setup After Cloning =====${NC}"
    Write-Host @"
This appears to be the first run after cloning. Please follow these steps:

${GREEN}1. Apply existing migrations to set up the database:${NC}
   ${BLUE}docker-compose exec api aerich upgrade${NC}

${GREEN}2. If you encounter migration errors, you may need to initialize the database:${NC}
   ${BLUE}docker-compose exec api aerich init -t src.database.config.TORTOISE_ORM${NC}
   ${BLUE}docker-compose exec api aerich init-db${NC}

${RED}IMPORTANT:${NC} Do NOT delete migration files in migrations/models/ unless you're starting a completely new project.
These files represent the database schema evolution and are essential for maintaining consistent state.

${YELLOW}===== For SSL Configuration (Production Environment) =====${NC}
"@

    if (-not $CERTBOT_EXISTS) {
        Write-Host "${RED}⚠️  SSL certificates are missing! The frontend won't work on port 443 without them.${NC}"
        Write-Host "For production deployment, you must copy the certbot directory from your development environment:"
        Write-Host "   ${BLUE}scp -r your-dev-machine:path/to/AERC/dry-farm/certbot ./dry-farm/${NC}"
        Write-Host "Then restart the containers:  ${BLUE}docker-compose restart${NC}"
    }
    else {
        Write-Host "${GREEN}✓ SSL certificates found in dry-farm/certbot.${NC} The frontend should work correctly on port 443."
    }

    Write-Host @"
${YELLOW}===== For Subsequent Database Updates =====${NC}
When you modify database models, execute these commands to update the database:

1. Create migration files:
   ${BLUE}docker-compose exec api aerich migrate --name descriptive_name_of_change${NC}

2. Apply migrations:
   ${BLUE}docker-compose exec api aerich upgrade${NC}
"@
}

Write-Host "`n${GREEN}✅ Setup complete. The application should now be running.${NC}"