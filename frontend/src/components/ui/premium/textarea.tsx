import { cn } from "@/lib/utils";
import { TextareaHTMLAttributes, forwardRef, useId } from "react";
import { controlBase, controlInvalid, controlPadding } from "./styles";
import { isInvalid } from "./utils";

export interface PremiumTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, PremiumTextareaProps>(
  ({ className, error = false, id, disabled, rows = 4, ...props }, ref) => {
    const generatedId = useId();
    const textareaId = id ?? generatedId;
    const invalid = isInvalid(error, props["aria-invalid"]);

    return (
      <textarea
        ref={ref}
        id={textareaId}
        rows={rows}
        disabled={disabled}
        aria-invalid={invalid || undefined}
        className={cn(
          controlBase,
          controlPadding,
          "min-h-[112px] resize-y",
          invalid && controlInvalid,
          className,
        )}
        {...props}
      />
    );
  },
);
Textarea.displayName = "PremiumTextarea";
