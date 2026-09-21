import React, { useState, useEffect, useRef } from "react";
import { Shell } from "./components/layout/Shell";
import { LoginView } from "./features/auth/LoginView";
import { DashboardView } from "./features/dashboard/DashboardView";
import { HoldingsView } from "./features/holdings/HoldingsView";
import { TransactionsView } from "./features/transactions/TransactionsView";
import { AnalyticsView } from "./features/analytics/AnalyticsView";
import { RiskView } from "./features/risk/RiskView";
import { OptionsView } from "./features/options/OptionsView";
import { AlertsView } from "./features/alerts/AlertsView";
import { PortfoliosView } from "./features/portfolios/PortfoliosView";
import { PortfolioListItem, PortfolioSummary } from "./types";
import { api } from "./services/api";
import { PortfolioWebSocket } from "./services/websocket";

export function App() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("portfolioiq_token")
  );
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("dashboard");

  // Portfolios state
  const [portfolios, setPortfolios] = useState<PortfolioListItem[]>([]);
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string>("");
  const [portfolioSummary, setPortfolioSummary] = useState<PortfolioSummary | null>(null);

  // Alerts counter
  const [unacknowledgedAlertsCount, setUnacknowledgedAlertsCount] = useState<number>(0);

  // Live tick simulation
  const [isSimulatingTick, setIsSimulatingTick] = useState(false);
  const wsRef = useRef<PortfolioWebSocket | null>(null);

  // Trade modal trigger from holdings
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);

  // 1. Initial auth check
  useEffect(() => {
    if (token) {
      api.getMe()
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem("portfolioiq_token");
          setToken(null);
        });
    }
  }, [token]);

  // 2. Load user portfolios
  const loadPortfolios = () => {
    if (!token) return;
    api.getPortfolios().then((res) => {
      const list = res.results || [];
      setPortfolios(list);
      if (list.length > 0 && !selectedPortfolioId) {
        const defaultP = list.find((p: any) => p.is_default) || list[0];
        setSelectedPortfolioId(defaultP.id);
      }
    });
  };

  useEffect(() => {
    loadPortfolios();
  }, [token]);

  // 3. Load portfolio summary
  const loadSummary = (pId: string = selectedPortfolioId) => {
    if (!token || !pId) return;
    api.getPortfolioSummary(pId)
      .then((summary) => setPortfolioSummary(summary))
      .catch((err) => console.error("Error loading summary:", err));
  };

  useEffect(() => {
    if (selectedPortfolioId) {
      loadSummary(selectedPortfolioId);
    }
  }, [selectedPortfolioId]);

  // 4. Alerts counter
  const refreshAlertCount = () => {
    if (!token) return;
    api.getAlertEvents().then((res) => {
      const active = (res.results || []).filter((e: any) => !e.is_acknowledged);
      setUnacknowledgedAlertsCount(active.length);
    });
  };

  useEffect(() => {
    refreshAlertCount();
  }, [token]);

  // 5. Setup WebSocket connection for selected portfolio
  useEffect(() => {
    if (!selectedPortfolioId) return;

    if (wsRef.current) {
      wsRef.current.disconnect();
    }

    const ws = new PortfolioWebSocket(selectedPortfolioId);
    ws.connect();

    ws.on("TICK_UPDATE", (tickData: any) => {
      // Real-time tick update: selectively update holdings row and reload summary smoothly
      setPortfolioSummary((prev) => {
        if (!prev) return prev;
        const updatedPositions = prev.positions.map((pos) => {
          if (pos.symbol.toUpperCase() === tickData.symbol?.toUpperCase()) {
            const newLtp = tickData.price;
            const newMarketVal = (parseFloat(pos.quantity) * parseFloat(newLtp)).toFixed(4);
            const newUnrealized = (parseFloat(newMarketVal) - parseFloat(pos.invested_capital)).toFixed(4);
            return {
              ...pos,
              ltp: newLtp,
              current_value: newMarketVal,
              unrealized_pnl: newUnrealized,
            };
          }
          return pos;
        });

        return {
          ...prev,
          positions: updatedPositions,
        };
      });

      // Also refresh summary aggregates
      loadSummary(selectedPortfolioId);
    });

    ws.on("RISK_ALERT", () => {
      refreshAlertCount();
    });

    wsRef.current = ws;

    return () => {
      ws.disconnect();
    };
  }, [selectedPortfolioId]);

  const handleSimulateTick = async () => {
    setIsSimulatingTick(true);
    try {
      await api.simulateTick();
    } catch (err) {
      console.error("Simulation error:", err);
    } finally {
      setTimeout(() => setIsSimulatingTick(false), 300);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("portfolioiq_token");
    setToken(null);
    setUser(null);
  };

  if (!token) {
    return (
      <LoginView
        onLoginSuccess={(tok, u) => {
          setToken(tok);
          setUser(u);
        }}
      />
    );
  }

  return (
    <Shell
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      portfolios={portfolios}
      selectedPortfolioId={selectedPortfolioId}
      setSelectedPortfolioId={setSelectedPortfolioId}
      unacknowledgedAlertsCount={unacknowledgedAlertsCount}
      onSimulateTick={handleSimulateTick}
      isSimulating={isSimulatingTick}
      onLogout={handleLogout}
      userEmail={user?.email}
    >
      {activeTab === "dashboard" && (
        <DashboardView
          summary={portfolioSummary}
          portfolioId={selectedPortfolioId}
          onNavigateToTab={setActiveTab}
        />
      )}

      {activeTab === "portfolios" && (
        <PortfoliosView
          portfolios={portfolios}
          selectedPortfolioId={selectedPortfolioId}
          onSelectPortfolio={(id) => {
            setSelectedPortfolioId(id);
            setActiveTab("dashboard");
          }}
          onRefreshPortfolios={loadPortfolios}
        />
      )}

      {activeTab === "holdings" && (
        <HoldingsView
          summary={portfolioSummary}
          onOpenTradeModal={() => {
            setIsTradeModalOpen(true);
            setActiveTab("transactions");
          }}
        />
      )}

      {activeTab === "transactions" && (
        <TransactionsView
          portfolioId={selectedPortfolioId}
          onTransactionUpdated={() => loadSummary(selectedPortfolioId)}
          isTradeModalOpen={isTradeModalOpen}
          setIsTradeModalOpen={setIsTradeModalOpen}
        />
      )}

      {activeTab === "analytics" && (
        <AnalyticsView
          portfolioId={selectedPortfolioId}
          summary={portfolioSummary}
        />
      )}

      {activeTab === "risk" && (
        <RiskView portfolioId={selectedPortfolioId} />
      )}

      {activeTab === "options" && (
        <OptionsView portfolioId={selectedPortfolioId} />
      )}

      {activeTab === "alerts" && (
        <AlertsView
          portfolioId={selectedPortfolioId}
          onRefreshAlertCount={refreshAlertCount}
        />
      )}
    </Shell>
  );
}

export default App;
