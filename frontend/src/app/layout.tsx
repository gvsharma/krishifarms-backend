import type { Metadata } from "next";
import { Inter, Noto_Sans_Telugu, Plus_Jakarta_Sans } from "next/font/google";
import { Providers } from "@/app/providers";
import "./globals.css";
import "@/styles/premium.css";

/** Helvetica stack via system fonts — no webfont files required. */
const helveticaClass = "font-helvetica";

/** Premium form scope only — CSS vars; body stays Helvetica for MUI shell. */
const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  variable: "--font-plus-jakarta",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-inter",
  display: "swap",
});

const notoTelugu = Noto_Sans_Telugu({
  subsets: ["telugu"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-noto-telugu",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "KrishiFarms",
    template: "%s · KrishiFarms",
  },
  description: "Farm operations CRM for procurement, ledger, workforce, and finance.",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${helveticaClass} ${notoTelugu.variable} ${plusJakarta.variable} ${inter.variable}`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
