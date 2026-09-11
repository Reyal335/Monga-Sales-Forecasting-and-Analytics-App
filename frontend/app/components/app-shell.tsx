"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import {
  authenticatedFetch,
  clearAccessToken,
  getAccessToken,
} from "@/app/lib/api";

type IconProps = { className?: string };

function DashboardIcon({ className }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1" />
      <rect x="14" y="3.5" width="6.5" height="6.5" rx="1" />
      <rect x="3.5" y="14" width="6.5" height="6.5" rx="1" />
      <rect x="14" y="14" width="6.5" height="6.5" rx="1" />
    </svg>
  );
}

function ForecastIcon({ className }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 19.5V5.25M4 19.5h16M7.5 15l3.25-3.25 2.5 1.75L18.5 8"
      />
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.5 8h3v3" />
    </svg>
  );
}

function MenuIcon({ className }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path strokeLinecap="round" d="M4 7h16M4 12h16M4 17h16" />
    </svg>
  );
}

function ChevronIcon({ className }: IconProps) {
  return (
    <svg
      aria-hidden="true"
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="m9 18 6-6-6-6" />
    </svg>
  );
}

function ChatIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.8">
      <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 18.5 3.75 21v-4.75A8.25 8.25 0 1 1 20.25 12a8.2 8.2 0 0 1-1.27 4.38" />
      <path strokeLinecap="round" d="M8 12h.01M12 12h.01M16 12h.01" strokeWidth="2.6" />
    </svg>
  );
}

function CloseIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" d="m6 6 12 12M18 6 6 18" />
    </svg>
  );
}

function SendIcon({ className }: IconProps) {
  return (
    <svg aria-hidden="true" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.9">
      <path strokeLinecap="round" strokeLinejoin="round" d="m21 3-7.5 18-3.75-7.5L3 9l18-6Z" />
      <path strokeLinecap="round" d="m9.75 13.5 4.125-4.125" />
    </svg>
  );
}

const navigation = [
  { href: "/", label: "Dashboard", Icon: DashboardIcon },
  { href: "/forecast", label: "Forecast", Icon: ForecastIcon },
  { href: "/analytics", label: "Menu Analytics", Icon: MenuIcon }
];

function Sidebar({
  collapsed,
  onClose,
}: {
  collapsed: boolean;
  onClose?: () => void;
}) {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Primary navigation"
      className="flex h-full flex-col px-3 py-5"
    >
      <div
        className={`mb-9 flex items-center ${collapsed ? "justify-center" : "gap-3 px-1"}`}
      >
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-indigo-600 text-sm font-bold tracking-tight text-white shadow-sm shadow-indigo-200">
          M
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-tight text-slate-950">
              Monga
            </p>
            <p className="mt-0.5 text-[11px] font-medium text-slate-500">
              Demand intelligence
            </p>
          </div>
        )}
      </div>
      <div className="space-y-1">
        {navigation.map(({ href, label, Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              onClick={onClose}
              title={collapsed ? label : undefined}
              className={`group flex h-11 items-center rounded-xl text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 ${collapsed ? "justify-center" : "gap-3 px-3"} ${isActive ? "bg-indigo-600 text-white shadow-sm shadow-indigo-200" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"}`}
            >
              <Icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

type ChatResponse = { response: string };

const suggestedPrompts = [
  "Which store has the highest projected demand this week?",
  "Summarize the biggest menu trends to watch.",
  "What should we prepare for tomorrow's busiest hours?",
];

function ChatPanel({
  messages,
  draft,
  error,
  isSending,
  inputRef,
  onClose,
  onDraftChange,
  onSubmit,
  onRetry,
  onSuggestion,
}: {
  messages: ChatMessage[];
  draft: string;
  error: string | null;
  isSending: boolean;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
  onClose: () => void;
  onDraftChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onRetry: () => void;
  onSuggestion: (prompt: string) => void;
}) {
  const newestMessageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    newestMessageRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [error, isSending, messages]);

  return (
    <aside
      aria-label="Monga assistant"
      className="fixed inset-x-0 bottom-0 z-50 flex max-h-[min(42rem,calc(100dvh-3rem))] flex-col border border-slate-200 bg-white shadow-2xl lg:inset-y-0 lg:left-auto lg:w-96 lg:max-h-none lg:border-y-0 lg:border-r-0"
    >
      <header className="flex shrink-0 items-center justify-between border-b border-slate-200 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-indigo-600 text-white shadow-sm shadow-indigo-200">
            <ChatIcon className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-950">Monga assistant</h2>
            <p className="text-xs text-slate-500">Ask about demand and menu performance</p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close chat"
          className="grid h-10 w-10 place-items-center rounded-lg text-slate-500 outline-none transition hover:bg-slate-100 hover:text-slate-900 focus-visible:ring-2 focus-visible:ring-indigo-600"
        >
          <CloseIcon className="h-5 w-5" />
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-5" aria-live="polite">
        {messages.length === 0 ? (
          <section className="flex min-h-full flex-col justify-center py-8" aria-labelledby="chat-empty-heading">
            <p className="text-sm font-medium text-indigo-600">Get a quick read</p>
            <h3 id="chat-empty-heading" className="mt-1 text-xl font-semibold tracking-tight text-slate-950">What would you like to know?</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">Ask a focused question about forecasts, locations, or menu demand.</p>
            <div className="mt-5 space-y-2">
              {suggestedPrompts.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => onSuggestion(prompt)}
                  disabled={isSending}
                  className="w-full border border-slate-200 px-3 py-3 text-left text-sm leading-5 text-slate-700 outline-none transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-950 focus-visible:ring-2 focus-visible:ring-indigo-600 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </section>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <article key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[88%] whitespace-pre-wrap px-3.5 py-2.5 text-sm leading-6 ${message.role === "user" ? "bg-indigo-600 text-white rounded-md" : "border border-slate-200 bg-slate-50 text-slate-800 rounded-md"}`}>
                  {message.content}
                </div>
              </article>
            ))}
            {isSending && (
              <div className="flex items-center gap-2 text-sm text-slate-500" role="status">
                <span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
                Monga assistant is thinking…
              </div>
            )}
          </div>
        )}
        {error && (
          <div className="mt-4 border border-red-200 bg-red-50 p-3 text-sm leading-5 text-red-800" role="alert">
            <p>{error}</p>
            <button type="button" onClick={onRetry} disabled={isSending} className="mt-2 font-semibold text-red-800 underline underline-offset-2 outline-none focus-visible:ring-2 focus-visible:ring-red-700 disabled:cursor-not-allowed disabled:opacity-60">
              Retry last question
            </button>
          </div>
        )}
        <div ref={newestMessageRef} />
      </div>

      <form onSubmit={onSubmit} className="shrink-0 border-t border-slate-200 p-4">
        <label htmlFor="chat-prompt" className="sr-only">Ask Monga assistant</label>
        <div className="flex items-end gap-2 border border-slate-300 bg-white p-1.5 focus-within:border-indigo-600 focus-within:ring-2 focus-within:ring-indigo-600">
          <textarea
            ref={inputRef}
            id="chat-prompt"
            rows={2}
            value={draft}
            onChange={(event) => onDraftChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
            maxLength={4000}
            disabled={isSending}
            placeholder="Ask about your forecasts…"
            className="max-h-28 min-h-10 flex-1 resize-y bg-transparent px-2 py-1.5 text-sm leading-5 text-slate-950 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isSending || !draft.trim()}
            aria-label="Send message"
            className="grid h-10 w-10 shrink-0 place-items-center bg-indigo-600 text-white outline-none transition hover:bg-indigo-700 focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-indigo-300"
          >
            {isSending ? <span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-white/80 border-t-transparent" /> : <SendIcon className="h-4 w-4" />}
          </button>
        </div>
        <p className="mt-2 text-xs text-slate-500">Enter to send · Shift+Enter for a new line</p>
      </form>
    </aside>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [lastPrompt, setLastPrompt] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const authenticatedRef = useRef(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    function clearChatState() {
      setMessages([]);
      setDraft("");
      setError(null);
      setLastPrompt(null);
      setIsSending(false);
      setIsChatOpen(false);
    }

    function syncAuthentication() {
      const hasAccessToken = Boolean(getAccessToken());
      if (authenticatedRef.current !== hasAccessToken) {
        authenticatedRef.current = hasAccessToken;
        if (hasAccessToken && window.matchMedia("(min-width: 1024px)").matches) {
          setIsChatOpen(true);
        }
        if (!hasAccessToken) clearChatState();
      }
      setIsAuthenticated(hasAccessToken);
    }

    syncAuthentication();
    window.addEventListener("storage", syncAuthentication);
    window.addEventListener("focus", syncAuthentication);
    const tokenCheck = window.setInterval(syncAuthentication, 1_000);
    return () => {
      window.removeEventListener("storage", syncAuthentication);
      window.removeEventListener("focus", syncAuthentication);
      window.clearInterval(tokenCheck);
    };
  }, [pathname]);

  async function sendPrompt(prompt: string, shouldAddUserMessage: boolean) {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isSending) return;

    setError(null);
    setLastPrompt(trimmedPrompt);
    setDraft("");
    if (shouldAddUserMessage) {
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "user", content: trimmedPrompt }]);
    }
    setIsSending(true);

    try {
      const response = await authenticatedFetch("/api/v1/chat/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: trimmedPrompt }),
      });

      if (response.status === 401) {
        clearAccessToken();
        setIsAuthenticated(false);
        setIsChatOpen(false);
        setMessages([]);
        router.replace("/login");
        return;
      }
      if (!response.ok) throw new Error("The assistant could not respond right now.");

      const payload = (await response.json()) as ChatResponse;
      if (!payload.response?.trim()) throw new Error("The assistant returned an empty response.");
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", content: payload.response.trim() }]);
      setLastPrompt(null);
    } catch {
      setError("The assistant is unavailable right now. Please try again.");
    } finally {
      setIsSending(false);
    }
  }

  function handleChatSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendPrompt(draft, true);
  }

  function handleSuggestion(prompt: string) {
    setDraft(prompt);
    window.requestAnimationFrame(() => inputRef.current?.focus());
  }

  if (pathname === "/login") return <>{children}</>;
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside
        className={`fixed inset-y-0 left-0 z-30 hidden border-r border-slate-200/80 bg-white transition-[width] duration-200 motion-reduce:transition-none lg:block ${isCollapsed ? "w-20" : "w-64"}`}
      >
        <Sidebar collapsed={isCollapsed} />
        <button
          type="button"
          onClick={() => setIsCollapsed((value) => !value)}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="absolute -right-3 top-8 grid h-6 w-6 place-items-center rounded-full border border-slate-200 bg-white text-slate-500 shadow-sm outline-none transition hover:border-indigo-200 hover:text-indigo-700 focus-visible:ring-2 focus-visible:ring-indigo-600"
        >
          <ChevronIcon
            className={`h-3.5 w-3.5 transition-transform ${isCollapsed ? "" : "rotate-180"}`}
          />
        </button>
      </aside>
      <div
        className={`min-h-screen transition-[padding] duration-200 motion-reduce:transition-none ${isCollapsed ? "lg:pl-20" : "lg:pl-64"} ${isAuthenticated && isChatOpen ? "lg:pr-96" : isAuthenticated ? "lg:pr-20" : ""}`}
      >
        <header className="sticky top-0 z-20 flex h-16 items-center border-b border-slate-200/80 bg-slate-50/95 px-4 backdrop-blur sm:px-6 lg:hidden">
          <button
            type="button"
            onClick={() => setIsMobileOpen(true)}
            aria-label="Open navigation"
            className="grid h-10 w-10 place-items-center rounded-lg text-slate-700 outline-none transition hover:bg-slate-200 focus-visible:ring-2 focus-visible:ring-indigo-600"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
          <div className="ml-3 flex items-center gap-2">
            <div className="grid h-7 w-7 place-items-center rounded-lg bg-indigo-600 text-xs font-bold text-white">
              M
            </div>
            <span className="text-sm font-semibold tracking-tight">Monga</span>
          </div>
        </header>
        {children}
      </div>
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 lg:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation menu"
        >
          <button
            type="button"
            aria-label="Close navigation"
            onClick={() => setIsMobileOpen(false)}
            className="absolute inset-0 bg-slate-950/30"
          />
          <aside className="relative h-full w-72 border-r border-slate-200 bg-white shadow-2xl">
            <Sidebar collapsed={false} onClose={() => setIsMobileOpen(false)} />
          </aside>
        </div>
      )}
      {isAuthenticated && !isChatOpen && (
        <button
          type="button"
          onClick={() => setIsChatOpen(true)}
          aria-label="Open Monga assistant"
          className="fixed bottom-5 right-5 z-30 grid h-12 w-12 place-items-center rounded-full bg-indigo-600 text-white shadow-lg shadow-indigo-300 outline-none transition hover:bg-indigo-700 focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2"
        >
          <ChatIcon className="h-5 w-5" />
        </button>
      )}
      {isAuthenticated && isChatOpen && (
        <>
          <button type="button" aria-label="Close chat" onClick={() => setIsChatOpen(false)} className="fixed inset-0 z-40 bg-slate-950/30 lg:hidden" />
          <ChatPanel
            messages={messages}
            draft={draft}
            error={error}
            isSending={isSending}
            inputRef={inputRef}
            onClose={() => setIsChatOpen(false)}
            onDraftChange={setDraft}
            onSubmit={handleChatSubmit}
            onRetry={() => lastPrompt && void sendPrompt(lastPrompt, false)}
            onSuggestion={handleSuggestion}
          />
        </>
      )}
    </div>
  );
}
