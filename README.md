# portfolio-analytics-platform

A full-stack web app for tracking portfolio holdings, performance and sector exposure, modelled on the kind of internal tool portfolio managers and analysts use at an investment fund.

> **Personal project.** This is a learning project built around a fictional fund. It contains no real client data, no real holdings, and is not affiliated with any investment firm.

## Status

Project scaffold only. The backend exposes a health check and the frontend displays whether it can reach the API. No features are built yet.

## Tech stack

| Layer    | Technology                                                    |
| -------- | ------------------------------------------------------------- |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4                      |
| Backend  | Python, FastAPI, uvicorn, python-dotenv                       |
| Database | PostgreSQL on Neon with SQLAlchemy and Alembic                |

## Project structure

```
backend/
  app/
    __init__.py       Marks app/ as a Python package
    main.py           FastAPI app, CORS config, GET /health
  requirements.txt    Pinned Python dependencies
  .env.example        Template for backend environment variables
frontend/
  src/
    main.tsx          React entry point
    App.tsx           Root component with the API status check
    index.css         Tailwind CSS import
  index.html          HTML shell that Vite serves
  vite.config.ts      Vite config (React and Tailwind plugins)
  .env.example        Template for frontend environment variables
```

## Local setup

Prerequisites: Python 3.12+ and Node.js 20.19+.

Run the backend and frontend in two separate terminals.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000. Check it with:

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Interactive API docs are generated automatically at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app runs at http://localhost:5173 and shows `API status: ok` when the backend is running.

### Environment variables

Real `.env` files are git-ignored and must never be committed. The `.env.example` files list the variables each side expects, with placeholder values only.

| File                    | Variable              | Purpose                                              |
| ----------------------- | --------------------- | ---------------------------------------------------- |
| `backend/.env.example`  | `DATABASE_URL`        | PostgreSQL connection string (not used yet)          |
| `backend/.env.example`  | `JWT_SECRET`          | Secret for signing auth tokens (not used yet)        |
| `backend/.env.example`  | `MARKET_DATA_API_KEY` | Market data provider API key (not used yet)          |
| `frontend/.env.example` | `VITE_API_URL`        | Backend base URL, defaults to `http://localhost:8000` |
