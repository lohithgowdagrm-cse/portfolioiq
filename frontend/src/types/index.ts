export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  default_currency: string;
}

export interface PortfolioSummary {
  portfolio_id: string;
  portfolio_name: string;
  currency: string;
  total_equity: string;
  cash_balance: string;
  holdings_value: string;
  invested_capital: string;
  unrealized_pnl: string;
  realized_pnl: string;
  total_pnl: string;
  total_return_pct: number;
  day_pnl: string;
  day_return_pct: number;
  positions_count: number;
  positions: PositionRow[];
}

export interface PositionRow {
  id: string;
  instrument_id: string;
  symbol: string;
  name: string;
  asset_class: string;
  sector: string;
  quantity: string;
  average_buy_price: string;
  ltp: string;
  prev_close: string;
  invested_capital: string;
  current_value: string;
  day_pnl: string;
  day_change_pct: number;
  unrealized_pnl: string;
  total_return_pct: number;
  realized_pnl: string;
  weight_pct: number;
}

export interface PortfolioListItem {
  id: string;
  name: string;
  description: string;
  base_currency: string;
  cash_balance: string;
  is_default: boolean;
  total_equity: string;
  total_invested: string;
  unrealized_pnl: string;
  total_return_pct: number;
  day_pnl: string;
  day_return_pct: number;
  positions_count: number;
}

export interface TransactionItem {
  id: string;
  portfolio: string;
  instrument: string;
  symbol: string;
  instrument_name: string;
  transaction_type: "BUY" | "SELL" | "DIVIDEND" | "BONUS" | "SPLIT";
  quantity: string;
  price: string;
  fees: string;
  taxes: string;
  total_amount: string;
  executed_at: string;
  notes: string;
}

export interface PerformanceCurvePoint {
  date: string;
  total_equity: number;
  invested_capital: number;
  unrealized_pnl: number;
  day_pnl: number;
  day_return_pct: number;
  portfolio_return_pct: number;
  benchmark_return_pct: number;
}

export interface RiskMetricsProfile {
  portfolio_id: string;
  portfolio_name: string;
  calculation_date: string;
  metrics: {
    volatility_annualized: string;
    sharpe_ratio: string;
    beta: string;
    max_drawdown_pct: string;
    var_95_dollar: string;
    var_95_pct: string;
    var_99_dollar: string;
    var_99_pct: string;
    herfindahl_index: string;
    top_position_weight_pct: string;
    top_3_concentration_pct: string;
  };
  drawdown: {
    max_drawdown_pct: string;
    peak_value: string;
    trough_value: string;
    drawdown_series: number[];
  };
  exposure: {
    sectors: Record<string, number>;
    asset_classes: Record<string, number>;
  };
}

export interface StressTestResponse {
  scenario_name: string;
  current_equity: string;
  projected_equity: string;
  cash_buffer: string;
  total_dollar_change: string;
  total_percentage_change: string;
  assumptions: Record<string, any>;
  position_impacts: Array<{
    symbol: string;
    name: string;
    current_value: string;
    projected_value: string;
    dollar_change: string;
    percentage_change: string;
    applied_shock_pct: number;
    assumption: string;
  }>;
}

export interface OptionsPortfolioData {
  portfolio_id: string;
  portfolio_name: string;
  open_options_count: number;
  aggregate_greeks: {
    portfolio_delta: string;
    portfolio_gamma: string;
    portfolio_theta: string;
    portfolio_vega: string;
    total_options_market_value: string;
  };
  expiration_exposure: {
    expiring_within_7_days: number;
    expiring_8_to_30_days: number;
    expiring_beyond_30_days: number;
  };
  positions: Array<{
    position_id: string;
    contract: {
      contract_id: string;
      symbol: string;
      underlying_name: string;
      option_type: "CALL" | "PUT";
      strike_price: string;
      expiration_date: string;
      days_to_expiry: number;
      spot_price: string;
      theoretical_price: string;
      intrinsic_value: string;
      extrinsic_value: string;
      moneyness: "ITM" | "ATM" | "OTM";
      greeks: {
        delta: string;
        gamma: string;
        theta: string;
        vega: string;
        rho: string;
      };
    };
    quantity: string;
    average_price: string;
    market_value: string;
    unrealized_pnl: string;
    position_delta: string;
    position_gamma: string;
    position_theta: string;
    position_vega: string;
  }>;
}

export interface AlertRuleItem {
  id: string;
  portfolio: string;
  portfolio_name: string;
  metric_type: string;
  comparator: string;
  threshold_value: string;
  is_active: boolean;
  created_at: string;
}

export interface AlertEventItem {
  id: string;
  metric_type: string;
  portfolio_name: string;
  threshold_value: string;
  triggered_value: string;
  message: string;
  is_acknowledged: boolean;
  created_at: string;
}
