import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "Demand Forecasting Dashboard", description: "Inventory demand forecasting overview" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}