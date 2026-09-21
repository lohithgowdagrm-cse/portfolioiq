# PortfolioIQ: REST API & WebSocket Protocol Reference

All REST API endpoints are versioned under `/api/v1/`.

Interactive Swagger UI documentation is available at:
* **Swagger UI**: `http://localhost:8000/api/docs/`
* **ReDoc**: `http://localhost:8000/api/redoc/`
* **OpenAPI Schema**: `http://localhost:8000/api/schema/`

---

## 1. Authentication

PortfolioIQ uses JSON Web Tokens (JWT) with rotating refresh tokens.

### Obtain Token Pair
`POST /api/v1/auth/login/`

**Request**:
```json
{
  "email": "demo@portfolioiq.io",
  "password": "Password123!"
}
```

**Response (200 OK)**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
    "email": "demo@portfolioiq.io",
    "first_name": "Demo",
    "last_name": "Manager",
    "default_currency": "INR"
  }
}
```

Include the access token in subsequent requests:
```http
Authorization: Bearer <access_token>
```

---

## 2. Standard Error Response Envelope

All API errors follow a predictable envelope:

```json
{
  "error": {
    "code": "INSUFFICIENT_POSITION",
    "message": "Cannot sell 50 shares of TCS. Available position is only 25.",
    "details": {}
  }
}
```

---

## 3. Endpoints Catalog

### Portfolios

#### List Portfolios
`GET /api/v1/portfolios/`

#### Portfolio Executive Summary
`GET /api/v1/portfolios/{id}/summary/`

**Response (200 OK)**:
```json
{
  "portfolio_id": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
  "portfolio_name": "Flagship Tech & Bluechip Alpha",
  "currency": "INR",
  "total_equity": "1084230.45",
  "cash_balance": "250000.00",
  "holdings_value": "834230.45",
  "invested_capital": "750000.00",
  "unrealized_pnl": "84230.45",
  "realized_pnl": "12500.00",
  "total_pnl": "96730.45",
  "total_return_pct": 11.23,
  "day_pnl": "24820.20",
  "day_return_pct": 2.34,
  "positions_count": 8,
  "positions": [...]
}
```

#### Holdings Table
`GET /api/v1/portfolios/{id}/positions/`

---

### Transactions

#### List Transactions
`GET /api/v1/transactions/?portfolio_id={id}&type={BUY|SELL|DIVIDEND}&symbol={ticker}`

#### Record Transaction
`POST /api/v1/transactions/`

**Request**:
```json
{
  "portfolio": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
  "instrument": "d2e3f4a5-6b7c-8d9e-0f1a-2b3c4d5e6f7a",
  "transaction_type": "BUY",
  "quantity": "20.0000",
  "price": "4150.0000",
  "fees": "25.0000",
  "taxes": "12.5000",
  "notes": "Tranche accumulation"
}
```

#### Delete Transaction (Ledger Replay)
`DELETE /api/v1/transactions/{id}/`

---

### Analytics & Exposure

#### Performance Curve
`GET /api/v1/analytics/performance/?portfolio_id={id}&timeframe={1W|1M|3M|6M|1Y|ALL}`

#### Sector & Asset Exposure
`GET /api/v1/analytics/exposure/?portfolio_id={id}`

#### Monthly Return Matrix Heatmap
`GET /api/v1/analytics/monthly-matrix/`

---

### Quantitative Risk Engine

#### Institutional Risk Profile
`GET /api/v1/risk/metrics/?portfolio_id={id}`

**Response (200 OK)**:
```json
{
  "portfolio_id": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
  "calculation_date": "2026-09-21",
  "metrics": {
    "volatility_annualized": "16.4200",
    "sharpe_ratio": "1.8400",
    "beta": "1.0800",
    "max_drawdown_pct": "6.7500",
    "var_95_dollar": "18500.00",
    "var_95_pct": "1.71",
    "var_99_dollar": "29400.00",
    "var_99_pct": "2.71",
    "herfindahl_index": "0.1850",
    "top_position_weight_pct": "26.40",
    "top_3_concentration_pct": "58.20"
  },
  "drawdown": {...},
  "exposure": {...}
}
```

#### Stress Testing
`POST /api/v1/risk/stress-test/`

**Request**:
```json
{
  "portfolio_id": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
  "market_shock_pct": -10.0,
  "custom_shocks": {
    "TCS": -15.0,
    "RELIANCE": -12.0
  }
}
```

---

### Options Desk

#### Open Options Positions with Greeks
`GET /api/v1/options/positions/?portfolio_id={id}`

#### Portfolio Greeks & Expiration Exposure
`GET /api/v1/options/portfolio-greeks/?portfolio_id={id}`

---

## 4. WebSocket Protocol

Connect to the ASGI WebSocket endpoint:
```text
ws://localhost:8000/ws/portfolio/{portfolio_id}/
```

### Inbound Heartbeat
```json
{
  "action": "PING"
}
```

### Outbound Events Broadcast

#### Price Tick Update (`TICK_UPDATE`)
```json
{
  "type": "TICK_UPDATE",
  "data": {
    "symbol": "TCS",
    "price": "4152.80",
    "change_amount": "32.30",
    "change_percent": 0.78,
    "timestamp": "2026-09-21T10:15:00Z"
  }
}
```

#### Portfolio Aggregates Update (`PORTFOLIO_UPDATE`)
```json
{
  "type": "PORTFOLIO_UPDATE",
  "data": {
    "portfolio_id": "c1f7b8e2-45e1-4c12-9c3f-7e8e5d3a1f90",
    "total_equity": "1084530.20",
    "day_pnl": "25120.00",
    "day_return_pct": 2.37
  }
}
```

#### Proactive Risk Alert Breach (`RISK_ALERT`)
```json
{
  "type": "RISK_ALERT",
  "data": {
    "rule_id": "a9b8c7d6-e5f4-3a2b-1c0d-9e8f7a6b5c4d",
    "metric_type": "DRAWDOWN",
    "message": "Drawdown reached 8.24%, exceeding threshold of 8.00%."
  }
}
```
