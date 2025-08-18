# AERC Deployment Directory Structure Initialization Script
# This script creates the necessary directory structure for AERC deployment

# Step 1: Get the deployment root directory from user
$deployRoot = Read-Host "Please enter the project directory path (e.g., C:\AERC or D:\Projects\AERC)"

# Create the root directory if it doesn't exist
if (-not (Test-Path $deployRoot)) {
    Write-Host "`nProject directory does not exist. Creating: $deployRoot" -ForegroundColor Yellow
    try {
        New-Item -ItemType Directory -Path $deployRoot -Force | Out-Null
        Write-Host "Successfully created project directory: $deployRoot" -ForegroundColor Green
    } catch {
        Write-Host "`nError: Failed to create directory '$deployRoot'. Please check permissions and path validity." -ForegroundColor Red
        Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`nProject directory already exists: $deployRoot" -ForegroundColor Green
}

Write-Host "`nProject root directory: $deployRoot" -ForegroundColor Cyan

# Step 2: Create directory structure mapping table
$directoryMap = @(
    "AERC-Data",
    "AERC-Data\backups",
    "AERC-Data\backups\CSV",
    "AERC-Deploy",
    "AERC-Deploy\app",
    "AERC-Deploy\releases",
    "AERC-Deploy\runtime",
    "AERC-Deploy\scripts",
    "AERC-Deploy\temp",
    "AERC-Deploy\temp\checkout"
)

# Step 3: Iterate and create folders
foreach ($relativePath in $directoryMap) {
    $fullPath = Join-Path $deployRoot $relativePath
    if (-not (Test-Path $fullPath)) {
        Write-Host "Creating folder: $fullPath" -ForegroundColor Green
        New-Item -ItemType Directory -Path $fullPath | Out-Null
    } else {
        Write-Host "Folder already exists, skipping: $fullPath" -ForegroundColor Yellow
    }
}

Write-Host "`nAERC deployment directory structure initialization completed." -ForegroundColor Cyan

# Step 4: Create .env file with user input
$envFilePath = Join-Path $deployRoot "AERC-Deploy\.env"
if (-not (Test-Path $envFilePath)) {
    Write-Host "`nConfiguring environment variables..." -ForegroundColor Cyan
    Write-Host "Press Enter to use default values shown in brackets." -ForegroundColor Yellow
    
    # Collect user inputs with defaults
    $secretKey = Read-Host "Enter SECRET_KEY [9561611c5e61802f7bf2ea77b1f494cc62b28f078b2db8e8889661c7683862da]"
    if ([string]::IsNullOrWhiteSpace($secretKey)) { 
        $secretKey = "9561611c5e61802f7bf2ea77b1f494cc62b28f078b2db8e8889661c7683862da" 
    }
    
    $postgresUser = Read-Host "Enter POSTGRES_USER [aerc_dryfarm_admin]"
    if ([string]::IsNullOrWhiteSpace($postgresUser)) { 
        $postgresUser = "aerc_dryfarm_admin" 
    }
    
    $postgresDb = Read-Host "Enter POSTGRES_DB [aerc_dryfarm]"
    if ([string]::IsNullOrWhiteSpace($postgresDb)) { 
        $postgresDb = "aerc_dryfarm" 
    }
    
    $postgresPassword = Read-Host "Enter POSTGRES_PASSWORD [U-_0ZjJQgCgTR*Evcm-m]"
    if ([string]::IsNullOrWhiteSpace($postgresPassword)) { 
        $postgresPassword = "U-_0ZjJQgCgTR*Evcm-m" 
    }
    
    $apiBaseUrl = Read-Host "Enter FAST_API_BASE_URL [/api]"
    if ([string]::IsNullOrWhiteSpace($apiBaseUrl)) { 
        $apiBaseUrl = "/api" 
    }
    
    $apiTarget = Read-Host "Enter FAST_API_TARGET [http://localhost:5000/]"
    if ([string]::IsNullOrWhiteSpace($apiTarget)) { 
        $apiTarget = "http://localhost:5000/" 
    }
    
    $apiVersion = Read-Host "Enter FAST_API_VERSION [v1]"
    if ([string]::IsNullOrWhiteSpace($apiVersion)) { 
        $apiVersion = "v1" 
    }
    
    # Generate DATABASE_URL
    $databaseUrl = "postgres://${postgresUser}:${postgresPassword}@localhost:5432/${postgresDb}"
    
    Write-Host "Creating .env file..." -ForegroundColor Green
    $envContent = @"
# api environment variables in docker-compose
SECRET_KEY=$secretKey

# postgres environment variables in docker-compose
POSTGRES_USER=$postgresUser
POSTGRES_DB=$postgresDb

# dry-farm environment variables in docker-compose
FAST_API_BASE_URL=$apiBaseUrl
FAST_API_TARGET=$apiTarget
FAST_API_VERSION=$apiVersion

POSTGRES_PASSWORD=$postgresPassword
DATABASE_URL=$databaseUrl
"@
    Set-Content -Path $envFilePath -Value $envContent -Encoding UTF8
    Write-Host "Created .env file at: $envFilePath" -ForegroundColor Green
} else {
    Write-Host "`n.env file already exists, skipping configuration." -ForegroundColor Yellow
}

# Step 5: Generate deployment scripts
$scriptsPath = Join-Path $deployRoot "AERC-Deploy\scripts"
Write-Host "`nGenerating deployment scripts..." -ForegroundColor Cyan

# Generate Bootstrap_DB.ps1
$bootstrapContent = @'
# Bootstrap_DB.ps1
# Set up PostgreSQL CLI environment and initialize database and user

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "`nThis script requires administrator privileges to modify system PATH." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and execute this script again." -ForegroundColor Yellow
    Write-Host "`nTo run as administrator:" -ForegroundColor Cyan
    Write-Host "1. Right-click on PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as administrator'" -ForegroundColor White
    Write-Host "3. Navigate to the script directory and run again" -ForegroundColor White
    Read-Host "`nPress Enter to exit"
    exit 1
}

Write-Host "`nStarting PostgreSQL CLI environment setup..." -ForegroundColor Cyan

# Detect PostgreSQL installation directory
$pgPath = Get-ChildItem "C:\Program Files\PostgreSQL" | 
    Where-Object { Test-Path "$($_.FullName)\bin\psql.exe" } |
    Select-Object -First 1

if ($pgPath) {
    $binPath = "$($pgPath.FullName)\bin"

    # Add PostgreSQL bin path to system PATH variable
    $currentPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
    if (-not $currentPath.Split(';') -contains $binPath) {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binPath", [EnvironmentVariableTarget]::Machine)
        Write-Host "`nPostgreSQL bin directory added to system PATH." -ForegroundColor Green
    } else {
        Write-Host "`nPostgreSQL bin directory already exists in system PATH." -ForegroundColor Yellow
    }

    # Check if psql is executable
    Write-Host "`nVerifying psql availability..."
    $psqlPath = "$binPath\psql.exe"
    try {
        & "$psqlPath" --version | Out-Host
    } catch {
        Write-Host "`nUnable to execute psql.exe. Please verify installation." -ForegroundColor Red
        exit 1
    }

    # Load environment variables from .env file
    $envPath = "..\.env"
    if (-not (Test-Path $envPath)) {
        Write-Host "`nError: .env file not found at $envPath. Please run init-aerc-deployment.ps1 first." -ForegroundColor Red
        exit 1
    }

    Write-Host "`nLoading environment variables from .env file..."
    $envVars = @{}
    Get-Content $envPath | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }

    # Get database parameters from .env
    $username = $envVars["POSTGRES_USER"]
    $password = $envVars["POSTGRES_PASSWORD"]
    $dbname = $envVars["POSTGRES_DB"]

    if (-not $username -or -not $password -or -not $dbname) {
        Write-Host "`nError: Missing required database parameters in .env file:" -ForegroundColor Red
        Write-Host "   POSTGRES_USER: $username"
        Write-Host "   POSTGRES_PASSWORD: $password"
        Write-Host "   POSTGRES_DB: $dbname"
        exit 1
    }

    Write-Host "`nDatabase parameters loaded from .env:"
    Write-Host "   User: $username"
    Write-Host "   Database: $dbname"
    Write-Host "   Password: [HIDDEN]"

    Write-Host "`nCreating PostgreSQL user and database..."
    & "$psqlPath" -U postgres -h localhost -c "CREATE USER $username WITH LOGIN PASSWORD '$password';"
    & "$psqlPath" -U postgres -h localhost -c "CREATE DATABASE $dbname OWNER $username;"
    & "$psqlPath" -U postgres -h localhost -d $dbname -c "SELECT 'Database $dbname has been created.';"

    # Enable PostGIS extensions on the new database
    Write-Host "`nEnabling PostGIS extensions on database '$dbname'..."
    $extensions = @(
        "postgis",
        "postgis_raster", 
        "postgis_topology",
        "fuzzystrmatch"
    )

    foreach ($ext in $extensions) {
        try {
            & "$psqlPath" -U postgres -h localhost -d $dbname -c "CREATE EXTENSION IF NOT EXISTS $ext;" 2>$null
            Write-Host "  Enabled extension: $ext" -ForegroundColor Green
        } catch {
            Write-Host "  Warning: Could not enable extension $ext" -ForegroundColor Yellow
        }
    }

    # Verify PostGIS installation
    Write-Host "`nVerifying PostGIS installation..."
    try {
        $postgisVersion = & "$psqlPath" -U postgres -h localhost -d $dbname -c "SELECT PostGIS_Version();" -t 2>$null
        if ($postgisVersion) {
            Write-Host "PostGIS version: $($postgisVersion.Trim())" -ForegroundColor Green
        }
    } catch {
        Write-Host "Warning: Could not verify PostGIS version" -ForegroundColor Yellow
    }

} else {
    Write-Host "`nCould not detect PostgreSQL installation or psql.exe. Initialization aborted." -ForegroundColor Red
    exit 1
}

Write-Host "`nPostgreSQL initialization completed." -ForegroundColor Cyan

# Add PostgreSQL bin directory to PATH
$pgBinPath = "C:\Program Files\PostgreSQL\17\bin"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")

try {
    if ($currentPath -notlike "*$pgBinPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pgBinPath", "Machine")
        Write-Host "PostgreSQL path added to system PATH" -ForegroundColor Green
    } else {
        Write-Host "PostgreSQL path already exists in system PATH" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error: Failed to modify system PATH: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   You may need to add '$pgBinPath' to PATH manually." -ForegroundColor Yellow
}

# Update current session PATH
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

# Verify PostgreSQL tools are accessible
Write-Host "`nVerifying PostgreSQL CLI tools..."
try {
    $psqlVersion = & "$pgBinPath\psql.exe" --version 2>$null
    $pgDumpVersion = & "$pgBinPath\pg_dump.exe" --version 2>$null
    $pgRestoreVersion = & "$pgBinPath\pg_restore.exe" --version 2>$null
    
    Write-Host "psql: $psqlVersion" -ForegroundColor Green
    Write-Host "pg_dump: $pgDumpVersion" -ForegroundColor Green
    Write-Host "pg_restore: $pgRestoreVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: PostgreSQL tools verification failed: $($_.Exception.Message)" -ForegroundColor Red
}
'@
Set-Content -Path (Join-Path $scriptsPath "Bootstrap_DB.ps1") -Value $bootstrapContent -Encoding UTF8
Write-Host "Generated: Bootstrap_DB.ps1" -ForegroundColor Green

# Generate Install_Backend_Service.ps1
$startApiContent = @'
# Setting paths
$projectRoot = Resolve-Path ".."  # Assume we are in scripts/
$venvPath = "$projectRoot\runtime\.venv"
$envFile = "$projectRoot\.env"

# Check if uv is installed
Write-Host "Checking uv package manager..." -ForegroundColor Cyan
try {
    $uvVersion = uv --version 2>$null
    if ($uvVersion) {
        Write-Host "uv is already installed: $uvVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "uv not found. Please install uv first." -ForegroundColor Red
    Write-Host "`nTo install uv, run the following command in a new PowerShell window:" -ForegroundColor Yellow
    Write-Host "winget install --id=astral-sh.uv -e" -ForegroundColor White
    Write-Host "`nAfter installation, restart PowerShell and run this script again." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Install and configure Python 3.13
Write-Host "`nConfiguring Python 3.13 via uv..." -ForegroundColor Cyan
try {
    # Check if Python 3.13 is already installed
    $pythonList = uv python list 2>$null | Select-String "3\.13"
    if ($pythonList) {
        Write-Host "Python 3.13 is already available via uv" -ForegroundColor Green
    } else {
        Write-Host "Installing Python 3.13..." -ForegroundColor Yellow
        uv python install 3.13
        Write-Host "Python 3.13 installed successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Failed to configure Python 3.13 via uv" -ForegroundColor Yellow
    Write-Host "Continuing with system Python..." -ForegroundColor Yellow
}

Write-Host "`nChecking virtual environment..." -ForegroundColor Cyan

# Check and create virtual environment
if (-Not (Test-Path "$venvPath\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment at: $venvPath" -ForegroundColor Yellow
    # Use Python 3.13 if available, otherwise use default
    try {
        uv venv $venvPath --python 3.13 --seed
        Write-Host "Virtual environment created with Python 3.13" -ForegroundColor Green
    } catch {
        Write-Host "Falling back to default Python version..." -ForegroundColor Yellow
        uv venv $venvPath --seed
    }
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
& "$venvPath\Scripts\Activate.ps1"

# Check requirements files, copy if missing
$reqFile = "$projectRoot\runtime\requirements.txt"
$reqDevFile = "$projectRoot\runtime\requirements-dev.txt"
$sourceReqFile = "$projectRoot\app\api\requirements.txt"
$sourceReqDevFile = "$projectRoot\app\api\requirements-dev.txt"

Write-Host "`nChecking requirements files..." -ForegroundColor Cyan

if (-Not (Test-Path $reqFile) -and (Test-Path $sourceReqFile)) {
    Copy-Item $sourceReqFile $reqFile
    Write-Host "requirements.txt copied to runtime" -ForegroundColor Yellow
}
if (-Not (Test-Path $reqDevFile) -and (Test-Path $sourceReqDevFile)) {
    Copy-Item $sourceReqDevFile $reqDevFile
    Write-Host "requirements-dev.txt copied to runtime" -ForegroundColor Yellow
}

# Install dependencies (if requirements.txt exists)
if (Test-Path $reqFile) {
    Write-Host "`nInstalling dependencies from requirements.txt..." -ForegroundColor Cyan
    uv pip install -r $reqFile
}
if (Test-Path $reqDevFile) {
    Write-Host "`nInstalling dev dependencies from requirements-dev.txt..." -ForegroundColor Cyan
    uv pip install -r $reqDevFile
}

# Load .env data and set DATABASE_URL environment variable
Write-Host "`nLoading .env file..." -ForegroundColor Cyan
if (Test-Path $envFile) {
    $envLines = Get-Content $envFile | Where-Object { $_ -match "=" }
    foreach ($line in $envLines) {
        $key, $value = $line -split '=', 2
        $trimmedKey = $key.Trim()
        $trimmedValue = $value.Trim().Trim("'").Trim('"')
        [Environment]::SetEnvironmentVariable($trimmedKey, $trimmedValue, [EnvironmentVariableTarget]::Process)
        Write-Host "Set $trimmedKey" -ForegroundColor Green
    }
} else {
    Write-Host ".env file not found at $envFile" -ForegroundColor Red
    exit 1
}

# Change to API directory for database operations
Set-Location "$projectRoot\app\api"

# Run database migrations with aerich
Write-Host "`nRunning database migrations..." -ForegroundColor Cyan
try {
    aerich upgrade
    Write-Host "Database migrations completed successfully" -ForegroundColor Green
} catch {
    Write-Host "Warning: Database migration failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "Continuing to start the API service..." -ForegroundColor Yellow
}

# Start uvicorn service
Write-Host "`nStarting FastAPI service..." -ForegroundColor Cyan

# Ask user if they want to run as a Windows service
$serviceChoice = Read-Host "`nDo you want to install/run this as a Windows service? (y/n) [n]"
if ($serviceChoice -eq 'y' -or $serviceChoice -eq 'Y') {
    # Install as Windows service
    $serviceName = "AERC-API"
    $serviceDisplayName = "AERC FastAPI Service"
    $serviceDescription = "AERC Dryfarm FastAPI Backend Service"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "Service '$serviceName' already exists. Stopping and removing..." -ForegroundColor Yellow
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        & sc.exe delete $serviceName
        Start-Sleep -Seconds 2
    }
    
    # Get Python executable path from virtual environment
    $uvicornModule = "$venvPath\Scripts\uvicorn.exe"
    
    # Create service command
    $workingDir = "$projectRoot\app\api"
    
    Write-Host "Installing Windows service..." -ForegroundColor Cyan
    
    # Use NSSM (Non-Sucking Service Manager) if available, otherwise use sc.exe
    $nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
    if ($nssmPath) {
        # Install service using NSSM
        & nssm install $serviceName $uvicornModule
        & nssm set $serviceName AppParameters "src.main:app --host 0.0.0.0 --port 5000"
        & nssm set $serviceName AppDirectory $workingDir
        & nssm set $serviceName DisplayName $serviceDisplayName
        & nssm set $serviceName Description $serviceDescription
        & nssm set $serviceName Start SERVICE_AUTO_START
        
        # Set stdout and stderr logging
        $logDir = "$projectRoot\runtime\logs"
        if (-not (Test-Path $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        & nssm set $serviceName AppStdout "$logDir\aerc-api-stdout.log"
        & nssm set $serviceName AppStderr "$logDir\aerc-api-stderr.log"
        & nssm set $serviceName AppRotateFiles 1
        & nssm set $serviceName AppRotateOnline 1
        & nssm set $serviceName AppRotateSeconds 86400
        & nssm set $serviceName AppRotateBytes 1048576
        
        # Set environment variables for the service
        $envString = "PATH=$env:PATH"
        foreach ($envVar in @("SECRET_KEY", "POSTGRES_USER", "POSTGRES_DB", "POSTGRES_PASSWORD", "DATABASE_URL", "FAST_API_BASE_URL", "FAST_API_TARGET", "FAST_API_VERSION")) {
            $envValue = [Environment]::GetEnvironmentVariable($envVar, [EnvironmentVariableTarget]::Process)
            if ($envValue) {
                $envString += "`n$envVar=$envValue"
            }
        }
        & nssm set $serviceName AppEnvironmentExtra $envString
        
        Write-Host "Service installed successfully using NSSM!" -ForegroundColor Green
    } else {
        Write-Host "NSSM not found. To install as a proper Windows service, please:" -ForegroundColor Yellow
        Write-Host "1. Run .\Install-NSSM.ps1 to install NSSM" -ForegroundColor White
        Write-Host "2. Restart PowerShell" -ForegroundColor White
        Write-Host "3. Run this script again" -ForegroundColor White
        Write-Host "`nAlternatively, running in foreground mode..." -ForegroundColor Yellow
        uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
        exit
    }
    
    # Start the service
    Write-Host "Starting service..." -ForegroundColor Cyan
    Start-Service -Name $serviceName
    
    # Check service status
    $serviceStatus = Get-Service -Name $serviceName
    if ($serviceStatus.Status -eq 'Running') {
        Write-Host "Service '$serviceName' is running successfully!" -ForegroundColor Green
        Write-Host "API is available at: http://localhost:5000" -ForegroundColor Cyan
        Write-Host "API documentation: http://localhost:5000/docs" -ForegroundColor Cyan
        Write-Host "`nService management commands:" -ForegroundColor Yellow
        Write-Host "  Stop service: Stop-Service -Name $serviceName" -ForegroundColor White
        Write-Host "  Start service: Start-Service -Name $serviceName" -ForegroundColor White
        Write-Host "  Remove service: nssm remove $serviceName confirm" -ForegroundColor White
    } else {
        Write-Host "Failed to start service. Status: $($serviceStatus.Status)" -ForegroundColor Red
        Write-Host "Check Windows Event Viewer for more details." -ForegroundColor Yellow
    }
} else {
    # Run in foreground mode
    Write-Host "Running in foreground mode..." -ForegroundColor Yellow
    uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
}
'@
Set-Content -Path (Join-Path $scriptsPath "Install_Backend_Service.ps1") -Value $startApiContent -Encoding UTF8
Write-Host "Generated: Install_Backend_Service.ps1" -ForegroundColor Green

# Generate Install_Frontend_Service.ps1
$startViteContent = @'
# Path configuration
$projectRoot = Resolve-Path ".."  # Assume we are in scripts/
$frontend    = "$projectRoot\app\dry-farm"
$sharedNode  = "$projectRoot\runtime\node_modules"
$linkPath    = "$frontend\node_modules"
$runtimeRoot = "$projectRoot\runtime"
$envFile     = "$projectRoot\.env"

# Load environment variables from .env file
Write-Host "Loading environment variables from .env file..."
if (Test-Path $envFile) {
    $envLines = Get-Content $envFile | Where-Object { $_ -match "=" -and $_ -notmatch "^\s*#" }
    foreach ($line in $envLines) {
        $key, $value = $line -split '=', 2
        $trimmedKey = $key.Trim()
        $trimmedValue = $value.Trim().Trim("'").Trim('"')
        [Environment]::SetEnvironmentVariable($trimmedKey, $trimmedValue, [EnvironmentVariableTarget]::Process)
        Write-Host "Set $trimmedKey" -ForegroundColor Green
    }
} else {
    Write-Host ".env file not found at $envFile" -ForegroundColor Yellow
}

# Initialize sharedNode environment if it doesn't exist
if (-not (Test-Path $sharedNode)) {
    Write-Host "Initializing sharedNode environment..."

    # Ensure runtimeRoot directory exists
    if (-not (Test-Path $runtimeRoot)) {
        New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
    }

    # Copy package.json and lock files
    Copy-Item "$frontend\package.json" "$runtimeRoot\package.json" -Force
    Copy-Item "$frontend\package-lock.json" "$runtimeRoot\package-lock.json" -Force

    # Run npm ci in runtimeRoot directory
    Push-Location $runtimeRoot
    npm ci
    Pop-Location
}

# Create junction link if it doesn't exist
if (-not (Test-Path $linkPath)) {
    try {
        New-Item -ItemType Junction -Path $linkPath -Target $sharedNode -ErrorAction Stop
        Write-Host "Junction created successfully: $linkPath"
    }
    catch {
        Write-Host "Failed to create Junction: $_"
    }
}
else {
    Write-Host "Junction already exists at $linkPath"
}

# Change to frontend directory and start Vite dev server
Write-Host "Starting Vite development server..."

# Ask user if they want to run as a Windows service
$serviceChoice = Read-Host "`nDo you want to install/run this as a Windows service? (y/n) [n]"
if ($serviceChoice -eq 'y' -or $serviceChoice -eq 'Y') {
    # Install as Windows service
    $serviceName = "AERC-Frontend"
    $serviceDisplayName = "AERC Vite Frontend Service"
    $serviceDescription = "AERC Dryfarm Vite Frontend Development Service"
    
    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "Service '$serviceName' already exists. Stopping and removing..." -ForegroundColor Yellow
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        & sc.exe delete $serviceName
        Start-Sleep -Seconds 2
    }
    
    # Get npm executable path - prefer .cmd over .ps1 for service compatibility
    $npmExe = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $npmExe) {
        $npmExe = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $npmExe) {
            Write-Host "Error: npm not found. Please ensure Node.js is installed and in PATH." -ForegroundColor Red
            exit 1
        }
        # If we got npm.ps1, try to find npm.cmd in the same directory
        if ($npmExe.Source -like "*.ps1") {
            $npmDir = Split-Path $npmExe.Source -Parent
            $npmCmd = Join-Path $npmDir "npm.cmd"
            if (Test-Path $npmCmd) {
                $npmExe = Get-Command $npmCmd
                Write-Host "Using npm.cmd instead of npm.ps1 for service compatibility" -ForegroundColor Yellow
            } else {
                Write-Host "Warning: Only npm.ps1 found, this may cause service startup issues" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host "Installing Windows service..." -ForegroundColor Cyan
    
    # Use NSSM (Non-Sucking Service Manager) if available
    $nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
    if ($nssmPath) {
        # Install service using NSSM
        & nssm install $serviceName $npmExe.Source
        & nssm set $serviceName AppParameters "run dev"
        & nssm set $serviceName AppDirectory $frontend
        & nssm set $serviceName DisplayName $serviceDisplayName
        & nssm set $serviceName Description $serviceDescription
        & nssm set $serviceName Start SERVICE_AUTO_START
        
        # Set stdout and stderr logging
        $logDir = "$projectRoot\runtime\logs"
        if (-not (Test-Path $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        & nssm set $serviceName AppStdout "$logDir\aerc-frontend-stdout.log"
        & nssm set $serviceName AppStderr "$logDir\aerc-frontend-stderr.log"
        & nssm set $serviceName AppRotateFiles 1
        & nssm set $serviceName AppRotateOnline 1
        & nssm set $serviceName AppRotateSeconds 86400
        & nssm set $serviceName AppRotateBytes 1048576
        
        # Set environment variables for the service
        $envString = "PATH=$env:PATH"
        foreach ($envVar in @("FAST_API_BASE_URL", "FAST_API_TARGET", "FAST_API_VERSION")) {
            $envValue = [Environment]::GetEnvironmentVariable($envVar, [EnvironmentVariableTarget]::Process)
            if ($envValue) {
                $envString += "`n$envVar=$envValue"
            }
        }
        & nssm set $serviceName AppEnvironmentExtra $envString
        
        Write-Host "Service installed successfully using NSSM!" -ForegroundColor Green
    } else {
        Write-Host "NSSM not found. To install as a proper Windows service, please:" -ForegroundColor Yellow
        Write-Host "1. Run .\Install-NSSM.ps1 to install NSSM" -ForegroundColor White
        Write-Host "2. Restart PowerShell" -ForegroundColor White
        Write-Host "3. Run this script again" -ForegroundColor White
        Write-Host "`nAlternatively, running in foreground mode..." -ForegroundColor Yellow
        Push-Location $frontend
        try {
            npm run dev
        } finally {
            Pop-Location
        }
        exit
    }
    
    # Start the service
    Write-Host "Starting service..." -ForegroundColor Cyan
    Start-Service -Name $serviceName
    
    # Check service status
    $serviceStatus = Get-Service -Name $serviceName
    if ($serviceStatus.Status -eq 'Running') {
        Write-Host "Service '$serviceName' is running successfully!" -ForegroundColor Green
        Write-Host "Frontend is available at: http://localhost:3000" -ForegroundColor Cyan
        Write-Host "(Vite default port - check actual port in service logs if different)" -ForegroundColor Gray
        Write-Host "`nService management commands:" -ForegroundColor Yellow
        Write-Host "  Stop service: Stop-Service -Name $serviceName" -ForegroundColor White
        Write-Host "  Start service: Start-Service -Name $serviceName" -ForegroundColor White
        Write-Host "  Remove service: nssm remove $serviceName confirm" -ForegroundColor White
    } else {
        Write-Host "Error: Failed to start service. Status: $($serviceStatus.Status)" -ForegroundColor Red
        Write-Host "Check Windows Event Viewer for more details." -ForegroundColor Yellow
        Write-Host "`nFor troubleshooting, run:" -ForegroundColor Yellow
        Write-Host ".\Debug-Services.ps1 -Service frontend" -ForegroundColor White
    }
} else {
    # Run in foreground mode
    Write-Host "Running in foreground mode..." -ForegroundColor Yellow
    Push-Location $frontend
    try {
        npm run dev
    } finally {
        Pop-Location
    }
}
'@
Set-Content -Path (Join-Path $scriptsPath "Install_Frontend_Service.ps1") -Value $startViteContent -Encoding UTF8
Write-Host "Generated: Install_Frontend_Service.ps1" -ForegroundColor Green

# Generate Manage_Services.ps1
$manageServicesContent = @'
# AERC Service Management Script
# This script helps manage AERC Windows services

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "install", "remove", "logs", "checkout", "sync", "deploy")]
    [string]$Action,
    
    [ValidateSet("api", "frontend", "all")]
    [string]$Service = "all",
    
    [string]$SvnUrl = "",
    
    [string]$CheckoutPath = "temp\checkout",
    
    [string]$TargetPath = "app"
)

# Check if running as administrator
function Test-IsAdmin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Show administrator privileges required message
function Show-AdminRequiredMessage {
    param([string]$Action)
    
    Write-Host "`n  Administrator Privileges Required" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "The '$Action' operation requires administrator privileges." -ForegroundColor Yellow
    Write-Host "`nTo run this command with administrator privileges:" -ForegroundColor Cyan
    Write-Host "1. Right-click on PowerShell and select 'Run as Administrator'" -ForegroundColor White
    Write-Host "2. Navigate to the scripts directory:" -ForegroundColor White
    Write-Host "   cd c:\AERC\AERC-Deploy\scripts" -ForegroundColor Gray
    Write-Host "3. Re-run the command:" -ForegroundColor White
    
    # Rebuild current command
    $currentCommand = ".\Manage_Services.ps1 -Action '$Action'"
    if ($Service -ne "all") { $currentCommand += " -Service '$Service'" }
    if ($SvnUrl) { $currentCommand += " -SvnUrl '$SvnUrl'" }
    if ($CheckoutPath -ne "temp\checkout") { $currentCommand += " -CheckoutPath '$CheckoutPath'" }
    if ($TargetPath -ne "app") { $currentCommand += " -TargetPath '$TargetPath'" }
    
    Write-Host "   $currentCommand" -ForegroundColor Gray
    Write-Host "`nAlternatively, you can start an elevated PowerShell with:" -ForegroundColor Cyan
    Write-Host "   Start-Process powershell -Verb RunAs" -ForegroundColor Gray
    Write-Host "`n" -ForegroundColor White
}

# Check if operation requires administrator privileges
$adminRequiredActions = @("start", "stop", "restart", "remove", "deploy")
if ($Action -in $adminRequiredActions) {
    if (-not (Test-IsAdmin)) {
        Show-AdminRequiredMessage -Action $Action
        exit 1
    }
    Write-Host "Running with Administrator privileges [OK]" -ForegroundColor Green
}

$apiServiceName = "AERC-API"
$frontendServiceName = "AERC-Frontend"

function Show-ServiceStatus {
    param([string]$ServiceName)
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction Stop
        $status = $service.Status
        $color = switch ($status) {
            'Running' { 'Green' }
            'Stopped' { 'Red' }
            'Paused' { 'Yellow' }
            'StartPending' { 'Cyan' }
            'StopPending' { 'Magenta' }
            default { 'Yellow' }
        }
        Write-Host "$ServiceName`: $status" -ForegroundColor $color
    }
    catch [System.ServiceProcess.ServiceController] {
        Write-Host "$ServiceName`: Not found" -ForegroundColor Gray
    }
    catch {
        if (-not (Test-IsAdmin)) {
            Write-Host "$ServiceName`: Access Denied (Administrator required)" -ForegroundColor Red
        } else {
            Write-Host "$ServiceName`: Error - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Start-AercService {
    param([string]$ServiceName)
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction Stop
        if ($service.Status -eq 'Running') {
            Write-Host "$ServiceName is already running." -ForegroundColor Yellow
            return $true
        }
        
        Write-Host "Starting $ServiceName..." -ForegroundColor Cyan
        Start-Service -Name $ServiceName -ErrorAction Stop
        
        # Wait for service to start
        $timeout = 30
        $elapsed = 0
        do {
            Start-Sleep -Seconds 1
            $elapsed++
            $service.Refresh()
        } while ($service.Status -ne 'Running' -and $elapsed -lt $timeout)
        
        if ($service.Status -eq 'Running') {
            Write-Host "$ServiceName started successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$ServiceName failed to start within $timeout seconds." -ForegroundColor Red
            return $false
        }
    }
    catch [System.ServiceProcess.ServiceController] {
        Write-Host "$ServiceName is not installed." -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "Failed to start $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Stop-AercService {
    param([string]$ServiceName)
    
    try {
        $service = Get-Service -Name $ServiceName -ErrorAction Stop
        if ($service.Status -eq 'Stopped') {
            Write-Host "$ServiceName is already stopped." -ForegroundColor Yellow
            return $true
        }
        
        Write-Host "Stopping $ServiceName..." -ForegroundColor Cyan
        Stop-Service -Name $ServiceName -Force -ErrorAction Stop
        
        # Wait for service to stop
        $timeout = 30
        $elapsed = 0
        do {
            Start-Sleep -Seconds 1
            $elapsed++
            $service.Refresh()
        } while ($service.Status -ne 'Stopped' -and $elapsed -lt $timeout)
        
        if ($service.Status -eq 'Stopped') {
            Write-Host "$ServiceName stopped successfully!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "$ServiceName failed to stop within $timeout seconds." -ForegroundColor Red
            return $false
        }
    }
    catch [System.ServiceProcess.ServiceController] {
        Write-Host "$ServiceName is not installed." -ForegroundColor Red
        return $false
    }
    catch {
        Write-Host "Failed to stop $ServiceName`: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Restart-AercService {
    param([string]$ServiceName)
    
    Stop-AercService $ServiceName
    Start-Sleep -Seconds 2
    Start-AercService $ServiceName
}

function Remove-AercService {
    param([string]$ServiceName)
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Removing $ServiceName..." -ForegroundColor Cyan
        Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
        
        # Check if NSSM is available
        $nssmPath = Get-Command nssm -ErrorAction SilentlyContinue
        if ($nssmPath) {
            & nssm remove $ServiceName confirm
        } else {
            & sc.exe delete $ServiceName
        }
        Write-Host "$ServiceName removed successfully!" -ForegroundColor Green
    } else {
        Write-Host "$ServiceName is not installed." -ForegroundColor Yellow
    }
}

function Show-ServiceLogs {
    param([string]$ServiceName)
    
    Write-Host "Checking Windows Event Log for $ServiceName..." -ForegroundColor Cyan
    
    # Check Application log for service events
    $events = Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='NSSM'} -MaxEvents 10 -ErrorAction SilentlyContinue |
              Where-Object { $_.Message -like "*$ServiceName*" }
    
    if ($events) {
        $events | ForEach-Object {
            $color = switch ($_.LevelDisplayName) {
                'Error' { 'Red' }
                'Warning' { 'Yellow' }
                'Information' { 'Green' }
                default { 'White' }
            }
            Write-Host "[$($_.TimeCreated)] $($_.LevelDisplayName): $($_.Message)" -ForegroundColor $color
        }
    } else {
        Write-Host "No recent log entries found for $ServiceName" -ForegroundColor Gray
    }
}

function Invoke-SvnCheckout {
    param(
        [string]$SvnUrl,
        [string]$CheckoutPath
    )
    
    # Check if SVN is available
    $svnCommand = Get-Command svn -ErrorAction SilentlyContinue
    if (-not $svnCommand) {
        Write-Host "ERROR: SVN command not found. Please install SVN client." -ForegroundColor Red
        return $false
    }
    
    if ([string]::IsNullOrEmpty($SvnUrl)) {
        Write-Host "ERROR: SVN URL is required for checkout." -ForegroundColor Red
        Write-Host "Usage: .\Manage_Services.ps1 -Action checkout -SvnUrl 'https://your-svn-repo/trunk'" -ForegroundColor Yellow
        return $false
    }
    
    # Ensure checkout path is absolute path
    if (-not [System.IO.Path]::IsPathRooted($CheckoutPath)) {
        # If relative path, should be relative to AERC-Deploy root directory, not scripts directory
        $scriptDir = Split-Path $PSScriptRoot -Parent
        $CheckoutPath = Join-Path $scriptDir $CheckoutPath
    }
    
    Write-Host "SVN Checkout Operation" -ForegroundColor Cyan
    Write-Host "=====================" -ForegroundColor Cyan
    Write-Host "Repository: $SvnUrl" -ForegroundColor White
    Write-Host "Target Path: $CheckoutPath" -ForegroundColor White
    
    # If target directory exists, ask for overwrite confirmation
    if (Test-Path $CheckoutPath) {
        $overwrite = Read-Host "Target directory exists. Overwrite? (y/N)"
        if ($overwrite -eq 'y' -or $overwrite -eq 'Y') {
            Write-Host "Removing existing directory..." -ForegroundColor Yellow
            Remove-Item $CheckoutPath -Recurse -Force
        } else {
            Write-Host "Operation cancelled." -ForegroundColor Yellow
            return $false
        }
    }
    
    # Create parent directory
    $parentDir = Split-Path $CheckoutPath -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
    
    try {
        Write-Host "Executing SVN checkout..." -ForegroundColor Cyan
        Write-Host "Note: If prompted for credentials, please enter your SVN username and password." -ForegroundColor Yellow
        
        # Use --non-interactive and --trust-server-cert to avoid interactive prompts
        $svnArgs = @(
            "checkout",
            $SvnUrl,
            $CheckoutPath,
            "--non-interactive",
            "--trust-server-cert"
        )
        
        # Execute SVN command and capture output
        $process = Start-Process -FilePath "svn" -ArgumentList $svnArgs -NoNewWindow -Wait -PassThru -RedirectStandardOutput "svn_output.log" -RedirectStandardError "svn_error.log"
        
        if ($process.ExitCode -eq 0) {
            Write-Host "SVN checkout completed successfully!" -ForegroundColor Green
            Write-Host "Files checked out to: $CheckoutPath" -ForegroundColor Green
            
            # Show checkout content summary
            if (Test-Path $CheckoutPath) {
                $itemCount = (Get-ChildItem $CheckoutPath -Recurse).Count
                Write-Host "Total items checked out: $itemCount" -ForegroundColor Cyan
            }
            
            return $true
        } else {
            Write-Host "SVN checkout failed with exit code: $($process.ExitCode)" -ForegroundColor Red
            
            # Read and display error information
            if (Test-Path "svn_error.log") {
                $errorContent = Get-Content "svn_error.log" -Raw
                if ($errorContent) {
                    Write-Host "Error details:" -ForegroundColor Red
                    Write-Host $errorContent -ForegroundColor Red
                }
                Remove-Item "svn_error.log" -ErrorAction SilentlyContinue
            }
            
            return $false
        }
    }
    catch {
        Write-Host "SVN checkout failed with exception: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    finally {
        # Clean up temporary log files
        Remove-Item "svn_output.log" -ErrorAction SilentlyContinue
        Remove-Item "svn_error.log" -ErrorAction SilentlyContinue
    }
}

function Sync-ProjectFiles {
    param(
        [string]$SourcePath,
        [string]$TargetPath
    )
    
    # Ensure paths are absolute paths
    if (-not [System.IO.Path]::IsPathRooted($SourcePath)) {
        $scriptDir = Split-Path $PSScriptRoot -Parent
        $SourcePath = Join-Path $scriptDir $SourcePath
    }
    if (-not [System.IO.Path]::IsPathRooted($TargetPath)) {
        $scriptDir = Split-Path $PSScriptRoot -Parent
        $TargetPath = Join-Path $scriptDir $TargetPath
    }
    
    Write-Host "Project Files Synchronization" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "Source: $SourcePath" -ForegroundColor White
    Write-Host "Target: $TargetPath" -ForegroundColor White
    
    # Check if source directory exists
    if (-not (Test-Path $SourcePath)) {
        Write-Host "ERROR: Source directory does not exist: $SourcePath" -ForegroundColor Red
        return $false
    }
    
    # Confirm whether to proceed with synchronization
    $confirm = Read-Host "This will overwrite files in the target directory. Continue? (y/N)"
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
        return $false
    }
    
    try {
        # Create target directory (if not exists)
        if (-not (Test-Path $TargetPath)) {
            Write-Host "Creating target directory..." -ForegroundColor Yellow
            New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
        }
        
        # Define items to synchronize
        $itemsToSync = @(
            @{ Source = "api"; Description = "Backend API code" },
            @{ Source = "dry-farm"; Description = "Frontend code" },
            @{ Source = "db"; Description = "Database scripts" },
            @{ Source = "version-snapshots"; Description = "Version snapshots" }
        )
        
        foreach ($item in $itemsToSync) {
            $srcPath = Join-Path $SourcePath $item.Source
            $dstPath = Join-Path $TargetPath $item.Source
            
            if (Test-Path $srcPath) {
                Write-Host "Syncing $($item.Description) ($($item.Source))..." -ForegroundColor Cyan
                
                # If target exists, delete first
                if (Test-Path $dstPath) {
                    Remove-Item $dstPath -Recurse -Force
                }
                
                # Copy entire directory
                Copy-Item $srcPath $dstPath -Recurse -Force
                Write-Host "  [OK] $($item.Source) synced successfully" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] $($item.Source) not found in source, skipping" -ForegroundColor Yellow
            }
        }
        
        # Sync important files in root directory
        $rootFiles = @("README-WINDOWS.md", ".env")
        foreach ($file in $rootFiles) {
            $srcFile = Join-Path $SourcePath $file
            $dstFile = Join-Path $TargetPath $file
            
            if (Test-Path $srcFile) {
                Write-Host "Syncing $file..." -ForegroundColor Cyan
                Copy-Item $srcFile $dstFile -Force
                Write-Host "  [OK] $file synced successfully" -ForegroundColor Green
            }
        }
        
        # Re-establish node_modules junction (if needed)
        Write-Host "`nRestoring node_modules junction..." -ForegroundColor Cyan
        $frontendPath = Join-Path $TargetPath "dry-farm"
        $nodeModulesJunction = Join-Path $frontendPath "node_modules"
        $scriptDir = Split-Path $PSScriptRoot -Parent
        $runtimeNodeModules = Join-Path $scriptDir "runtime\node_modules"
        
        # Check if runtime/node_modules exists
        if (Test-Path $runtimeNodeModules) {
            # If junction doesn't exist, re-establish it
            if (-not (Test-Path $nodeModulesJunction)) {
                try {
                    Write-Host "Creating node_modules junction: $nodeModulesJunction -> $runtimeNodeModules" -ForegroundColor Yellow
                    New-Item -ItemType Junction -Path $nodeModulesJunction -Target $runtimeNodeModules -Force | Out-Null
                    Write-Host "  [OK] node_modules junction created successfully" -ForegroundColor Green
                }
                catch {
                    Write-Host "  [WARNING] Failed to create node_modules junction: $($_.Exception.Message)" -ForegroundColor Red
                    Write-Host "  You may need to run 'npm install' in the dry-farm directory" -ForegroundColor Yellow
                }
            } else {
                Write-Host "  [OK] node_modules junction already exists" -ForegroundColor Green
            }
        } else {
            Write-Host "  [WARNING] runtime/node_modules not found, skipping junction creation" -ForegroundColor Yellow
            Write-Host "  Please run the frontend installation script first" -ForegroundColor Yellow
        }
        
    Write-Host "`nSynchronization completed successfully!" -ForegroundColor Green
    return $true
    }
    catch {
        Write-Host "Synchronization failed with exception: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Invoke-FullDeploy {
    param(
        [string]$SvnUrl,
        [string]$CheckoutPath,
        [string]$TargetPath
    )
    
    Write-Host "Full Deployment Process" -ForegroundColor Magenta
    Write-Host "=======================" -ForegroundColor Magenta
    
    # Step 1: Stop services
    Write-Host "`nStep 1: Stopping services..." -ForegroundColor Cyan
    Stop-AercService $apiServiceName
    Stop-AercService $frontendServiceName
    
    # Step 2: SVN Checkout
    Write-Host "`nStep 2: SVN Checkout..." -ForegroundColor Cyan
    $checkoutSuccess = Invoke-SvnCheckout -SvnUrl $SvnUrl -CheckoutPath $CheckoutPath
    if (-not $checkoutSuccess) {
        Write-Host "Deployment failed at SVN checkout step." -ForegroundColor Red
        return $false
    }
    
    # Step 3: Sync Files
    Write-Host "`nStep 3: Synchronizing files..." -ForegroundColor Cyan
    $syncSuccess = Sync-ProjectFiles -SourcePath $CheckoutPath -TargetPath $TargetPath
    if (-not $syncSuccess) {
        Write-Host "Deployment failed at file synchronization step." -ForegroundColor Red
        return $false
    }
    
    # Step 4: Restart services
    Write-Host "`nStep 4: Restarting services..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    Start-AercService $apiServiceName
    Start-AercService $frontendServiceName
    
    Write-Host "`nDeployment completed successfully! 🎉" -ForegroundColor Green
    Write-Host "Please verify the services are running correctly." -ForegroundColor Yellow
    
    return $true
}

# Determine which services to operate on
$services = switch ($Service) {
    "api" { @($apiServiceName) }
    "frontend" { @($frontendServiceName) }
    "all" { @($apiServiceName, $frontendServiceName) }
}

# Execute the requested action
switch ($Action) {
    "status" {
        Write-Host "`nAERC Services Status:" -ForegroundColor Cyan
        Write-Host "===================" -ForegroundColor Cyan
        foreach ($svc in $services) {
            Show-ServiceStatus $svc
        }
    }
    
    "start" {
        foreach ($svc in $services) {
            Start-AercService $svc
        }
    }
    
    "stop" {
        foreach ($svc in $services) {
            Stop-AercService $svc
        }
    }
    
    "restart" {
        foreach ($svc in $services) {
            Restart-AercService $svc
        }
    }
    
    "remove" {
        $confirmation = Read-Host "Are you sure you want to remove the service(s)? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            foreach ($svc in $services) {
                Remove-AercService $svc
            }
        } else {
            Write-Host "Operation cancelled." -ForegroundColor Yellow
        }
    }
    
    "install" {
        Write-Host "To install services, please run:" -ForegroundColor Cyan
        Write-Host "  .\Install_Backend_Service.ps1 (and choose 'y' for service installation)" -ForegroundColor White
        Write-Host "  .\Install_Frontend_Service.ps1 (and choose 'y' for service installation)" -ForegroundColor White
    }
    
    "logs" {
        foreach ($svc in $services) {
            Write-Host "`nLogs for $svc" -ForegroundColor Cyan
            Write-Host "===============" -ForegroundColor Cyan
            Show-ServiceLogs $svc
        }
    }
    
    "checkout" {
        $success = Invoke-SvnCheckout -SvnUrl $SvnUrl -CheckoutPath $CheckoutPath
        if ($success) {
            Write-Host "`nNext steps:" -ForegroundColor Yellow
            Write-Host "  1. Review the checked out files in: $CheckoutPath" -ForegroundColor White
            Write-Host "  2. Run sync command: .\Manage_Services.ps1 -Action sync" -ForegroundColor White
        }
    }
    
    "sync" {
        $success = Sync-ProjectFiles -SourcePath $CheckoutPath -TargetPath $TargetPath
        if ($success) {
            Write-Host "`nNext steps:" -ForegroundColor Yellow
            Write-Host "  1. Restart services: .\Manage_Services.ps1 -Action restart" -ForegroundColor White
            Write-Host "  2. Check service status: .\Manage_Services.ps1 -Action status" -ForegroundColor White
        }
    }
    
    "deploy" {
        if ([string]::IsNullOrEmpty($SvnUrl)) {
            Write-Host "ERROR: SVN URL is required for deployment." -ForegroundColor Red
            Write-Host "Usage: .\Manage_Services.ps1 -Action deploy -SvnUrl 'https://your-svn-repo/trunk'" -ForegroundColor Yellow
        } else {
            Invoke-FullDeploy -SvnUrl $SvnUrl -CheckoutPath $CheckoutPath -TargetPath $TargetPath
        }
    }
}

Write-Host "`nUsage examples:" -ForegroundColor Yellow
Write-Host "Service Management:" -ForegroundColor Cyan
Write-Host "  .\Manage_Services.ps1 -Action status" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action start -Service api" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action restart -Service all" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action logs -Service frontend" -ForegroundColor White

Write-Host "`nDeployment Operations:" -ForegroundColor Cyan
Write-Host "  .\Manage_Services.ps1 -Action checkout -SvnUrl 'https://your-svn-repo/trunk'" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action sync" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action deploy -SvnUrl 'https://your-svn-repo/trunk'" -ForegroundColor White

Write-Host "`nCustom Paths:" -ForegroundColor Cyan
Write-Host "  .\Manage_Services.ps1 -Action checkout -SvnUrl 'https://repo/trunk' -CheckoutPath 'custom\path'" -ForegroundColor White
Write-Host "  .\Manage_Services.ps1 -Action sync -CheckoutPath 'custom\path' -TargetPath 'production'" -ForegroundColor White

Write-Host "`nNote:" -ForegroundColor Yellow
Write-Host "  - Service operations (start/stop/restart/remove/deploy) require Administrator privileges" -ForegroundColor Gray
Write-Host "  - Please run PowerShell as Administrator for service management operations" -ForegroundColor Gray
Write-Host "  - Status, logs, checkout, and sync can run without elevation" -ForegroundColor Gray
'@
Set-Content -Path (Join-Path $scriptsPath "Manage_Services.ps1") -Value $manageServicesContent -Encoding UTF8
Write-Host "Generated: Manage_Services.ps1" -ForegroundColor Green

Write-Host "`nAll deployment scripts generated successfully!" -ForegroundColor Green

# Step 6: Show next steps
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Checkout project from SVN:" -ForegroundColor White
Write-Host "   svn checkout https://IRR/svn/Project-IRR/trunk $deployRoot\AERC-Deploy\temp\checkout" -ForegroundColor Gray
Write-Host "2. Copy updated files from checkout to app directory using Robocopy:" -ForegroundColor White
Write-Host "   robocopy `"$deployRoot\AERC-Deploy\temp\checkout`" `"$deployRoot\AERC-Deploy\app`" /MIR /LOG:`"$deployRoot\AERC-Deploy\deploy_$(Get-Date -Format 'yyyyMMdd_HHmmss').log`" /V" -ForegroundColor Gray
Write-Host "   (This will mirror the checkout directory to app, excluding .svn folders and temporary files)" -ForegroundColor DarkGray
Write-Host "3. Copy your data files to the AERC-Data directory" -ForegroundColor White
Write-Host "4. Configure your .env file based on the template" -ForegroundColor White
Write-Host "5. Run the deployment scripts from the AERC-Deploy\scripts directory:" -ForegroundColor White
Write-Host "   .\Bootstrap_DB.ps1     # Initialize PostgreSQL database" -ForegroundColor Gray
Write-Host "   .\Install_Backend_Service.ps1        # Start API service" -ForegroundColor Gray
Write-Host "   .\Install_Frontend_Service.ps1       # Start frontend service" -ForegroundColor Gray
Write-Host "   .\Manage_Services.ps1  # Manage services" -ForegroundColor Gray
