# portfolio-analytics-platform

[![CI](https://github.com/d4n1elliu/portfolio-analytics-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/d4n1elliu/portfolio-analytics-platform/actions/workflows/ci.yml)

**Live site:** https://portfolio-analytics.daniel-liu.dev

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
| Hosting  | Docker, Caddy, GitHub Actions, GitHub Container Registry      |

## Project structure

```
portfolio-analytics-platform/
├── .env.prod.example         Template for the server's settings
├── .gitignore
├── .nvmrc                    Node version for local use and CI
├── .python-version           Python version for local use and CI
├── docker-compose.prod.yml   Production setup that runs both containers
├── README.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml            Lint, tests, type check and Docker builds
│       └── deploy.yml        Publishes images and deploys after CI passes
│
├── frontend/
│   ├── src/
│   │   ├── api/              Typed calls to the backend such as trades
│   │   ├── components/       Shared components such as DataTable and Pagination
│   │   ├── hooks/            Data loading hooks such as useApiQuery
│   │   ├── lib/              Shared helpers such as date and currency formatting
│   │   ├── pages/            One component per screen such as TradesPage
│   │   ├── App.tsx           Root component
│   │   ├── config.ts         API address, locale, currency and page size
│   │   └── main.tsx          React entry point
│   ├── .dockerignore
│   ├── .env.example          Template for frontend environment variables
│   ├── .oxlintrc.json        Linter settings
│   ├── Caddyfile             Caddy settings for HTTPS and the /api proxy
│   ├── Dockerfile            Builds the app and serves it with Caddy
│   ├── index.html            HTML shell that Vite serves
│   ├── package-lock.json
│   ├── package.json          Dependencies and npm scripts
│   ├── tsconfig.app.json     TypeScript settings for the app code
│   ├── tsconfig.json         Points to the two TypeScript configs
│   ├── tsconfig.node.json    TypeScript settings for vite.config.ts
│   └── vite.config.ts        Vite settings with React and Tailwind plugins
│
└── backend/
    ├── alembic/              Migration setup and the files in versions/
    ├── app/
    │   ├── models/           Database tables such as Security and Trade
    │   ├── routes/           HTTP endpoints such as trades and securities
    │   ├── schemas/          Shapes of the JSON the API returns
    │   ├── services/         Business logic such as CSV parsing and import
    │   ├── config.py         Reads settings from environment variables
    │   ├── database.py       Engine, sessions and the get_db dependency
    │   └── main.py           FastAPI app, CORS and health endpoints
    ├── sample_data/          Example CSV files for the trade import
    ├── scripts/              One-off scripts such as seed.py
    ├── tests/                pytest tests such as CSV rules and health
    ├── .dockerignore
    ├── .env.example          Template for backend environment variables
    ├── alembic.ini           Alembic settings with no database URL
    ├── Dockerfile            Production image for the API
    ├── pytest.ini            pytest settings
    ├── requirements-dev.txt  Runtime packages plus test and lint tools
    ├── requirements.txt      Pinned packages the app needs to run
    └── ruff.toml             Linter settings
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

Prerequisites: Python 3.12+ and Node.js 24+.

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

## Deployment

The site runs on a VPS as two Docker containers. The database stays on Neon.

| Container | What it does |
| --------- | ------------ |
| `web`     | Caddy. Serves the built React app, gets the HTTPS certificate, and passes `/api/*` to the backend. The only container open to the internet |
| `backend` | The FastAPI app, run by uvicorn as a non-root user |

### How a change goes live

1. A pull request runs the CI workflow: lint, tests, type check and a build of both Docker images.
2. When the pull request is merged, CI runs again on `main`.
3. If it passes, the Deploy workflow builds both images and pushes them to the GitHub Container Registry, tagged with the commit.
4. The workflow then connects to the server over SSH, pulls those images, runs `alembic upgrade head`, and restarts the containers.
5. It finishes by checking `https://<domain>/api/health/db`. The run fails if the site does not come up healthy.

### One-time server setup

The server needs Docker with the Compose plugin, and ports 80 and 443 open.

1. Add the SSH user to the `docker` group.
2. Create the folder `~/portfolio-analytics` in that user's home folder.
3. Copy `.env.prod.example` to `~/portfolio-analytics/.env.prod` and fill in real values. `SITE_DOMAIN` must already point at the server.

The Deploy workflow needs these repository secrets:

| Secret            | Value |
| ----------------- | ----- |
| `SSH_HOST`        | Address of the server |
| `SSH_USER`        | User the workflow logs in as |
| `SSH_PRIVATE_KEY` | Private key for that user, used only for deploys |
| `SSH_KNOWN_HOSTS` | The server's host key, from `ssh-keyscan -t ed25519 <host>` |

### Running the production setup by hand

From the folder holding `docker-compose.prod.yml` and `.env.prod`:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f
```

To load the starting securities on a new database:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod run --rm backend python -m scripts.seed
```
