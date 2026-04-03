# Quick Start Validation Guide

This guide helps you quickly validate the AssistGen refactored system.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] MySQL 8.0+ installed (or Docker)
- [ ] Git installed

## Quick Validation Steps

### Step 1: Environment Setup (5-10 minutes)

```bash
# Navigate to project directory
cd assistgen-refactored

# Run automated setup script
./scripts/setup_dev.sh

# Or manually:
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Step 2: Configuration (2-3 minutes)

```bash
# Backend configuration
cd backend
cp .env.example .env
# Edit .env and set:
# - DATABASE_URL (MySQL connection)
# - SECRET_KEY (generate a random string)
# - DEEPSEEK_API_KEY (if you have one)

# Frontend configuration
cd ../frontend
cp .env.example .env
# Edit .env and set:
# - VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Database Setup (2-3 minutes)

**Option A: Using Docker (Recommended)**
```bash
cd assistgen-refactored
docker-compose up -d database redis
```

**Option B: Manual MySQL Setup**
```sql
CREATE DATABASE assistgen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'assistgen_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON assistgen.* TO 'assistgen_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 4: Start Services (1 minute)

**Terminal 1 - Backend:**
```bash
cd assistgen-refactored/backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd assistgen-refactored/frontend
npm run dev
```

### Step 5: Validation Tests (5 minutes)

#### Test 1: Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"AssistGen","version":"2.0.0"}
```

#### Test 2: API Documentation
Open in browser: http://localhost:8000/api/docs
- [ ] Swagger UI loads
- [ ] All endpoints are listed
- [ ] Documentation is readable

#### Test 3: Frontend Access
Open in browser: http://localhost:5173
- [ ] Frontend loads without errors
- [ ] Login page is visible
- [ ] UI is responsive

#### Test 4: User Registration (Optional - requires database)
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'
```

#### Test 5: Frontend-Backend Integration
1. Open frontend: http://localhost:5173
2. Try to register a new user
3. Try to login
4. Check browser console for errors

## Validation Checklist

### Project Structure ✅
- [ ] All directories exist (`backend/`, `frontend/`, `docs/`, `tests/`, `config/`, `scripts/`)
- [ ] Backend has proper structure (`app/api/`, `app/core/`, `app/models/`, `app/schemas/`, `app/services/`)
- [ ] Frontend has proper structure (`src/api/`, `src/stores/`, `src/views/`, `src/styles/`)

### Configuration ✅
- [ ] `backend/.env.example` exists
- [ ] `frontend/.env.example` exists
- [ ] `config/development.env.example` exists
- [ ] `config/production.env.example` exists
- [ ] `docker-compose.yml` exists

### Documentation ✅
- [ ] Main `README.md` is comprehensive
- [ ] API documentation exists (`docs/api/README.md`)
- [ ] Database documentation exists (`docs/database/README.md`)
- [ ] Architecture documentation exists (`docs/architecture/README.md`)
- [ ] Deployment guide exists (`docs/deployment/README.md`)
- [ ] Migration guide exists (`docs/migration/README.md`)

### Code Quality ✅
- [ ] All Python files have docstrings
- [ ] All functions have parameter documentation
- [ ] API endpoints have request/response documentation
- [ ] Error handling is implemented
- [ ] Security best practices followed

### Runtime Validation ⚠️
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] API documentation is accessible
- [ ] Frontend UI loads correctly
- [ ] Health check endpoint works
- [ ] User registration works (if database configured)
- [ ] Authentication works (if database configured)

## Common Issues and Solutions

### Issue: "Module not found" errors
**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Database connection failed"
**Solution:** Check DATABASE_URL in `.env` and ensure MySQL is running:
```bash
# Check MySQL status
mysql -u root -p -e "SHOW DATABASES;"

# Or start Docker database
docker-compose up -d database
```

### Issue: "Port already in use"
**Solution:** Change port in configuration or stop the process using the port:
```bash
# Backend: Change PORT in .env
# Frontend: Change port in vite.config.ts
```

### Issue: "CORS errors in browser"
**Solution:** Ensure CORS_ORIGINS in backend `.env` includes frontend URL:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Quick Test Commands

```bash
# Run system validation
python scripts/validate_system.py

# Run backend tests (if tests are written)
cd backend
pytest

# Run frontend tests (if tests are written)
cd frontend
npm test

# Check code quality
cd backend
python scripts/validate_quality.py
```

## Success Criteria

The system is validated when:

1. ✅ All project structure checks pass
2. ✅ All configuration files exist
3. ✅ All documentation is complete
4. ✅ Backend starts without errors
5. ✅ Frontend starts without errors
6. ✅ API documentation is accessible
7. ✅ Frontend UI loads correctly
8. ✅ Health check endpoint responds

## Next Steps After Validation

1. **Review Documentation:**
   - Read `README.md` for full project overview
   - Review `docs/api/README.md` for API details
   - Check `docs/deployment/README.md` for production deployment

2. **Configure for Your Environment:**
   - Set up actual database credentials
   - Configure LLM API keys (DeepSeek, Ollama)
   - Set up Redis for caching (optional)

3. **Test Core Functionality:**
   - User registration and authentication
   - Conversation creation and management
   - Chat functionality (requires LLM API key)

4. **Deploy to Production:**
   - Follow `docs/deployment/README.md`
   - Use Docker Compose for containerized deployment
   - Set up monitoring and logging

## Support

For issues or questions:
- Check `VALIDATION_REPORT.md` for detailed validation results
- Review documentation in `docs/` directory
- Check `docs/deployment/README.md` for troubleshooting

---

**Estimated Time:** 15-20 minutes for complete validation
**Difficulty:** Beginner to Intermediate
**Prerequisites:** Basic command line knowledge, Python and Node.js installed
