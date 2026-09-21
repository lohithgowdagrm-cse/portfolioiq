import React from "react";
import { cn } from "../../lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, ...props }, ref) => {
    return (
      <div className="w-full space-y-1">
        {label && (
          <label className="text-xs font-medium text-slate-700 dark:text-zinc-300">
            {label}
          </label>
        )}
        <input
          type={type}
          className={cn(
            "flex h-8 w-full rounded-sm border border-slate-300 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-1 text-xs text-slate-900 dark:text-zinc-100 placeholder:text-slate-400 dark:placeholder:text-zinc-500 focus:outline-none focus:ring-1 focus:ring-slate-900 dark:focus:ring-zinc-400 disabled:cursor-not-allowed disabled:opacity-50 font-mono",
            error && "border-rose-500 focus:ring-rose-500",
            className
          )}
          ref={ref}
          {...props}
        />
        {error && <p className="text-[11px] text-rose-600 dark:text-rose-400">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";
