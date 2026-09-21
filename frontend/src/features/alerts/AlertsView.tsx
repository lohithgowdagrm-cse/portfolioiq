import React, { useState, useEffect } from "react";
import { Bell, ShieldCheck, CheckCircle2, Plus, AlertTriangle, FileText } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { AlertRuleItem, AlertEventItem } from "../../types";
import { api } from "../../services/api";

interface AlertsViewProps {
  portfolioId: string;
  onRefreshAlertCount: () => void;
}

export const AlertsView: React.FC<AlertsViewProps> = ({
  portfolioId,
  onRefreshAlertCount,
}) => {
  const [events, setEvents] = useState<AlertEventItem[]>([]);
  const [rules, setRules] = useState<AlertRuleItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<"events" | "rules" | "audit">("events");

  // Create rule modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [metricType, setMetricType] = useState("DRAWDOWN");
  const [comparator, setComparator] = useState("GT");
  const [threshold, setThreshold] = useState("8.0");

  const loadAlertsData = () => {
    setIsLoading(true);
    Promise.all([
      api.getAlertEvents().then((res) => setEvents(res.results || [])),
      api.getAlertRules().then((res) => setRules(res.results || [])),
      fetch("http://localhost:8000/api/v1/audit/logs/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("portfolioiq_token")}`,
        },
      })
        .then((r) => (r.ok ? r.json() : { results: [] }))
        .then((d) => setAuditLogs(d.results || [])),
    ])
      .catch((err) => console.error("Error loading alerts/audit:", err))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadAlertsData();
  }, [portfolioId]);

  const handleAcknowledge = async (eventId: string) => {
    try {
      await api.acknowledgeAlert(eventId);
      loadAlertsData();
      onRefreshAlertCount();
    } catch (err: any) {
      alert(err.message || "Failed to acknowledge alert.");
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createAlertRule({
        portfolio: portfolioId,
        metric_type: metricType,
        comparator: comparator,
        threshold_value: threshold,
      });
      setIsCreateModalOpen(false);
      loadAlertsData();
    } catch (err: any) {
      alert(err.message || "Failed to create rule.");
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-900 dark:text-zinc-100 font-mono">
            Proactive Risk Alerts & Audit Trail
          </h2>
          <p className="text-[11px] text-slate-500 font-mono">
            Automated threshold monitors, event history, and system audit logs
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {/* Sub Tab Switcher */}
          <div className="flex rounded-sm border border-slate-200 dark:border-zinc-800 p-0.5 bg-white dark:bg-zinc-900 font-mono text-[11px]">
            <button
              onClick={() => setActiveSubTab("events")}
              className={`px-3 py-0.5 rounded-sm transition-colors ${
                activeSubTab === "events"
                  ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Active Events ({events.filter((e) => !e.is_acknowledged).length})
            </button>
            <button
              onClick={() => setActiveSubTab("rules")}
              className={`px-3 py-0.5 rounded-sm transition-colors ${
                activeSubTab === "rules"
                  ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Configured Rules ({rules.length})
            </button>
            <button
              onClick={() => setActiveSubTab("audit")}
              className={`px-3 py-0.5 rounded-sm transition-colors ${
                activeSubTab === "audit"
                  ? "bg-slate-900 text-white dark:bg-zinc-100 dark:text-zinc-950 font-semibold"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Audit Trail ({auditLogs.length})
            </button>
          </div>

          {activeSubTab === "rules" && (
            <Button size="sm" onClick={() => setIsCreateModalOpen(true)} className="h-8">
              <Plus className="mr-1 h-3.5 w-3.5" />
              New Rule
            </Button>
          )}
        </div>
      </div>

      {/* Subtab Content */}
      {activeSubTab === "events" && (
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Triggered Alert Incidents</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                  <tr>
                    <th className="px-3.5 py-2 font-medium">Status</th>
                    <th className="px-3.5 py-2 font-medium">Timestamp</th>
                    <th className="px-3.5 py-2 font-medium">Portfolio</th>
                    <th className="px-3.5 py-2 font-medium">Metric</th>
                    <th className="px-3.5 py-2 font-medium">Incident Message</th>
                    <th className="px-3.5 py-2 text-right font-medium">Triggered Val</th>
                    <th className="px-3 py-2 text-center font-medium">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-slate-400">
                        No active risk alert incidents.
                      </td>
                    </tr>
                  ) : (
                    events.map((ev) => (
                      <tr key={ev.id} className="hover:bg-slate-50/70">
                        <td className="px-3.5 py-2">
                          <Badge variant={ev.is_acknowledged ? "default" : "loss"}>
                            {ev.is_acknowledged ? "ACKNOWLEDGED" : "ACTIVE BREACH"}
                          </Badge>
                        </td>
                        <td className="px-3.5 py-2 text-slate-500 whitespace-nowrap">
                          {new Date(ev.created_at).toLocaleString()}
                        </td>
                        <td className="px-3.5 py-2 text-slate-700 dark:text-zinc-300">
                          {ev.portfolio_name}
                        </td>
                        <td className="px-3.5 py-2 font-semibold text-slate-900 dark:text-zinc-100">
                          {ev.metric_type}
                        </td>
                        <td className="px-3.5 py-2 text-slate-600 dark:text-zinc-300">
                          {ev.message}
                        </td>
                        <td className="px-3.5 py-2 text-right font-bold text-rose-700 dark:text-rose-400">
                          {ev.triggered_value}
                        </td>
                        <td className="px-3 py-2 text-center">
                          {!ev.is_acknowledged && (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleAcknowledge(ev.id)}
                              className="h-6 text-[10px]"
                            >
                              Ack
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {activeSubTab === "rules" && (
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Configured Threshold Rules</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                  <tr>
                    <th className="px-3.5 py-2 font-medium">Portfolio</th>
                    <th className="px-3.5 py-2 font-medium">Metric</th>
                    <th className="px-3.5 py-2 font-medium">Condition</th>
                    <th className="px-3.5 py-2 font-medium">Threshold</th>
                    <th className="px-3.5 py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                  {rules.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/70">
                      <td className="px-3.5 py-2.5 font-medium text-slate-900 dark:text-zinc-100">
                        {r.portfolio_name}
                      </td>
                      <td className="px-3.5 py-2.5">{r.metric_type}</td>
                      <td className="px-3.5 py-2.5">{r.comparator}</td>
                      <td className="px-3.5 py-2.5 font-bold text-slate-900 dark:text-zinc-100">
                        {r.threshold_value}
                      </td>
                      <td className="px-3.5 py-2.5">
                        <Badge variant={r.is_active ? "profit" : "default"}>
                          {r.is_active ? "MONITORING" : "PAUSED"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {activeSubTab === "audit" && (
        <Card>
          <CardHeader className="pb-2 pt-3 px-4">
            <CardTitle>Immutable System Audit Trail</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-slate-50 dark:bg-zinc-950/80 border-b border-slate-200 dark:border-zinc-800 text-[11px] text-slate-500 uppercase">
                  <tr>
                    <th className="px-3.5 py-2 font-medium">Timestamp</th>
                    <th className="px-3.5 py-2 font-medium">Action</th>
                    <th className="px-3.5 py-2 font-medium">Entity</th>
                    <th className="px-3.5 py-2 font-medium">Entity ID</th>
                    <th className="px-3.5 py-2 font-medium">IP Address</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-zinc-800/60">
                  {auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-8 text-center text-slate-400">
                        No audit events recorded yet.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-50/70">
                        <td className="px-3.5 py-2 text-slate-500 whitespace-nowrap">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="px-3.5 py-2 font-bold text-slate-900 dark:text-zinc-100">
                          {log.action}
                        </td>
                        <td className="px-3.5 py-2 text-slate-600 dark:text-zinc-400">
                          {log.entity_type}
                        </td>
                        <td className="px-3.5 py-2 text-slate-400 truncate max-w-[140px]">
                          {log.entity_id}
                        </td>
                        <td className="px-3.5 py-2 text-slate-400">{log.ip_address || "127.0.0.1"}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Rule Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Configure Risk Alert Rule"
      >
        <form onSubmit={handleCreateRule} className="space-y-3 font-mono text-xs">
          <div className="space-y-1">
            <label className="text-slate-600 dark:text-zinc-400">Metric Type</label>
            <select
              value={metricType}
              onChange={(e) => setMetricType(e.target.value)}
              className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900"
            >
              <option value="DRAWDOWN">Portfolio Drawdown (%)</option>
              <option value="CONCENTRATION">Position Weight Concentration (%)</option>
              <option value="DAILY_LOSS">Daily Portfolio Loss (₹)</option>
              <option value="VOLATILITY">Annualized Volatility (%)</option>
              <option value="OPTION_EXPIRY">Option Expiry Horizon (Days)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="space-y-1">
              <label className="text-slate-600 dark:text-zinc-400">Condition</label>
              <select
                value={comparator}
                onChange={(e) => setComparator(e.target.value)}
                className="h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-2 text-xs text-slate-900 dark:text-zinc-100 focus:outline-none focus:ring-1 focus:ring-slate-900"
              >
                <option value="GT">Greater Than (&gt;)</option>
                <option value="GTE">Greater Than or Equal (&gt;=)</option>
                <option value="LT">Less Than (&lt;)</option>
                <option value="LTE">Less Than or Equal (&lt;=)</option>
              </select>
            </div>
            <Input
              label="Threshold Value"
              type="number"
              step="any"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              required
            />
          </div>

          <div className="flex justify-end space-x-2 pt-3 border-t border-slate-100 dark:border-zinc-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" size="sm">
              Save Rule
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
