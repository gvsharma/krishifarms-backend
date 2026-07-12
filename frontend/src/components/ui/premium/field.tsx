"use client";

import { cn } from "@/lib/utils";
import {
  HTMLAttributes,
  ReactElement,
  ReactNode,
  cloneElement,
  isValidElement,
  useId,
} from "react";
import { Label } from "./label";
import { errorBase, helperBase } from "./styles";

type ControlProps = {
  id?: string;
  error?: boolean;
  "aria-describedby"?: string;
  "aria-invalid"?: boolean | "true" | "false";
  "aria-required"?: boolean | "true" | "false";
};

export interface PremiumFieldProps extends Omit<HTMLAttributes<HTMLDivElement>, "children"> {
  label?: ReactNode;
  htmlFor?: string;
  helperText?: ReactNode;
  error?: ReactNode;
  required?: boolean;
  optional?: boolean;
  /** Single form control (Input / Textarea / custom). Wired to label + a11y ids. */
  children: ReactNode;
}

export function Field({
  label,
  htmlFor,
  helperText,
  error,
  required,
  optional,
  className,
  children,
  ...props
}: PremiumFieldProps) {
  const uid = useId();
  const controlId = htmlFor ?? `kf-field-${uid}`;
  const helperId = helperText && !error ? `${controlId}-helper` : undefined;
  const errorId = error ? `${controlId}-error` : undefined;
  const describedBy = [errorId, helperId].filter(Boolean).join(" ") || undefined;

  let control = children;
  if (isValidElement(children)) {
    const child = children as ReactElement<ControlProps>;
    const prevDescribedBy = child.props["aria-describedby"];
    control = cloneElement(child, {
      id: child.props.id ?? controlId,
      "aria-describedby": describedBy
        ? [describedBy, prevDescribedBy].filter(Boolean).join(" ")
        : prevDescribedBy,
      "aria-invalid": error ? true : child.props["aria-invalid"],
      "aria-required": required ? true : child.props["aria-required"],
      error: error ? true : child.props.error,
    });
  }

  return (
    <div className={cn("flex w-full flex-col gap-1.5", className)} {...props}>
      {label ? (
        <Label htmlFor={controlId} required={required} optional={optional}>
          {label}
        </Label>
      ) : null}
      {control}
      {error ? (
        <p id={errorId} role="alert" className={errorBase}>
          {error}
        </p>
      ) : null}
      {!error && helperText ? (
        <p id={helperId} className={helperBase}>
          {helperText}
        </p>
      ) : null}
    </div>
  );
}
Field.displayName = "PremiumField";
