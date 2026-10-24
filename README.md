# ColdChain 360 - Backend API

Production-grade FastAPI backend for the ColdChain 360 Multi-Modal Logistics & Telematics Platform.

## 🚀 Quick Local Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and configure your Supabase PostgreSQL connection:
   ```bash
   cp .env.example .env
   ```

4. **Seed Database (Initial Data)**:
   ```bash
   python seed.py
   ```

5. **Start Development Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 Deploying on Render (render.com)

1. Push this `backend/` folder to a separate GitHub repository (e.g., `coldchain360-backend`).
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Web Service**.
4. Connect your `coldchain360-backend` repository.
5. Render will automatically detect settings from `render.yaml` or use:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add your **Environment Variables** in Render:
   - `DATABASE_URL`: `postgresql://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres`
   - `SECRET_KEY`: (Click Generate or provide a random 32+ char string)
   - `BACKEND_CORS_ORIGINS`: `*` (or your frontend Vercel/Netlify URL)
   - `DEBUG`: `False`
7. Click **Create Web Service**. Your API will be live at `https://coldchain360-backend.onrender.com`!

---

## 🧪 Testing

Run automated tests:
```bash
python test_routes.py
python test_auth_deps.py
python tests/test_ai_intelligence.py
```
