# portfolio-analytics-platform

A full-stack web app for tracking portfolio holdings, performance and sector exposure, modelled on the kind of internal tool portfolio managers and analysts use at an investment fund.

> **Personal project.** This is a learning project built around a fictional fund. It contains no real client data, no real holdings, and is not affiliated with any investment firm.

## Status

The first feature is in place: trades can be imported from a CSV file and viewed in a table. The database has tables for securities, trades and prices, with a seed script for a starting set of securities. Holdings, prices, charts and authentication are not built yet.

## Tech stack

| Layer    | Technology                                                    |
| -------- | ------------------------------------------------------------- |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4                      |
| Backend  | Python, FastAPI, uvicorn, python-dotenv, pytest               |
| Database | PostgreSQL on Neon, SQLAlchemy 2, Alembic, psycopg 3          |

## Project structure

```
backend/
  app/
    main.py           FastAPI app, CORS config, health endpoints, router registration
    config.py         Loads .env and exposes settings such as DATABASE_URL
    database.py       Engine, session factory, Base class, get_db dependency
    models/           Database tables: Security, Trade, Price
    routes/           HTTP endpoints. Read the request, call a service, return the response
      dependencies.py Shared paging and CSV upload handling
      errors.py       Turns import errors into HTTP responses for every endpoint
    schemas/          Pydantic shapes of the JSON the API returns
      common.py       Shapes shared by endpoints: Page, ImportResult, ImportRejected
    services/         Business logic. No HTTP code
      csv_parsing.py  Reads and checks any CSV file (shared by all imports)
      trade_csv.py    The rules for one row of a trades CSV
      trade_import.py Saves a validated trades CSV in one transaction
      market_time.py  Today's date in the market's time zone
      trades.py       Queries for listing trades
      securities.py   Queries for listing securities
  alembic/            Migration setup and the migration files in versions/
  scripts/seed.py     Inserts the starting set of securities
  sample_data/        Example CSV files for the trade import
  tests/              pytest unit tests
  alembic.ini         Alembic settings (no database URL is stored here)
  pytest.ini          pytest settings
  requirements.txt    Pinned dependencies the app needs to run
  requirements-dev.txt  The same, plus the test and lint tools
  ruff.toml           Linter settings
  .env.example        Template for backend environment variables
frontend/
  src/
    main.tsx          React entry point
    App.tsx           Root component
    config.ts         App-wide settings: API address, locale, currency, page size
    api/              The only code that calls the backend, with typed functions per endpoint
    hooks/            useApiQuery: loads data and tracks loading and error states
    lib/format.ts     Shared date, currency, quantity and count formatting
    pages/            One component per screen (TradesPage)
    components/       Reusable pieces: Button, Alert, Card, PageLayout, DataTable,
                      Pagination, CsvImportForm, and TradeTable built on DataTable
    index.css         Tailwind CSS import
  index.html          HTML shell that Vite serves
  vite.config.ts      Vite config (React and Tailwind plugins)
  .env.example        Template for frontend environment variables
```

A request flows through the backend in one direction: a route calls a service, and a service uses the models. Routes contain no business rules and services contain no HTTP code, so each can be changed and tested separately.

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

## API

| Method | Path             | What it does                                                    |
| ------ | ---------------- | --------------------------------------------------------------- |
| `GET`  | `/health`        | Confirms the API is running                                     |
| `GET`  | `/health/db`     | Confirms the API can reach the database                         |
| `GET`  | `/securities`    | Lists every security, ordered by ticker                         |
| `GET`  | `/trades`        | Lists trades, newest first, with the ticker and security name   |
| `POST` | `/trades/import` | Imports trades from a CSV file                                  |

`GET /trades` takes `limit` (1 to 500, default 50) and `offset` (default 0), and returns `{"items": [...], "total": 30, "limit": 50, "offset": 0}`. Decimal values are returned as strings, such as `"45.250000"`, so no precision is lost.

The interactive docs at http://localhost:8000/docs list every endpoint and let you try them.

### Importing trades from CSV

`POST /trades/import` takes a multipart upload with the file in a field named `file`:

```bash
curl -F "file=@sample_data/trades_sample.csv" http://localhost:8000/trades/import
# {"imported":30}
```

The first row of the file must be a header. Column order does not matter and extra columns are ignored.

| Column       | Required | Rules                                                              |
| ------------ | -------- | ------------------------------------------------------------------ |
| `trade_date` | Yes      | `YYYY-MM-DD`, not in the future (in the market's time zone)        |
| `ticker`     | Yes      | Must match a security in the database. Case-insensitive            |
| `side`       | Yes      | `BUY` or `SELL`. Case-insensitive                                  |
| `quantity`   | Yes      | Greater than 0, at most 6 decimal places                           |
| `price`      | Yes      | Greater than 0, at most 6 decimal places                           |
| `fees`       | No       | 0 or more, at most 2 decimal places. Defaults to 0 if left out     |

Numbers must be plain digits with an optional decimal point, such as `1500` or `45.25`. Thousands separators and currency symbols are rejected.

```csv
trade_date,ticker,side,quantity,price,fees
2026-03-10,BHP,BUY,400,41.85,29.95
2026-03-17,TLS,SELL,1500,4.385,19.95
```

**The import is all or nothing.** Every row is checked before anything is saved. If any row is invalid, no trades are saved and the response lists every problem, so the file can be fixed and uploaded again without creating a partial import.

| Status | Meaning                                                                                      |
| ------ | -------------------------------------------------------------------------------------------- |
| `201`  | Every row was saved. The body is `{"imported": <count>}`                                     |
| `400`  | The file is not a readable trades CSV: wrong extension, empty, missing a required column, or more than 5000 rows |
| `413`  | The file is larger than 1 MB                                                                 |
| `422`  | One or more rows are invalid. Nothing was saved                                              |

A `422` response lists each problem with its row number (the header is row 1), the column, and a message:

```json
{
  "detail": "The import was rejected and nothing was saved. Fix 2 errors and upload the file again.",
  "errors": [
    {"row": 4, "column": "ticker", "message": "'XYZ' is not a known security."},
    {"row": 6, "column": "quantity", "message": "quantity must be greater than 0."}
  ]
}
```

Two example files are in `backend/sample_data/`: `trades_sample.csv` (30 valid trades) and `trades_invalid.csv` (rows that each break a different rule).

### Known limitations

- **Importing the same file twice creates duplicate trades.** The import has no way to tell a repeated upload from two genuine trades with the same details.
- **Sells are not checked against holdings.** A file can sell more of a security than was ever bought, because positions are not calculated yet.

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
pip install -r requirements-dev.txt
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

### Tests

Run the backend tests from `backend/` with the virtual environment active:

```bash
pytest
```

The tests cover the CSV validation rules. They do not connect to a database, so they run without a `.env` file.

### Linting

Check the backend code for common mistakes from `backend/`:

```bash
ruff check .
```

The settings are in `backend/ruff.toml`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app runs at http://localhost:5173. It shows the Trades page, where you can upload a CSV file and see the saved trades. The backend must be running for it to load data.

### Environment variables

Real `.env` files are git-ignored and must never be committed. The `.env.example` files list the variables each side expects, with placeholder values only.

| File                    | Variable              | Purpose                                              |
| ----------------------- | --------------------- | ---------------------------------------------------- |
| `backend/.env.example`  | `DATABASE_URL`        | Neon PostgreSQL connection string (required)         |
| `backend/.env.example`  | `JWT_SECRET`          | Secret for signing auth tokens (not used yet)        |
| `backend/.env.example`  | `MARKET_DATA_API_KEY` | Market data provider API key (not used yet)          |
| `backend/.env.example`  | `CORS_ORIGINS`        | Optional. Comma-separated addresses allowed to call the API. Defaults to `http://localhost:5173` |
| `backend/.env.example`  | `MARKET_TIMEZONE`     | Optional. Time zone that decides "today" for trade dates. Defaults to `Australia/Sydney` |
| `backend/.env.example`  | `IMPORT_MAX_FILE_BYTES`, `IMPORT_MAX_ROWS` | Optional. CSV upload limits. Default to 1 MB and 5000 rows |
| `backend/.env.example`  | `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` | Optional. Page sizes for list endpoints. Default to 50 and 500 |
| `frontend/.env.example` | `VITE_API_URL`        | Backend base URL, defaults to `http://localhost:8000` |
