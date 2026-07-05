import type { Metadata } from "next";
import { Noto_Sans_Telugu } from "next/font/google";
import { Providers } from "@/app/providers";
import "./globals.css";

/** Helvetica stack via system fonts — no webfont files required. */
const helveticaClass = "font-helvetica";

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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${helveticaClass} ${notoTelugu.variable}`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
