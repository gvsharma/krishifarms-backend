"use client";

import { cn } from "@/lib/utils";
import { Eye, EyeOff } from "lucide-react";
import {
  InputHTMLAttributes,
  ReactNode,
  forwardRef,
  useId,
  useState,
} from "react";
import {
  controlBase,
  controlHeight,
  controlInvalid,
  controlPadding,
  slotChrome,
} from "./styles";
import { isInvalid } from "./utils";

export interface PremiumInputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, "prefix" | "size"> {
  /** Visual error state (also set when `aria-invalid` is true). */
  error?: boolean;
  /** Leading adornment (icon or short text). */
  prefix?: ReactNode;
  /** Trailing adornment. Overridden by password visibility toggle when `type="password"`. */
  suffix?: ReactNode;
  /** Hide the built-in password show/hide control. */
  disablePasswordToggle?: boolean;
}

export const Input = forwardRef<HTMLInputElement, PremiumInputProps>(
  (
    {
      className,
      type = "text",
      error = false,
      prefix,
      suffix,
      disablePasswordToggle = false,
      disabled,
      id,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const inputId = id ?? generatedId;
    const isPassword = type === "password";
    const [visible, setVisible] = useState(false);
    const showToggle = isPassword && !disablePasswordToggle;
    const resolvedType = showToggle && visible ? "text" : type;
    const invalid = isInvalid(error, props["aria-invalid"]);
    const hasLeading = Boolean(prefix);
    const hasTrailing = Boolean(suffix) || showToggle;

    return (
      <div className="relative w-full">
        {hasLeading ? (
          <span className={cn(slotChrome, "left-0 pl-4")} aria-hidden>
            {prefix}
          </span>
        ) : null}
        <input
          ref={ref}
          id={inputId}
          type={resolvedType}
          disabled={disabled}
          aria-invalid={invalid || undefined}
          className={cn(
            controlBase,
            controlHeight,
            controlPadding,
            hasLeading && "pl-11",
            hasTrailing && "pr-11",
            invalid && controlInvalid,
            className,
          )}
          {...props}
        />
        {showToggle ? (
          <button
            type="button"
            disabled={disabled}
            aria-label={visible ? "Hide password" : "Show password"}
            aria-pressed={visible}
            onClick={() => setVisible((v) => !v)}
            className={cn(
              "absolute inset-y-0 right-0 z-[1] flex items-center pr-3.5",
              "rounded-r-premium-control text-premium-muted-fg",
              "transition-colors duration-150 ease-premium",
              "hover:text-premium-primary",
              "focus-visible:outline-none focus-visible:text-premium-primary",
              "focus-visible:shadow-premium-soft",
              "disabled:pointer-events-none disabled:opacity-50",
            )}
          >
            {visible ? (
              <EyeOff className="h-[18px] w-[18px]" strokeWidth={1.75} aria-hidden />
            ) : (
              <Eye className="h-[18px] w-[18px]" strokeWidth={1.75} aria-hidden />
            )}
          </button>
        ) : hasTrailing && suffix ? (
          <span className={cn(slotChrome, "right-0 pr-4")} aria-hidden>
            {suffix}
          </span>
        ) : null}
      </div>
    );
  },
);
Input.displayName = "PremiumInput";
