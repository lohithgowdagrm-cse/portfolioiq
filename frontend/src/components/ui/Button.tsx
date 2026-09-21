import React from "react";
import { cn } from "../../lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading, children, disabled, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 select-none rounded-sm";

    const variantStyles = {
      primary: "bg-slate-900 text-slate-50 hover:bg-slate-800 dark:bg-zinc-100 dark:text-zinc-950 dark:hover:bg-zinc-200 border border-transparent shadow-subtle",
      secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200 dark:bg-zinc-800 dark:text-zinc-100 dark:hover:bg-zinc-700 border border-slate-200 dark:border-zinc-700",
      outline: "border border-slate-300 dark:border-zinc-700 bg-transparent hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-900 dark:text-zinc-100",
      danger: "bg-rose-600 text-white hover:bg-rose-700 dark:bg-rose-700 dark:hover:bg-rose-600 border border-transparent",
      ghost: "hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-300",
    };

    const sizeStyles = {
      sm: "h-7 px-2.5 text-xs",
      md: "h-8 px-3.5 text-xs tracking-tight",
      lg: "h-9 px-4 text-sm",
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variantStyles[variant], sizeStyles[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <span className="mr-1.5 h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
