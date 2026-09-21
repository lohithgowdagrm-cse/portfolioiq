# PortfolioIQ: Architectural Design & Engineering Specifications

This document outlines the technical design principles, computational formulas, database models, and architectural decisions governing **PortfolioIQ**.

---

## 1. Domain Service Isolation Principle

Financial calculations must never live in presentation layers:
* **React Components** only render formatted values and trigger user actions.
* **DRF Serializers** only validate incoming payload shapes and serialize output data.
* **Views** only handle HTTP protocol negotiation, permission checks, and delegate to domain services.
* **Domain Services** (`apps/*/services/`) are pure Python modules responsible for all mathematical calculations, ledger reconciliations, and risk modeling.

```text
[HTTP Request] ──> [Permission Check] ──> [View] ──> [Domain Service] ──> [DB / Redis]
                                                           │
                                                   (Pure Math & Rules)
```

---

## 2. Precision & Floating-Point Protection

Standard IEEE 754 floating-point numbers (`0.1 + 0.2 = 0.30000000000000004`) create compounding balance drift in financial ledgers.

### Rules Implemented
1. All monetary quantities, transaction prices, cash balances, and position holdings use `Decimal(18, 4)`.
2. Percentage returns and volatility use `Decimal(8, 4)` or `Decimal(10, 4)`.
3. Intermediate multiplication (e.g. $\text{quantity} \times \text{price}$) is quantized explicitly to 4 decimal places before model validation:
   ```python
   self.total_amount = computed.quantize(Decimal("0.0001"))
   ```
4. SciPy and NumPy floating point outputs (e.g. from CDF/PDF functions in Black-Scholes) are rounded and converted to string representations before Decimal initialization:
   ```python
   Decimal(str(round(delta, 4)))
   ```

---

## 3. Position Cost Basis & Ledger Replay

### Average Cost Calculation
When accumulating shares over multiple `BUY` tranches:
$$\bar{P}_{\text{new}} = \frac{(\text{Prior Qty} \times \bar{P}_{\text{prior}}) + (\text{Tx Qty} \times P_{\text{tx}}) + \text{Fees} + \text{Taxes}}{\text{Prior Qty} + \text{Tx Qty}}$$

### Realized P&L on SELL
$$\text{Realized P\&L} = (\text{Sell Price} - \bar{P}_{\text{avg}}) \times \text{Sold Qty} - \text{Fees} - \text{Taxes}$$
The average cost per share for remaining inventory remains unchanged upon a sale.

### Chronological Ledger Replay
If a transaction is deleted or edited, positions are not adjusted incrementally (which risks cascading errors). Instead, `PortfolioCalculationService.recalculate_portfolio_from_ledger` resets position balances to zero and replays all transactions chronologically:
```python
with transaction.atomic():
    Position.objects.filter(portfolio=portfolio).update(
        quantity=Decimal("0.0000"),
        average_buy_price=Decimal("0.0000"),
        total_invested=Decimal("0.0000"),
        realized_pnl=Decimal("0.0000"),
    )
    txs = Transaction.objects.filter(portfolio=portfolio).order_by("executed_at", "created_at")
    for tx in txs:
        cls.apply_transaction_to_position(...)
```

---

## 4. Quantitative Risk Engine Methodology

### Annualized Volatility
$$\sigma_{\text{ann}} = \sqrt{252} \times \text{std}(\mathbf{r}_{\text{daily}}, \text{ddof}=1) \times 100$$
* **Assumption**: 252 trading days per calendar year.

### Sharpe Ratio
$$\text{Sharpe} = \frac{\bar{R}_p - R_f}{\sigma_p}$$
* $R_f$: 6.5% annual sovereign 91-day T-bill baseline, normalized to daily rate $R_f / 252$.

### Portfolio Beta
$$\beta = \frac{\text{Cov}(R_p, R_b)}{\text{Var}(R_b)}$$
* Evaluated against benchmark index (NIFTY 50).

### Historical Value at Risk (VaR)
Non-parametric historical simulation. Empirically sorts daily percentage returns $\mathbf{r}$ over the lookback window (default 90–252 trading days):
$$\text{VaR}_{95\%} = -\text{Percentile}(\mathbf{r}, 5) \times \text{Portfolio Value}$$
$$\text{VaR}_{99\%} = -\text{Percentile}(\mathbf{r}, 1) \times \text{Portfolio Value}$$

### Maximum Drawdown (MDD)
$$\text{Drawdown}_t = \frac{\text{Peak}_t - \text{Value}_t}{\text{Peak}_t}$$
$$\text{MDD} = \max_t (\text{Drawdown}_t)$$

---

## 5. Options Desk & Greeks Methodology

Analytical European option pricing via Black-Scholes-Merton:
$$d_1 = \frac{\ln(S/K) + (r + \frac{1}{2}\sigma^2)T}{\sigma\sqrt{T}}$$
$$d_2 = d_1 - \sigma\sqrt{T}$$

### Greeks Derivatives
* **Delta ($\Delta$)**: $\Phi(d_1)$ (Call) or $\Phi(d_1) - 1$ (Put)
* **Gamma ($\Gamma$)**: $\frac{\phi(d_1)}{S \sigma \sqrt{T}}$
* **Theta ($\Theta$)**: Daily time decay $\frac{\partial V}{\partial t} / 365$
* **Vega ($\nu$)**: Sensitivity per 1% change in implied volatility: $\frac{S \phi(d_1) \sqrt{T}}{100}$
* **Rho ($\rho$)**: Sensitivity per 1% change in interest rate: $\frac{K T e^{-rT} \Phi(d_2)}{100}$

### Portfolio Greeks Scaling
Total portfolio exposure incorporates lot multiplier:
$$\Delta_{\text{portfolio}} = \sum_{i} \Delta_i \times \text{Quantity}_i \times \text{Multiplier}_i$$

---

## 6. Multi-Tenant Authorization & IDOR Security

To prevent Insecure Direct Object Reference (IDOR) attacks:
1. Every portfolio, position, transaction, and alert rule query filters strictly through `portfolio__user = request.user` or `user = request.user`.
2. Object-level permissions (`IsOwner`, `IsPortfolioOwner`) raise `404 Not Found` (rather than `403 Forbidden`) when an unowned ID is requested, preventing enumeration of foreign resource IDs.
3. Automated integration tests (`test_idor_protection_user_cannot_access_other_users_portfolio`) run in CI to verify that User A cannot read or modify User B's portfolio.
