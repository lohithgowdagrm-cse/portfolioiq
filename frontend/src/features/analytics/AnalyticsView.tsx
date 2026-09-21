import React, { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { formatPercent, formatINR } from "../../lib/utils";
import { api } from "../../services/api";
import { PortfolioSummary } from "../../types";

interface AnalyticsViewProps {
  portfolioId: string;
  summary: PortfolioSummary | null;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ portfolioId, summary }) => {
  const [curveData, setCurveData] = useState<any[]>([]);
  const [matrixData, setMatrixData] = useState<any[]>([]);
  const [exposureData, setExposureData] = useState<any>(null);
  const [timeframe, setTimeframe] = useState("6M");

  useEffect(() => {
    if (!portfolioId) return;
    api.getPerformanceCurve(portfolioId, timeframe).then((res) => {
      setCurveData(res.series || []);
    });
    api.getMonthlyMatrix().then((res) => {
      setMatrixData(res.matrix || []);
    });
    api.getExposure(portfolioId).then((res) => {
      setExposureData(res);
    });
  }, [portfolioId, timeframe]);

  // Transform curve data for underwater drawdown curve
  let peak = 0;
  const drawdownData = curveData.map((pt) => {
    if (pt.total_equity > peak) peak = pt.total_equity;
    const dd = peak > 0 ? ((peak - pt.total_equity) / peak) * 100.0 : 0;
    return {
      date: pt.date,
      drawdown: -round2(dd),
    };
  });

  function round2(num: number) {
    return Math.round(num * 100) / 100;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
            Portfolio Performance & Return Attribution
          </h2>
          <p className="text-[11px] text-slate-500 font-mono">
            Analytical return curves, monthly performance matrix, and drawdown depth
          </p>
        </div>

        <div className="flex rounded-sm border border-slate-200 dark:border-zinc-800 p-0.5 bg-white dark:bg-zinc-900 font-mono text-[11px]">
          {["1M", "3M", "6M", "1Y", "ALL"].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-2.5 py-0.5 rounded-sm transition-colors ${
                timeframe === tf
                  ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Cumulative Return Curve vs Benchmark */}
      <Card>
        <CardHeader className="pb-2 pt-3 px-4 flex flex-row items-center justify-between">
          <div>
            <CardTitle>Cumulative Return Curve (%)</CardTitle>
            <p className="text-[11px] text-slate-500 font-mono">
              Normalized relative performance vs NIFTY 50 benchmark
            </p>
          </div>
          <div className="flex items-center space-x-3 text-[11px] font-mono">
            <span className="flex items-center space-x-1 text-slate-900 dark:text-zinc-100 font-semibold">
              <span className="inline-block h-2 w-2 bg-slate-900 dark:bg-zinc-100" />
              <span>Portfolio</span>
            </span>
            <span className="flex items-center space-x-1 text-slate-400">
              <span className="inline-block h-2 w-2 bg-slate-400" />
              <span>NIFTY 50</span>
            </span>
          </div>
        </CardHeader>
        <CardContent className="p-4 pt-1">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={curveData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="2 2" stroke="#e2e8f0" strokeOpacity={0.6} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                  tickLine={false}
                  tickFormatter={(val) => `${val}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "11px",
                    fontFamily: "monospace",
                    color: "#f8fafc",
                  }}
                  formatter={(val: any) => [`${Number(val).toFixed(2)}%`]}
                />
                <Line
                  type="monotone"
                  dataKey="portfolio_return_pct"
                  name="Portfolio"
                  stroke="#0f172a"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="benchmark_return_pct"
                  name="NIFTY 50"
                  stroke="#94a3b8"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Drawdown Underwater Curve */}
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Historical Underwater Drawdown (%)</CardTitle>
            <p className="text-[11px] text-slate-500 font-mono">
              Peak-to-trough decline tracking capital preservation
            </p>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-52 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={drawdownData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#e2e8f0" strokeOpacity={0.6} />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                    tickLine={false}
                    tickFormatter={(val) => `${val}%`}
                    domain={[-15, 0]}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      borderColor: "#334155",
                      fontSize: "11px",
                      fontFamily: "monospace",
                      color: "#f8fafc",
                    }}
                    formatter={(val: any) => [`${val}%`, "Drawdown"]}
                  />
                  <Area
                    type="monotone"
                    dataKey="drawdown"
                    stroke="#e11d48"
                    fill="#ffe4e6"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Position Weight & Return Contribution */}
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Holding Performance Contribution</CardTitle>
            <p className="text-[11px] text-slate-500 font-mono">
              Individual asset total percentage return
            </p>
          </CardHeader>
          <CardContent className="p-4 pt-1">
            <div className="h-52 w-full">
              {summary && summary.positions ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={summary.positions.slice(0, 8)}
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="2 2" stroke="#e2e8f0" strokeOpacity={0.6} />
                    <XAxis
                      dataKey="symbol"
                      tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: "#64748b", fontFamily: "monospace" }}
                      tickLine={false}
                      tickFormatter={(val) => `${val}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0f172a",
                        borderColor: "#334155",
                        fontSize: "11px",
                        fontFamily: "monospace",
                        color: "#f8fafc",
                      }}
                      formatter={(val: any) => [`${Number(val).toFixed(2)}%`, "Total Return"]}
                    />
                    <Bar dataKey="total_return_pct" fill="#0f172a" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : null}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Monthly Return Matrix (Heatmap) */}
      <Card>
        <CardHeader className="pb-2 pt-3 px-4">
          <CardTitle>Monthly Return Matrix Heatmap (%)</CardTitle>
          <p className="text-[11px] text-slate-500 font-mono">
            Calendar year and month historical returns
          </p>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-center text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-zinc-950/80 border-y border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                <tr>
                  <th className="px-3 py-2 text-left">Year</th>
                  {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map(
                    (m) => (
                      <th key={m} className="px-2 py-2 font-medium">
                        {m}
                      </th>
                    )
                  )}
                  <th className="px-3 py-2 font-semibold">Annual</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                {matrixData.map((row) => (
                  <tr key={row.year} className="hover:bg-slate-50/60">
                    <td className="px-3 py-2.5 text-left font-bold text-slate-900 dark:text-zinc-100">
                      {row.year}
                    </td>
                    {["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map(
                      (m) => {
                        const val = row.months[m];
                        if (val === undefined) {
                          return (
                            <td key={m} className="px-2 py-2.5 text-slate-300 dark:text-zinc-700">
                              —
                            </td>
                          );
                        }
                        const isPos = val >= 0;
                        return (
                          <td key={m} className="px-2 py-2.5">
                            <span
                              className={`px-1.5 py-0.5 rounded-sm font-medium ${
                                isPos
                                  ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400"
                                  : "bg-rose-50 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400"
                              }`}
                            >
                              {val > 0 ? `+${val.toFixed(1)}%` : `${val.toFixed(1)}%`}
                            </span>
                          </td>
                        );
                      }
                    )}
                    <td className="px-3 py-2.5 font-bold text-slate-900 dark:text-zinc-100">
                      +{row.annual}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
