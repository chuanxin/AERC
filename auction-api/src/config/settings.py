import os
from dotenv import load_dotenv

load_dotenv()

# App
APP_NAME = "Auction Platform API"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://auction:auction@localhost:5432/auction_db")

# Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# JWT
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# Meilisearch
MEILISEARCH_URL = os.getenv("MEILISEARCH_URL", "http://localhost:7700")
MEILISEARCH_KEY = os.getenv("MEILISEARCH_KEY", "")

# Auction defaults
AUCTION_AUTO_EXTEND_MINUTES = 5
AUCTION_MIN_DURATION_HOURS = 1
AUCTION_MAX_DURATION_DAYS = 30

# Upload
MAX_IMAGE_SIZE_MB = 10
MAX_IMAGES_PER_AUCTION = 10
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
