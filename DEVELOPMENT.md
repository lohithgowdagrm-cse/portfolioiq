# PortfolioIQ: Developer Setup & Engineering Guide

This guide describes how to run, test, and contribute to **PortfolioIQ** locally.

---

## 1. Quick Start

### Native Environment Setup

```bash
# 1. Create Python 3.12 Virtual Environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install Backend Dependencies
pip install -r backend/requirements/dev.txt

# 3. Initialize Database & Seed Demo Records
python backend/manage.py migrate
python backend/manage.py seed_data

# 4. Start ASGI Daphne Backend Server
python backend/manage.py runserver
```

In a second terminal:
```bash
# 5. Start React/Vite Frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` and log in with:
* Email: `demo@portfolioiq.io`
* Password: `Password123!`

---

## 2. Running Test Suites

### Backend Unit & Integration Tests (pytest)
```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests/
```
Output:
```text
21 passed in 4.73s
```

### Frontend Tests (Vitest & RTL)
```bash
cd frontend
npm run test
```
Output:
```text
Test Files  2 passed (2)
Tests       4 passed (4)
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 3. Code Style & Quality Standards

* **Python Linting**:
  ```bash
  source .venv/bin/activate
  ruff check backend/
  ```
* **Frontend Linting & Type Checking**:
  ```bash
  cd frontend
  npm run build  # includes tsc -b
  ```

---

## 4. Running Background Workers Locally

To test Celery background processing locally with Redis:

```bash
# Terminal 1: Redis server
redis-server

# Terminal 2: Celery worker
source .venv/bin/activate
celery -A config worker -l info --workdir=backend

# Terminal 3: Celery beat periodic scheduler
source .venv/bin/activate
celery -A config beat -l info --workdir=backend
```

---

## 5. Adding New Market Data Providers

To plug in a live external market data provider (e.g. Interactive Brokers, AlphaVantage, Polygon):
1. Inherit from `MarketDataProvider` in `backend/apps/market_data/base.py`.
2. Implement:
   * `get_latest_quote(symbol: str) -> Dict[str, Any]`
   * `get_historical_candles(symbol, start_date, end_date) -> List[Dict[str, Any]]`
   * `simulate_tick(symbol, current_price) -> Dict[str, Any]`
3. Add provider configuration to `MarketDataService.get_provider()` in `backend/apps/market_data/services/market_data_service.py`.
