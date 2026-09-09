"use client";

import { useCallback, useEffect, useState } from "react";

type DecimalValue = number | string;

type MenuPerformance = {
  item_id: string;
  item_name: string;
  category: string;
  unit_price: DecimalValue;
  total_recipe_cost: DecimalValue;
  contribution_margin: DecimalValue;
  total_revenue: DecimalValue;
  total_profit: DecimalValue;
};

type PerformanceSummary = {
  total_items: number;
  total_revenue: DecimalValue;
  total_profit: DecimalValue;
  average_margin: DecimalValue;
  top_performing_items: MenuPerformance[];
};

type PerformanceResults = {
  items: MenuPerformance[];
  total_count: number;
  filters: {
    days_back: number;
    category: string | null;
    min_profit: DecimalValue | null;
    limit: number;
    offset: number;
  };
};

type ApiResponse<T> = { results: T };

const API_BASE_URL = "http://localhost:8000/api/v1/analytics";

function formatNumber(value: DecimalValue) {
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue.toLocaleString() : String(value);
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <article className="border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold tracking-tight text-slate-900">{value}</p>
    </article>
  );
}

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [performance, setPerformance] = useState<PerformanceResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [retryKey, setRetryKey] = useState(0);

  const loadAnalytics = useCallback(async (signal: AbortSignal) => {
    setIsLoading(true);
    setError(null);

    try {
      const [summaryResponse, performanceResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/summary`, { cache: "no-store", signal }),
        fetch(`${API_BASE_URL}/`, { cache: "no-store", signal }),
      ]);

      if (!summaryResponse.ok || !performanceResponse.ok) {
        const failedResponse = !summaryResponse.ok ? summaryResponse : performanceResponse;
        throw new Error(`Request failed with status ${failedResponse.status}`);
      }

      const [summaryPayload, performancePayload] = await Promise.all([
        summaryResponse.json() as Promise<ApiResponse<PerformanceSummary>>,
        performanceResponse.json() as Promise<ApiResponse<PerformanceResults>>,
      ]);

      setSummary(summaryPayload.results);
      setPerformance(performancePayload.results);
    } catch (loadError) {
      if (loadError instanceof DOMException && loadError.name === "AbortError") return;
      setError(loadError instanceof Error ? loadError.message : "Unable to load menu analytics.");
    } finally {
      if (!signal.aborted) setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void loadAnalytics(controller.signal);
    return () => controller.abort();
  }, [loadAnalytics, retryKey]);

  if (isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 p-6 text-slate-600">
        <div className="flex items-center gap-3">
          <span aria-hidden="true" className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
          Loading menu analytics…
        </div>
      </main>
    );
  }

  if (error || !summary || !performance) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 p-6">
        <section className="max-w-md border border-red-200 bg-white p-6 text-center shadow-sm" aria-live="polite">
          <p className="text-sm font-medium text-red-700">Analytics unavailable</p>
          <h1 className="mt-2 text-xl font-semibold text-slate-900">Could not load menu performance</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">{error ?? "The analytics response did not include the expected results."}</p>
          <button
            type="button"
            onClick={() => setRetryKey((value) => value + 1)}
            className="mt-5 border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-indigo-300 hover:text-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Try again
          </button>
        </section>
      </main>
    );
  }

  const isEmpty = performance.items.length === 0;
  const metrics = [
    ["Total items", summary.total_items.toLocaleString()],
    ["Total revenue", formatNumber(summary.total_revenue)],
    ["Total profit", formatNumber(summary.total_profit)],
    ["Average margin", formatNumber(summary.average_margin)],
  ];

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 border-b border-slate-200 pb-6">
          <p className="text-sm font-medium text-indigo-600">Menu intelligence</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight">Menu performance analytics</h1>
          <p className="mt-2 text-sm text-slate-600">Performance for the last {performance.filters.days_back} days.</p>
        </header>

        <section aria-label="Performance summary" className="grid gap-px overflow-hidden border border-slate-200 bg-slate-200 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map(([label, value]) => <MetricCard key={label} label={label} value={value} />)}
        </section>

        <section className="mt-8 overflow-hidden border border-slate-200 bg-white shadow-sm" aria-labelledby="performance-table-heading">
          <div className="flex flex-col gap-1 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-baseline sm:justify-between">
            <div>
              <h2 id="performance-table-heading" className="font-semibold text-slate-900">Item performance</h2>
              <p className="mt-1 text-sm text-slate-500">Revenue, cost, and profit by menu item.</p>
            </div>
            <p className="text-sm text-slate-500">{performance.total_count.toLocaleString()} items</p>
          </div>

          {isEmpty ? (
            <div className="px-5 py-16 text-center">
              <h3 className="text-base font-semibold text-slate-900">No menu performance data yet</h3>
              <p className="mt-2 text-sm text-slate-500">There are no items to show for the selected reporting period.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-[1000px] w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th scope="col" className="px-5 py-3 font-medium">Item</th>
                    <th scope="col" className="px-5 py-3 font-medium">Category</th>
                    <th scope="col" className="px-5 py-3 text-right font-medium">Unit price</th>
                    <th scope="col" className="px-5 py-3 text-right font-medium">Recipe cost</th>
                    <th scope="col" className="px-5 py-3 text-right font-medium">Contribution margin</th>
                    <th scope="col" className="px-5 py-3 text-right font-medium">Total revenue</th>
                    <th scope="col" className="px-5 py-3 text-right font-medium">Total profit</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {performance.items.map((item) => (
                    <tr key={item.item_id} className="hover:bg-slate-50">
                      <th scope="row" className="whitespace-nowrap px-5 py-4 text-left font-medium text-slate-900">{item.item_name}</th>
                      <td className="whitespace-nowrap px-5 py-4 text-slate-600">{item.category}</td>
                      <td className="whitespace-nowrap px-5 py-4 text-right tabular-nums text-slate-700">{formatNumber(item.unit_price)}</td>
                      <td className="whitespace-nowrap px-5 py-4 text-right tabular-nums text-slate-700">{formatNumber(item.total_recipe_cost)}</td>
                      <td className="whitespace-nowrap px-5 py-4 text-right tabular-nums text-slate-700">{formatNumber(item.contribution_margin)}</td>
                      <td className="whitespace-nowrap px-5 py-4 text-right tabular-nums font-medium text-slate-900">{formatNumber(item.total_revenue)}</td>
                      <td className="whitespace-nowrap px-5 py-4 text-right tabular-nums font-medium text-emerald-700">{formatNumber(item.total_profit)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
