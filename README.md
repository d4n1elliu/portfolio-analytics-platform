# portfolio-analytics-platform

A full-stack web app for tracking portfolio holdings, performance and sector exposure, modelled on the kind of internal tool portfolio managers and analysts use at an investment fund.

> **Personal project.** This is a learning project built around a fictional fund. It contains no real client data, no real holdings, and is not affiliated with any investment firm.

## Status

Scaffold, database layer and core data model. The database has tables for securities, trades and prices, with a seed script for a starting set of securities. The backend exposes health checks for the API and the database, and the frontend displays whether it can reach the API. There are no feature endpoints yet.

## Tech stack

| Layer    | Technology                                                    |
| -------- | ------------------------------------------------------------- |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4                      |
| Backend  | Python, FastAPI, uvicorn, python-dotenv                       |
| Database | PostgreSQL on Neon, SQLAlchemy 2, Alembic, psycopg 3          |

## Project structure

```
backend/
  app/
    __init__.py       Marks app/ as a Python package
    main.py           FastAPI app, CORS config, health endpoints
    config.py         Loads .env and exposes settings such as DATABASE_URL
    database.py       Engine, session factory, Base class, get_db dependency
    models/
      __init__.py     Imports every model so Alembic can see all the tables
      common.py       Column types and columns shared by more than one model
      security.py     Security model (securities table)
      trade.py        Trade model (trades table) and the TradeSide values
      price.py        Price model (prices table)
  alembic/
    env.py            Connects Alembic to the app's database URL and models
    script.py.mako    Template used to generate new migration files
    versions/         Migration files, one per schema change
  scripts/
    seed.py           Inserts the starting set of securities
  alembic.ini         Alembic settings (no database URL is stored here)
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

## Data model

Three tables hold everything the analytics will be built on.

| Table        | One row is                       | Key columns                                                        |
| ------------ | -------------------------------- | ------------------------------------------------------------------ |
| `securities` | An instrument the fund can hold  | `ticker` (unique), `name`, `sector`, `asset_class`, `currency`     |
| `trades`     | One buy or sell of a security    | `security_id`, `trade_date`, `side`, `quantity`, `price`, `fees`   |
| `prices`     | One day's closing price          | `security_id`, `price_date`, `close`                               |

A security has many trades and many prices. The database enforces the basic rules itself: `side` must be `BUY` or `SELL`, quantities and prices must be greater than zero, fees cannot be negative, and a security can have only one closing price per day.

**Why there is no holdings table.** The current position in a security is calculated by adding up its trades (buys minus sells). Storing positions in a second table would mean keeping two copies of the same fact in sync, and any bug that updates one but not the other would leave them disagreeing. With the trade ledger as the single source of truth, a position can always be recalculated and can be worked out as at any past date.

**Why Numeric, not Float.** Money and quantity columns use exact decimal types. Floating-point numbers cannot represent values like 0.1 exactly, and the small errors add up across many trades.

| Column                                      | Type             | Reason                                                                 |
| ------------------------------------------- | ---------------- | ---------------------------------------------------------------------- |
| `trades.quantity`                           | `Numeric(18, 6)` | Allows fractional units as well as whole shares                        |
| `trades.price`, `prices.close`              | `Numeric(18, 6)` | Covers sub-cent prices and average fill prices with several decimals   |
| `trades.fees`                               | `Numeric(18, 2)` | A cash amount in dollars and cents                                     |

## Local setup

Prerequisites: Python 3.12+ and Node.js 20.19+.

Run the backend and frontend in two separate terminals.

### Database (Neon)

The backend needs a PostgreSQL database and will not start without `DATABASE_URL`.

1. Create a free project at https://neon.tech.
2. In the project dashboard, click **Connect** and copy the connection string. It starts with `postgresql://`.
3. Paste it unchanged as `DATABASE_URL` in `backend/.env` (created in the next step). The app selects the psycopg 3 driver itself.

Neon suspends a database after a few minutes without activity, so the first request after a pause takes around a second longer while it wakes up.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then set DATABASE_URL in .env
alembic upgrade head    # create the database tables
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000. Check it with:

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/health/db
# {"status":"ok","database":"connected"}
```

`/health` reports that the API process is up and does not touch the database. `/health/db` runs a query, and returns `503` if the database cannot be reached.

Interactive API docs are generated automatically at http://localhost:8000/docs.

### Database migrations

Schema changes are managed with Alembic. Run these from `backend/` with the virtual environment active.

| Command                                            | What it does                                                   |
| -------------------------------------------------- | -------------------------------------------------------------- |
| `alembic revision --autogenerate -m "add accounts"` | Creates a migration by comparing the models with the database |
| `alembic upgrade head`                             | Applies all migrations that have not been run yet              |
| `alembic downgrade -1`                             | Reverts the most recent migration                              |
| `alembic current`                                  | Shows which migration the database is on                       |
| `alembic history`                                  | Lists all migrations in order                                  |

Always read an autogenerated migration before applying it. Autogenerate does not detect everything, for example table or column renames, which it sees as a drop and an add.

### Seed data

After `alembic upgrade head` has created the tables, load the starting set of 10 ASX securities. Run this from `backend/` with the virtual environment active:

```bash
python -m scripts.seed
```

The script is safe to run more than once. A security whose ticker already exists is skipped, so no duplicates are created. It adds securities only, not trades or prices.

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
| `backend/.env.example`  | `DATABASE_URL`        | Neon PostgreSQL connection string (required)         |
| `backend/.env.example`  | `JWT_SECRET`          | Secret for signing auth tokens (not used yet)        |
| `backend/.env.example`  | `MARKET_DATA_API_KEY` | Market data provider API key (not used yet)          |
| `frontend/.env.example` | `VITE_API_URL`        | Backend base URL, defaults to `http://localhost:8000` |
