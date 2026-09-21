import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Sliders,
  AlertTriangle,
  Flame,
  Activity,
  Percent,
  TrendingDown,
  Layers,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { formatINR, formatPercent } from "../../lib/utils";
import { RiskMetricsProfile, StressTestResponse } from "../../types";
import { api } from "../../services/api";

interface RiskViewProps {
  portfolioId: string;
}

export const RiskView: React.FC<RiskViewProps> = ({ portfolioId }) => {
  const [riskData, setRiskData] = useState<RiskMetricsProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Stress testing workbench state
  const [marketShock, setMarketShock] = useState<number>(-10.0);
  const [customShocks, setCustomShocks] = useState<Record<string, number>>({
    TCS: -12.0,
    INFY: -8.0,
    RELIANCE: -15.0,
  });
  const [useCustomShocks, setUseCustomShocks] = useState(false);
  const [stressResult, setStressResult] = useState<StressTestResponse | null>(null);
  const [isStressTesting, setIsStressTesting] = useState(false);

  useEffect(() => {
    if (!portfolioId) return;
    setIsLoading(true);
    api.getRiskMetrics(portfolioId)
      .then((res) => {
        setRiskData(res);
      })
      .catch((err) => console.error("Error loading risk metrics:", err))
      .finally(() => setIsLoading(false));
  }, [portfolioId]);

  const handleRunStressTest = (shock: number = marketShock, isCustom: boolean = useCustomShocks) => {
    if (!portfolioId) return;
    setIsStressTesting(true);
    api.runStressTest({
      portfolio_id: portfolioId,
      market_shock_pct: isCustom ? 0 : shock,
      custom_shocks: isCustom ? customShocks : undefined,
    })
      .then((res) => setStressResult(res))
      .catch((err) => console.error("Error running stress test:", err))
      .finally(() => setIsStressTesting(false));
  };

  useEffect(() => {
    if (portfolioId) {
      handleRunStressTest(-10.0, false);
    }
  }, [portfolioId]);

  if (isLoading || !riskData) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-xs text-slate-400 font-mono">
          Computing quantitative risk profile and historical VaR...
        </div>
      </div>
    );
  }

  const m = riskData.metrics;

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
          Risk Analytics & Capital Adequacy
        </h2>
        <p className="text-[11px] text-slate-500 font-mono">
          Deterministic quantitative risk metrics, VaR percentiles, and stress testing workbench
        </p>
      </div>

      {/* Institutional Metric Strip */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-6 font-mono">
        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Annualized Volatility</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {m.volatility_annualized}%
            </div>
            <div className="text-[10px] text-slate-500">252-day historical</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Sharpe Ratio</div>
            <div className="text-lg font-bold text-emerald-700 dark:text-emerald-400">
              {m.sharpe_ratio}
            </div>
            <div className="text-[10px] text-slate-500">Rf = 6.5% T-bill</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Portfolio Beta</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {m.beta}
            </div>
            <div className="text-[10px] text-slate-500">vs NIFTY 50 benchmark</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Max Drawdown</div>
            <div className="text-lg font-bold text-rose-700 dark:text-rose-400">
              -{m.max_drawdown_pct}%
            </div>
            <div className="text-[10px] text-slate-500">Peak-to-trough</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">VaR 95% (1-Day)</div>
            <div className="text-lg font-bold text-rose-700 dark:text-rose-400">
              {formatINR(m.var_95_dollar)}
            </div>
            <div className="text-[10px] text-slate-500">
              {m.var_95_pct}% equity loss
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">VaR 99% (1-Day)</div>
            <div className="text-lg font-bold text-rose-700 dark:text-rose-400">
              {formatINR(m.var_99_dollar)}
            </div>
            <div className="text-[10px] text-slate-500">
              {m.var_99_pct}% tail risk
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Interactive Stress Testing Workbench */}
      <Card className="border-l-2 border-l-slate-900 dark:border-l-zinc-100">
        <CardHeader className="pb-3 pt-3 px-4 flex flex-row items-center justify-between">
          <div className="space-y-0.5">
            <CardTitle>Hypothetical Scenario & Stress Testing</CardTitle>
            <p className="text-[11px] text-slate-500 font-mono">
              Simulate macro market contractions and idiosyncratic single-asset drops
            </p>
          </div>
          <div className="flex items-center space-x-2 font-mono text-xs">
            {/* Quick Macro Shock Buttons */}
            {[-5, -10, -20].map((shock) => (
              <button
                key={shock}
                onClick={() => {
                  setMarketShock(shock);
                  setUseCustomShocks(false);
                  handleRunStressTest(shock, false);
                }}
                className={`px-2.5 py-1 rounded-sm border transition-colors ${
                  !useCustomShocks && marketShock === shock
                    ? "border-rose-600 bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300 font-bold"
                    : "border-slate-300 dark:border-zinc-700 text-slate-600 dark:text-zinc-400 hover:bg-slate-100"
                }`}
              >
                Market {shock}%
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent className="p-4 space-y-4">
          {stressResult && (
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 font-mono">
              <div className="rounded-sm border border-slate-200 dark:border-zinc-800 p-2.5 bg-slate-50 dark:bg-zinc-950/50">
                <div className="text-[10px] text-slate-400 uppercase">Current Equity</div>
                <div className="text-sm font-bold text-slate-900 dark:text-zinc-100">
                  {formatINR(stressResult.current_equity)}
                </div>
              </div>

              <div className="rounded-sm border border-slate-200 dark:border-zinc-800 p-2.5 bg-slate-50 dark:bg-zinc-950/50">
                <div className="text-[10px] text-slate-400 uppercase">Projected Equity</div>
                <div className="text-sm font-bold text-slate-900 dark:text-zinc-100">
                  {formatINR(stressResult.projected_equity)}
                </div>
              </div>

              <div className="rounded-sm border border-slate-200 dark:border-zinc-800 p-2.5 bg-slate-50 dark:bg-zinc-950/50">
                <div className="text-[10px] text-slate-400 uppercase">Estimated Loss</div>
                <div className="text-sm font-bold text-rose-700 dark:text-rose-400">
                  {formatINR(stressResult.total_dollar_change)}
                </div>
              </div>

              <div className="rounded-sm border border-slate-200 dark:border-zinc-800 p-2.5 bg-slate-50 dark:bg-zinc-950/50">
                <div className="text-[10px] text-slate-400 uppercase">Percentage Impact</div>
                <div className="text-sm font-bold text-rose-700 dark:text-rose-400">
                  {stressResult.total_percentage_change}%
                </div>
              </div>
            </div>
          )}

          {/* Position Impact Table */}
          {stressResult && (
            <div className="overflow-x-auto rounded-sm border border-slate-200 dark:border-zinc-800">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                  <tr>
                    <th className="px-3 py-2 font-medium">Position</th>
                    <th className="px-3 py-2 font-medium">Assumption</th>
                    <th className="px-3 py-2 font-medium text-right">Current Value</th>
                    <th className="px-3 py-2 font-medium text-right">Projected Value</th>
                    <th className="px-3 py-2 font-medium text-right">Dollar Impact</th>
                    <th className="px-3 py-2 font-medium text-right">% Change</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                  {stressResult.position_impacts.map((pos) => (
                    <tr key={pos.symbol} className="hover:bg-slate-50/70">
                      <td className="px-3 py-2 font-bold text-slate-900 dark:text-zinc-100">
                        {pos.symbol}
                      </td>
                      <td className="px-3 py-2 text-slate-500">{pos.assumption}</td>
                      <td className="px-3 py-2 text-right">{formatINR(pos.current_value)}</td>
                      <td className="px-3 py-2 text-right font-medium">
                        {formatINR(pos.projected_value)}
                      </td>
                      <td className="px-3 py-2 text-right text-rose-700 dark:text-rose-400 font-medium">
                        {formatINR(pos.dollar_change)}
                      </td>
                      <td className="px-3 py-2 text-right text-rose-700 dark:text-rose-400 font-bold">
                        {pos.percentage_change}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Concentration & Diversification Breakdown */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Diversification & Concentration Metrics</CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-3 font-mono text-xs">
            <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-zinc-800">
              <span className="text-slate-500">Herfindahl-Hirschman Index (HHI)</span>
              <span className="font-bold text-slate-900 dark:text-zinc-100">
                {m.herfindahl_index}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-zinc-800">
              <span className="text-slate-500">Top Position Concentration</span>
              <span className="font-bold text-slate-900 dark:text-zinc-100">
                {m.top_position_weight_pct}%
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-slate-100 dark:border-zinc-800">
              <span className="text-slate-500">Top 3 Holdings Concentration</span>
              <span className="font-bold text-slate-900 dark:text-zinc-100">
                {m.top_3_concentration_pct}%
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Sector Exposure Distribution</CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-2 font-mono text-xs">
            {Object.entries(riskData.exposure.sectors || {}).map(([sec, wt]) => (
              <div key={sec} className="flex justify-between items-center py-0.5">
                <span className="text-slate-600 dark:text-zinc-400">{sec}</span>
                <span className="font-semibold text-slate-900 dark:text-zinc-100">{wt}%</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
