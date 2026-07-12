import { cn } from "@/lib/utils";
import { HTMLAttributes, forwardRef } from "react";
import { PREMIUM_SCOPE } from "./constants";

export interface PremiumScopeProps extends HTMLAttributes<HTMLDivElement> {}

/** Opt-in wrapper that applies `.kf-premium` tokens + Inter body font. */
export const Scope = forwardRef<HTMLDivElement, PremiumScopeProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn(PREMIUM_SCOPE, className)} {...props} />
  ),
);
Scope.displayName = "PremiumScope";
