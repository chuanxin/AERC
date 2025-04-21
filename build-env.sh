#!/bin/zsh

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# check if .env file exists or api/migrations/models directory is empty
FIRST_RUN=false
if [ ! -f .env ] || [ ! -d "api/migrations/models" ] || [ -z "$(ls -A api/migrations/models 2>/dev/null)" ]; then
    FIRST_RUN=true
fi

# Check if certbot directory exists for SSL certificates
CERTBOT_EXISTS=false
if [ -d "dry-farm/certbot" ] && [ ! -z "$(ls -A dry-farm/certbot 2>/dev/null)" ]; then
    CERTBOT_EXISTS=true
fi

# generate new secret key
NEW_SECRET_KEY=$(openssl rand -hex 32)

# set database url
DATABASE_URL="postgres://hello_fastapi:hello_fastapi@db:5432/hello_fastapi_dev"

# set postgres user, password, database
POSTGRES_USER="hello_fastapi"
POSTGRES_PASSWORD="hello_fastapi"
POSTGRES_DB="hello_fastapi_dev"

# set dry-farm environment variables
FAST_API_BASE_URL=/api
FAST_API_TARGET=http://api:5000/
FAST_API_VERSION=v1

# create .env file
if [ ! -f .env ]; then
    touch .env
fi

# update SECRET_KEY
if grep -q "^SECRET_KEY=" .env; then
    sed -i '' "s/^SECRET_KEY=.*$/SECRET_KEY=$NEW_SECRET_KEY/" .env
else
    echo "# api environment variables in docker-compose" >> .env
    echo "SECRET_KEY=$NEW_SECRET_KEY" >> .env
fi

# update DATABASE_URL
if grep -q "^DATABASE_URL=" .env; then
    sed -i '' "s|^DATABASE_URL=.*$|DATABASE_URL=$DATABASE_URL|" .env
else
    echo "DATABASE_URL=$DATABASE_URL" >> .env
fi

# update postgres environment variables
if grep -q "^POSTGRES_USER=" .env; then
    sed -i '' "s/^POSTGRES_USER=.*$/POSTGRES_USER=$POSTGRES_USER/" .env
else
    echo -e "\n# postgres environment variables in docker-compose" >> .env
    echo "POSTGRES_USER=$POSTGRES_USER" >> .env
fi

if grep -q "^POSTGRES_PASSWORD=" .env; then
    sed -i '' "s/^POSTGRES_PASSWORD=.*$/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
else
    echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD" >> .env
fi

if grep -q "^POSTGRES_DB=" .env; then
    sed -i '' "s/^POSTGRES_DB=.*$/POSTGRES_DB=$POSTGRES_DB/" .env
else
    echo "POSTGRES_DB=$POSTGRES_DB" >> .env
fi

# update dry-farm environment variables
if grep -q "^FAST_API_BASE_URL=" .env; then
    sed -i '' "s|^FAST_API_BASE_URL=.*$|FAST_API_BASE_URL=$FAST_API_BASE_URL|" .env
else
    echo -e "\n# dry-farm environment variables in docker-compose" >> .env
    echo "FAST_API_BASE_URL=$FAST_API_BASE_URL" >> .env
fi
if grep -q "^FAST_API_TARGET=" .env; then
    sed -i '' "s|^FAST_API_TARGET=.*$|FAST_API_TARGET=$FAST_API_TARGET|" .env
else
    echo "FAST_API_TARGET=$FAST_API_TARGET" >> .env
fi
if grep -q "^FAST_API_VERSION=" .env; then
    sed -i '' "s|^FAST_API_VERSION=.*$|FAST_API_VERSION=$FAST_API_VERSION|" .env
else
    echo "FAST_API_VERSION=$FAST_API_VERSION" >> .env
fi

# Check for certbot directory and display warning if missing
if [ "$CERTBOT_EXISTS" = false ]; then
    echo -e "\n${RED}===== WARNING: SSL Certificates Missing =====${NC}"
    echo -e "The ${YELLOW}dry-farm/certbot${NC} directory is missing or empty."
    echo -e "If you're running on a production environment with port 443, SSL certificates are required."
    echo -e "Please copy the certbot directory from your development environment:"
    echo -e "   ${BLUE}scp -r your-dev-machine:path/to/AERC/dry-farm/certbot ./dry-farm/${NC}"
    echo -e "Or press any key to continue without SSL (suitable for local development only)..."
    read -n 1 -s
fi

# build docker
echo -e "\n${GREEN}===== Building Docker Containers =====${NC}"
docker-compose build --no-cache
docker-compose up -d

sleep 3
# Display service access information
echo -e "\n${BLUE}===== Service Access Information =====${NC}"
# Get frontend service external port
FRONTEND_PORT=$(docker-compose port dry-farm 3000 | cut -d':' -f2)
echo "Frontend service accessible at  ➜  ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"

# Get API service external port
API_PORT=$(docker-compose port api 5000 | cut -d':' -f2)
echo "API service accessible at  ➜  ${YELLOW}http://localhost:${API_PORT}${NC}"

# display database initialization information
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
    
    echo -e "\n${YELLOW}===== For SSL Configuration (Production Environment) =====${NC}"
    if [ "$CERTBOT_EXISTS" = false ]; then
        echo -e "${RED}⚠️  SSL certificates are missing! The frontend won't work on port 443 without them.${NC}"
        echo -e "For production deployment, you must copy the certbot directory from your development environment:"
        echo -e "   ${BLUE}scp -r your-dev-machine:path/to/AERC/dry-farm/certbot ./dry-farm/${NC}"
        echo -e "Then restart the containers:  ${BLUE}docker-compose restart${NC}"
    else
        echo -e "${GREEN}✓ SSL certificates found in dry-farm/certbot.${NC} The frontend should work correctly on port 443."
    fi
    
    echo -e "\n${YELLOW}===== For Subsequent Database Updates =====${NC}"
    echo -e "When you modify database models, execute these commands to update the database:"
    echo -e "\n1. Create migration files:"
    echo -e "   ${BLUE}docker-compose exec api aerich migrate --name descriptive_name_of_change${NC}"
    
    echo -e "\n2. Apply migrations:"
    echo -e "   ${BLUE}docker-compose exec api aerich upgrade${NC}"
fi

echo -e "\n${GREEN}✅ Setup complete. The application should now be running.${NC}"
# Display service logs
# echo -e "\n===== Frontend Service Logs ====="
# docker-compose logs dry-farm | tail -n 4