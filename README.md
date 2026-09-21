# PortfolioIQ: Real-Time Financial Portfolio & Risk Analytics Platform

[![CI Pipeline](https://github.com/portfolioiq/portfolioiq/actions/workflows/ci.yml/badge.svg)](https://github.com/portfolioiq/portfolioiq/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Django 5.1](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com/)
[![React 19](https://img.shields.io/badge/react-19-61dafb.svg)](https://react.dev/)
[![Tailwind CSS 4](https://img.shields.io/badge/tailwind-v4-38bdf8.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **PortfolioIQ** is a production-quality financial portfolio accounting and quantitative risk analytics platform designed for institutional rigor, high-density terminal usability, and mathematical precision.

---

## Architecture Diagram

```text
                    PortfolioIQ Architecture

                       ┌──────────────┐
                       │ React 19 App │
                       └──────┬───────┘
                              │
                    REST (DRF) / WebSocket (Channels)
                              │
                     ┌────────▼────────┐
                     │   Django 5.1    │
                     │  Daphne Server  │
                     └────────┬────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
        PostgreSQL 16      Redis 7          Celery 5.4
             │                │                │
             ▼                ▼                ▼
        Transactional       Cache &        Background
        Ledger & Snapshots  Channel Layer  Tasks & Beat
             │
             ▼
        ┌──────────────────────────────────────────────┐
        │       Deterministic Domain Engine Layer      │
        ├──────────────────────┬───────────────────────┤
        │ Portfolio Accounting │ Weighted Cost Basis   │
        │ Risk Analytics       │ VaR, Sharpe, Beta, DD │
        │ Options Desk         │ Black-Scholes Greeks  │
        │ Stress Testing       │ Macro & Asset Shocks  │
        │ Market Data Adapter  │ Geometric Brownian M. │
        └──────────────────────────────────────────────┘
```

---

## Core Capabilities & Features

### 1. Deterministic Portfolio Accounting Engine
* **Weighted Average Cost Basis**: Exact decimal accounting across multiple `BUY` tranches.
* **Realized & Unrealized P&L**: Reconciled atomically on `SELL`, `DIVIDEND`, `SPLIT`, and `BONUS` share events.
* **Immutable Transaction Ledger**: Chronological replay capability ensuring zero balance drift.
* **Oversell Prevention**: Built-in validation rejecting any attempt to sell more shares than currently held.

### 2. Quantitative Risk Analytics Engine
* **Annualized Historical Volatility**: $\sigma_{\text{ann}} = \sqrt{252} \times \text{std}(\mathbf{r})$.
* **Sharpe Ratio**: Configurable risk-free rate benchmark (default 6.5% sovereign T-bill).
* **Portfolio Beta**: Covariance against benchmark index (NIFTY 50 / S&P 500).
* **Maximum Drawdown**: Peak-to-trough decline tracking capital preservation.
* **Historical Value at Risk (VaR)**: 95% and 99% daily confidence intervals using empirical percentile distributions.
* **Diversification Index**: Herfindahl-Hirschman Index (HHI) for position and sector exposure.

### 3. Options Pricing & Analytical Greeks
* **Black-Scholes European Analytical Model**: Theoretical pricing vs market quotes.
* **First- & Second-Order Greeks**: Delta ($\Delta$), Gamma ($\Gamma$), daily Theta ($\Theta$), Vega ($\nu$), and Rho ($\rho$).
* **Portfolio-Level Greeks Aggregation**: Weighted underlying share exposure.
* **Expiration Horizon Bucketing**: Exposure distribution for contracts expiring in $\le 7$ days, 8–30 days, and $> 30$ days.

### 4. Interactive Scenario Stress Testing
* **Macro Market Shocks**: Instant portfolio revaluation under $-5\%$, $-10\%$, and $-20\%$ systemic drawdowns.
* **Custom Asset Shocks**: Single-stock stress testing (e.g. TCS $-12\%$, RELIANCE $-15\%$).

### 5. Pluggable Market Data & Real-Time WebSockets
* **Provider Abstraction**: Pluggable `MarketDataProvider` architecture.
* **Mock Stochastic Engine**: High-fidelity Geometric Brownian Motion tick synthesis for deterministic offline testing.
* **WebSockets (Django Channels)**: Selective push notifications for price ticks, P&L adjustments, and risk breaches without full page reloads.

### 6. Proactive Alerts & Immutable Audit Trail
* **Automated Risk Monitors**: Configurable rules for Drawdown breaches, single-position concentration limits, and daily loss stops.
* **System Audit Trail**: Complete action history tracking user, action, entity, timestamp, and IP address.

---

## Utilitarian Design System

PortfolioIQ adheres to a strict minimalist, utilitarian design language inspired by professional fintech terminals:
* **Strict Monochrome Palette**: Tailwind Slate and Zinc base with muted emerald (profit) and rose (loss) semantic indicators.
* **High Information Density**: Compact financial tables with sticky headers, sortable columns, and tabular numerals (`font-mono`).
* **Zero AI Clichés**: No glowing neon borders, no glassmorphism backdrop blurs, no 3D charts, and no decorative animations.

---

## Technology Stack

| Layer | Technologies | Justification |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS v4, Lucide | Instant HMR, type-safe components, high-density layouts |
| **Backend** | Python 3.12, Django 5.1, DRF, Daphne, Channels | Proven financial data modeling, robust ORM, ASGI WebSockets |
| **Domain Logic** | NumPy, SciPy, Pandas, Pure Decimal | IEEE 754 precision compliance, analytical normal distributions |
| **Storage & Caching**| PostgreSQL 16, Redis 7 | Relational ACID ledger guarantees, O(1) quote caching, pub/sub |
| **Asynchronous** | Celery 5.4, Celery Beat | Non-blocking market ingestion, nightly snapshots, scheduled alerts |
| **Testing** | pytest, pytest-django, Vitest, Testing Library | 100% test pass rate across math, API, and UI layers |
| **Containerization**| Docker, Docker Compose, Nginx | Turnkey local deployment and production parity |

---

## Getting Started

### Prerequisites
* Docker & Docker Compose **OR** Python 3.12+ and Node.js 24+

### Option A: Turnkey Docker Setup (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/portfolioiq/portfolioiq.git
cd portfolioiq

# 2. Launch full stack with seed data
docker compose up --build
```
Once initialized, access:
* **Frontend Application**: `http://localhost`
* **REST API & Swagger Docs**: `http://localhost:8000/api/docs/`
* **Demo Login**: `demo@portfolioiq.io` / `Password123!`

---

### Option B: Local Native Development Setup

#### 1. Backend Setup
```bash
# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements/dev.txt

# Run migrations and seed data
python backend/manage.py migrate
python backend/manage.py seed_data

# Run Django development ASGI server
python backend/manage.py runserver
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Verification & Testing

### Backend Test Suite (21 Unit & Integration Tests)
```bash
source .venv/bin/activate
PYTHONPATH=backend pytest backend/tests/
```
Tests cover:
* Weighted average cost calculations
* Partial sell realized P&L accounting
* Over-selling prevention & validation
* Annualized volatility & Sharpe ratio formulas
* Beta covariance vs NIFTY 50
* Historical VaR empirical percentile lookups
* Black-Scholes Call/Put parity & Greeks ($\Delta, \Gamma, \Theta, \nu$)
* API authorization & IDOR isolation

### Frontend Test Suite
```bash
cd frontend
npm run test
```
Tests cover:
* Holdings data table filtering, sorting, and empty states
* Executive dashboard rendering and locale-aware Indian Rupee formatting

---

## Environment Variables

Copy `.env.example` to `.env`:

```ini
DJANGO_ENV=development
SECRET_KEY=your-secure-production-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,backend,frontend

# Database (PostgreSQL or SQLite fallback for local quick tests)
DATABASE_URL=postgres://portfolioiq:portfolioiq_secret@localhost:5432/portfolioiq_db
USE_SQLITE=False

# Redis
REDIS_URL=redis://localhost:6379/0

# Market Data
MARKET_DATA_PROVIDER=mock
```

---

## Seed Data Accounts

The seeding script generates 5 realistic institutional profiles:

| Email | Role | Default Currency | Password |
| :--- | :--- | :--- | :--- |
| `demo@portfolioiq.io` | Portfolio Manager | INR (₹) | `Password123!` |
| `risk_analyst@portfolioiq.io` | Risk Analyst | INR (₹) | `Password123!` |
| `quant_lead@portfolioiq.io` | Quant Lead | USD ($) | `Password123!` |
| `fund_manager@portfolioiq.io` | Fund Manager | INR (₹) | `Password123!` |
| `compliance_officer@portfolioiq.io` | Compliance Officer | USD ($) | `Password123!` |

Pre-seeded portfolios for `demo@portfolioiq.io`:
1. **Flagship Tech & Bluechip Alpha** (High-growth equities + top Indian bluechips)
2. **All-Weather Dividend & Value** (Defensive cash cows, banking leaders, and ETFs)
3. **Derivatives Hedged Strategy** (Long equity positions paired with index Put protection)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
