"use client";

import type { ButtonHTMLAttributes, InputHTMLAttributes, TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/cn";

export function Button({ className, variant = "primary", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger" }): React.JSX.Element {
  return <button className={cn("inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60", variant === "primary" && "bg-primary text-primary-foreground shadow-soft hover:opacity-95", variant === "secondary" && "bg-secondary text-secondary-foreground hover:bg-secondary/90", variant === "ghost" && "bg-transparent text-text hover:bg-panel", variant === "danger" && "bg-danger text-danger-foreground hover:opacity-95", className)} {...props} />;
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>): React.JSX.Element {
  return <input className={cn("h-11 w-full rounded-xl border border-line bg-canvas px-3 text-sm text-text placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary", className)} {...props} />;
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>): React.JSX.Element {
  return <textarea className={cn("min-h-28 w-full rounded-xl border border-line bg-canvas px-3 py-2 text-sm text-text placeholder:text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary", className)} {...props} />;
}

export function Checkbox({ className, ...props }: InputHTMLAttributes<HTMLInputElement>): React.JSX.Element {
  return <input type="checkbox" className={cn("h-4 w-4 rounded border-line text-primary focus-visible:ring-2 focus-visible:ring-primary", className)} {...props} />;
}

export function Radio({ className, ...props }: InputHTMLAttributes<HTMLInputElement>): React.JSX.Element {
  return <input type="radio" className={cn("h-4 w-4 border-line text-primary focus-visible:ring-2 focus-visible:ring-primary", className)} {...props} />;
}

export function Switch({ checked, onChange, className, ...props }: InputHTMLAttributes<HTMLInputElement>): React.JSX.Element {
  return (
    <label className={cn("inline-flex cursor-pointer items-center gap-2", className)}>
      <span className="sr-only">Toggle</span>
      <input
        type="checkbox"
        className="peer sr-only"
        checked={checked}
        onChange={onChange}
        {...props}
      />
      <span className="relative h-6 w-11 rounded-full bg-line transition peer-checked:bg-primary after:absolute after:left-1 after:top-1 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition peer-checked:after:translate-x-5" />
    </label>
  );
}
