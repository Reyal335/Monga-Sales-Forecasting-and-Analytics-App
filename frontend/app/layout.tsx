import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "./components/app-shell";

export const metadata: Metadata = { title: "Demand Forecasting Dashboard", description: "Inventory demand forecasting overview" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><AppShell>{children}</AppShell></body></html>;
}
