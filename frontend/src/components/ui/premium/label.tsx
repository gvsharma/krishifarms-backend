import { cn } from "@/lib/utils";
import { LabelHTMLAttributes, forwardRef } from "react";
import { labelBase } from "./styles";

export interface PremiumLabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
  optional?: boolean;
}

export const Label = forwardRef<HTMLLabelElement, PremiumLabelProps>(
  ({ className, children, required, optional, ...props }, ref) => (
    <label ref={ref} className={cn(labelBase, className)} {...props}>
      <span className="inline">{children}</span>
      {required ? (
        <span className="ml-0.5 text-premium-accent" aria-hidden>
          *
        </span>
      ) : null}
      {optional && !required ? (
        <span className="ml-1.5 font-normal text-premium-muted-fg">(optional)</span>
      ) : null}
    </label>
  ),
);
Label.displayName = "PremiumLabel";
