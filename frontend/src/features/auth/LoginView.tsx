import React, { useState } from "react";
import { Lock, Mail, ArrowRight, ShieldCheck } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { api } from "../../services/api";

interface LoginViewProps {
  onLoginSuccess: (token: string, user: any) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState("demo@portfolioiq.io");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const res = await api.login({ email, password });
      localStorage.setItem("portfolioiq_token", res.access);
      onLoginSuccess(res.access, res.user);
    } catch (err: any) {
      setError(err.message || "Invalid credentials. Please verify your email and password.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-slate-100/70 dark:bg-zinc-950 p-4 font-sans">
      <div className="w-full max-w-sm space-y-4">
        {/* Terminal Title */}
        <div className="text-center space-y-1">
          <div className="font-mono text-base font-bold tracking-tight text-slate-900 dark:text-zinc-50">
            PORTFOLIO<span className="text-slate-500">IQ</span>
          </div>
          <p className="text-xs text-slate-500 dark:text-zinc-400 font-mono">
            Institutional Portfolio & Risk Engine
          </p>
        </div>

        <Card className="shadow-subtle border-slate-200 dark:border-zinc-800">
          <CardHeader className="pb-2 pt-4 px-5">
            <CardTitle>Authentication</CardTitle>
          </CardHeader>
          <CardContent className="p-5 pt-2">
            <form onSubmit={handleSubmit} className="space-y-3 font-mono text-xs">
              {error && (
                <div className="rounded-sm border border-rose-200 bg-rose-50 dark:bg-rose-950/40 p-2 text-[11px] text-rose-700 dark:text-rose-400">
                  {error}
                </div>
              )}

              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />

              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <Button type="submit" size="md" className="w-full mt-2" isLoading={isLoading}>
                <span>Sign In to Terminal</span>
                <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
              </Button>

              <div className="rounded-sm border border-slate-100 dark:border-zinc-800 bg-slate-50 dark:bg-zinc-900 p-2.5 space-y-1 text-[11px] text-slate-500">
                <div className="font-semibold text-slate-700 dark:text-zinc-300">
                  Pre-configured Demo Credentials:
                </div>
                <div>User: <code className="text-slate-900 dark:text-zinc-100 font-bold">demo@portfolioiq.io</code></div>
                <div>Pass: <code className="text-slate-900 dark:text-zinc-100 font-bold">Password123!</code></div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
