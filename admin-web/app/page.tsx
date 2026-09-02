"use client";

import { FormEvent, useState } from "react";

const sections = ["Dashboard", "Employees", "Departments", "Roles", "Audit"];
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function AdminShell() {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch(`${apiUrl}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
    });
    if (!response.ok) {
      setError("Sign-in failed. Check your credentials.");
      return;
    }
    const tokens = (await response.json()) as { access_token: string };
    setAccessToken(tokens.access_token);
  }

  if (!accessToken) {
    return <main className="login"><form className="loginCard" onSubmit={login}>
      <p className="eyebrow">DWCO Admin</p><h1>Sign in</h1>
      <label>Work email<input name="email" type="email" autoComplete="username" required /></label>
      <label>Password<input name="password" type="password" autoComplete="current-password" required /></label>
      {error && <p role="alert" className="error">{error}</p>}
      <button type="submit" className="primary">Sign in</button>
    </form></main>;
  }

  return <main className="shell">
    <aside><h1>DWCO Admin</h1><nav>{sections.map(section => <a href={`#${section.toLowerCase()}`} key={section}>{section}</a>)}</nav></aside>
    <section className="content"><header><span>Foundation workspace</span><button type="button" onClick={() => setAccessToken(null)}>Sign out</button></header>
      <article><p className="eyebrow">Authenticated admin shell</p><h2>Dashboard</h2><p>Tenant-scoped workforce administration will appear here.</p></article>
    </section>
  </main>;
}
