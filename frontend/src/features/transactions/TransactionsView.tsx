import React, { useState, useEffect } from "react";
import { Plus, Trash2, Filter, Receipt, RefreshCw } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { formatINR } from "../../lib/utils";
import { TransactionItem } from "../../types";
import { api } from "../../services/api";

interface TransactionsViewProps {
  portfolioId: string;
  onTransactionUpdated: () => void;
  isTradeModalOpen?: boolean;
  setIsTradeModalOpen?: (open: boolean) => void;
}

export const TransactionsView: React.FC<TransactionsViewProps> = ({
  portfolioId,
  onTransactionUpdated,
  isTradeModalOpen,
  setIsTradeModalOpen,
}) => {
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [typeFilter, setTypeFilter] = useState("ALL");
  const [localModalOpen, setLocalModalOpen] = useState(false);
  const [instruments, setInstruments] = useState<any[]>([]);

  // Form State
  const [selectedInst, setSelectedInst] = useState("");
  const [txType, setTxType] = useState("BUY");
  const [quantity, setQuantity] = useState("10");
  const [price, setPrice] = useState("1000");
  const [fees, setFees] = useState("20");
  const [taxes, setTaxes] = useState("10");
  const [notes, setNotes] = useState("");
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const modalOpen = isTradeModalOpen !== undefined ? isTradeModalOpen : localModalOpen;
  const setModalOpen = setIsTradeModalOpen || setLocalModalOpen;

  const loadTransactions = () => {
    if (!portfolioId) return;
    setIsLoading(true);
    api.getTransactions({
      portfolio_id: portfolioId,
      type: typeFilter === "ALL" ? undefined : typeFilter,
    })
      .then((res) => setTransactions(res.results || []))
      .catch((err) => console.error("Error loading transactions:", err))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadTransactions();
  }, [portfolioId, typeFilter]);

  useEffect(() => {
    api.getInstruments().then((res) => {
      setInstruments(res.results || []);
      if (res.results && res.results.length > 0 && !selectedInst) {
        setSelectedInst(res.results[0].id);
        setPrice(res.results[0].latest_price || "1000");
      }
    });
  }, []);

  const handleInstrumentChange = (instId: string) => {
    setSelectedInst(instId);
    const inst = instruments.find((i) => i.id === instId);
    if (inst && inst.latest_price) {
      setPrice(inst.latest_price);
    }
  };

  const handleSubmitTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");

    const q = parseFloat(quantity);
    const p = parseFloat(price);

    if (!q || q <= 0) {
      setFormError("Quantity must be strictly greater than zero.");
      return;
    }
    if (p < 0) {
      setFormError("Price cannot be negative.");
      return;
    }

    setIsSubmitting(true);
    try {
      await api.recordTransaction({
        portfolio: portfolioId,
        instrument: selectedInst,
        transaction_type: txType,
        quantity: quantity,
        price: price,
        fees: fees || "0",
        taxes: taxes || "0",
        notes: notes,
      });
      setModalOpen(false);
      setNotes("");
      loadTransactions();
      onTransactionUpdated();
    } catch (err: any) {
      setFormError(err.message || "Failed to record transaction.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (txId: string) => {
    if (!confirm("Are you sure you want to delete this transaction? All portfolio balances will be reconciled.")) {
      return;
    }
    try {
      await api.deleteTransaction(txId);
      loadTransactions();
      onTransactionUpdated();
    } catch (err: any) {
      alert(err.message || "Failed to delete transaction.");
    }
  };

  const getBadgeVariant = (type: string) => {
    switch (type) {
      case "BUY":
        return "profit";
      case "SELL":
        return "loss";
      case "DIVIDEND":
        return "default";
      default:
        return "outline";
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
            Transaction Ledger
          </h2>
          <p className="text-[11px] text-slate-500 font-mono">
            Immutable trade records and audit trail • Reconciles positions atomically
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Type Filter Chips */}
          <div className="flex rounded-sm border border-slate-200 dark:border-zinc-800 p-0.5 bg-white dark:bg-zinc-900 font-mono text-[11px]">
            {["ALL", "BUY", "SELL", "DIVIDEND"].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`px-2 py-0.5 rounded-sm transition-colors ${
                  typeFilter === t
                    ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                    : "text-slate-500 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          <Button size="sm" onClick={() => setModalOpen(true)} className="h-8">
            <Plus className="mr-1 h-3.5 w-3.5" />
            Record Trade
          </Button>
        </div>
      </div>

      {/* Transaction Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase select-none">
                <tr>
                  <th className="px-3.5 py-2.5 font-medium">Type</th>
                  <th className="px-3.5 py-2.5 font-medium">Timestamp</th>
                  <th className="px-3.5 py-2.5 font-medium">Instrument</th>
                  <th className="px-3 py-2.5 font-medium text-right">Qty</th>
                  <th className="px-3 py-2.5 font-medium text-right">Price</th>
                  <th className="px-3 py-2.5 font-medium text-right">Fees & Taxes</th>
                  <th className="px-3 py-2.5 font-medium text-right">Total Cash Impact</th>
                  <th className="px-3.5 py-2.5 font-medium">Notes</th>
                  <th className="px-2 py-2.5 text-center font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                {isLoading ? (
                  <tr>
                    <td colSpan={9} className="py-8 text-center text-slate-400">
                      Loading ledger records...
                    </td>
                  </tr>
                ) : transactions.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-8 text-center text-slate-400">
                      No transactions found for this portfolio.
                    </td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr
                      key={tx.id}
                      className="hover:bg-slate-50/90 dark:hover:bg-zinc-800/50 transition-colors"
                    >
                      <td className="px-3.5 py-2">
                        <Badge variant={getBadgeVariant(tx.transaction_type)}>
                          {tx.transaction_type}
                        </Badge>
                      </td>
                      <td className="px-3.5 py-2 text-slate-500 whitespace-nowrap">
                        {tx.executed_at ? new Date(tx.executed_at).toLocaleDateString() : "-"}
                      </td>
                      <td className="px-3.5 py-2">
                        <div className="font-bold text-slate-900 dark:text-zinc-100">
                          {tx.symbol}
                        </div>
                        <div className="text-[10px] text-slate-400 truncate max-w-[140px]">
                          {tx.instrument_name}
                        </div>
                      </td>
                      <td className="px-3 py-2 text-right font-medium text-slate-800 dark:text-zinc-200">
                        {Number(tx.quantity).toFixed(2)}
                      </td>
                      <td className="px-3 py-2 text-right text-slate-700 dark:text-zinc-300">
                        {formatINR(tx.price)}
                      </td>
                      <td className="px-3 py-2 text-right text-slate-500">
                        {formatINR(parseFloat(tx.fees || "0") + parseFloat(tx.taxes || "0"))}
                      </td>
                      <td className="px-3 py-2 text-right font-bold text-slate-900 dark:text-zinc-100">
                        {formatINR(tx.total_amount)}
                      </td>
                      <td className="px-3.5 py-2 text-slate-500 text-[11px] truncate max-w-[180px]">
                        {tx.notes || "—"}
                      </td>
                      <td className="px-2 py-2 text-center">
                        <button
                          onClick={() => handleDelete(tx.id)}
                          className="rounded-sm p-1 text-slate-400 hover:text-rose-600 hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
                          title="Delete transaction and reconcile ledger"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Record Transaction Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Record Financial Transaction"
      >
        <form onSubmit={handleSubmitTransaction} className="space-y-3 font-mono text-xs">
          {formError && (
            <div className="rounded-sm border border-rose-200 bg-rose-50 dark:bg-rose-950/40 p-2 text-rose-700 dark:text-rose-400 text-xs">
              {formError}
            </div>
          )}

          <div className="space-y-1">
            <label className="text-slate-600 dark:text-zinc-400">Instrument Universe</label>
            <select
              value={selectedInst}
              onChange={(e) => handleInstrumentChange(e.target.value)}
              className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2.5 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer"
            >
              {instruments.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.symbol} — {i.name} ({i.currency})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-slate-600 dark:text-zinc-400">Type</label>
              <select
                value={txType}
                onChange={(e) => setTxType(e.target.value)}
                className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2.5 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900 cursor-pointer"
              >
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
                <option value="DIVIDEND">DIVIDEND</option>
                <option value="SPLIT">STOCK SPLIT</option>
                <option value="BONUS">BONUS SHARES</option>
              </select>
            </div>
            <Input
              label="Quantity"
              type="number"
              step="any"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-2">
            <Input
              label="Price (₹)"
              type="number"
              step="any"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
            />
            <Input
              label="Brokerage Fees"
              type="number"
              step="any"
              value={fees}
              onChange={(e) => setFees(e.target.value)}
            />
            <Input
              label="STT & Taxes"
              type="number"
              step="any"
              value={taxes}
              onChange={(e) => setTaxes(e.target.value)}
            />
          </div>

          {/* Cash impact estimate */}
          <div className="rounded-sm border border-slate-200 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-950 p-2 text-[11px] text-slate-600 dark:text-zinc-400 flex justify-between">
            <span>Estimated Cash Impact:</span>
            <span className="font-bold text-slate-900 dark:text-zinc-100">
              {formatINR(
                (parseFloat(quantity || "0") * parseFloat(price || "0")) +
                (txType === "BUY" ? (parseFloat(fees || "0") + parseFloat(taxes || "0")) : 0)
              )}
            </span>
          </div>

          <div className="space-y-1">
            <label className="text-slate-600 dark:text-zinc-400">Trade Notes</label>
            <input
              type="text"
              placeholder="e.g. Fundamental rebalancing or target allocation"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2.5 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900"
            />
          </div>

          <div className="flex justify-end space-x-2 pt-2 border-t border-slate-100 dark:border-zinc-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={isSubmitting}>
              Confirm Trade
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
