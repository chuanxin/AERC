# AERC Dryfarm System - Windows Deployment Guide

This guide provides step-by-step instructions for deploying the AERC Dryfarm system on Windows environments.

## Prerequisites

- Windows 10/11 with administrator privileges
- Internet connection for downloading packages
- PowerShell 5.1 or later

## Installation Steps

### 1. Install PowerShell Package Management

Install the winget-install script to ensure proper package management:

```powershell
Install-Script -Name winget-install
```

### 2. Install Windows Terminal

Install modern Windows Terminal for better command-line experience:

```powershell
winget install --id Microsoft.WindowsTerminal -e
```

**Note**: After installation, restart your terminal or use Windows Terminal for remaining steps.

### 3. Install PostgreSQL 17

Install PostgreSQL database server:

```powershell
winget install --id PostgreSQL.PostgreSQL.17 -e
```

**Post-installation**:
- **Default credentials**: Username `postgres` / Password `postgres`
- PostgreSQL service should start automatically
- The database server will be accessible on `localhost:5432`

**Note**: When using winget to install PostgreSQL, the default superuser account is automatically created with:
- Username: `postgres`
- Password: `postgres`

You can change this password later using:
```powershell
psql -U postgres -c "ALTER USER postgres PASSWORD 'your_new_password';"
```

### 4. Install PostGIS Extension

1. Open **Start Menu** → **PostgreSQL 17** → **Application Stack Builder**
2. Select your PostgreSQL installation
3. Navigate to **Spatial Extensions**
4. Select **PostGIS** (latest version)
5. Follow the installation wizard
6. Complete the PostGIS installation

### 5. Install UV Package Manager

Install UV for fast Python package management:

```powershell
winget install --id astral-sh.uv -e
```

**Important**: Restart PowerShell/Terminal after installation to refresh PATH.

### 6. Install Python 3.13

Use UV to install Python 3.13:

```powershell
uv python install 3.13
```

### 7. Update Shell Configuration

Update shell to recognize UV Python installations:

```powershell
uv python update-shell
```

**Important**: Restart PowerShell/Terminal after this step.

### 8. Install Node Version Manager

Install NVM for Windows to manage Node.js versions:

```powershell
winget install --id CoreyButler.NVMforWindows -e
```

**Important**: Restart PowerShell/Terminal after installation.

### 9. Install Node.js LTS

Install the latest LTS version of Node.js:

```powershell
nvm install lts
```

### 10. Use Node.js LTS

Set the installed LTS version as active:

```powershell
# Check installed versions
nvm list

# Use the LTS version (replace X.X.X with actual version number)
nvm use X.X.X
```

Example:
```powershell
nvm use 20.11.0
```

### 10.1. Install NSSM Service Manager

Install NSSM (Non-Sucking Service Manager) for Windows service management:

```powershell
winget install --id NSSM.NSSM -e
```

**What NSSM provides**:
- Converts console applications into Windows services
- Enables persistent running of API and frontend services
- Automatic service restart on system reboot
- Service management and monitoring capabilities

**Note**: Restart PowerShell after installation for PATH updates to take effect.

## AERC System Deployment

### 11. Initialize AERC Deployment

Navigate to the AERC deployment directory and run the initialization script:

```powershell
# Navigate to your AERC project directory
cd "C:\path\to\your\AERC\deploy\AERC-Deploy"

# Run initialization script
.\scripts\Init-AERC-Deployment.ps1
```

**What this script does**:
- Creates necessary directory structure
- Generates `.env` configuration file with interactive prompts
- Sets up project environment variables

**Required Information**:
- Database name (for your AERC application)
- Database username (for your AERC application)
- Database password (for your AERC application)
- API configuration settings

**Note**: These are separate from the PostgreSQL superuser account (`postgres/postgres`). The initialization script will help you create application-specific database credentials.

### 12. Bootstrap Database

Run the database setup script **as Administrator**:

```powershell
# Right-click PowerShell → Run as Administrator
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Bootstrap_DB.ps1
```

**What this script does**:
- Configures PostgreSQL CLI tools in system PATH
- Uses PostgreSQL superuser (`postgres`) to create application database and user
- Creates database user and database as specified in `.env` file
- Enables PostGIS extensions
- Verifies database setup

### 13. Start API Service

Launch the FastAPI backend service:

```powershell
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Start_API.ps1
```

**Interactive Options**:
- Choose `n` (default): Run in foreground mode, suitable for development and testing
- Choose `y`: Install as Windows service, suitable for production environments

**What this script does**:
- Verifies UV and Python 3.13 installation
- Creates and activates Python virtual environment
- Installs Python dependencies
- Runs database migrations
- Starts FastAPI server on `http://localhost:5000`
- **Optional**: Install as Windows service for persistent running

### 14. Start Frontend Development Server

In a **new terminal window**, launch the Vite development server:

```powershell
cd "C:\path\to\your\AERC\deploy\AERC-Deploy\scripts"

.\Start_Vite.ps1
```

**Interactive Options**:
- Choose `n` (default): Run in foreground mode, suitable for development and testing
- Choose `y`: Install as Windows service, suitable for production environments

**What this script does**:
- Loads environment variables
- Sets up shared Node.js modules
- Creates junction links for efficient development
- Starts Vite dev server on `http://localhost:3000`
- **Optional**: Install as Windows service for persistent running

### 15. Service Management (Optional)

If you chose to install as Windows services, use the service management scripts:

```powershell
# Check all service status
.\Manage-Services.ps1 -Action status

# Start all services
.\Manage-Services.ps1 -Action start

# Stop all services
.\Manage-Services.ps1 -Action stop

# Restart all services
.\Manage-Services.ps1 -Action restart

# Manage specific services only
.\Manage-Services.ps1 -Action start -Service api
.\Manage-Services.ps1 -Action restart -Service frontend

# Remove services
.\Manage-Services.ps1 -Action remove
```

**Service Management Features**:
- Unified management of API and frontend services
- Check service running status
- Start, stop, restart services
- Remove unwanted services

## Verification

After completing all steps, you should have:

1. **Database**: PostgreSQL 17 with PostGIS extensions running
2. **API Service**: FastAPI running on `http://localhost:5000`
3. **Frontend**: Vite development server running on `http://localhost:3000`

### Quick Health Check

1. **Database Connection**:
   ```powershell
   # Test PostgreSQL superuser connection
   psql -U postgres -h localhost
   
   # Test application database connection
   psql -U [your_db_user] -d [your_db_name] -h localhost
   ```

2. **API Health**:
   Open browser: `http://localhost:5000/docs`

3. **Frontend Access**:
   Open browser: `http://localhost:3000`

## Troubleshooting

### Common Issues

1. **PowerShell Execution Policy**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **PATH not updated after installations**:
   - Restart PowerShell/Terminal
   - Or restart computer if issues persist

3. **Database connection errors**:
   - Verify PostgreSQL service is running
   - Check database credentials in `.env` file (for application database)
   - Ensure PostGIS extensions are properly installed
   - Default PostgreSQL superuser is `postgres/postgres`
   - Test connection: `psql -U postgres -h localhost`

4. **UV or Python not found**:
   - Restart terminal after UV installation
   - Verify installation: `uv --version`
   - Manually add to PATH if needed

5. **Node.js/NPM issues**:
   - Verify NVM installation: `nvm version`
   - List available versions: `nvm list`
   - Switch to correct version: `nvm use [version]`

### Service Troubleshooting

1. **Service permission issues**
   - Ensure PowerShell is running as Administrator
   - Check service account has appropriate permissions

2. **Environment variable issues**
   - Service environment variables differ from interactive mode
   - Check environment variable configuration in service settings

3. **Port occupation issues**
   ```powershell
   # Check processes using the ports
   netstat -ano | findstr :5000
   netstat -ano | findstr :5173
   
   # Kill the process using the port (replace PID)
   taskkill /F /PID <PID>
   ```

### Getting Help

1. Check script output for specific error messages
2. Verify all prerequisites are properly installed
3. Ensure you're running PowerShell as Administrator when required
4. Review the `.env` file for correct configuration

## Directory Structure

After successful deployment, your directory structure should look like:

```
AERC-Deploy/
├── .env                          # Environment configuration
├── app/
│   ├── api/                      # FastAPI backend
│   └── dry-farm/                 # Frontend application
├── runtime/
│   ├── .venv/                    # Python virtual environment
│   └── node_modules/             # Shared Node.js modules
└── scripts/
    ├── Init-AERC-Deployment.ps1  # Initialization script
    ├── Bootstrap_DB.ps1          # Database setup
    ├── Start_API.ps1             # API server launcher
    └── Start_Vite.ps1            # Frontend dev server launcher
```

## Security Notes

- Store database passwords securely
- Review `.env` file contents before committing to version control
- Run database scripts with appropriate privileges only
- Keep your system and dependencies updated

---

**Last Updated**: August 2025  
**AERC Version**: Windows Deployment Branch  
**Document Version**: 1.1 English Edition
