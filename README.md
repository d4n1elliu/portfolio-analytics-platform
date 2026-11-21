# portfolio-analytics-platform

[![CI](https://github.com/d4n1elliu/portfolio-analytics-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/d4n1elliu/portfolio-analytics-platform/actions/workflows/ci.yml)

**Live site:** https://portfolio-analytics.daniel-liu.dev

A full-stack web app for tracking portfolio holdings, performance and sector exposure, modelled on the kind of internal tool portfolio managers and analysts use at an investment fund.

> **Personal project.** This is a learning project built around a fictional fund. It contains no real client data, no real holdings, and is not affiliated with any investment firm.

## Status

Four features are in place:

- **Trades.** Trades can be imported from a CSV file and viewed in a table.
- **Holdings.** The Holdings page shows the fund's current positions, calculated from those trades.
- **Prices and valuation.** Daily closing prices are stored for each security and refreshed on weekdays. The Holdings page uses them to show what each position is worth, and the Dashboard page shows the portfolio's value, its unrealised profit, and three charts.
- **Login and roles.** Every page needs a sign in, and each account has a role that decides what it can do.

## Tech stack

| Layer    | Technology                                                    |
| -------- | ------------------------------------------------------------- |
| Frontend | React, TypeScript, Vite, Tailwind CSS v4, ECharts             |
| Backend  | Python, FastAPI, uvicorn, python-dotenv, pytest, yfinance, argon2-cffi, PyJWT |
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
│       ├── deploy.yml        Publishes images and deploys after CI passes
│       └── refresh-prices.yml  Fetches closing prices on weekdays
│
├── frontend/
│   ├── public/               Files served as they are, such as the favicon
│   ├── src/
│   │   ├── api/              Typed calls to the backend such as holdings
│   │   ├── components/       Shared components such as DataTable and Chart
│   │   ├── hooks/            Shared hooks such as useApiQuery and useSignInAttempt
│   │   ├── lib/              Helpers such as formatting and chart colours
│   │   ├── pages/            One component per screen such as DashboardPage
│   │   ├── App.tsx           Root component and page routes
│   │   ├── config.ts         API address, locale, currency and page size
│   │   ├── main.tsx          React entry point
│   │   └── routes.ts         Address of each page
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
    │   ├── models/           Database tables such as Security, Trade and User
    │   ├── routes/           HTTP endpoints such as holdings and auth
    │   ├── schemas/          Shapes of the JSON the API returns
    │   ├── services/         Business logic such as positions and valuation
    │   ├── config.py         Reads settings from environment variables
    │   ├── database.py       Engine, sessions and the get_db dependency
    │   └── main.py           FastAPI app, CORS and health endpoints
    ├── jobs/                 Price jobs that run outside the API
    ├── sample_data/          Example trade files and a year of closing prices
    ├── scripts/              One-off scripts such as seed.py and seed_users.py
    ├── tests/                pytest tests such as positions and valuation
    ├── .dockerignore
    ├── .env.example          Template for backend environment variables
    ├── alembic.ini           Alembic settings with no database URL
    ├── Dockerfile            Production image for the API
    ├── pytest.ini            pytest settings
    ├── requirements-dev.txt  Runtime packages plus test and lint tools
    ├── requirements-jobs.txt Runtime packages plus those the price jobs need
    ├── requirements.txt      Pinned packages the app needs to run
    └── ruff.toml             Linter settings
```

A request flows through the backend in one direction: a route calls a service, and a service uses the models. Routes contain no business rules and services contain no HTTP code, so each can be changed and tested separately.

## Data model

Four tables hold the data.

| Table        | One row is                       | Key columns                                                        |
| ------------ | -------------------------------- | ------------------------------------------------------------------ |
| `securities` | An instrument the fund can hold  | `ticker` (unique), `name`, `sector`, `asset_class`, `currency`     |
| `trades`     | One buy or sell of a security    | `security_id`, `trade_date`, `side`, `quantity`, `price`, `fees`   |
| `prices`     | One day's closing price          | `security_id`, `price_date`, `close`                               |
| `users`      | A person who can sign in         | `email` (unique), `name`, `password_hash`, `role`, `is_active`     |

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
| `POST` | `/auth/login`    | Signs in with an email and password                             |
| `POST` | `/auth/logout`   | Signs out                                                       |
| `GET`  | `/auth/me`       | Returns the signed-in user                                      |
| `GET`  | `/holdings`      | Lists the current position in each security, ordered by ticker  |
| `GET`  | `/portfolio/history` | Lists the value of the portfolio on each priced date, oldest first |
| `GET`  | `/portfolio/performance` | Returns the portfolio's return over 1 month, 3 months, year to date, 1 year and since inception |
| `GET`  | `/securities`    | Lists every security, ordered by ticker                         |
| `GET`  | `/trades`        | Lists trades, newest first, with the ticker and security name   |
| `POST` | `/trades/import` | Imports trades from a CSV file                                  |

Every endpoint below `/auth/me` needs a sign in. See [Login and roles](#login-and-roles).

`GET /trades` takes `limit` (1 to 500, default 50) and `offset` (default 0), and returns `{"items": [...], "total": 30, "limit": 50, "offset": 0}`. Decimal values are returned as strings, such as `"45.250000"`, so no precision is lost.

`GET /holdings` returns one item per security that has trades, with `ticker`, `security_name`, `sector`, `asset_class`, `currency`, `quantity`, `average_cost`, `cost_basis`, `realised_pnl` and `oversold_quantity`, plus the valuation fields described under [Prices and valuation](#prices-and-valuation). Positions that have been fully sold are left out unless `include_closed=true` is added.

The interactive docs at http://localhost:8000/docs list every endpoint and let you try them.

### Login and roles

Every page needs a sign in. There is no sign-up: accounts are created by a seed script.

| Role              | Can view everything | Can import trades |
| ----------------- | ------------------- | ----------------- |
| Operations        | Yes                 | Yes               |
| Portfolio Manager | Yes                 | No                |
| Analyst           | Yes                 | No                |

Signing in sets a cookie that lasts 8 hours. After 10 failed attempts, sign-ins from that address are blocked for up to 15 minutes.

The seed script creates one demo account per role: `operations@example.com`, `pm@example.com` and `analyst@example.com`. Their passwords are chosen when the script is run and are not stored in this repository.

Not included: sign-up, password reset, email verification and account management.

### Holdings and average cost

Positions are worked out from the trades on every request, using the weighted average cost method:

- **A buy** adds `quantity × price + fees` to the cost basis. The average cost is the cost basis divided by the quantity held, so a buy changes it.
- **A sell** removes units at the current average cost, so it does not change the average. The realised profit or loss is what the sale brought in, less its fees, minus the cost of the units sold.
- Trades are applied oldest first. Trades on the same day are applied in the order they were imported.
- The calculation uses exact decimals and is not rounded. The response rounds money to cents and average cost to six decimal places.

For example, the three BHP trades in `sample_data/trades_sample.csv`:

| Trade                          | Quantity | Cost basis | Average cost | Realised P&L |
| ------------------------------ | -------- | ---------- | ------------ | ------------ |
| Buy 400 at 41.85, fees 29.95   | 400      | 16,769.95  | 41.924875    | 0            |
| Buy 200 at 43.10, fees 19.95   | 600      | 25,409.90  | 42.349833    | 0            |
| Sell 250 at 45.72, fees 29.95  | 350      | 14,822.44  | 42.349833    | 812.59       |

The sell brings in `250 × 45.72 − 29.95 = 11,400.05`. The 250 units cost `250 × 42.349833 = 10,587.46`, so the realised profit is `812.59`.

**Sells that exceed the position.** The import does not check a sell against what is held. A sell is applied only to the units actually held, the quantity stops at zero, and the rest is reported as `oversold_quantity`. An oversold position is always returned, even when closed, and the Holdings page shows a warning naming the security.

### Prices and valuation

The database stores one closing price per security per day. Each open position is valued at its latest stored price, and `GET /holdings` returns:

| Field               | Meaning                                              |
| ------------------- | ---------------------------------------------------- |
| `last_price`        | The latest stored closing price                      |
| `price_date`        | The day that price is from                           |
| `market_value`      | `quantity × last_price`                              |
| `unrealised_pnl`    | `market_value − cost_basis`                          |
| `unrealised_return` | `unrealised_pnl ÷ cost_basis`, as a fraction         |
| `weight`            | The holding's share of the total market value        |

These fields are `null` for a closed position or a security with no stored price.

Prices come from Yahoo Finance and are saved by a job that runs outside the API. The pages only read stored prices, so they keep working if Yahoo is unavailable.

### Portfolio value over time

`GET /portfolio/history` returns the value of the portfolio on each day that has a price, oldest first:

```json
[
  {"date": "2026-11-12", "market_value": "197787.90", "cost_basis": "173658.10", "unrealised_pnl": "24129.80"},
  {"date": "2026-11-13", "market_value": "196592.45", "cost_basis": "173658.10", "unrealised_pnl": "22934.35"}
]
```

Each point counts the trades made up to that day and values them at that day's prices. A security with no price yet is left out.

### Portfolio performance

`GET /portfolio/performance` returns a time-weighted return. Each day's gain is measured on the value held at the start of that day, so money going in or out does not count as a gain or a loss. A buy counts as cash in at its cost and fees, and a sell as cash out at its proceeds after fees.

A period has no return when the price history does not reach back to its start. Dividends are not counted.

### Importing trades from CSV

`POST /trades/import` takes a multipart upload with the file in a field named `file`:

```bash
curl -b cookies.txt -F "file=@sample_data/trades_sample.csv" http://localhost:8000/trades/import
# {"imported":30}
```

Only the Operations role can import, so this needs that account's session cookie.

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
- **Sells are not checked against holdings on import.** A file can sell more of a security than was ever bought. The position is then reported as oversold instead of the import being rejected.
- **Every trade is read on each `/holdings` request.** This is fine at the current size and would need revisiting for a much larger ledger.
- **Prices are daily closing prices for ASX tickers only.** There are no intraday prices.
- **Dividends are not counted.** Profit is the change in price only.
- **Currencies are not converted.** The Dashboard shows a warning instead of totals if positions use more than one currency.
- **Signing out does not cancel the session.** A copied session cookie would work until it expires.
- **The stale price warning does not know public holidays.** It counts Monday to Friday as business days, so it can appear a day early after a long weekend.

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

Then load a year of closing prices for those securities. This needs no network and is also safe to run more than once:

```bash
python -m jobs.seed_prices
```

Last, create the three demo accounts. Add a password of at least 12 characters for each to `backend/.env`:

```
DEMO_PASSWORD_OPERATIONS=...
DEMO_PASSWORD_PORTFOLIO_MANAGER=...
DEMO_PASSWORD_ANALYST=...
```

```bash
python -m scripts.seed_users
```

An account that already exists is skipped.

### Refreshing prices

To fetch the latest closing prices from Yahoo Finance:

```bash
pip install -r requirements-jobs.txt
python -m jobs.refresh_prices
```

### Tests

Run the backend tests from `backend/` with the virtual environment active:

```bash
pytest
```

The tests cover the CSV rules, positions, valuation, price refresh and portfolio history. They do not use a database or the network, so they run without a `.env` file.

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

The app runs at http://localhost:5173. It opens on a sign in page and has three pages after that. The backend must be running.

| Page      | What it shows |
| --------- | ------------- |
| Dashboard | Market value, unrealised P&L and unrealised return, the return over each period, and charts of portfolio value over time, sector allocation and unrealised P&L by holding |
| Holdings  | The current positions with their last price, market value, unrealised P&L and weight. Has sorting, a search box, filters for sector and asset class, summary figures, and a warning when prices are more than three business days old |
| Trades    | A form to upload a CSV file, and the saved trades |

### Environment variables

Real `.env` files are git-ignored and must never be committed. The `.env.example` files list the variables each side expects, with placeholder values only.

| File                    | Variable              | Purpose                                              |
| ----------------------- | --------------------- | ---------------------------------------------------- |
| `backend/.env.example`  | `DATABASE_URL`        | Neon PostgreSQL connection string (required)         |
| `backend/.env.example`  | `JWT_SECRET`          | Secret for signing session tokens. Needed to sign in |
| `backend/.env.example`  | `CORS_ORIGINS`        | Optional. Comma-separated addresses allowed to call the API. Defaults to `http://localhost:5173` |
| `backend/.env.example`  | `MARKET_TIMEZONE`     | Optional. Time zone that decides "today" for trade dates. Defaults to `Australia/Sydney` |
| `backend/.env.example`  | `SESSION_MINUTES`     | Optional. How long a sign in lasts. Defaults to 480  |
| `backend/.env.example`  | `IMPORT_MAX_FILE_BYTES`, `IMPORT_MAX_ROWS` | Optional. CSV upload limits. Default to 1 MB and 5000 rows |
| `backend/.env.example`  | `PRICE_REFRESH_OVERLAP_DAYS`, `PRICE_LOOKBACK_DAYS` | Optional. Price refresh settings. Default to 5 and 365 days |
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

### Price refresh

The Refresh prices workflow fetches the latest closing prices and saves them to the database. It runs on weekdays at 08:00 UTC, after the ASX has closed, and can also be started by hand from the Actions tab.

It needs one more repository secret:

| Secret         | Value |
| -------------- | ----- |
| `DATABASE_URL` | The Neon connection string |

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

Create the demo accounts the same way, with `python -m scripts.seed_users`. `JWT_SECRET` must be set in `.env.prod`, or nobody can sign in.
