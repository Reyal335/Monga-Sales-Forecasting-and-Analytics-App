"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

type IconProps = { className?: string };

function DashboardIcon({ className }: IconProps) {
  return <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1" /><rect x="14" y="3.5" width="6.5" height="6.5" rx="1" /><rect x="3.5" y="14" width="6.5" height="6.5" rx="1" /><rect x="14" y="14" width="6.5" height="6.5" rx="1" /></svg>;
}

function ForecastIcon({ className }: IconProps) {
  return <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8"><path strokeLinecap="round" strokeLinejoin="round" d="M4 19.5V5.25M4 19.5h16M7.5 15l3.25-3.25 2.5 1.75L18.5 8" /><path strokeLinecap="round" strokeLinejoin="round" d="M15.5 8h3v3" /></svg>;
}

function MenuIcon({ className }: IconProps) {
  return <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" /></svg>;
}

function ChevronIcon({ className }: IconProps) {
  return <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="m9 18 6-6-6-6" /></svg>;
}

const navigation = [
  { href: "/", label: "Dashboard", Icon: DashboardIcon },
  { href: "/forecast", label: "Forecast", Icon: ForecastIcon },
];

function Sidebar({ collapsed, onClose }: { collapsed: boolean; onClose?: () => void }) {
  const pathname = usePathname();
  return <nav aria-label="Primary navigation" className="flex h-full flex-col px-3 py-5"><div className={`mb-9 flex items-center ${collapsed ? "justify-center" : "gap-3 px-1"}`}><div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-indigo-600 text-sm font-bold tracking-tight text-white shadow-sm shadow-indigo-200">M</div>{!collapsed && <div className="min-w-0"><p className="truncate text-sm font-semibold tracking-tight text-slate-950">Monga</p><p className="mt-0.5 text-[11px] font-medium text-slate-500">Demand intelligence</p></div>}</div><div className="space-y-1">{navigation.map(({ href, label, Icon }) => { const isActive = href === "/" ? pathname === "/" : pathname.startsWith(href); return <Link key={href} href={href} onClick={onClose} title={collapsed ? label : undefined} className={`group flex h-11 items-center rounded-xl text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 ${collapsed ? "justify-center" : "gap-3 px-3"} ${isActive ? "bg-indigo-600 text-white shadow-sm shadow-indigo-200" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"}`}><Icon className="h-5 w-5 shrink-0" />{!collapsed && <span>{label}</span>}</Link>; })}</div></nav>;
}

export function AppShell({ children }: { children: ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  return <div className="min-h-screen bg-slate-50 text-slate-900"><aside className={`fixed inset-y-0 left-0 z-30 hidden border-r border-slate-200/80 bg-white transition-[width] duration-200 motion-reduce:transition-none lg:block ${isCollapsed ? "w-20" : "w-64"}`}><Sidebar collapsed={isCollapsed} /><button type="button" onClick={() => setIsCollapsed((value) => !value)} aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"} className="absolute -right-3 top-8 grid h-6 w-6 place-items-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-sm outline-none transition hover:border-indigo-200 hover:text-indigo-700 focus-visible:ring-2 focus-visible:ring-indigo-600"><ChevronIcon className={`h-3.5 w-3.5 transition-transform ${isCollapsed ? "" : "rotate-180"}`} /></button></aside><div className={`min-h-screen transition-[padding] duration-200 motion-reduce:transition-none ${isCollapsed ? "lg:pl-20" : "lg:pl-64"}`}><header className="sticky top-0 z-20 flex h-16 items-center border-b border-slate-200/80 bg-slate-50/95 px-4 backdrop-blur sm:px-6 lg:hidden"><button type="button" onClick={() => setIsMobileOpen(true)} aria-label="Open navigation" className="grid h-10 w-10 place-items-center rounded-lg text-slate-700 outline-none transition hover:bg-slate-200 focus-visible:ring-2 focus-visible:ring-indigo-600"><MenuIcon className="h-5 w-5" /></button><div className="ml-3 flex items-center gap-2"><div className="grid h-7 w-7 place-items-center rounded-lg bg-indigo-600 text-xs font-bold text-white">M</div><span className="text-sm font-semibold tracking-tight">Monga</span></div></header>{children}</div>{isMobileOpen && <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Navigation menu"><button type="button" aria-label="Close navigation" onClick={() => setIsMobileOpen(false)} className="absolute inset-0 bg-slate-950/30" /><aside className="relative h-full w-72 border-r border-slate-200 bg-white shadow-2xl"><Sidebar collapsed={false} onClose={() => setIsMobileOpen(false)} /></aside></div>}</div>;
}
