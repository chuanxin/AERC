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

# Check PostGIS status
check_postgis() {
    echo -e "${BLUE}Checking PostGIS status...${NC}"
    
    # Check if database container is running
    if ! $COMPOSE_CMD -f $COMPOSE_FILE ps | grep -q "aerc-db.*Up"; then
        echo -e "${RED}Error: Database container is not running. Please start services first.${NC}"
        return 1
    fi
    
    # Check PostGIS extensions
    echo -e "${BLUE}Checking PostGIS extensions...${NC}"
    DB_CHECK_RESULT=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    SELECT extname, extversion FROM pg_extension WHERE extname LIKE '%postgis%' OR extname LIKE '%geos%' OR extname LIKE '%fuzzystrmatch%';
    " 2>/dev/null || echo "ERROR")
    
    if [[ "$DB_CHECK_RESULT" == *"ERROR"* ]] || [[ -z "$DB_CHECK_RESULT" ]]; then
        echo -e "${RED}❌ PostGIS extensions are not installed${NC}"
        echo -e "${YELLOW}Use './aerc-manager.sh init-postgis' to initialize PostGIS${NC}"
        return 1
    else
        echo -e "${GREEN}✅ PostGIS extensions found:${NC}"
        echo "$DB_CHECK_RESULT"
    fi
    
    # Test PostGIS functionality
    echo -e "${BLUE}Testing PostGIS functionality...${NC}"
    POSTGIS_TEST_OUTPUT=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT PostGIS_version() as postgis_version;" 2>&1)
    POSTGIS_TEST_EXIT_CODE=$?
    
    if [ $POSTGIS_TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ PostGIS core functionality test passed${NC}"
        echo "$POSTGIS_TEST_OUTPUT"
    else
        echo -e "${RED}❌ PostGIS functionality test failed${NC}"
        echo -e "${YELLOW}Error details:${NC}"
        echo "$POSTGIS_TEST_OUTPUT"
        return 1
    fi
    
    # Test GEOS/PROJ support (integrated in PostGIS 3.5+)
    echo -e "${BLUE}Checking GEOS/PROJ integration...${NC}"
    if [[ "$POSTGIS_TEST_OUTPUT" == *"USE_GEOS=1"* ]]; then
        echo -e "${GREEN}✅ GEOS support: Enabled${NC}"
    else
        echo -e "${YELLOW}⚠️ GEOS support: Unknown status${NC}"
    fi
    
    if [[ "$POSTGIS_TEST_OUTPUT" == *"USE_PROJ=1"* ]]; then
        echo -e "${GREEN}✅ PROJ support: Enabled${NC}"
    else
        echo -e "${YELLOW}⚠️ PROJ support: Unknown status${NC}"
    fi
    
    # Note for PostGIS 3.4+ users
    if [[ "$POSTGIS_TEST_OUTPUT" == *"3.4"* ]] || [[ "$POSTGIS_TEST_OUTPUT" == *"3.5"* ]]; then
        echo -e "${BLUE}ℹ️ PostGIS 3.4+ Note: GEOS_version() and PROJ_version() functions have been removed for security reasons${NC}"
        echo -e "${BLUE}   GEOS/PROJ integration status is shown in PostGIS_version() output${NC}"
    fi
    
    # Test spatial operations
    echo -e "${BLUE}Testing spatial operations...${NC}"
    SPATIAL_TEST_OUTPUT=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT ST_AsText(ST_Point(121.5, 25.0)) as taipei_point;" 2>&1)
    SPATIAL_TEST_EXIT_CODE=$?
    
    if [ $SPATIAL_TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✅ Spatial operations test passed${NC}"
        echo "$SPATIAL_TEST_OUTPUT"
    else
        echo -e "${RED}❌ Spatial operations test failed${NC}"
        echo -e "${YELLOW}Error details:${NC}"
        echo "$SPATIAL_TEST_OUTPUT"
        return 1
    fi
    
    echo -e "${GREEN}🎉 PostGIS is fully functional!${NC}"
}

# Performance test for PostgreSQL with/without PostGIS
performance_test() {
    echo -e "${BLUE}Running PostgreSQL + PostGIS performance test...${NC}"
    
    # Check if database container is running
    if ! $COMPOSE_CMD -f $COMPOSE_FILE ps | grep -q "aerc-db.*Up"; then
        echo -e "${RED}Error: Database container is not running. Please start services first.${NC}"
        return 1
    fi
    
    echo -e "\n${BLUE}=== Performance Test Results ===${NC}"
    
    # Test 1: Basic database operations
    echo -e "\n${BLUE}1. Testing basic database operations...${NC}"
    START_TIME=$(date +%s%N)
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    DROP TABLE IF EXISTS perf_test;
    CREATE TABLE perf_test (id SERIAL PRIMARY KEY, name VARCHAR(100), value NUMERIC);
    INSERT INTO perf_test (name, value) 
    SELECT 'test_' || generate_series, random() * 1000 
    FROM generate_series(1, 10000);
    " > /dev/null 2>&1
    END_TIME=$(date +%s%N)
    BASIC_TIME=$((($END_TIME - $START_TIME) / 1000000))
    echo -e "${GREEN}   Basic operations (10K inserts): ${BASIC_TIME}ms${NC}"
    
    # Test 2: Query performance
    echo -e "\n${BLUE}2. Testing query performance...${NC}"
    START_TIME=$(date +%s%N)
    RESULT=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    SELECT COUNT(*) FROM perf_test WHERE value > 500;
    " 2>/dev/null)
    END_TIME=$(date +%s%N)
    QUERY_TIME=$((($END_TIME - $START_TIME) / 1000000))
    echo -e "${GREEN}   Query performance (10K records): ${QUERY_TIME}ms${NC}"
    
    # Test 3: Spatial operations (if PostGIS available)
    echo -e "\n${BLUE}3. Testing spatial operations...${NC}"
    START_TIME=$(date +%s%N)
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    DROP TABLE IF EXISTS spatial_perf_test;
    CREATE TABLE spatial_perf_test (
        id SERIAL PRIMARY KEY, 
        name VARCHAR(100), 
        location GEOMETRY(POINT, 4326)
    );
    INSERT INTO spatial_perf_test (name, location)
    SELECT 
        'point_' || generate_series,
        ST_Point(120 + random() * 2, 24 + random() * 2)
    FROM generate_series(1, 1000);
    CREATE INDEX idx_spatial_perf_location ON spatial_perf_test USING GIST (location);
    " > /dev/null 2>&1
    END_TIME=$(date +%s%N)
    SPATIAL_TIME=$((($END_TIME - $START_TIME) / 1000000))
    echo -e "${GREEN}   Spatial operations (1K points + index): ${SPATIAL_TIME}ms${NC}"
    
    # Test 4: Spatial query performance
    echo -e "\n${BLUE}4. Testing spatial query performance...${NC}"
    START_TIME=$(date +%s%N)
    SPATIAL_RESULT=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    SELECT COUNT(*) FROM spatial_perf_test 
    WHERE ST_DWithin(location, ST_Point(121.5, 25.0), 0.5);
    " 2>/dev/null)
    END_TIME=$(date +%s%N)
    SPATIAL_QUERY_TIME=$((($END_TIME - $START_TIME) / 1000000))
    echo -e "${GREEN}   Spatial query (distance search): ${SPATIAL_QUERY_TIME}ms${NC}"
    
    # Memory usage
    echo -e "\n${BLUE}5. Checking memory usage...${NC}"
    MEMORY_INFO=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db ps aux | grep postgres | head -1 | awk '{print $4 "% RAM, " $6/1024 "MB"}' 2>/dev/null)
    echo -e "${GREEN}   PostgreSQL memory usage: ${MEMORY_INFO}${NC}"
    
    # Database size
    echo -e "\n${BLUE}6. Checking database size...${NC}"
    DB_SIZE=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    SELECT pg_size_pretty(pg_database_size('${POSTGRES_DB:-hello_fastapi_dev}'));
    " 2>/dev/null | grep -v "pg_size_pretty" | grep -v "row" | tr -d ' ')
    echo -e "${GREEN}   Database size: ${DB_SIZE}${NC}"
    
    # Summary
    echo -e "\n${YELLOW}=== Performance Summary ===${NC}"
    echo -e "Basic operations:    ${BASIC_TIME}ms"
    echo -e "Query performance:   ${QUERY_TIME}ms"
    echo -e "Spatial operations:  ${SPATIAL_TIME}ms"
    echo -e "Spatial queries:     ${SPATIAL_QUERY_TIME}ms"
    echo -e "Memory usage:        ${MEMORY_INFO}"
    echo -e "Database size:       ${DB_SIZE}"
    
    # Cleanup
    echo -e "\n${BLUE}Cleaning up test data...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "
    DROP TABLE IF EXISTS perf_test;
    DROP TABLE IF EXISTS spatial_perf_test;
    " > /dev/null 2>&1
    
    echo -e "${GREEN}✅ Performance test completed${NC}"
}

# Debug PostGIS functions individually
debug_postgis_functions() {
    echo -e "${BLUE}Debugging PostGIS functions individually...${NC}"
    
    # Check if database container is running
    if ! $COMPOSE_CMD -f $COMPOSE_FILE ps | grep -q "aerc-db.*Up"; then
        echo -e "${RED}Error: Database container is not running. Please start services first.${NC}"
        return 1
    fi
    
    echo -e "\n${BLUE}=== Testing Individual PostGIS Functions ===${NC}"
    
    # Test 1: PostGIS_version()
    echo -e "\n${BLUE}1. Testing PostGIS_version()...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT PostGIS_version();" || echo -e "${RED}PostGIS_version() failed${NC}"
    
    # Test 2: GEOS_version()
    echo -e "\n${BLUE}2. Testing GEOS_version()...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT GEOS_version();" || echo -e "${RED}GEOS_version() failed${NC}"
    
    # Test 3: PROJ_version()
    echo -e "\n${BLUE}3. Testing PROJ_version()...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT PROJ_version();" || echo -e "${RED}PROJ_version() failed${NC}"
    
    # Test 4: Simple spatial function
    echo -e "\n${BLUE}4. Testing ST_Point()...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT ST_Point(121.5, 25.0);" || echo -e "${RED}ST_Point() failed${NC}"
    
    # Test 5: ST_AsText with ST_Point
    echo -e "\n${BLUE}5. Testing ST_AsText(ST_Point())...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT ST_AsText(ST_Point(121.5, 25.0));" || echo -e "${RED}ST_AsText(ST_Point()) failed${NC}"
    
    # Test 6: Check function permissions
    echo -e "\n${BLUE}6. Checking function permissions...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT has_function_privilege('${POSTGRES_USER:-hello_fastapi}', 'postgis_version()', 'execute');" || echo -e "${RED}Permission check failed${NC}"
    
    # Test 7: List all PostGIS functions
    echo -e "\n${BLUE}7. Available PostGIS functions (first 10):${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT proname FROM pg_proc WHERE proname LIKE 'st_%' OR proname LIKE 'postgis%' LIMIT 10;" || echo -e "${RED}Function listing failed${NC}"
}

# Diagnose PostGIS installation issues
diagnose_postgis() {
    echo -e "${BLUE}Diagnosing PostGIS installation...${NC}"
    
    # Check if database container is running
    if ! $COMPOSE_CMD -f $COMPOSE_FILE ps | grep -q "aerc-db.*Up"; then
        echo -e "${RED}Error: Database container is not running. Please start services first.${NC}"
        return 1
    fi
    
    echo -e "${BLUE}1. Checking installed packages in container...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db dpkg -l | grep -i postgis || echo -e "${RED}No PostGIS packages found${NC}"
    
    echo -e "\n${BLUE}2. Looking for PostGIS control files...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db find /usr -name 'postgis.control' 2>/dev/null || echo -e "${RED}PostGIS control files not found${NC}"
    
    echo -e "\n${BLUE}3. Checking PostgreSQL extension directory...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db ls -la /usr/local/share/postgresql/extension/ | grep postgis || echo -e "${RED}No PostGIS extensions found${NC}"
    
    echo -e "\n${BLUE}4. Checking available extensions in PostgreSQL...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -c "SELECT name FROM pg_available_extensions WHERE name LIKE '%postgis%';" 2>/dev/null || echo -e "${RED}Cannot query available extensions${NC}"
    
    echo -e "\n${BLUE}5. Database logs (last 20 lines):${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE logs --tail=20 db
    
    echo -e "\n${YELLOW}===== Recommendations =====${NC}"
    echo -e "If PostGIS packages are missing, try:"
    echo -e "1. ${BLUE}./aerc-manager.sh stop${NC}"
    echo -e "2. ${BLUE}docker-compose build --no-cache db${NC}"
    echo -e "3. ${BLUE}./aerc-manager.sh start${NC}"
    echo -e "\nFor debugging package installation:"
    echo -e "4. ${BLUE}docker-compose exec db apt list --installed | grep postgis${NC}"
    echo -e "\nAlternatively, switch to official PostGIS image:"
    echo -e "5. ${BLUE}cp db/Dockerfile.official db/Dockerfile${NC}"
    echo -e "6. Rebuild and restart"
}

# Initialize PostGIS manually
init_postgis() {
    echo -e "${BLUE}Initializing PostGIS extensions...${NC}"
    
    # Check if database container is running
    if ! $COMPOSE_CMD -f $COMPOSE_FILE ps | grep -q "aerc-db.*Up"; then
        echo -e "${RED}Error: Database container is not running. Please start services first.${NC}"
        return 1
    fi
    
    # Check if initialization script exists in container
    echo -e "${BLUE}Checking if PostGIS initialization script exists in container...${NC}"
    SCRIPT_EXISTS=$($COMPOSE_CMD -f $COMPOSE_FILE exec -T db test -f /docker-entrypoint-initdb.d/init-postgis.sql && echo "EXISTS" || echo "MISSING")
    
    if [ "$SCRIPT_EXISTS" = "MISSING" ]; then
        echo -e "${RED}❌ PostGIS initialization script not found in container${NC}"
        echo -e "${YELLOW}The script should be automatically copied during docker build.${NC}"
        echo -e "${YELLOW}Try rebuilding the database container:${NC}"
        echo -e "   ${BLUE}./aerc-manager.sh stop${NC}"
        echo -e "   ${BLUE}docker-compose build db${NC}"
        echo -e "   ${BLUE}./aerc-manager.sh start${NC}"
        return 1
    fi
    
    # Execute PostGIS initialization script from within container
    echo -e "${BLUE}Executing PostGIS initialization script from container...${NC}"
    $COMPOSE_CMD -f $COMPOSE_FILE exec -T db psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -f /docker-entrypoint-initdb.d/init-postgis.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PostGIS initialization completed successfully${NC}"
        echo -e "${BLUE}Running PostGIS verification...${NC}"
        check_postgis
    else
        echo -e "${RED}❌ PostGIS initialization failed${NC}"
        echo -e "${YELLOW}You can manually initialize PostGIS by running:${NC}"
        echo -e "   ${BLUE}docker exec aerc-db-1 psql -U ${POSTGRES_USER:-hello_fastapi} -d ${POSTGRES_DB:-hello_fastapi_dev} -f /docker-entrypoint-initdb.d/init-postgis.sql${NC}"
        return 1
    fi
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
    
    # Check PostGIS after initial setup
    echo -e "\n${BLUE}===== PostGIS Status Check =====${NC}"
    sleep 2  # Wait a bit more for database to be fully ready
    check_postgis
    
    if [ $? -ne 0 ]; then
        echo -e "\n${YELLOW}===== PostGIS Initialization Required =====${NC}"
        echo -e "PostGIS extensions are not installed. This is normal for first-time setup."
        echo -e "Run the following command to initialize PostGIS:"
        echo -e "   ${BLUE}./aerc-manager.sh init-postgis${NC}"
    fi
    
    echo -e "\n${GREEN}✅ Setup complete. The application should now be running.${NC}"
}

# Display help information
show_help() {
    echo -e "${CYAN}===== AERC Project Management Script =====${NC}"
    echo -e "${YELLOW}Usage:${NC} ./${SCRIPT_NAME} [command] [parameters]"
    echo
    echo -e "${YELLOW}Available commands:${NC}"
    echo -e "  ${GREEN}setup${NC}           - Set up the environment"
    echo -e "  ${GREEN}start${NC}           - Start services"
    echo -e "  ${GREEN}stop${NC}            - Stop services"
    echo -e "  ${GREEN}restart${NC}         - Restart services"
    echo -e "  ${GREEN}status${NC}          - Check service status"
    echo -e "  ${GREEN}logs [n]${NC}        - View logs (optional: show last n lines, default 100)"
    echo -e "  ${GREEN}backup${NC}          - Backup data"
    echo -e "  ${GREEN}update${NC}          - Update services"
    echo -e "  ${GREEN}env${NC}             - Edit environment variables"
    echo -e "  ${GREEN}build${NC}           - Build and start services (similar to original build-env.sh)"
    echo -e "  ${GREEN}check-postgis${NC}    - Check PostGIS installation and functionality"
    echo -e "  ${GREEN}init-postgis${NC}     - Initialize PostGIS extensions manually"
    echo -e "  ${GREEN}diagnose-postgis${NC}  - Diagnose PostGIS installation issues"
    echo -e "  ${GREEN}debug-postgis${NC}     - Debug PostGIS functions individually"
    echo -e "  ${GREEN}performance-test${NC}  - Run PostgreSQL + PostGIS performance test"
    echo -e "  ${GREEN}help${NC}            - Display this help information"
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
        check-postgis)
            check_compose_file
            check_postgis
            ;;
        init-postgis)
            check_compose_file
            init_postgis
            ;;
        diagnose-postgis)
            check_compose_file
            diagnose_postgis
            ;;
        debug-postgis)
            check_compose_file
            debug_postgis_functions
            ;;
        performance-test)
            check_compose_file
            performance_test
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