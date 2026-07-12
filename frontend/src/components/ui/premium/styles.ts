import { cn } from "@/lib/utils";

/** Shared control chrome — 52px / 16px radius / soft ring */
export const controlBase = cn(
  "w-full appearance-none bg-premium-surface text-[15px] leading-[22px] text-premium-primary",
  "rounded-premium-control border border-premium-border",
  "placeholder:text-[var(--kf-placeholder,#9CA3AF)]",
  "transition-[border-color,box-shadow,background-color] duration-150 ease-premium",
  "hover:border-[var(--kf-border-strong,#D1D5DB)]",
  "kf-focus-ring",
  "disabled:cursor-not-allowed disabled:bg-premium-muted disabled:text-premium-muted-fg",
  "disabled:hover:border-premium-border disabled:opacity-60",
);

export const controlPadding = "px-4 py-[14px]";

export const controlHeight = "h-premium-control min-h-premium-control";

export const controlInvalid = cn(
  "border-premium-error hover:border-premium-error",
  "aria-[invalid=true]:border-premium-error",
);

export const labelBase = cn(
  "block text-[13px] font-medium leading-5 tracking-[-0.01em] text-premium-primary",
  "font-premium-display",
);

export const helperBase = "mt-0.5 text-[13px] leading-5 text-premium-muted-fg";

export const errorBase = "mt-0.5 text-[13px] leading-5 text-premium-error";

export const slotChrome =
  "pointer-events-none absolute inset-y-0 z-[1] flex items-center text-premium-muted-fg";
