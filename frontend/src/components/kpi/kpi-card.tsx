import { cn, formatPercent } from "@/lib/utils";
import { TrendingDown, TrendingUp, type LucideIcon } from "lucide-react";

interface KpiCardProps {
  label: string;
  value: string;
  delta?: number;
  deltaLabel?: string;
  icon: LucideIcon;
  iconClassName?: string;
  className?: string;
  delay?: number;
}

export function KpiCard({
  label,
  value,
  delta,
  deltaLabel = "vs last month",
  icon: Icon,
  iconClassName,
  className,
  delay = 0,
}: KpiCardProps) {
  const positive = delta !== undefined && delta >= 0;

  return (
    <article
      className={cn(
        "surface-card group flex flex-col gap-4 p-5 transition-shadow duration-300 hover:shadow-card-hover",
        "animate-fade-up opacity-0",
        className,
      )}
      style={{ animationDelay: `${delay}ms`, animationFillMode: "forwards" }}
    >
      <div className="flex items-start justify-between gap-3">
        <div
          className={cn(
            "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary",
            iconClassName,
          )}
        >
          <Icon className="h-5 w-5" strokeWidth={2} />
        </div>
        {delta !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
              positive
                ? "bg-success/10 text-success"
                : "bg-destructive/10 text-destructive",
            )}
          >
            {positive ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingDown className="h-3 w-3" />
            )}
            {formatPercent(delta)}
          </span>
        )}
      </div>
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          {label}
        </p>
        <p className="kpi-value mt-1 text-foreground">{value}</p>
        {delta !== undefined && (
          <p className="mt-1 text-xs text-muted-foreground">{deltaLabel}</p>
        )}
      </div>
    </article>
  );
}
