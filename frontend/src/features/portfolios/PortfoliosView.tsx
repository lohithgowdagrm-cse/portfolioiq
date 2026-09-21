import React, { useState } from "react";
import { Briefcase, Plus, CheckCircle2 } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { formatINR, formatPercent } from "../../lib/utils";
import { PortfolioListItem } from "../../types";
import { api } from "../../services/api";

interface PortfoliosViewProps {
  portfolios: PortfolioListItem[];
  selectedPortfolioId: string;
  onSelectPortfolio: (id: string) => void;
  onRefreshPortfolios: () => void;
}

export const PortfoliosView: React.FC<PortfoliosViewProps> = ({
  portfolios,
  selectedPortfolioId,
  onSelectPortfolio,
  onRefreshPortfolios,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [currency, setCurrency] = useState("INR");
  const [initialCash, setInitialCash] = useState("250000");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    try {
      await api.createPortfolio({
        name,
        description,
        base_currency: currency,
        cash_balance: initialCash,
      });
      setIsModalOpen(false);
      setName("");
      setDescription("");
      onRefreshPortfolios();
    } catch (err: any) {
      alert(err.message || "Failed to create portfolio.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
            Portfolio Management
          </h2>
          <p className="text-[11px] text-slate-500 font-mono">
            Multi-strategy segregation, ledger accounts, and capital deployment
          </p>
        </div>

        <Button size="sm" onClick={() => setIsModalOpen(true)} className="h-8">
          <Plus className="mr-1 h-3.5 w-3.5" />
          Create Portfolio
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {portfolios.map((p) => {
          const isSelected = p.id === selectedPortfolioId;
          const isPos = p.total_return_pct >= 0;

          return (
            <Card
              key={p.id}
              className={`cursor-pointer transition-all ${
                isSelected
                  ? "border-slate-900 dark:border-zinc-100 ring-1 ring-slate-900 dark:ring-zinc-100"
                  : "hover:border-slate-300 dark:hover:border-zinc-700"
              }`}
              onClick={() => onSelectPortfolio(p.id)}
            >
              <CardHeader className="pb-2 pt-3 px-4 flex flex-row items-start justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-slate-900 dark:text-zinc-100 font-mono text-sm">
                      {p.name}
                    </h3>
                    {p.is_default && <Badge variant="outline">DEFAULT</Badge>}
                  </div>
                  <p className="text-[11px] text-slate-500 font-mono line-clamp-2 mt-0.5">
                    {p.description || "Active strategy account"}
                  </p>
                </div>
                {isSelected && (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
                )}
              </CardHeader>
              <CardContent className="p-4 pt-2 space-y-3 font-mono text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-zinc-800">
                  <span className="text-slate-500">Portfolio Value</span>
                  <span className="font-bold text-slate-900 dark:text-zinc-100">
                    {formatINR(p.total_equity)}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-zinc-800">
                  <span className="text-slate-500">Cash Reserve</span>
                  <span className="font-medium text-slate-700 dark:text-zinc-300">
                    {formatINR(p.cash_balance)}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100 dark:border-zinc-800">
                  <span className="text-slate-500">Total Return</span>
                  <span
                    className={`font-semibold ${
                      isPos ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
                    }`}
                  >
                    {formatINR(p.unrealized_pnl, true)} ({formatPercent(p.total_return_pct, true)})
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Positions</span>
                  <span className="font-medium text-slate-700 dark:text-zinc-300">
                    {p.positions_count} assets
                  </span>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Create Portfolio Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Investment Portfolio"
      >
        <form onSubmit={handleCreate} className="space-y-3 font-mono text-xs">
          <Input
            label="Portfolio Name"
            placeholder="e.g. Quantitative Macro Long/Short"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <div className="space-y-1">
            <label className="text-slate-600 dark:text-zinc-400">Description</label>
            <input
              type="text"
              placeholder="Investment mandate & risk parameters"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2.5 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-slate-600 dark:text-zinc-400">Base Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2.5 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer"
              >
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>
            <Input
              label="Starting Cash Reserve"
              type="number"
              step="any"
              value={initialCash}
              onChange={(e) => setInitialCash(e.target.value)}
              required
            />
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100 dark:border-zinc-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={isSubmitting}>
              Create Portfolio
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
