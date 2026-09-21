import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { DashboardView } from "../features/dashboard/DashboardView";
import { PortfolioSummary } from "../types";

// Mock resize observer and api call
(globalThis as any).ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

vi.mock("../services/api", () => ({
  api: {
    getPerformanceCurve: vi.fn().mockResolvedValue({ series: [] }),
  },
}));

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
  positions_count: 1,
  positions: [],
};

describe("DashboardView Component", () => {
  it("renders top metric cards with formatted Indian Rupee figures", async () => {
    render(
      <DashboardView
        summary={mockSummary}
        portfolioId="test-portfolio-1"
        onNavigateToTab={() => {}}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Portfolio Value")).toBeInTheDocument();
    });

    expect(screen.getAllByText("Day P&L")[0]).toBeInTheDocument();
    expect(screen.getByText("Total P&L")).toBeInTheDocument();
    expect(screen.getByText("Invested Capital")).toBeInTheDocument();

    // Check formatted values
    expect(screen.getByText("₹10,84,230.45")).toBeInTheDocument();
    expect(screen.getByText("+₹24,820.20")).toBeInTheDocument();
  });
});

