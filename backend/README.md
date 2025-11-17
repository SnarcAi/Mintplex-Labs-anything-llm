# MissYak Social - Backend API

FastAPI-based backend for MissYak Social platform.

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── core/          # Core configuration, database, security
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic (LiveKit, storage)
│   └── main.py        # FastAPI application
├── migrations/        # Alembic migrations
├── seed_data.py       # Database seeding script
├── requirements.txt   # Python dependencies
└── .env.example       # Environment template
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Start PostgreSQL (if not using Docker)
# Create database
createdb missyak_social

# Or use Docker
docker run -d \
  --name missyak-postgres \
  -e POSTGRES_DB=missyak_social \
  -e POSTGRES_USER=missyak \
  -e POSTGRES_PASSWORD=missyak123 \
  -p 5432:5432 \
  postgres:15-alpine
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required settings**:
```env
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql+asyncpg://missyak:missyak123@localhost:5432/missyak_social
REDIS_URL=redis://localhost:6379/0
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
LIVEKIT_WS_URL=wss://your-project.livekit.cloud
```

### 4. Initialize Database

```bash
# Run migrations (creates tables)
# Note: For V1, we use init_db() in main.py
# For production, set up Alembic:
# alembic init migrations
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head

# Run the app to create tables
python -m app.main

# Seed demo data
python seed_data.py
```

### 5. Run Development Server

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the shortcut
python -m app.main
```

Server will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login with email/password |
| GET | `/api/v1/auth/me` | Get current user (auth required) |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/{user_id}` | Get user profile |
| PATCH | `/api/v1/users/me` | Update own profile (auth required) |

### Live Rooms

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/rooms` | Create new room (auth required) |
| POST | `/api/v1/rooms/{room_id}/start` | Start streaming (host only) |
| POST | `/api/v1/rooms/{room_id}/join` | Join as viewer (auth required) |
| POST | `/api/v1/rooms/{room_id}/end` | End room (host only) |
| GET | `/api/v1/rooms/live` | List currently live rooms |
| GET | `/api/v1/rooms/{room_id}` | Get room details |
| GET | `/api/v1/rooms/{room_id}/messages` | Get chat messages |
| POST | `/api/v1/rooms/{room_id}/messages` | Send chat message (auth required) |

### Recipes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/recipes` | Create recipe (auth required) |
| GET | `/api/v1/recipes?sort=latest\|top` | List recipes |
| GET | `/api/v1/recipes/{recipe_id}` | Get recipe details |
| POST | `/api/v1/recipes/{recipe_id}/like` | Like recipe (auth required) |
| DELETE | `/api/v1/recipes/{recipe_id}/like` | Unlike recipe (auth required) |

### Shop

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/shop/products?category=...` | List products |
| GET | `/api/v1/shop/products/{product_id}` | Get product details |

---

## 🗄️ Database Models

### User
- id (UUID)
- email (unique)
- password_hash
- display_name
- avatar_url
- bio
- grill_level (CAYLAK, AMATOR, USTA)
- created_at, updated_at

### LiveRoom
- id (UUID)
- host_user_id → users.id
- title
- description
- status (CREATED, LIVE, ENDED)
- provider_room_id (LiveKit room ID)
- created_at, started_at, ended_at

### LiveRoomMessage
- id (UUID)
- room_id → live_rooms.id
- user_id → users.id
- message_text
- created_at

### Recipe
- id (UUID)
- author_user_id → users.id
- title
- description
- image_url
- meat_type (KOFTE, BONFILE, BALIK, TAVUK, OTHER)
- difficulty (1-3)
- like_count
- created_at

### RecipeLike
- id (UUID)
- recipe_id → recipes.id
- user_id → users.id
- created_at
- UNIQUE(recipe_id, user_id)

### ShopProduct
- id (UUID)
- name
- description
- image_url
- price
- currency
- category (GRILL, FUEL, ACCESSORY, BUNDLE)
- external_url
- is_active
- created_at, updated_at

---

## 🔐 Authentication

### JWT Token Flow

1. User registers or logs in → receives JWT token
2. Client includes token in Authorization header: `Bearer <token>`
3. Protected endpoints verify token via `get_current_user` dependency
4. Token expires after 7 days (configurable)

### Example:

```python
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "display_name": "Mangal Ustası",
    ...
  }
}

# Use token in subsequent requests
GET /api/v1/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📹 LiveKit Integration

### Setup

1. Create account at https://livekit.io
2. Get API credentials from dashboard
3. Add to `.env`:
   ```env
   LIVEKIT_API_KEY=APIxxxxxxx
   LIVEKIT_API_SECRET=secretxxxxxxx
   LIVEKIT_WS_URL=wss://your-project.livekit.cloud
   ```

### How It Works

1. Host creates room → backend generates unique `provider_room_id`
2. Host starts room → backend returns LiveKit token with publish permissions
3. Viewers join → backend returns LiveKit token with subscribe-only permissions
4. Mobile app uses token to connect to LiveKit and stream video

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 🚀 Deployment

### Option 1: Docker

```bash
# Build image
docker build -t missyak-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  missyak-backend
```

### Option 2: Traditional Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=False

# Run with gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Production Checklist

- [ ] Use managed PostgreSQL (AWS RDS, etc.)
- [ ] Use managed Redis (ElastiCache, etc.)
- [ ] Set strong SECRET_KEY (32+ random chars)
- [ ] Configure CORS_ORIGINS for your domain
- [ ] Set up S3 for file uploads
- [ ] Enable SSL/HTTPS
- [ ] Set DEBUG=False
- [ ] Configure proper logging
- [ ] Set up monitoring (Sentry, etc.)
- [ ] Run migrations
- [ ] Seed product data

---

## 📦 Dependencies

Core:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **sqlalchemy** - ORM
- **asyncpg** - PostgreSQL async driver
- **redis** - Cache
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **livekit-api** - Video streaming SDK

Optional:
- **boto3** - AWS S3 uploads
- **alembic** - Database migrations
- **pytest** - Testing

---

## 🐛 Troubleshooting

### Database connection errors

```bash
# Check if PostgreSQL is running
psql -h localhost -U missyak -d missyak_social

# Check DATABASE_URL format
# Should be: postgresql+asyncpg://user:pass@host:port/dbname
```

### LiveKit errors

```bash
# Verify credentials
# Test at: https://livekit.io/dashboard

# Check room creation
# Enable debug logging in .env
DEBUG=True
```

### Import errors

```bash
# Make sure you're in the backend directory
cd backend

# Run with module syntax
python -m app.main

# Or add backend to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [LiveKit Server SDK](https://docs.livekit.io/server-sdk-python/)
- [Pydantic](https://docs.pydantic.dev/)

---

**Questions? Check the main [README](../README.md) or create an issue.**
