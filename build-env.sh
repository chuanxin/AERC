#!/bin/zsh

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# generate new secret key
NEW_SECRET_KEY=$(openssl rand -hex 32)

# set database url
DATABASE_URL="postgres://hello_fastapi:hello_fastapi@db:5432/hello_fastapi_dev"

# set postgres user, password, database
POSTGRES_USER="hello_fastapi"
POSTGRES_PASSWORD="hello_fastapi"
POSTGRES_DB="hello_fastapi_dev"

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

# build docker
docker-compose up -d --build

sleep 3
# Display service access information
echo -e "\n${BLUE}===== Service Access Information =====${NC}"
# Get frontend service external port
FRONTEND_PORT=$(docker-compose port dry-farm 3000 | cut -d':' -f2)
echo "Frontend service accessible at  ➜  ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"

# Get API service external port
API_PORT=$(docker-compose port api 5000 | cut -d':' -f2)
echo "API service accessible at  ➜  ${YELLOW}http://localhost:${API_PORT}${NC}"

# Display service logs
# echo -e "\n===== Frontend Service Logs ====="
# docker-compose logs dry-farm | tail -n 4