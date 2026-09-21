import React, { useState, useEffect } from "react";
import { Binary, Clock, ShieldCheck, Activity } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { formatINR } from "../../lib/utils";
import { OptionsPortfolioData } from "../../types";
import { api } from "../../services/api";

interface OptionsViewProps {
  portfolioId: string;
}

export const OptionsView: React.FC<OptionsViewProps> = ({ portfolioId }) => {
  const [optionsData, setOptionsData] = useState<OptionsPortfolioData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!portfolioId) return;
    setIsLoading(true);
    api.getOptionsPositions(portfolioId)
      .then((res) => setOptionsData(res))
      .catch((err) => console.error("Error loading options data:", err))
      .finally(() => setIsLoading(false));
  }, [portfolioId]);

  if (isLoading || !optionsData) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-xs text-slate-400 font-mono">
          Evaluating options contracts and computing Greeks via Black-Scholes...
        </div>
      </div>
    );
  }

  const g = optionsData.aggregate_greeks;
  const exp = optionsData.expiration_exposure;

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
          Options Desk & Derivatives Greeks
        </h2>
        <p className="text-[11px] text-slate-500 font-mono">
          Live analytical Greeks, contract moneyness, and expiration horizon
        </p>
      </div>

      {/* Aggregate Portfolio Greeks Strip */}
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5 font-mono">
        <Card className="border-l-2 border-l-slate-900 dark:border-l-zinc-100">
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Portfolio Delta (Δ)</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {g.portfolio_delta}
            </div>
            <div className="text-[10px] text-slate-500">Underlying shares equivalent</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Portfolio Gamma (Γ)</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {g.portfolio_gamma}
            </div>
            <div className="text-[10px] text-slate-500">Δ sensitivity per ₹1 move</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Portfolio Theta (Θ)</div>
            <div className="text-lg font-bold text-rose-700 dark:text-rose-400">
              {formatINR(g.portfolio_theta)}
            </div>
            <div className="text-[10px] text-slate-500">Daily time decay</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Portfolio Vega (ν)</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {formatINR(g.portfolio_vega)}
            </div>
            <div className="text-[10px] text-slate-500">Per 1% IV shift</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-3 space-y-1">
            <div className="text-[10px] text-slate-400 uppercase">Options Market Value</div>
            <div className="text-lg font-bold text-slate-900 dark:text-zinc-100">
              {formatINR(g.total_options_market_value)}
            </div>
            <div className="text-[10px] text-slate-500">{optionsData.open_options_count} active contracts</div>
          </CardContent>
        </Card>
      </div>

      {/* Expiration Exposure Strip */}
      <div className="grid grid-cols-3 gap-3 font-mono text-xs">
        <Card className="p-3 flex items-center justify-between">
          <span className="text-slate-500">Expiring in ≤ 7 Days</span>
          <Badge variant={exp.expiring_within_7_days > 0 ? "warning" : "default"}>
            {exp.expiring_within_7_days} Contracts
          </Badge>
        </Card>
        <Card className="p-3 flex items-center justify-between">
          <span className="text-slate-500">Expiring in 8–30 Days</span>
          <Badge variant="default">{exp.expiring_8_to_30_days} Contracts</Badge>
        </Card>
        <Card className="p-3 flex items-center justify-between">
          <span className="text-slate-500">Expiring in &gt; 30 Days</span>
          <Badge variant="default">{exp.expiring_beyond_30_days} Contracts</Badge>
        </Card>
      </div>

      {/* Open Options Position Ledger */}
      <Card>
        <CardHeader className="pb-2 pt-3 px-4 flex flex-row items-center justify-between">
          <CardTitle>Open Derivatives Positions</CardTitle>
          <span className="text-[11px] font-mono text-slate-400">
            Model: Black-Scholes Analytical
          </span>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase select-none">
                <tr>
                  <th className="px-3.5 py-2.5 font-medium">Underlying</th>
                  <th className="px-3 py-2.5 font-medium">Type</th>
                  <th className="px-3 py-2.5 font-medium text-right">Strike</th>
                  <th className="px-3 py-2.5 font-medium text-right">Expiry</th>
                  <th className="px-3 py-2.5 font-medium text-right">Lots / Qty</th>
                  <th className="px-3 py-2.5 font-medium text-right">Avg Entry</th>
                  <th className="px-3 py-2.5 font-medium text-right">Theo Price</th>
                  <th className="px-3 py-2.5 font-medium text-right">Market Val</th>
                  <th className="px-3 py-2.5 font-medium text-right">P&L</th>
                  <th className="px-3 py-2.5 font-medium text-right">Delta (Δ)</th>
                  <th className="px-3 py-2.5 font-medium text-right">Theta (Θ)</th>
                  <th className="px-3 py-2.5 font-medium text-right">Vega (ν)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                {optionsData.positions.length === 0 ? (
                  <tr>
                    <td colSpan={12} className="py-8 text-center text-slate-400">
                      No open options positions in this portfolio.
                    </td>
                  </tr>
                ) : (
                  optionsData.positions.map((pos) => {
                    const c = pos.contract;
                    const isPos = parseFloat(pos.unrealized_pnl) >= 0;
                    return (
                      <tr key={pos.position_id} className="hover:bg-slate-50/70">
                        <td className="px-3.5 py-2">
                          <div className="font-bold text-slate-900 dark:text-zinc-100">
                            {c.symbol}
                          </div>
                          <div className="text-[10px] text-slate-400">
                            Spot: {formatINR(c.spot_price)}
                          </div>
                        </td>
                        <td className="px-3 py-2">
                          <Badge variant={c.option_type === "CALL" ? "profit" : "loss"}>
                            {c.option_type}
                          </Badge>
                        </td>
                        <td className="px-3 py-2 text-right font-medium">
                          {formatINR(c.strike_price)}
                        </td>
                        <td className="px-3 py-2 text-right text-slate-600 dark:text-zinc-400">
                          <div>{c.expiration_date}</div>
                          <div className="text-[10px] text-slate-400">{c.days_to_expiry}d left</div>
                        </td>
                        <td className="px-3 py-2 text-right font-medium">
                          {Number(pos.quantity).toFixed(0)} lots
                        </td>
                        <td className="px-3 py-2 text-right text-slate-600 dark:text-zinc-400">
                          {formatINR(pos.average_price)}
                        </td>
                        <td className="px-3 py-2 text-right font-medium text-slate-900 dark:text-zinc-100">
                          {formatINR(c.theoretical_price)}
                        </td>
                        <td className="px-3 py-2 text-right font-bold text-slate-900 dark:text-zinc-100">
                          {formatINR(pos.market_value)}
                        </td>
                        <td
                          className={`px-3 py-2 text-right font-bold ${
                            isPos
                              ? "text-emerald-700 dark:text-emerald-400"
                              : "text-rose-700 dark:text-rose-400"
                          }`}
                        >
                          {formatINR(pos.unrealized_pnl, true)}
                        </td>
                        <td className="px-3 py-2 text-right font-medium">
                          {pos.position_delta}
                        </td>
                        <td className="px-3 py-2 text-right text-rose-700 dark:text-rose-400 font-medium">
                          {formatINR(pos.position_theta)}
                        </td>
                        <td className="px-3 py-2 text-right font-medium">
                          {formatINR(pos.position_vega)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
