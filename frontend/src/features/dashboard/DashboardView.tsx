import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { TrendingUp, TrendingDown, DollarSign, Wallet, PieChart, Shield } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { formatINR, formatPercent } from "../../lib/utils";
import { PortfolioSummary, PerformanceCurvePoint } from "../../types";
import { api } from "../../services/api";

interface DashboardViewProps {
  summary: PortfolioSummary | null;
  portfolioId: string;
  onNavigateToTab: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  summary,
  portfolioId,
  onNavigateToTab,
}) => {
  const [timeframe, setTimeframe] = useState("3M");
  const [curveData, setCurveData] = useState<PerformanceCurvePoint[]>([]);
  const [showBenchmark, setShowBenchmark] = useState(true);
  const [isLoadingChart, setIsLoadingChart] = useState(false);

  useEffect(() => {
    if (!portfolioId) return;
    setIsLoadingChart(true);
    api.getPerformanceCurve(portfolioId, timeframe)
      .then((res) => {
        setCurveData(res.series || []);
      })
      .catch((err) => console.error("Error loading performance curve:", err))
      .finally(() => setIsLoadingChart(false));
  }, [portfolioId, timeframe]);

  if (!summary) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-xs text-slate-400 font-mono">Loading portfolio metrics...</div>
      </div>
    );
  }

  const isDayPositive = parseFloat(summary.day_pnl) >= 0;
  const isTotalPositive = parseFloat(summary.total_pnl) >= 0;

  // Compute sector distribution from positions
  const sectorWeights: Record<string, number> = {};
  summary.positions.forEach((pos) => {
    const s = pos.sector || "Unassigned";
    sectorWeights[s] = (sectorWeights[s] || 0) + Number(pos.weight_pct);
  });
  const sortedSectors = Object.entries(sectorWeights).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-5">
      {/* 5-Second Top Metrics Strip */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {/* Total Portfolio Equity */}
        <Card className="border-l-2 border-l-slate-900 dark:border-l-zinc-100">
          <CardContent className="p-3.5 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              <span>Portfolio Value</span>
              <Wallet className="h-3.5 w-3.5 text-slate-400" />
            </div>
            <div className="font-mono text-xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
              {formatINR(summary.total_equity)}
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              Cash: <span className="font-medium text-slate-700 dark:text-zinc-300">{formatINR(summary.cash_balance)}</span>
            </div>
          </CardContent>
        </Card>

        {/* Day P&L */}
        <Card>
          <CardContent className="p-3.5 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              <span>Day P&L</span>
              {isDayPositive ? (
                <TrendingUp className="h-3.5 w-3.5 text-emerald-600" />
              ) : (
                <TrendingDown className="h-3.5 w-3.5 text-rose-600" />
              )}
            </div>
            <div
              className={`font-mono text-xl font-bold tracking-tight ${
                isDayPositive ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
              }`}
            >
              {formatINR(summary.day_pnl, true)}
            </div>
            <div className="text-[11px] font-mono font-medium">
              <span
                className={
                  isDayPositive ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
                }
              >
                {formatPercent(summary.day_return_pct, true)}
              </span>
              <span className="text-slate-400 ml-1">today</span>
            </div>
          </CardContent>
        </Card>

        {/* Total Unrealized P&L */}
        <Card>
          <CardContent className="p-3.5 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              <span>Total P&L</span>
              <DollarSign className="h-3.5 w-3.5 text-slate-400" />
            </div>
            <div
              className={`font-mono text-xl font-bold tracking-tight ${
                isTotalPositive ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
              }`}
            >
              {formatINR(summary.total_pnl, true)}
            </div>
            <div className="text-[11px] font-mono font-medium">
              <span
                className={
                  isTotalPositive ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
                }
              >
                {formatPercent(summary.total_return_pct, true)}
              </span>
              <span className="text-slate-400 ml-1">all-time</span>
            </div>
          </CardContent>
        </Card>

        {/* Invested Capital */}
        <Card>
          <CardContent className="p-3.5 space-y-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 dark:text-zinc-400 uppercase tracking-wider">
              <span>Invested Capital</span>
              <span className="font-mono text-[10px] text-slate-400">
                {summary.positions_count} Holdings
              </span>
            </div>
            <div className="font-mono text-xl font-bold tracking-tight text-slate-900 dark:text-zinc-50">
              {formatINR(summary.invested_capital)}
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              Realized P&L:{" "}
              <span
                className={
                  parseFloat(summary.realized_pnl) >= 0
                    ? "text-emerald-700 dark:text-emerald-400 font-medium"
                    : "text-rose-700 dark:text-rose-400 font-medium"
                }
              >
                {formatINR(summary.realized_pnl, true)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Charts & Allocation Section */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
        {/* Performance Chart (2 Cols) */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2 pt-3 px-4">
            <div className="space-y-0.5">
              <CardTitle>Performance Trajectory</CardTitle>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">
                Equity growth vs. Benchmark NIFTY 50
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowBenchmark(!showBenchmark)}
                className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded-sm border transition-colors ${
                  showBenchmark
                    ? "border-slate-400 bg-slate-100 text-slate-900 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-100"
                    : "border-transparent text-slate-400 hover:text-slate-600"
                }`}
              >
                Benchmark (NIFTY)
              </button>
              {/* Timeframe Selectors */}
              <div className="flex rounded-sm border border-slate-200 dark:border-zinc-800 p-0.5 bg-slate-50 dark:bg-zinc-950 font-mono text-[10px]">
                {["1W", "1M", "3M", "6M", "1Y", "ALL"].map((tf) => (
                  <button
                    key={tf}
                    onClick={() => setTimeframe(tf)}
                    className={`px-2 py-0.5 rounded-sm font-medium transition-colors ${
                      timeframe === tf
                        ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950"
                        : "text-slate-500 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-100"
                    }`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-4 pt-2">
            <div className="h-64 w-full">
              {isLoadingChart ? (
                <div className="flex h-full items-center justify-center text-xs text-slate-400 font-mono">
                  Refreshing chart series...
                </div>
              ) : curveData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={curveData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="2 2" stroke="#e2e8f0" strokeOpacity={0.6} />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                      tickLine={false}
                      axisLine={{ stroke: "#cbd5e1" }}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                      tickLine={false}
                      axisLine={{ stroke: "#cbd5e1" }}
                      domain={["auto", "auto"]}
                      tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#334155",
                        borderRadius: "2px",
                        fontSize: "11px",
                        fontFamily: "monospace",
                        color: "#f8fafc",
                      }}
                      formatter={(val: any, name: any) => [
                        name === "total_equity" ? formatINR(val) : `${Number(val).toFixed(2)}%`,
                        name === "total_equity" ? "Equity" : "Benchmark",
                      ]}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Line
                      type="monotone"
                      dataKey="total_equity"
                      stroke="#0f172a"
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4, strokeWidth: 0, fill: "#0f172a" }}
                    />
                    {showBenchmark && (
                      <Line
                        type="monotone"
                        dataKey="benchmark_return_pct"
                        stroke="#94a3b8"
                        strokeWidth={1.5}
                        strokeDasharray="4 4"
                        dot={false}
                        yAxisId={0}
                      />
                    )}
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-xs text-slate-400 font-mono">
                  No snapshot history available yet.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Sector Exposure Breakdown (1 Col) */}
        <Card>
          <CardHeader className="pb-2 pt-3 px-4 flex flex-row items-center justify-between">
            <CardTitle>Sector Exposure</CardTitle>
            <PieChart className="h-3.5 w-3.5 text-slate-400" />
          </CardHeader>
          <CardContent className="p-4 pt-1 space-y-3">
            {sortedSectors.map(([sector, weight]) => (
              <div key={sector} className="space-y-1">
                <div className="flex justify-between text-xs font-mono">
                  <span className="truncate text-slate-700 dark:text-zinc-300">{sector}</span>
                  <span className="font-semibold text-slate-900 dark:text-zinc-100">
                    {weight.toFixed(1)}%
                  </span>
                </div>
                <div className="h-1.5 w-full rounded-sm bg-slate-100 dark:bg-zinc-800 overflow-hidden">
                  <div
                    className="h-full bg-slate-900 dark:bg-zinc-200 transition-all duration-300"
                    style={{ width: `${Math.min(100, weight)}%` }}
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Top Holdings Overview Strip */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2 pt-3 px-4">
          <div>
            <CardTitle>Top Holdings Glance</CardTitle>
            <p className="text-[11px] text-slate-500 dark:text-zinc-400 font-mono">
              Positions ranked by total portfolio weight
            </p>
          </div>
          <button
            onClick={() => onNavigateToTab("holdings")}
            className="text-xs font-mono text-slate-700 dark:text-zinc-300 hover:underline"
          >
            View Full Holdings Table →
          </button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-zinc-950/60 border-y border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                <tr>
                  <th className="px-4 py-2 font-medium">Instrument</th>
                  <th className="px-4 py-2 font-medium">Asset Class</th>
                  <th className="px-4 py-2 font-medium text-right">LTP</th>
                  <th className="px-4 py-2 font-medium text-right">Day P&L</th>
                  <th className="px-4 py-2 font-medium text-right">Total Return</th>
                  <th className="px-4 py-2 font-medium text-right">Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                {summary.positions.slice(0, 6).map((pos) => {
                  const dayPos = parseFloat(pos.day_pnl) >= 0;
                  const retPos = pos.total_return_pct >= 0;
                  return (
                    <tr
                      key={pos.id}
                      className="hover:bg-slate-50/80 dark:hover:bg-zinc-800/40 transition-colors"
                    >
                      <td className="px-4 py-2.5">
                        <div className="font-semibold text-slate-900 dark:text-zinc-100">
                          {pos.symbol}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate max-w-[180px]">
                          {pos.name}
                        </div>
                      </td>
                      <td className="px-4 py-2.5 text-slate-600 dark:text-zinc-400">
                        {pos.asset_class}
                      </td>
                      <td className="px-4 py-2.5 text-right font-medium">
                        {formatINR(pos.ltp)}
                      </td>
                      <td
                        className={`px-4 py-2.5 text-right ${
                          dayPos
                            ? "text-emerald-700 dark:text-emerald-400"
                            : "text-rose-700 dark:text-rose-400"
                        }`}
                      >
                        {formatINR(pos.day_pnl, true)} ({formatPercent(pos.day_change_pct, true)})
                      </td>
                      <td
                        className={`px-4 py-2.5 text-right ${
                          retPos
                            ? "text-emerald-700 dark:text-emerald-400"
                            : "text-rose-700 dark:text-rose-400"
                        }`}
                      >
                        {formatPercent(pos.total_return_pct, true)}
                      </td>
                      <td className="px-4 py-2.5 text-right font-semibold">
                        {Number(pos.weight_pct).toFixed(2)}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
