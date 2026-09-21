import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { HoldingsView } from "../features/holdings/HoldingsView";
import { PortfolioSummary } from "../types";

const mockSummary: PortfolioSummary = {
  portfolio_id: "test-portfolio-1",
  portfolio_name: "Flagship Alpha",
  currency: "INR",
  total_equity: "1084230.45",
  cash_balance: "250000.00",
  holdings_value: "834230.45",
  invested_capital: "750000.00",
  unrealized_pnl: "84230.45",
  realized_pnl: "12500.00",
  total_pnl: "96730.45",
  total_return_pct: 11.23,
  day_pnl: "24820.20",
  day_return_pct: 2.34,
  positions_count: 2,
  positions: [
    {
      id: "pos-1",
      instrument_id: "inst-1",
      symbol: "TCS",
      name: "Tata Consultancy Services Ltd.",
      asset_class: "EQUITY",
      sector: "Information Technology",
      quantity: "25.0000",
      average_buy_price: "4000.0000",
      ltp: "4150.0000",
      prev_close: "4100.0000",
      invested_capital: "100000.0000",
      current_value: "103750.0000",
      day_pnl: "1250.0000",
      day_change_pct: 1.22,
      unrealized_pnl: "3750.0000",
      total_return_pct: 3.75,
      realized_pnl: "0.0000",
      weight_pct: 9.57,
    },
    {
      id: "pos-2",
      instrument_id: "inst-2",
      symbol: "RELIANCE",
      name: "Reliance Industries Ltd.",
      asset_class: "EQUITY",
      sector: "Energy",
      quantity: "50.0000",
      average_buy_price: "2800.0000",
      ltp: "2950.0000",
      prev_close: "2900.0000",
      invested_capital: "140000.0000",
      current_value: "147500.0000",
      day_pnl: "2500.0000",
      day_change_pct: 1.72,
      unrealized_pnl: "7500.0000",
      total_return_pct: 5.36,
      realized_pnl: "0.0000",
      weight_pct: 13.60,
    },
  ],
};

describe("HoldingsView Component", () => {
  it("renders holdings table with instruments and metrics", () => {
    render(<HoldingsView summary={mockSummary} />);

    expect(screen.getByText("TCS")).toBeInTheDocument();
    expect(screen.getByText("RELIANCE")).toBeInTheDocument();
    expect(screen.getByText("Tata Consultancy Services Ltd.")).toBeInTheDocument();
  });

  it("filters positions when typing in the search input", () => {
    render(<HoldingsView summary={mockSummary} />);

    const searchInput = screen.getByPlaceholderText("Filter ticker...");
    fireEvent.change(searchInput, { target: { value: "RELIANCE" } });

    expect(screen.getByText("RELIANCE")).toBeInTheDocument();
    expect(screen.queryByText("TCS")).not.toBeInTheDocument();
  });

  it("shows empty state if filter matches no instruments", () => {
    render(<HoldingsView summary={mockSummary} />);

    const searchInput = screen.getByPlaceholderText("Filter ticker...");
    fireEvent.change(searchInput, { target: { value: "NONEXISTENT" } });

    expect(
      screen.getByText("No holdings match your filter criteria.")
    ).toBeInTheDocument();
  });
});
