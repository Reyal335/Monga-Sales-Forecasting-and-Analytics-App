"use client";

import { useEffect, useState } from "react";

type Prediction = { date: string; store_name: string; item_name: string; predicted_qty: number };
type DashboardSummary = { total_projected_units: number; active_skus: number; top_demand_location: string; model_type: string; recent_predictions: Prediction[] };
const API_URL = "http://localhost:8000/api/dashboard/summary";

function ChartIcon() {
  return <svg aria-hidden="true" className="h-8 w-8 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M3 3v18h18M7 16l3-4 3 2 5-7" /></svg>;
}

export default function Home() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function loadSummary() {
      try {
        const response = await fetch(API_URL, { signal: controller.signal });
        if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
        setSummary((await response.json()) as DashboardSummary);
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError(err instanceof Error ? err.message : "Unable to load dashboard data.");
      }
    }
    void loadSummary();
    return () => controller.abort();
  }, []);

  if (error) return <main className="grid min-h-screen place-items-center bg-slate-50 p-6"><div className="max-w-md rounded-xl border border-red-200 bg-white p-6 text-center shadow-sm"><h1 className="text-lg font-semibold text-slate-900">Could not load the dashboard</h1><p className="mt-2 text-sm text-slate-600">{error}. Ensure the FastAPI server is running on port 8000.</p></div></main>;
  if (!summary) return <main className="grid min-h-screen place-items-center bg-slate-50"><div className="flex items-center gap-3 text-slate-600"><span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />Loading forecast data…</div></main>;

  const cards = [["Total projected units", summary.total_projected_units.toLocaleString()], ["Active SKUs", String(summary.active_skus)], ["Top demand store", summary.top_demand_location], ["Model type", summary.model_type]];
  return <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:px-6 lg:px-8"><div className="mx-auto max-w-7xl"><header className="mb-8 flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-center sm:justify-between"><div><p className="text-sm font-medium text-indigo-600">Inventory intelligence</p><h1 className="mt-1 text-3xl font-bold tracking-tight">Demand Forecasting Dashboard</h1></div><span className="inline-flex w-fit items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-700"><span className="h-2 w-2 rounded-full bg-emerald-500" />Model online</span></header><section aria-label="Summary statistics" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{cards.map(([label, value]) => <article key={label} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><p className="text-sm font-medium text-slate-500">{label}</p><p className="mt-2 text-xl font-semibold text-slate-900">{value}</p></article>)}</section><section className="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-100 p-8 sm:p-12"><div className="flex min-h-56 flex-col items-center justify-center text-center"><ChartIcon /><h2 className="mt-4 text-lg font-semibold">Forecast vs Actual Sales (Chart Placeholder)</h2><p className="mt-2 max-w-md text-sm text-slate-500">Connect your charting library and historical sales data here to visualize forecast accuracy.</p></div></section><section className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"><div className="border-b border-slate-200 px-5 py-4"><h2 className="font-semibold">Recent predictions</h2></div><div className="overflow-x-auto"><table className="min-w-full divide-y divide-slate-200 text-sm"><thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500"><tr><th className="px-5 py-3 font-medium">Date</th><th className="px-5 py-3 font-medium">Store</th><th className="px-5 py-3 font-medium">Item</th><th className="px-5 py-3 text-right font-medium">Predicted qty</th></tr></thead><tbody className="divide-y divide-slate-100">{summary.recent_predictions.map((prediction) => <tr key={`${prediction.date}-${prediction.store_name}-${prediction.item_name}`}><td className="whitespace-nowrap px-5 py-4 text-slate-600">{prediction.date}</td><td className="whitespace-nowrap px-5 py-4 font-medium">{prediction.store_name}</td><td className="whitespace-nowrap px-5 py-4 text-slate-600">{prediction.item_name}</td><td className="whitespace-nowrap px-5 py-4 text-right font-semibold text-indigo-700">{prediction.predicted_qty.toLocaleString()}</td></tr>)}</tbody></table></div></section></div></main>;
}