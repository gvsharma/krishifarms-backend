import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  // MUI CssBaseline owns the CSS reset. Tailwind preflight's unlayered
  // `* { border: 0 }` overrides MUI OutlinedInput borders when enableCssLayer
  // wraps component styles in `@layer mui` (labels/fields collapse/overlap).
  corePlugins: {
    preflight: false,
  },
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border) / <alpha-value>)",
        input: "hsl(var(--input) / <alpha-value>)",
        ring: "hsl(var(--ring) / <alpha-value>)",
        background: "hsl(var(--background) / <alpha-value>)",
        foreground: "hsl(var(--foreground) / <alpha-value>)",
        primary: {
          DEFAULT: "hsl(var(--primary) / <alpha-value>)",
          foreground: "hsl(var(--primary-foreground) / <alpha-value>)",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary) / <alpha-value>)",
          foreground: "hsl(var(--secondary-foreground) / <alpha-value>)",
        },
        muted: {
          DEFAULT: "hsl(var(--muted) / <alpha-value>)",
          foreground: "hsl(var(--muted-foreground) / <alpha-value>)",
        },
        accent: {
          DEFAULT: "hsl(var(--accent) / <alpha-value>)",
          foreground: "hsl(var(--accent-foreground) / <alpha-value>)",
        },
        card: {
          DEFAULT: "hsl(var(--card) / <alpha-value>)",
          foreground: "hsl(var(--card-foreground) / <alpha-value>)",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar) / <alpha-value>)",
          foreground: "hsl(var(--sidebar-foreground) / <alpha-value>)",
          accent: "hsl(var(--sidebar-accent) / <alpha-value>)",
          border: "hsl(var(--sidebar-border) / <alpha-value>)",
        },
        success: {
          DEFAULT: "hsl(var(--success) / <alpha-value>)",
          foreground: "hsl(var(--success-foreground) / <alpha-value>)",
        },
        warning: {
          DEFAULT: "hsl(var(--warning) / <alpha-value>)",
          foreground: "hsl(var(--warning-foreground) / <alpha-value>)",
        },
        harvest: {
          DEFAULT: "hsl(var(--harvest) / <alpha-value>)",
          foreground: "hsl(var(--harvest-foreground) / <alpha-value>)",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive) / <alpha-value>)",
          foreground: "hsl(var(--destructive-foreground) / <alpha-value>)",
        },
        premium: {
          bg: "var(--kf-bg, #FAFAFA)",
          surface: "var(--kf-surface, #FFFFFF)",
          primary: "var(--kf-primary, #111827)",
          accent: "var(--kf-accent, #E11D48)",
          "secondary-accent": "var(--kf-secondary-accent, #C084FC)",
          border: "var(--kf-border, #E5E7EB)",
          muted: "var(--kf-muted, #F3F4F6)",
          "muted-fg": "var(--kf-muted-fg, #6B7280)",
          success: "var(--kf-success, #16A34A)",
          error: "var(--kf-error, #DC2626)",
        },
      },
      fontFamily: {
        sans: [
          "Helvetica Neue",
          "Helvetica",
          "Arial",
          "var(--font-noto-telugu)",
          "sans-serif",
        ],
        display: ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
        helvetica: ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
        telugu: ["var(--font-noto-telugu)", "Noto Sans", "sans-serif"],
        /** Premium form scope (`.kf-premium`) */
        "premium-sans": ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
        "premium-display": [
          "var(--font-plus-jakarta)",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xl: "calc(var(--radius) + 4px)",
        "2xl": "calc(var(--radius) + 8px)",
        /** Premium controls — 16px textbox / 14px button */
        "premium-control": "16px",
        "premium-btn": "14px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(45,106,79,0.06)",
        "card-hover": "0 4px 12px rgba(0,0,0,0.06), 0 8px 24px rgba(45,106,79,0.08)",
        sidebar: "2px 0 12px rgba(0,0,0,0.03)",
        "premium-soft": "0 0 0 3px var(--kf-focus-ring, rgba(17,24,39,0.12))",
        "premium-error": "0 0 0 3px var(--kf-focus-ring-accent, rgba(225,29,72,0.18))",
      },
      height: {
        "premium-control": "52px",
        "premium-btn": "48px",
      },
      minHeight: {
        "premium-control": "52px",
        "premium-btn": "48px",
      },
      spacing: {
        sidebar: "260px",
        "sidebar-collapsed": "72px",
        header: "64px",
      },
      transitionTimingFunction: {
        premium: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fadeUp 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards",
        shimmer: "shimmer 1.8s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
