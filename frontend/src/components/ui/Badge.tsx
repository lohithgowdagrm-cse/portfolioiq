import React from "react";
import { cn } from "../../lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "profit" | "loss" | "warning" | "outline";
}

export const Badge: React.FC<BadgeProps> = ({ className, variant = "default", children, ...props }) => {
  const variantStyles = {
    default: "bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-zinc-700",
    profit: "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50",
    loss: "bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-400 border-rose-200 dark:border-rose-800/50",
    warning: "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50",
    outline: "border-slate-300 dark:border-zinc-700 text-slate-800 dark:text-zinc-200 bg-transparent",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center px-1.5 py-0.5 rounded-sm text-[11px] font-medium border font-mono tracking-tight",
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
