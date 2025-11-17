# 🔥 MissYak Social - V1 MVP

**A mobile-first social platform for grilling & rakı culture, integrated with MissYak product e-commerce.**

Built for a 3-person team to ship in 4-6 weeks.

---

## 📋 Overview

MissYak Social is a complete social platform where users can:

- 🔴 **Host & join live grill streams** (1 host + viewers with chat)
- 📖 **Share & discover recipes** (photos, descriptions, likes)
- 🛒 **Shop MissYak products** (bioethanol grills, fuel, accessories)
- 👤 **Create profiles** with grill skill levels (Çaylak / Amator / Usta)

---

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Video Streaming**: LiveKit Cloud integration
- **Storage**: S3-compatible (or local for dev)
- **Auth**: JWT-based authentication

### Frontend
- **Framework**: React Native (Expo)
- **Navigation**: React Navigation v6
- **State**: React Context API
- **Video**: LiveKit React Native SDK

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Redis
- Docker & Docker Compose (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone <repo-url>
cd MissFlora-_SnarcAi

# 2. Set up backend environment
cd backend
cp .env.example .env
# Edit .env with your LiveKit credentials and other settings

# 3. Start all services
cd ..
docker-compose up -d

# 4. Run database migrations and seed data
docker-compose exec backend python seed_data.py

# 5. Backend is now running at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Option 2: Manual Setup

See detailed instructions in:
- [Backend README](./backend/README.md)
- [Mobile README](./mobile/README.md)

---

## 📱 Mobile App Setup

```bash
cd mobile

# 1. Install dependencies
npm install

# 2. Update API URL in src/services/api.ts
# Change API_BASE_URL to your backend URL

# 3. Start Expo dev server
npm start

# 4. Run on device/emulator
npm run android  # For Android
npm run ios      # For iOS
```

---

## 🔑 Key Features (V1)

### ✅ Implemented

1. **Authentication**
   - Email/password registration & login
   - JWT token-based sessions
   - User profiles with avatars

2. **Live Streaming**
   - Create live grill rooms
   - Host video streaming (LiveKit)
   - Viewer mode (watch + text chat)
   - Real-time chat messages

3. **Recipe Feed**
   - Post recipes with photos
   - Browse latest/top recipes
   - Like/unlike recipes
   - Recipe details with author info

4. **Shop**
   - Product catalog (grills, fuel, accessories, bundles)
   - Category filtering
   - External checkout links
   - Product detail pages

5. **User Profiles**
   - Grill skill levels (CAYLAK, AMATOR, USTA)
   - Bio and avatar
   - Account management

### 🔮 Planned for V2+

- Multi-host rooms (4-way video)
- Location-based "Mangal Radar"
- Gamification (XP, badges, leaderboards)
- In-app payments
- Content moderation
- Push notifications
- Recipe search & filters
- User following/followers

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Auth
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

#### Live Rooms
- `GET /api/v1/rooms/live` - List live rooms
- `POST /api/v1/rooms` - Create room
- `POST /api/v1/rooms/{id}/start` - Start streaming
- `POST /api/v1/rooms/{id}/join` - Join as viewer
- `POST /api/v1/rooms/{id}/end` - End room
- `GET /api/v1/rooms/{id}/messages` - Get chat messages
- `POST /api/v1/rooms/{id}/messages` - Send message

#### Recipes
- `GET /api/v1/recipes?sort=latest|top` - List recipes
- `POST /api/v1/recipes` - Create recipe
- `GET /api/v1/recipes/{id}` - Get recipe detail
- `POST /api/v1/recipes/{id}/like` - Like recipe
- `DELETE /api/v1/recipes/{id}/like` - Unlike recipe

#### Shop
- `GET /api/v1/shop/products?category=...` - List products
- `GET /api/v1/shop/products/{id}` - Get product detail

---

## 🧪 Testing

### Backend

```bash
cd backend

# Run tests (when implemented)
pytest

# Check code quality
black app/
```

### Mobile

```bash
cd mobile

# Type checking
npx tsc --noEmit

# Linting
npx eslint .
```

---

## 🔐 Environment Variables

### Backend (.env)

Required variables:
```env
SECRET_KEY=<random-32-char-string>
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/missyak_social
REDIS_URL=redis://localhost:6379/0

# LiveKit (get from livekit.io)
LIVEKIT_API_KEY=<your-api-key>
LIVEKIT_API_SECRET=<your-api-secret>
LIVEKIT_WS_URL=wss://your-project.livekit.cloud

# Optional: S3 for production
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
S3_BUCKET_NAME=missyak-social
```

See `backend/.env.example` for all options.

---

## 🗄️ Database Schema

Key tables:

- **users** - User accounts and profiles
- **live_rooms** - Live streaming rooms
- **live_room_messages** - Chat messages
- **recipes** - User-posted recipes
- **recipe_likes** - Recipe likes
- **shop_products** - Product catalog

See `backend/app/models/` for detailed schema.

---

## 📦 Deployment

### Backend (Production)

1. **Use managed PostgreSQL** (AWS RDS, DigitalOcean, etc.)
2. **Use managed Redis** (AWS ElastiCache, Redis Cloud, etc.)
3. **Set up LiveKit Cloud** (https://livekit.io)
4. **Deploy backend** to:
   - AWS ECS/Fargate
   - DigitalOcean App Platform
   - Heroku
   - Railway.app

5. **Configure S3** for file uploads
6. **Set environment variables** in production
7. **Run migrations**: `alembic upgrade head`
8. **Seed products**: `python seed_data.py`

### Mobile (Production)

```bash
cd mobile

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios

# Submit to stores
eas submit
```

See Expo EAS documentation: https://docs.expo.dev/eas/

---

## 👥 Team & Contribution

This project is designed for a 3-person team:

1. **Founder** - Product vision, business logic
2. **18-year-old genius** - Mobile app development
3. **72-year-old hacker** - Backend & infrastructure

### Development Workflow

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add feature X"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request
6. Review & merge

---

## 🛠️ Tech Stack Details

### Backend Dependencies
- fastapi - Web framework
- sqlalchemy - ORM
- asyncpg - PostgreSQL driver
- redis - Cache
- livekit-api - Video streaming
- python-jose - JWT handling
- passlib - Password hashing
- boto3 - S3 uploads

### Mobile Dependencies
- expo - React Native framework
- react-navigation - Navigation
- @livekit/react-native - Video streaming
- axios - HTTP client
- @react-native-async-storage - Local storage

---

## 📖 Documentation

- [Backend Documentation](./backend/README.md)
- [Mobile Documentation](./mobile/README.md)
- [API Reference](http://localhost:8000/docs) (when running)

---

## 🐛 Known Issues & Limitations (V1)

1. **LiveKit integration** - Requires LiveKit Cloud account (free tier available)
2. **Image uploads** - Currently uses URLs; need to implement upload endpoint for V2
3. **Real-time chat** - Currently REST polling; WebSocket planned for V2
4. **No push notifications** - Planned for V2
5. **Basic error handling** - Will improve in V2

---

## 📄 License

Proprietary - MissYak © 2025

---

## 🙏 Support

For questions or issues:
- Create an issue in this repository
- Contact: team@missyak.com

---

**Built with ❤️ and 🔥 by the MissYak team**
