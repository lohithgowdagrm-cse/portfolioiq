import React, { useState } from "react";
import {
  LayoutDashboard,
  Briefcase,
  Layers,
  Receipt,
  LineChart,
  ShieldAlert,
  Binary,
  Bell,
  Sun,
  Moon,
  Zap,
  LogOut,
  Search,
  ChevronDown,
} from "lucide-react";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { cn } from "../../lib/utils";
import { PortfolioListItem } from "../../types";

interface ShellProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  portfolios: PortfolioListItem[];
  selectedPortfolioId: string;
  setSelectedPortfolioId: (id: string) => void;
  unacknowledgedAlertsCount: number;
  onSimulateTick: () => void;
  isSimulating: boolean;
  onLogout: () => void;
  userEmail?: string;
  children: React.ReactNode;
}

export const Shell: React.FC<ShellProps> = ({
  activeTab,
  setActiveTab,
  portfolios,
  selectedPortfolioId,
  setSelectedPortfolioId,
  unacknowledgedAlertsCount,
  onSimulateTick,
  isSimulating,
  onLogout,
  userEmail,
  children,
}) => {
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    if (document.documentElement.classList.contains("dark")) {
      document.documentElement.classList.remove("dark");
      setIsDark(false);
    } else {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    }
  };

  const navItems = [
    { id: "dashboard", label: "Overview", icon: LayoutDashboard },
    { id: "portfolios", label: "Portfolios", icon: Briefcase },
    { id: "holdings", label: "Holdings", icon: Layers },
    { id: "transactions", label: "Transactions", icon: Receipt },
    { id: "analytics", label: "Analytics", icon: LineChart },
    { id: "risk", label: "Risk Engine", icon: ShieldAlert },
    { id: "options", label: "Options Desk", icon: Binary },
    { id: "alerts", label: "Alerts & Audit", icon: Bell, badge: unacknowledgedAlertsCount },
  ];

  const currentPortfolio = portfolios.find((p) => p.id === selectedPortfolioId) || portfolios[0];

  return (
    <div className="flex h-screen w-full flex-col bg-slate-50 dark:bg-zinc-950 font-sans text-slate-900 dark:text-zinc-100 overflow-hidden">
      {/* Top Application Header */}
      <header className="flex h-12 w-full items-center justify-between border-b border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/90 px-4 select-none shrink-0 z-20">
        <div className="flex items-center space-x-6">
          <div className="flex items-baseline space-x-2">
            <span className="font-mono text-sm font-bold tracking-tight text-slate-900 dark:text-zinc-50">
              PORTFOLIO<span className="text-slate-500 dark:text-zinc-400">IQ</span>
            </span>
            <span className="text-[10px] uppercase font-mono tracking-widest text-slate-400 dark:text-zinc-500 border-l border-slate-200 dark:border-zinc-700 pl-2 hidden sm:inline">
              Real-Time Portfolio & Risk Analytics
            </span>
          </div>

          {/* Portfolio Selector */}
          <div className="relative">
            <select
              value={selectedPortfolioId}
              onChange={(e) => setSelectedPortfolioId(e.target.value)}
              className="h-7 appearance-none rounded-sm border border-slate-300 dark:border-zinc-700 bg-slate-50 dark:bg-zinc-800/80 px-2.5 pr-7 text-xs font-medium text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900 dark:focus:ring-zinc-400 cursor-pointer"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.base_currency})
                </option>
              ))}
            </select>
            <ChevronDown className="pointer-events-none absolute right-2 top-2 h-3 w-3 text-slate-400" />
          </div>
        </div>

        <div className="flex items-center space-x-2.5">
          {/* Live Tick Simulation Button */}
          <Button
            variant="outline"
            size="sm"
            onClick={onSimulateTick}
            isLoading={isSimulating}
            className="border-slate-300 dark:border-zinc-700 text-slate-700 dark:text-zinc-300 font-mono text-[11px]"
            title="Simulate live market Brownian tick & WebSocket broadcast"
          >
            <Zap className="mr-1 h-3 w-3 text-amber-500" />
            <span>Simulate Tick</span>
          </Button>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="flex h-7 w-7 items-center justify-center rounded-sm border border-slate-200 dark:border-zinc-700 text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
            title="Toggle theme"
          >
            {isDark ? <Sun className="h-3.5 w-3.5" /> : <Moon className="h-3.5 w-3.5" />}
          </button>

          {/* Alerts Counter */}
          <button
            onClick={() => setActiveTab("alerts")}
            className="relative flex h-7 items-center space-x-1.5 rounded-sm border border-slate-200 dark:border-zinc-700 px-2 text-xs text-slate-700 dark:text-zinc-300 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
          >
            <Bell className="h-3.5 w-3.5 text-slate-500" />
            <span className="font-mono text-[11px]">Alerts</span>
            {unacknowledgedAlertsCount > 0 && (
              <span className="flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-600 text-[10px] font-bold text-white px-1">
                {unacknowledgedAlertsCount}
              </span>
            )}
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-2 border-l border-slate-200 dark:border-zinc-800 pl-2.5">
            <span className="font-mono text-[11px] text-slate-500 dark:text-zinc-400 hidden md:inline">
              {userEmail || "demo@portfolioiq.io"}
            </span>
            <button
              onClick={onLogout}
              className="flex h-7 w-7 items-center justify-center rounded-sm text-slate-400 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
              title="Sign out"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace with Compact Sidebar */}
      <div className="flex flex-1 overflow-hidden">
        {/* Compact Sidebar */}
        <aside className="w-52 shrink-0 border-r border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900/60 p-2 flex flex-col justify-between select-none">
          <nav className="space-y-0.5">
            <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-zinc-500">
              Workspace
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={cn(
                    "flex w-full items-center justify-between rounded-sm px-2.5 py-1.5 text-xs font-medium transition-colors text-left",
                    isActive
                      ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                      : "text-slate-600 dark:text-zinc-400 hover:bg-slate-100 dark:hover:bg-zinc-800 hover:text-slate-900 dark:hover:text-zinc-100"
                  )}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className="h-3.5 w-3.5 shrink-0" />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span
                      className={cn(
                        "rounded-full px-1.5 py-0.2 text-[10px] font-bold font-mono",
                        isActive
                          ? "bg-white text-slate-900 dark:bg-zinc-900 dark:text-zinc-100"
                          : "bg-rose-600 text-white"
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          {/* Quick Terminal Meta */}
          <div className="rounded-sm border border-slate-100 dark:border-zinc-800/80 bg-slate-50 dark:bg-zinc-950/40 p-2 space-y-1 text-[11px] font-mono">
            <div className="text-[10px] text-slate-400 uppercase tracking-wider">Engine Status</div>
            <div className="flex items-center justify-between text-slate-600 dark:text-zinc-300">
              <span>Accounting</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between text-slate-600 dark:text-zinc-300">
              <span>Risk Engine</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Active</span>
            </div>
            <div className="flex items-center justify-between text-slate-600 dark:text-zinc-300">
              <span>WebSocket</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Online</span>
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-5 bg-slate-50/50 dark:bg-zinc-950">
          <div className="mx-auto max-w-7xl space-y-5">{children}</div>
        </main>
      </div>
    </div>
  );
};
