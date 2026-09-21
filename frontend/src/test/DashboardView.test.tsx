import "@testing-library/jest-dom/vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardView } from "../features/dashboard/DashboardView";
import { PortfolioSummary } from "../types";
import { api } from "../services/api";

// Mock Recharts ResponsiveContainer for jsdom
vi.mock("recharts", async () => {
  const original = await vi.importActual<any>("recharts");
  return {
    ...original,
    ResponsiveContainer: ({ children }: any) => (
      <div className="recharts-responsive-container" style={{ width: 800, height: 300 }}>
        {children}
      </div>
    ),
  };
});

vi.mock("../services/api", () => ({
  api: {
    getPerformanceCurve: vi.fn().mockResolvedValue({
      series: [
        { date: "2026-09-01", total_equity: 1000000, portfolio_return_pct: 0, benchmark_return_pct: 0 },
        { date: "2026-09-21", total_equity: 1084230, portfolio_return_pct: 8.42, benchmark_return_pct: 3.12 },
      ],
    }),
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
  positions_count: 2,
  positions: [
    {
      id: "pos-1",
      instrument_id: "inst-1",
      symbol: "TCS",
      name: "Tata Consultancy Services Ltd.",
      asset_class: "EQUITY",
      sector: "Information Technology",
      quantity: "38.00",
      average_buy_price: "3942.32",
      ltp: "3657.19",
      prev_close: "3547.00",
      invested_capital: "149808.06",
      current_value: "138973.22",
      day_pnl: "4184.94",
      day_change_pct: 3.10,
      unrealized_pnl: "-10834.84",
      total_return_pct: -7.23,
      realized_pnl: "0.00",
      weight_pct: "10.17",
    },
    {
      id: "pos-2",
      instrument_id: "inst-2",
      symbol: "RELIANCE",
      name: "Reliance Industries Ltd.",
      asset_class: "EQUITY",
      sector: "Energy & Petrochemicals",
      quantity: "59.00",
      average_buy_price: "2792.29",
      ltp: "2845.88",
      prev_close: "2838.00",
      invested_capital: "164744.85",
      current_value: "167906.92",
      day_pnl: "455.48",
      day_change_pct: 0.27,
      unrealized_pnl: "3162.07",
      total_return_pct: 1.92,
      realized_pnl: "0.00",
      weight_pct: "12.29",
    },
  ],
};

describe("DashboardView Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state when summary is null", () => {
    render(
      <DashboardView
        summary={null}
        portfolioId=""
        onNavigateToTab={() => {}}
      />
    );

    expect(screen.getByText("Loading portfolio metrics...")).toBeInTheDocument();
  });


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
    expect(screen.getByText("+₹96,730.45")).toBeInTheDocument();
    expect(screen.getByText("₹7,50,000.00")).toBeInTheDocument();
  });

  it("renders top holdings glance and sector exposure correctly", async () => {
    render(
      <DashboardView
        summary={mockSummary}
        portfolioId="test-portfolio-1"
        onNavigateToTab={() => {}}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("Top Holdings Glance")).toBeInTheDocument();
    });

    // Holdings row items
    expect(screen.getByText("TCS")).toBeInTheDocument();
    expect(screen.getByText("Tata Consultancy Services Ltd.")).toBeInTheDocument();
    expect(screen.getByText("RELIANCE")).toBeInTheDocument();

    // Sector exposure items
    expect(screen.getByText("Sector Exposure")).toBeInTheDocument();
    expect(screen.getByText("Information Technology")).toBeInTheDocument();
    expect(screen.getByText("Energy & Petrochemicals")).toBeInTheDocument();
  });

  it("triggers onNavigateToTab when 'View Full Holdings Table' is clicked", async () => {
    const handleNavigate = vi.fn();
    render(
      <DashboardView
        summary={mockSummary}
        portfolioId="test-portfolio-1"
        onNavigateToTab={handleNavigate}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("View Full Holdings Table →")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("View Full Holdings Table →"));
    expect(handleNavigate).toHaveBeenCalledWith("holdings");
  });

  it("calls api.getPerformanceCurve when changing timeframe", async () => {
    render(
      <DashboardView
        summary={mockSummary}
        portfolioId="test-portfolio-1"
        onNavigateToTab={() => {}}
      />
    );

    await waitFor(() => {
      expect(api.getPerformanceCurve).toHaveBeenCalledWith("test-portfolio-1", "3M");
    });

    // Click 1M button
    const btn1M = screen.getByRole("button", { name: "1M" });
    fireEvent.click(btn1M);

    await waitFor(() => {
      expect(api.getPerformanceCurve).toHaveBeenCalledWith("test-portfolio-1", "1M");
    });
  });
});
