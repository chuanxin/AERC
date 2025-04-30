#!/bin/zsh

# AERC Project Management Script
# Usage: ./aerc-manager.sh [command] [params]

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
SCRIPT_NAME=$(basename "${(%):-%N}")

# Check if Docker and Docker Compose are installed
check_prerequisites() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Warning: docker-compose command not found, trying docker compose...${NC}"
        if ! docker compose version &> /dev/null; then
            echo -e "${RED}Error: Docker Compose is not installed. Please install Docker Compose first.${NC}"
            exit 1
        fi
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
}

# Check directory structure
check_directory_structure() {
    # Ensure backup directory exists
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${BLUE}Creating backup directory...${NC}"
        mkdir -p "$BACKUP_DIR"
    fi
}

# Check if Docker Compose file exists
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}Error: $COMPOSE_FILE does not exist. Please make sure the script is run in the correct directory.${NC}"
        exit 1
    fi
}

# Setup AERC environment
setup_environment() {
    echo -e "${PURPLE}===== Setting up AERC Environment =====${NC}"
    
    # Check if .env file exists or api/migrations/models directory is empty
    FIRST_RUN=false
    if [ ! -f $ENV_FILE ] || [ ! -d "api/migrations/models" ] || [ -z "$(ls -A api/migrations/models 2>/dev/null)" ]; then
        FIRST_RUN=true
    fi

    # Check if certbot directory exists for SSL certificates
    CERTBOT_EXISTS=false
    if [ -d "dry-farm/certbot" ] && [ ! -z "$(ls -A dry-farm/certbot 2>/dev/null)" ]; then
        CERTBOT_EXISTS=true
    fi

    # Generate new secret key
    NEW_SECRET_KEY=$(openssl rand -hex 32)

    # Set database url
    DATABASE_URL="postgres://hello_fastapi:hello_fastapi@db:5432/hello_fastapi_dev"

    # Set postgres user, password, database
    POSTGRES_USER="hello_fastapi"
    POSTGRES_PASSWORD="hello_fastapi"
    POSTGRES_DB="hello_fastapi_dev"

    # Set dry-farm environment variables
    FAST_API_BASE_URL=/api
    FAST_API_TARGET=http://api:5000/
    FAST_API_VERSION=v1

    # Create .env file
    if [ ! -f $ENV_FILE ]; then
        touch $ENV_FILE
    fi

    # Update SECRET_KEY
    if grep -q "^SECRET_KEY=" $ENV_FILE; then
        sed -i.bak "s/^SECRET_KEY=.*$/SECRET_KEY=$NEW_SECRET_KEY/" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "# api environment variables in docker-compose" >> $ENV_FILE
        echo "SECRET_KEY=$NEW_SECRET_KEY" >> $ENV_FILE
    fi

    # Update DATABASE_URL
    if grep -q "^DATABASE_URL=" $ENV_FILE; then
        sed -i.bak "s|^DATABASE_URL=.*$|DATABASE_URL=$DATABASE_URL|" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "DATABASE_URL=$DATABASE_URL" >> $ENV_FILE
    fi

    # Update postgres environment variables
    if grep -q "^POSTGRES_USER=" $ENV_FILE; then
        sed -i.bak "s/^POSTGRES_USER=.*$/POSTGRES_USER=$POSTGRES_USER/" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo -e "\n# postgres environment variables in docker-compose" >> $ENV_FILE
        echo "POSTGRES_USER=$POSTGRES_USER" >> $ENV_FILE
    fi

    if grep -q "^POSTGRES_PASSWORD=" $ENV_FILE; then
        sed -i.bak "s/^POSTGRES_PASSWORD=.*$/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> $ENV_FILE
    fi

    if grep -q "^POSTGRES_DB=" $ENV_FILE; then
        sed -i.bak "s/^POSTGRES_DB=.*$/POSTGRES_DB=$POSTGRES_DB/" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "POSTGRES_DB=$POSTGRES_DB" >> $ENV_FILE
    fi

    # Update dry-farm environment variables
    if grep -q "^FAST_API_BASE_URL=" $ENV_FILE; then
        sed -i.bak "s|^FAST_API_BASE_URL=.*$|FAST_API_BASE_URL=$FAST_API_BASE_URL|" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo -e "\n# dry-farm environment variables in docker-compose" >> $ENV_FILE
        echo "FAST_API_BASE_URL=$FAST_API_BASE_URL" >> $ENV_FILE
    fi
    
    if grep -q "^FAST_API_TARGET=" $ENV_FILE; then
        sed -i.bak "s|^FAST_API_TARGET=.*$|FAST_API_TARGET=$FAST_API_TARGET|" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "FAST_API_TARGET=$FAST_API_TARGET" >> $ENV_FILE
    fi
    
    if grep -q "^FAST_API_VERSION=" $ENV_FILE; then
        sed -i.bak "s|^FAST_API_VERSION=.*$|FAST_API_VERSION=$FAST_API_VERSION|" $ENV_FILE && rm -f "${ENV_FILE}.bak"
    else
        echo "FAST_API_VERSION=$FAST_API_VERSION" >> $ENV_FILE
    fi

    # Check for certbot directory and display warning if missing
    if [ "$CERTBOT_EXISTS" = false ]; then
        echo -e "\n${RED}===== WARNING: SSL Certificates Missing =====${NC}"
        echo -e "The ${YELLOW}dry-farm/certbot${NC} directory is missing or empty."
        echo -e "If you're running on a production environment with port 443, SSL certificates are required."
        echo -e "Please copy the certbot directory from your development environment:"
        echo -e "   ${BLUE}scp -r your-dev-machine:path/to/AERC/dry-farm/certbot ./dry-farm/${NC}"
        echo -e "Or press any key to continue without SSL (suitable for local development only)..."
        read -k 1
        echo
    fi

    echo -e "${GREEN}AERC environment setup completed!${NC}"
}

# Start services
start_services() {
    echo -e "${BLUE}Starting AERC services...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE up -d
    
    # Wait for services to initialize
    sleep 3
    
    # Display service information
    echo -e "${GREEN}AERC services started${NC}"
    
    # Get frontend service external port
    FRONTEND_PORT=$($COMPOSE_CMD -f $COMPOSE_FILE port dry-farm 3000 | cut -d':' -f2)
    echo -e "Frontend service accessible at  ➜  ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
    
    # Get API service external port
    API_PORT=$($COMPOSE_CMD -f $COMPOSE_FILE port api 5000 | cut -d':' -f2)
    echo -e "API service accessible at  ➜  ${YELLOW}http://localhost:${API_PORT}${NC}"
}

# Stop services
stop_services() {
    echo -e "${BLUE}Stopping AERC services...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE down
    echo -e "${GREEN}AERC services stopped${NC}"
}

# Restart services
restart_services() {
    echo -e "${BLUE}Restarting AERC services...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE restart
    echo -e "${GREEN}AERC services restarted${NC}"
}

# Check service status
check_status() {
    echo -e "${BLUE}AERC service status:${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE ps
}

# View logs
view_logs() {
    local lines=$1
    
    if [ -z "$lines" ]; then
        lines=100
    fi
    
    echo -e "${BLUE}AERC service logs (last $lines lines):${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE logs --tail=$lines
}

# Backup data
backup_data() {
    echo -e "${BLUE}Backing up AERC data...${NC}"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/aerc"
    
    # Stop services to ensure data consistency
    $COMPOSE_CMD -f $COMPOSE_FILE stop
    
    # Backup PostgreSQL data
    echo -e "${BLUE}Backing up PostgreSQL data...${NC}"
    docker run --rm --volumes-from aerc-db-1 -v $(pwd)/$BACKUP_DIR/aerc:/backup alpine tar -czf /backup/postgres_data_$DATE.tar.gz /var/lib/postgresql/data
    
    # Backup configuration files
    echo -e "${BLUE}Backing up configuration files...${NC}"
    cp $COMPOSE_FILE "$BACKUP_DIR/aerc/docker-compose_$DATE.yml"
    cp $ENV_FILE "$BACKUP_DIR/aerc/env_$DATE"
    
    # Restart services
    $COMPOSE_CMD -f $COMPOSE_FILE start
    
    echo -e "${GREEN}Backup completed! Backup files are saved in $BACKUP_DIR/aerc directory${NC}"
}

# Update services
update_services() {
    echo -e "${BLUE}Updating AERC services...${NC}"
    
    # Backup first
    backup_data
    
    # Pull latest images
    $COMPOSE_CMD -f $COMPOSE_FILE pull
    
    # Rebuild and restart services
    $COMPOSE_CMD -f $COMPOSE_FILE up -d --build
    
    echo -e "${GREEN}AERC services updated!${NC}"
}

# Edit environment variables
edit_env() {
    # Determine which editor to use
    if [ -n "$EDITOR" ]; then
        echo -e "${BLUE}Using $EDITOR to edit environment variables file...${NC}"
        $EDITOR "$ENV_FILE"
    elif command -v nano &> /dev/null; then
        echo -e "${BLUE}Using nano to edit environment variables file...${NC}"
        nano "$ENV_FILE"
    elif command -v vim &> /dev/null; then
        echo -e "${BLUE}Using vim to edit environment variables file...${NC}"
        vim "$ENV_FILE"
    else
        echo -e "${RED}No editor found. Please manually edit the $ENV_FILE file.${NC}"
    fi
    
    echo -e "${GREEN}Environment variables file updated. You may need to restart services to apply changes.${NC}"
}

# Build and start AERC (similar to original build-env.sh)
build_aerc() {
    echo -e "${PURPLE}===== Building and Starting AERC Services =====${NC}"
    
    # Call setup function
    setup_environment
    
    # Build docker
    echo -e "\n${GREEN}===== Building Docker Containers =====${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE build --no-cache
    $COMPOSE_CMD -f $COMPOSE_FILE up -d
    
    sleep 3
    
    # Display service access information
    echo -e "\n${BLUE}===== Service Access Information =====${NC}"
    # Get frontend service external port
    FRONTEND_PORT=$($COMPOSE_CMD -f $COMPOSE_FILE port dry-farm 3000 | cut -d':' -f2)
    echo -e "Frontend service accessible at  ➜  ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
    
    # Get API service external port
    API_PORT=$($COMPOSE_CMD -f $COMPOSE_FILE port api 5000 | cut -d':' -f2)
    echo -e "API service accessible at  ➜  ${YELLOW}http://localhost:${API_PORT}${NC}"
    
    # Display first run instructions
    FIRST_RUN=false
    if [ ! -f $ENV_FILE ] || [ ! -d "api/migrations/models" ] || [ -z "$(ls -A api/migrations/models 2>/dev/null)" ]; then
        FIRST_RUN=true
    fi
    
    if [ "$FIRST_RUN" = true ]; then
        echo -e "\n${YELLOW}===== First Time Setup After Cloning =====${NC}"
        echo -e "This appears to be the first run after cloning. Please follow these steps:"
        
        echo -e "\n${GREEN}1. Apply existing migrations to set up the database:${NC}"
        echo -e "   ${BLUE}docker-compose exec api aerich upgrade${NC}"
        
        echo -e "\n${GREEN}2. If you encounter migration errors, you may need to initialize the database:${NC}"
        echo -e "   ${BLUE}docker-compose exec api aerich init -t src.database.config.TORTOISE_ORM${NC}"
        echo -e "   ${BLUE}docker-compose exec api aerich init-db${NC}"
        
        echo -e "\n${RED}IMPORTANT:${NC} Do NOT delete migration files in migrations/models/ unless you're starting a completely new project."
        echo -e "These files represent the database schema evolution and are essential for maintaining consistent state."
        
        echo -e "\n${YELLOW}===== For Subsequent Database Updates =====${NC}"
        echo -e "When you modify database models, execute these commands to update the database:"
        
        echo -e "\n1. Create migration files:"
        echo -e "   ${BLUE}docker-compose exec api aerich migrate --name descriptive_name_of_change${NC}"
        
        echo -e "\n2. Apply migrations:"
        echo -e "   ${BLUE}docker-compose exec api aerich upgrade${NC}"
    fi
    
    echo -e "\n${GREEN}✅ Setup complete. The application should now be running.${NC}"
}

# Display help information
show_help() {
    echo -e "${CYAN}===== AERC Project Management Script =====${NC}"
    echo -e "${YELLOW}Usage:${NC} ./${SCRIPT_NAME} [command] [parameters]"
    echo
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}setup${NC}    - Set up the environment"
    echo -e "  ${GREEN}start${NC}    - Start services"
    echo -e "  ${GREEN}stop${NC}     - Stop services"
    echo -e "  ${GREEN}restart${NC}  - Restart services"
    echo -e "  ${GREEN}status${NC}   - Check service status"
    echo -e "  ${GREEN}logs [n]${NC} - View logs (optional: show last n lines, default 100)"
    echo -e "  ${GREEN}backup${NC}   - Backup data"
    echo -e "  ${GREEN}update${NC}   - Update services"
    echo -e "  ${GREEN}env${NC}      - Edit environment variables"
    echo -e "  ${GREEN}build${NC}    - Build and start services (similar to original build-env.sh)"
    echo -e "  ${GREEN}help${NC}     - Display this help information"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ./${SCRIPT_NAME} start        # Start AERC services"
    echo -e "  ./${SCRIPT_NAME} logs 50      # View last 50 lines of logs"
    echo -e "  ./${SCRIPT_NAME} build        # Build and start AERC (similar to original build-env.sh)"
}

# Main function
main() {
    check_prerequisites
    check_directory_structure
    
    local command=$1
    local param=$2
    
    # Check if command parameter is provided
    if [ -z "$command" ]; then
        show_help
        exit 0
    fi
    
    # Process commands
    case "$command" in
        setup)
            setup_environment
            ;;
        start)
            check_compose_file
            start_services
            ;;
        stop)
            check_compose_file
            stop_services
            ;;
        restart)
            check_compose_file
            restart_services
            ;;
        status)
            check_compose_file
            check_status
            ;;
        logs)
            check_compose_file
            view_logs "$param"
            ;;
        backup)
            check_compose_file
            backup_data
            ;;
        update)
            check_compose_file
            update_services
            ;;
        env)
            edit_env
            ;;
        build)
            build_aerc
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$command'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"