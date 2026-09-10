"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { API_URL, setAccessToken, type TokenResponse } from "@/app/lib/api";

type FieldErrors = {
  email?: string;
  password?: string;
};

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function MongaMark() {
  return <div aria-hidden="true" className="grid h-11 w-11 place-items-center rounded-xl bg-indigo-600 text-lg font-bold tracking-tight text-white shadow-sm shadow-indigo-200">M</div>;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  function validate() {
    const errors: FieldErrors = {};
    const trimmedEmail = email.trim();

    if (!trimmedEmail) errors.email = "Enter your email address.";
    else if (!emailPattern.test(trimmedEmail)) errors.email = "Enter a valid email address.";
    if (!password) errors.password = "Enter your password.";

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setIsSuccess(false);

    if (!validate()) return;

    setIsSubmitting(true);

    try {
      const body = new URLSearchParams({ username: email.trim(), password });
      const response = await fetch(`${API_URL}/api/v1/auth/token`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });

      if (response.status === 401) {
        setFormError("That email or password is incorrect. Please try again.");
        return;
      }

      if (!response.ok) {
        setFormError("We couldn’t sign you in right now. Please try again shortly.");
        return;
      }

      const payload = (await response.json()) as TokenResponse;
      if (!payload.access_token) {
        setFormError("The sign-in response was incomplete. Please try again.");
        return;
      }

      setAccessToken(payload.access_token);
      setIsSuccess(true);
      window.setTimeout(() => router.replace("/"), 400);
    } catch {
      setFormError("We couldn’t reach the sign-in service. Check your connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900 sm:grid sm:place-items-center sm:p-6">
      <section className="mx-auto w-full max-w-md border border-slate-200 bg-white p-6 shadow-sm sm:p-8" aria-labelledby="login-heading">
        <div className="flex items-center gap-3">
          <MongaMark />
          <div>
            <p className="text-sm font-semibold tracking-tight text-slate-950">Monga</p>
            <p className="text-xs font-medium text-slate-500">Demand intelligence</p>
          </div>
        </div>

        <header className="mt-9">
          <p className="text-sm font-medium text-indigo-600">Welcome back</p>
          <h1 id="login-heading" className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Sign in to your workspace</h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">Access forecasts and inventory insights for your locations.</p>
        </header>

        <form className="mt-7 space-y-5" onSubmit={handleSubmit} noValidate>
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-800">Email address</label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => {
                setEmail(event.target.value);
                setFieldErrors((errors) => ({ ...errors, email: undefined }));
              }}
              aria-invalid={Boolean(fieldErrors.email)}
              aria-describedby={fieldErrors.email ? "email-error" : undefined}
              className={`mt-2 block h-11 w-full border bg-white px-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 ${fieldErrors.email ? "border-red-400 focus:border-red-500" : "border-slate-300 focus:border-indigo-600"}`}
              placeholder="name@company.com"
              disabled={isSubmitting || isSuccess}
            />
            {fieldErrors.email && <p id="email-error" className="mt-2 text-sm text-red-700">{fieldErrors.email}</p>}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-800">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setFieldErrors((errors) => ({ ...errors, password: undefined }));
              }}
              aria-invalid={Boolean(fieldErrors.password)}
              aria-describedby={fieldErrors.password ? "password-error" : undefined}
              className={`mt-2 block h-11 w-full border bg-white px-3 text-sm text-slate-950 outline-none transition placeholder:text-slate-400 focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 ${fieldErrors.password ? "border-red-400 focus:border-red-500" : "border-slate-300 focus:border-indigo-600"}`}
              placeholder="Enter your password"
              disabled={isSubmitting || isSuccess}
            />
            {fieldErrors.password && <p id="password-error" className="mt-2 text-sm text-red-700">{fieldErrors.password}</p>}
          </div>

          {formError && <div className="border border-red-200 bg-red-50 px-4 py-3 text-sm leading-5 text-red-800" role="alert">{formError}</div>}
          {isSuccess && <div className="border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-5 text-emerald-800" role="status">Signed in successfully. Opening your dashboard…</div>}

          <button type="submit" disabled={isSubmitting || isSuccess} className="flex h-11 w-full items-center justify-center gap-2 bg-indigo-600 px-4 text-sm font-semibold text-white outline-none transition hover:bg-indigo-700 focus-visible:ring-2 focus-visible:ring-indigo-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-indigo-400">
            {isSubmitting && <span aria-hidden="true" className="h-4 w-4 animate-spin rounded-full border-2 border-white/80 border-t-transparent" />}
            {isSubmitting ? "Signing in…" : isSuccess ? "Signed in" : "Sign in"}
          </button>
        </form>

        <p className="mt-6 border-t border-slate-100 pt-5 text-center text-xs leading-5 text-slate-500">Use the email and password provided by your Monga administrator.</p>
      </section>
    </main>
  );
}
