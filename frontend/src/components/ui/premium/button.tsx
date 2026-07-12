import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "primary" | "secondary" | "danger";
type Size = "sm" | "md";

export interface PremiumButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  /** Full-width control (forms / mobile). */
  fullWidth?: boolean;
}

const variants: Record<Variant, string> = {
  primary: cn(
    "bg-premium-primary text-white",
    "hover:bg-[#0b1220] active:bg-[#030712]",
    "shadow-[0_1px_2px_rgba(17,24,39,0.08)]",
    "focus-visible:shadow-premium-soft",
  ),
  secondary: cn(
    "bg-premium-surface text-premium-primary",
    "border border-premium-border",
    "hover:bg-premium-muted hover:border-[var(--kf-border-strong,#D1D5DB)]",
    "active:bg-[#ebebeb]",
    "focus-visible:shadow-premium-soft",
  ),
  danger: cn(
    "bg-premium-error text-white",
    "hover:bg-[#b91c1c] active:bg-[#991b1b]",
    "shadow-[0_1px_2px_rgba(220,38,38,0.18)]",
    "focus-visible:shadow-premium-error",
  ),
};

const sizes: Record<Size, string> = {
  sm: "h-10 min-h-10 gap-1.5 px-3.5 text-[13px] rounded-[12px]",
  md: "h-premium-btn min-h-premium-btn gap-2 px-5 text-[15px] rounded-premium-btn",
};

export const Button = forwardRef<HTMLButtonElement, PremiumButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      fullWidth = false,
      type = "button",
      disabled,
      ...props
    },
    ref,
  ) => (
    <button
      ref={ref}
      type={type}
      disabled={disabled}
      className={cn(
        "inline-flex items-center justify-center font-semibold tracking-[-0.01em]",
        "font-premium-display",
        "transition-[background-color,border-color,box-shadow,transform,opacity] duration-150 ease-premium",
        "focus-visible:outline-none",
        "active:scale-[0.985]",
        "disabled:pointer-events-none disabled:opacity-45",
        "motion-reduce:transition-none motion-reduce:active:scale-100",
        variants[variant],
        sizes[size],
        fullWidth && "w-full",
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "PremiumButton";
