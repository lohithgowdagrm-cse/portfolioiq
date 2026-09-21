import React, { useState, useMemo } from "react";
import {
  ArrowUpDown,
  Search,
  SlidersHorizontal,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  Plus,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Badge } from "../../components/ui/Badge";
import { formatINR, formatPercent } from "../../lib/utils";
import { PositionRow, PortfolioSummary } from "../../types";

interface HoldingsViewProps {
  summary: PortfolioSummary | null;
  onOpenTradeModal?: (symbol?: string) => void;
}

type SortField =
  | "symbol"
  | "quantity"
  | "average_buy_price"
  | "ltp"
  | "invested_capital"
  | "current_value"
  | "day_pnl"
  | "unrealized_pnl"
  | "total_return_pct"
  | "weight_pct";

export const HoldingsView: React.FC<HoldingsViewProps> = ({
  summary,
  onOpenTradeModal,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [sectorFilter, setSectorFilter] = useState("ALL");
  const [sortField, setSortField] = useState<SortField>("weight_pct");
  const [sortAsc, setSortAsc] = useState(false);

  // Column visibility toggles
  const [visibleColumns, setVisibleColumns] = useState({
    qty: true,
    avgPrice: true,
    ltp: true,
    invested: true,
    currentValue: true,
    dayPnl: true,
    totalPnl: true,
    returnPct: true,
    weight: true,
  });
  const [showColMenu, setShowColMenu] = useState(false);

  const positions = summary?.positions || [];

  // Extract unique sectors
  const sectors = useMemo(() => {
    const set = new Set<string>();
    positions.forEach((p) => {
      if (p.sector) set.add(p.sector);
    });
    return ["ALL", ...Array.from(set)];
  }, [positions]);

  // Filter and sort positions
  const filteredPositions = useMemo(() => {
    return positions
      .filter((pos) => {
        const matchesSearch =
          pos.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
          pos.name.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesSector = sectorFilter === "ALL" || pos.sector === sectorFilter;
        return matchesSearch && matchesSector;
      })
      .sort((a, b) => {
        let valA: any = a[sortField];
        let valB: any = b[sortField];

        if (
          [
            "quantity",
            "average_buy_price",
            "ltp",
            "invested_capital",
            "current_value",
            "day_pnl",
            "unrealized_pnl",
            "total_return_pct",
            "weight_pct",
          ].includes(sortField)
        ) {
          valA = parseFloat(valA) || 0;
          valB = parseFloat(valB) || 0;
        }

        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
      });
  }, [positions, searchQuery, sectorFilter, sortField, sortAsc]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false); // Default descending for financial metrics
    }
  };

  if (!summary) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-xs text-slate-400 font-mono">Loading holdings ledger...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with Search and Quick Actions */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
            Portfolio Holdings Ledger
          </h2>
          <p className="text-[11px] text-slate-500 font-mono">
            {filteredPositions.length} active positions • Reconciled against ledger
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Search Input */}
          <div className="relative w-48">
            <Search className="pointer-events-none absolute left-2.5 top-2.5 h-3 w-3 text-slate-400" />
            <input
              type="text"
              placeholder="Filter ticker..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 pl-7 pr-2.5 text-xs font-mono text-slate-900 dark:text-zinc-100 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-900 dark:focus:ring-zinc-400"
            />
          </div>

          {/* Sector Filter */}
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            className="h-8 rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-2 text-xs font-mono text-slate-800 dark:text-zinc-200 focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer"
          >
            {sectors.map((s) => (
              <option key={s} value={s}>
                {s === "ALL" ? "All Sectors" : s}
              </option>
            ))}
          </select>

          {/* Column Toggle */}
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowColMenu(!showColMenu)}
              className="h-8 text-xs font-mono text-slate-600 dark:text-zinc-400"
            >
              <SlidersHorizontal className="mr-1.5 h-3 w-3" />
              Columns
            </Button>
            {showColMenu && (
              <div className="absolute right-0 mt-1 z-30 w-44 rounded-sm border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-2 shadow-lg space-y-1 text-[11px] font-mono">
                {Object.entries(visibleColumns).map(([key, val]) => (
                  <label key={key} className="flex items-center space-x-2 cursor-pointer py-0.5">
                    <input
                      type="checkbox"
                      checked={val}
                      onChange={() =>
                        setVisibleColumns((prev) => ({ ...prev, [key]: !val }))
                      }
                      className="rounded-sm border-slate-300 text-slate-900"
                    />
                    <span className="capitalize">{key.replace(/([A-Z])/g, " $1")}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {onOpenTradeModal && (
            <Button size="sm" onClick={() => onOpenTradeModal()} className="h-8">
              <Plus className="mr-1 h-3.5 w-3.5" />
              Trade
            </Button>
          )}
        </div>
      </div>

      {/* High Density Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase select-none sticky top-0">
                <tr>
                  <th
                    onClick={() => handleSort("symbol")}
                    className="px-3.5 py-2.5 font-medium cursor-pointer hover:text-slate-900 dark:hover:text-zinc-100"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Instrument</span>
                      <ArrowUpDown className="h-2.5 w-2.5" />
                    </div>
                  </th>
                  {visibleColumns.qty && (
                    <th
                      onClick={() => handleSort("quantity")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Qty
                    </th>
                  )}
                  {visibleColumns.avgPrice && (
                    <th
                      onClick={() => handleSort("average_buy_price")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Avg Price
                    </th>
                  )}
                  {visibleColumns.ltp && (
                    <th
                      onClick={() => handleSort("ltp")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      LTP
                    </th>
                  )}
                  {visibleColumns.invested && (
                    <th
                      onClick={() => handleSort("invested_capital")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Invested
                    </th>
                  )}
                  {visibleColumns.currentValue && (
                    <th
                      onClick={() => handleSort("current_value")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Current Val
                    </th>
                  )}
                  {visibleColumns.dayPnl && (
                    <th
                      onClick={() => handleSort("day_pnl")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Day P&L
                    </th>
                  )}
                  {visibleColumns.totalPnl && (
                    <th
                      onClick={() => handleSort("unrealized_pnl")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Total P&L
                    </th>
                  )}
                  {visibleColumns.returnPct && (
                    <th
                      onClick={() => handleSort("total_return_pct")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Return
                    </th>
                  )}
                  {visibleColumns.weight && (
                    <th
                      onClick={() => handleSort("weight_pct")}
                      className="px-3 py-2.5 font-medium text-right cursor-pointer hover:text-slate-900"
                    >
                      Weight
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                {filteredPositions.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="py-8 text-center text-slate-400">
                      No holdings match your filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredPositions.map((pos) => {
                    const dayPos = parseFloat(pos.day_pnl) >= 0;
                    const retPos = pos.total_return_pct >= 0;

                    return (
                      <tr
                        key={pos.id}
                        className="hover:bg-slate-50/90 dark:hover:bg-zinc-800/50 transition-colors"
                      >
                        <td className="px-3.5 py-2">
                          <div className="font-bold text-slate-900 dark:text-zinc-100">
                            {pos.symbol}
                          </div>
                          <div className="text-[10px] text-slate-400 truncate max-w-[170px]">
                            {pos.name}
                          </div>
                        </td>
                        {visibleColumns.qty && (
                          <td className="px-3 py-2 text-right font-medium text-slate-800 dark:text-zinc-200">
                            {Number(pos.quantity).toFixed(2)}
                          </td>
                        )}
                        {visibleColumns.avgPrice && (
                          <td className="px-3 py-2 text-right text-slate-600 dark:text-zinc-400">
                            {formatINR(pos.average_buy_price)}
                          </td>
                        )}
                        {visibleColumns.ltp && (
                          <td className="px-3 py-2 text-right font-bold text-slate-900 dark:text-zinc-100">
                            {formatINR(pos.ltp)}
                          </td>
                        )}
                        {visibleColumns.invested && (
                          <td className="px-3 py-2 text-right text-slate-600 dark:text-zinc-400">
                            {formatINR(pos.invested_capital)}
                          </td>
                        )}
                        {visibleColumns.currentValue && (
                          <td className="px-3 py-2 text-right font-bold text-slate-900 dark:text-zinc-100">
                            {formatINR(pos.current_value)}
                          </td>
                        )}
                        {visibleColumns.dayPnl && (
                          <td
                            className={`px-3 py-2 text-right ${
                              dayPos
                                ? "text-emerald-700 dark:text-emerald-400"
                                : "text-rose-700 dark:text-rose-400"
                            }`}
                          >
                            <div className="font-semibold">{formatINR(pos.day_pnl, true)}</div>
                            <div className="text-[10px]">
                              {formatPercent(pos.day_change_pct, true)}
                            </div>
                          </td>
                        )}
                        {visibleColumns.totalPnl && (
                          <td
                            className={`px-3 py-2 text-right font-semibold ${
                              retPos
                                ? "text-emerald-700 dark:text-emerald-400"
                                : "text-rose-700 dark:text-rose-400"
                            }`}
                          >
                            {formatINR(pos.unrealized_pnl, true)}
                          </td>
                        )}
                        {visibleColumns.returnPct && (
                          <td
                            className={`px-3 py-2 text-right font-semibold ${
                              retPos
                                ? "text-emerald-700 dark:text-emerald-400"
                                : "text-rose-700 dark:text-rose-400"
                            }`}
                          >
                            {formatPercent(pos.total_return_pct, true)}
                          </td>
                        )}
                        {visibleColumns.weight && (
                          <td className="px-3 py-2 text-right font-semibold text-slate-800 dark:text-zinc-200">
                            {Number(pos.weight_pct).toFixed(2)}%
                          </td>
                        )}
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
