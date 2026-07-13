# Premium form controls

Linear / Stripe / Apple-inspired form primitives. **Opt-in only** — wrap a subtree with `Scope` / `kf-premium` so the MUI shell theme stays untouched.

Dark mode: `.dark .kf-premium` swaps CSS variables (`--kf-primary`, `--kf-surface`, …) so inputs/labels stay readable. `PremiumDialog` / `SoftAlert` also adapt via MUI `applyStyles("dark", …)`.

## Setup (already wired)

| Piece | Path |
|-------|------|
| CSS variables | `frontend/src/styles/premium.css` (imported from root layout) |
| Tokens | `@/lib/design/premium` |
| Fonts | Plus Jakarta Sans (`--font-plus-jakarta`) + Inter (`--font-inter`) — variables only; body stays Helvetica for MUI |

## Import (siblings)

```tsx
import {
  Button,
  Field,
  Input,
  Label,
  Scope,
  Textarea,
  PREMIUM_SCOPE,
  premiumTokens,
} from "@/components/ui/premium";
```

## Usage

```tsx
import { Button, Field, Input, Scope, Textarea } from "@/components/ui/premium";

export function ExampleForm() {
  return (
    <Scope className="mx-auto max-w-md space-y-4 p-6">
      <Field label="Email" required helperText="Work email preferred">
        <Input type="email" placeholder="you@farm.com" autoComplete="email" />
      </Field>

      <Field label="Password" error="Must be at least 8 characters">
        <Input type="password" autoComplete="current-password" />
      </Field>

      <Field label="Notes" optional>
        <Textarea placeholder="Optional context…" />
      </Field>

      <div className="flex gap-3 pt-1">
        <Button type="submit">Save</Button>
        <Button type="button" variant="secondary">
          Cancel
        </Button>
        <Button type="button" variant="danger">
          Delete
        </Button>
      </div>
    </Scope>
  );
}
```

### Prefix / suffix

```tsx
<Input prefix={<span className="text-sm">₹</span>} placeholder="0.00" inputMode="decimal" />
<Input suffix={<span className="text-sm">kg</span>} />
```

`type="password"` gets a show/hide toggle automatically (disable with `disablePasswordToggle`).

### Class-only scope

```tsx
<form className={PREMIUM_SCOPE}>{/* … */}</form>
```

## API

| Component | Key props |
|-----------|-----------|
| `Scope` | standard `div` attrs — applies `kf-premium` |
| `Input` | `error`, `prefix`, `suffix`, `disablePasswordToggle` + native input attrs |
| `Textarea` | `error` + native textarea attrs |
| `Label` | `required`, `optional` |
| `Field` | `label`, `helperText`, `error`, `required`, `optional`, `htmlFor` — clones child with `id` / `aria-*` |
| `Button` | `variant`: `primary` \| `secondary` \| `danger`; `size`: `sm` \| `md`; `fullWidth` |

## Specs

- Textbox: **52px** height, **16px** radius, **16px** horizontal padding, soft focus ring
- Palette: bg `#FAFAFA`, primary `#111827`, accent `#E11D48`, secondary accent `#C084FC`, border `#E5E7EB`, success `#16A34A`, error `#DC2626`

## Do not

- Mass-migrate existing MUI pages yet
- Put `kf-premium` on the app shell root (would restyle MUI chrome)
- Confuse with legacy `@/components/ui/input` / `button` (pre-premium shadcn-style)
