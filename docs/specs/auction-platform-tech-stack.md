# Auction Platform Tech Stack Specification

> Based on AERC project's proven stack, extended for real-time auction requirements.

## 1. Architecture Overview

```
                         ┌──────────────────────┐
                         │   Nginx (Reverse      │
                         │   Proxy + Static)      │
                         └──────────┬─────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
             ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
             │  Vue 3 SPA  │ │  FastAPI    │ │  FastAPI    │
             │  (Static)   │ │  Instance 1 │ │  Instance 2 │
             └─────────────┘ └──────┬──────┘ └──────┬──────┘
                                    │               │
                         ┌──────────▼───────────────▼──┐
                         │         Redis               │
                         │  (Cache + Pub/Sub + Queue)   │
                         └──────────┬──────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
             ┌──────▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
             │ PostgreSQL  │ │   Celery    │ │   Celery    │
             │   17        │ │   Worker    │ │   Beat      │
             └─────────────┘ └─────────────┘ └─────────────┘
```

## 2. Frontend Stack

### Core Framework (Same as AERC)

| Package | Version | Purpose |
|---------|---------|---------|
| **vue** | ^3.5 | UI framework (Composition API) |
| **typescript** | ~5.9 | Type safety |
| **vite** | ^7.0 | Build tool + HMR |
| **pinia** | ^2.3 | State management |
| **vue-router** | ^4.5 | Client-side routing |

### UI Framework (Choose One)

| Option | When to Use |
|--------|-------------|
| **Vuetify 3** | Fast development, admin-heavy UI, consistent Material Design |
| **PrimeVue + Tailwind CSS** | Custom branding needed, auction-specific UI components |

**Recommendation**: Start with **Vuetify 3** (team familiarity from AERC), migrate individual components to custom designs later if branding demands it.

### New Dependencies for Auction

| Package | Purpose |
|---------|---------|
| **socket.io-client** ^4.8 | Real-time bid updates via WebSocket |
| **@vueuse/core** ^12.0 | Composable utilities (useWebSocket, useIntervalFn for countdown) |
| **dayjs** ^1.11 | Lightweight date/time (auction countdown, timezone handling) |
| **vue-virtual-scroller** ^2.0 | Virtual list for large auction catalogs |
| **@tanstack/vue-query** ^5.0 | Server state management (cache, pagination, optimistic updates) |
| **swiper** ^11.0 | Image gallery/carousel for auction items |
| **compressorjs** ^1.2 | Client-side image compression before upload |

### Frontend Architecture

```
auction-web/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── pages/                    # File-based routing
│   │   ├── index.vue             # Homepage / featured auctions
│   │   ├── auctions/
│   │   │   ├── index.vue         # Auction listing (search + filter)
│   │   │   ├── [id].vue          # Auction detail + live bidding
│   │   │   └── create.vue        # Create new auction (seller)
│   │   ├── user/
│   │   │   ├── profile.vue
│   │   │   ├── my-auctions.vue   # Seller dashboard
│   │   │   ├── my-bids.vue       # Buyer bid history
│   │   │   └── wallet.vue        # Payment methods
│   │   └── admin/
│   │       ├── dashboard.vue
│   │       ├── auctions.vue      # Auction management
│   │       └── users.vue         # User management
│   ├── components/
│   │   ├── auction/
│   │   │   ├── AuctionCard.vue       # Auction preview card
│   │   │   ├── BidPanel.vue          # Real-time bid interface
│   │   │   ├── CountdownTimer.vue    # Auction countdown
│   │   │   ├── BidHistory.vue        # Live bid history feed
│   │   │   ├── ImageGallery.vue      # Multi-image viewer
│   │   │   └── AuctionStatus.vue     # Status badge
│   │   ├── search/
│   │   │   ├── SearchBar.vue
│   │   │   └── FilterPanel.vue
│   │   └── common/
│   │       ├── PriceDisplay.vue
│   │       └── NotificationToast.vue
│   ├── stores/
│   │   ├── auth.ts               # Auth state (JWT, from AERC pattern)
│   │   ├── auction.ts            # Current auction detail state
│   │   ├── bidding.ts            # Real-time bidding state (WebSocket)
│   │   ├── search.ts             # Search/filter state
│   │   └── notification.ts       # Push notification state
│   ├── composables/
│   │   ├── useSocket.ts          # Socket.IO connection management
│   │   ├── useCountdown.ts       # Auction countdown logic
│   │   ├── useBidding.ts         # Bid submission + optimistic update
│   │   └── useImageUpload.ts     # Image compression + upload
│   ├── services/
│   │   ├── api.ts                # Axios instance + interceptors (from AERC)
│   │   ├── auctionService.ts     # Auction CRUD API
│   │   ├── bidService.ts         # Bid API
│   │   ├── userService.ts        # Auth + profile API
│   │   ├── paymentService.ts     # Payment API
│   │   └── searchService.ts      # Search API
│   ├── types/
│   │   ├── auction.ts
│   │   ├── bid.ts
│   │   ├── user.ts
│   │   └── payment.ts
│   └── utils/
│       ├── currency.ts           # Price formatting
│       └── time.ts               # Time utilities
├── package.json
├── vite.config.mts
├── tsconfig.json
└── Dockerfile
```

## 3. Backend Stack

### Core Framework (Same as AERC)

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | 0.115+ | API framework |
| **uvicorn** | 0.34+ | ASGI server |
| **tortoise-orm** | 0.25+ | Async ORM |
| **aerich** | 0.8+ | DB migrations |
| **asyncpg** | 0.30+ | PostgreSQL async driver |
| **python-jose** | 3.4+ | JWT handling |
| **passlib[bcrypt]** | 1.7+ | Password hashing |

### New Dependencies for Auction

| Package | Version | Purpose |
|---------|---------|---------|
| **python-socketio** | ^5.12 | WebSocket server (Socket.IO protocol) |
| **redis[hiredis]** | ^5.2 | Redis client with C parser for speed |
| **celery[redis]** | ^5.4 | Distributed task queue |
| **celery-redbeat** | ^2.2 | Redis-based Celery Beat scheduler |
| **meilisearch** | ^0.33 | Full-text search client |
| **pillow** | ^11.0 | Image processing (already in AERC) |
| **python-multipart** | ^0.0.20 | File upload (already in AERC) |
| **httpx** | ^0.28 | Async HTTP for payment gateway calls |

### Backend Architecture

```
auction-api/
├── src/
│   ├── main.py                   # FastAPI app + Socket.IO mount
│   ├── config/
│   │   ├── settings.py           # Environment-based config
│   │   └── redis.py              # Redis connection pool
│   ├── database/
│   │   ├── config.py             # Tortoise ORM config
│   │   ├── models/
│   │   │   ├── user.py           # User + seller profile
│   │   │   ├── auction.py        # Auction + auction item
│   │   │   ├── bid.py            # Bid (append-only)
│   │   │   ├── payment.py        # Payment + transaction
│   │   │   └── notification.py   # Notification log
│   │   └── register.py
│   ├── auth/
│   │   ├── jwthandler.py         # JWT (from AERC pattern)
│   │   └── permissions.py        # Role-based access (buyer/seller/admin)
│   ├── routes/
│   │   ├── auth.py               # Login, register, token refresh
│   │   ├── auctions.py           # Auction CRUD
│   │   ├── bids.py               # Bid placement (atomic)
│   │   ├── search.py             # Search proxy to Meilisearch
│   │   ├── payments.py           # Payment integration
│   │   ├── users.py              # User profile
│   │   ├── admin.py              # Admin operations
│   │   └── uploads.py            # Image upload
│   ├── services/
│   │   ├── auction_service.py    # Auction business logic
│   │   ├── bid_service.py        # Atomic bid logic (core)
│   │   ├── payment_service.py    # Payment gateway abstraction
│   │   ├── search_service.py     # Meilisearch indexing
│   │   ├── notification_service.py  # Email + push
│   │   └── image_service.py      # Image resize + storage
│   ├── socket/
│   │   ├── server.py             # Socket.IO server setup
│   │   ├── events.py             # Event handlers (join_room, leave_room)
│   │   └── emitters.py           # Broadcast helpers (bid_update, auction_end)
│   ├── tasks/
│   │   ├── celery_app.py         # Celery configuration
│   │   ├── auction_tasks.py      # End auction, extend time
│   │   ├── notification_tasks.py # Async email/push
│   │   ├── search_tasks.py       # Index update
│   │   └── payment_tasks.py      # Payment verification
│   ├── schemas/
│   │   ├── auction.py            # Pydantic models
│   │   ├── bid.py
│   │   ├── user.py
│   │   └── payment.py
│   └── utils/
│       ├── currency.py
│       └── time.py
├── migrations/
├── pyproject.toml
├── requirements.txt
└── Dockerfile
```

## 4. Database Schema (Core Tables)

```sql
-- Users (extended from AERC pattern)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'buyer',  -- buyer | seller | admin
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    avatar_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seller profiles
CREATE TABLE seller_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    display_name VARCHAR(200) NOT NULL,
    description TEXT,
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_sales INTEGER DEFAULT 0,
    verified_at TIMESTAMPTZ
);

-- Auctions
CREATE TABLE auctions (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    starting_price DECIMAL(12,2) NOT NULL,
    current_price DECIMAL(12,2) NOT NULL,
    reserve_price DECIMAL(12,2),          -- minimum price to sell
    bid_increment DECIMAL(10,2) NOT NULL, -- minimum bid step
    bid_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',   -- draft | active | ended | sold | cancelled
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    auto_extend BOOLEAN DEFAULT true,     -- extend if bid in last 5 min
    extend_minutes INTEGER DEFAULT 5,
    winner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auction images
CREATE TABLE auction_images (
    id SERIAL PRIMARY KEY,
    auction_id INTEGER REFERENCES auctions(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false
);

-- Categories
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(id),
    slug VARCHAR(100) UNIQUE NOT NULL,
    sort_order INTEGER DEFAULT 0
);

-- Bids (append-only, never delete)
CREATE TABLE bids (
    id SERIAL PRIMARY KEY,
    auction_id INTEGER REFERENCES auctions(id),
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL,
    is_winning BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_bids_auction_amount ON bids(auction_id, amount DESC);
CREATE INDEX idx_bids_user ON bids(user_id);

-- Payments
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    auction_id INTEGER REFERENCES auctions(id),
    buyer_id INTEGER REFERENCES users(id),
    seller_id INTEGER REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL,
    platform_fee DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending | paid | refunded | failed
    payment_method VARCHAR(50),
    gateway_tx_id VARCHAR(200),
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Watchlist (user favorites)
CREATE TABLE watchlist (
    user_id INTEGER REFERENCES users(id),
    auction_id INTEGER REFERENCES auctions(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, auction_id)
);
```

## 5. Critical Implementation: Atomic Bidding

This is the most important piece of the entire platform. Race conditions here = lost money.

```python
# src/services/bid_service.py

from tortoise.transactions import in_transaction
from src.database.models.auction import Auction
from src.database.models.bid import Bid
from src.schemas.bid import BidCreate, BidResponse
from src.socket.emitters import broadcast_bid_update


class BidError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message


async def place_bid(auction_id: int, user_id: int, amount: float) -> BidResponse:
    """
    Atomic bid placement with SELECT FOR UPDATE.
    No race conditions. No partial states.
    """
    async with in_transaction() as conn:
        # Lock the auction row — other bids on same auction wait here
        auction = await Auction.select_for_update().get_or_none(id=auction_id)

        if not auction:
            raise BidError("NOT_FOUND", "Auction not found")

        if auction.status != "active":
            raise BidError("NOT_ACTIVE", "Auction is not active")

        if auction.seller_id == user_id:
            raise BidError("SELF_BID", "Cannot bid on your own auction")

        min_bid = auction.current_price + auction.bid_increment
        if amount < min_bid:
            raise BidError("TOO_LOW", f"Minimum bid is {min_bid}")

        # Create bid and update auction in same transaction
        bid = await Bid.create(
            auction_id=auction_id,
            user_id=user_id,
            amount=amount,
            is_winning=True,
        )

        # Unmark previous winning bid
        await Bid.filter(
            auction_id=auction_id, is_winning=True
        ).exclude(id=bid.id).update(is_winning=False)

        # Update auction state
        auction.current_price = amount
        auction.bid_count += 1
        auction.winner_id = user_id
        await auction.save()

        # Auto-extend if bid in final minutes
        if auction.auto_extend:
            await _maybe_extend_auction(auction)

    # Outside transaction: broadcast to all watchers
    await broadcast_bid_update(auction_id, {
        "bid_id": bid.id,
        "amount": amount,
        "user_id": user_id,
        "bid_count": auction.bid_count,
        "current_price": amount,
        "end_time": auction.end_time.isoformat(),
    })

    return BidResponse(id=bid.id, amount=amount, is_winning=True)
```

## 6. Real-Time Architecture: Socket.IO

```python
# src/socket/server.py

import socketio
from src.config.redis import REDIS_URL

# Use Redis adapter for multi-instance deployment
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],  # Configured via FastAPI CORS
    client_manager=socketio.AsyncRedisManager(REDIS_URL),
)


@sio.event
async def connect(sid, environ, auth):
    """Authenticate WebSocket connection via JWT."""
    token = auth.get("token") if auth else None
    if not token:
        raise socketio.exceptions.ConnectionRefusedError("No token")
    # Validate JWT, store user_id in session
    user = await validate_token(token)
    await sio.save_session(sid, {"user_id": user.id})


@sio.event
async def join_auction(sid, data):
    """Join an auction room to receive live bid updates."""
    auction_id = data.get("auction_id")
    await sio.enter_room(sid, f"auction:{auction_id}")


@sio.event
async def leave_auction(sid, data):
    auction_id = data.get("auction_id")
    await sio.leave_room(sid, f"auction:{auction_id}")
```

```python
# src/socket/emitters.py

from src.socket.server import sio


async def broadcast_bid_update(auction_id: int, bid_data: dict):
    """Push bid update to all users watching this auction."""
    await sio.emit("bid_update", bid_data, room=f"auction:{auction_id}")


async def broadcast_auction_end(auction_id: int, result: dict):
    """Notify all watchers that auction has ended."""
    await sio.emit("auction_ended", result, room=f"auction:{auction_id}")
```

## 7. Docker Compose

```yaml
# docker-compose.yml

services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: auction
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: auction_db
      TZ: Asia/Taipei
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redisdata:/data
    ports:
      - "6379:6379"

  api:
    build: ./auction-api
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 5000
    environment:
      DATABASE_URL: postgres://auction:${DB_PASSWORD}@db:5432/auction_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
      MEILISEARCH_URL: http://search:7700
      MEILISEARCH_KEY: ${MEILI_KEY}
    depends_on:
      - db
      - redis
    ports:
      - "5001:5000"

  celery-worker:
    build: ./auction-api
    command: celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4
    environment:
      DATABASE_URL: postgres://auction:${DB_PASSWORD}@db:5432/auction_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

  celery-beat:
    build: ./auction-api
    command: celery -A src.tasks.celery_app beat --scheduler=redbeat.RedBeatScheduler --loglevel=info
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis

  search:
    image: getmeili/meilisearch:v1.12
    environment:
      MEILI_MASTER_KEY: ${MEILI_KEY}
      MEILI_ENV: development
    volumes:
      - meilidata:/meili_data
    ports:
      - "7700:7700"

  web:
    build: ./auction-web
    ports:
      - "3000:3000"
    depends_on:
      - api

volumes:
  pgdata:
  redisdata:
  meilidata:
```

## 8. Frontend Composable: Real-Time Bidding

```typescript
// src/composables/useBidding.ts

import { ref, computed, onUnmounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'
import type { Bid, AuctionLive } from '@/types/auction'

export function useBidding(auctionId: number) {
  const auth = useAuthStore()
  const socket = ref<Socket | null>(null)
  const currentPrice = ref(0)
  const bidCount = ref(0)
  const endTime = ref('')
  const recentBids = ref<Bid[]>([])
  const isConnected = ref(false)
  const bidError = ref('')

  const minBid = computed(() => currentPrice.value + bidIncrement.value)
  const bidIncrement = ref(0)

  function connect() {
    socket.value = io(import.meta.env.VITE_WS_URL, {
      auth: { token: auth.token },
    })

    socket.value.on('connect', () => {
      isConnected.value = true
      socket.value?.emit('join_auction', { auction_id: auctionId })
    })

    socket.value.on('bid_update', (data: AuctionLive) => {
      currentPrice.value = data.current_price
      bidCount.value = data.bid_count
      endTime.value = data.end_time
      recentBids.value.unshift({
        id: data.bid_id,
        amount: data.amount,
        user_id: data.user_id,
        created_at: new Date().toISOString(),
      })
    })

    socket.value.on('auction_ended', (result) => {
      // Handle auction end
    })

    socket.value.on('disconnect', () => {
      isConnected.value = false
    })
  }

  function disconnect() {
    socket.value?.emit('leave_auction', { auction_id: auctionId })
    socket.value?.disconnect()
  }

  onUnmounted(disconnect)

  return {
    connect,
    disconnect,
    currentPrice,
    bidCount,
    endTime,
    recentBids,
    isConnected,
    minBid,
    bidError,
  }
}
```

## 9. Payment Integration Pattern

```python
# src/services/payment_service.py
# Abstract payment gateway — swap ECPay/Stripe without touching business logic

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentRequest:
    order_id: str
    amount: float
    description: str
    buyer_email: str
    return_url: str


@dataclass
class PaymentResult:
    success: bool
    gateway_tx_id: str
    message: str


class PaymentGateway(ABC):
    @abstractmethod
    async def create_payment(self, request: PaymentRequest) -> str:
        """Returns payment URL for redirect."""
        ...

    @abstractmethod
    async def verify_callback(self, payload: dict) -> PaymentResult:
        """Verify payment gateway callback."""
        ...


class ECPayGateway(PaymentGateway):
    """ECPay (綠界) for Taiwan market."""

    async def create_payment(self, request: PaymentRequest) -> str:
        # ECPay AIO SDK integration
        ...

    async def verify_callback(self, payload: dict) -> PaymentResult:
        # Verify CheckMacValue
        ...


class StripeGateway(PaymentGateway):
    """Stripe for international market."""

    async def create_payment(self, request: PaymentRequest) -> str:
        # Stripe Checkout Session
        ...

    async def verify_callback(self, payload: dict) -> PaymentResult:
        # Verify webhook signature
        ...
```

## 10. Technology Decision Summary

### Keep from AERC (Proven, Team Knows It)

- Vue 3 + TypeScript + Vite
- Vuetify 3 (unless heavy custom branding needed)
- Pinia
- FastAPI + Uvicorn
- Tortoise ORM + Aerich + AsyncPG
- PostgreSQL 17
- JWT auth (python-jose + passlib)
- Docker Compose deployment
- Axios + interceptors pattern

### Add for Auction (New Requirements)

| Component | Technology | Why |
|-----------|-----------|-----|
| Real-time | **Socket.IO** (python-socketio + socket.io-client) | Room-based broadcasting, auto-reconnect, Redis adapter for scaling |
| Cache | **Redis 7** | Bid cache, pub/sub, rate limiting, session |
| Task Queue | **Celery + Redis** | Auction end triggers, async notifications, payment verification |
| Search | **Meilisearch** | Full-text search, faceted filtering, typo tolerance, lightweight |
| Image Storage | **MinIO** or cloud S3 | Object storage for auction images |

### Explicitly NOT Using

| Technology | Why Not |
|------------|---------|
| Next.js / Nuxt | Team has no React/Nuxt experience. Vue 3 SPA is sufficient |
| GraphQL | REST + WebSocket covers all needs. GraphQL adds complexity without clear benefit for this use case |
| MongoDB | Auction data is highly relational (bids → auctions → users → payments). PostgreSQL is the right choice |
| Kafka | Overkill for expected scale. Redis pub/sub handles inter-service messaging fine |
| Microservices | Start monolithic. Split only when actual scaling bottlenecks appear |
