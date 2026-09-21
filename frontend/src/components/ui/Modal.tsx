import React from "react";
import { X } from "lucide-react";
import { cn } from "../../lib/utils";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-[1px] p-4">
      <div
        className={cn(
          "w-full max-w-lg rounded-sm border border-slate-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 text-slate-900 dark:text-zinc-100 shadow-lg animate-in fade-in zoom-in-95 duration-100",
          className
        )}
      >
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-800 px-4 py-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="rounded-sm p-1 text-slate-400 hover:bg-slate-100 dark:hover:bg-zinc-800 hover:text-slate-600 dark:hover:text-zinc-200 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
};
