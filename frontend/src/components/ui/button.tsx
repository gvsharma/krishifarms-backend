import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

type Variant = "default" | "secondary" | "ghost" | "outline" | "soft";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: "sm" | "md" | "icon";
}

const variants: Record<Variant, string> = {
  default:
    "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm active:scale-[0.98] disabled:opacity-50",
  secondary:
    "bg-secondary text-secondary-foreground hover:bg-secondary/90 shadow-sm active:scale-[0.98] disabled:opacity-50",
  soft: "bg-accent text-accent-foreground hover:bg-accent/80 active:scale-[0.98] disabled:opacity-50",
  ghost: "text-foreground hover:bg-muted disabled:opacity-50",
  outline:
    "border border-border bg-card text-foreground hover:bg-muted/60 disabled:opacity-50",
};

const sizes: Record<NonNullable<ButtonProps["size"]>, string> = {
  sm: "h-8 px-3 text-xs font-medium",
  md: "h-10 px-4 text-sm font-medium",
  icon: "h-9 w-9 shrink-0 p-0",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "md", ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-lg transition-all duration-200 ease-premium",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  ),
);
Button.displayName = "Button";
