"use client";

import { FormEvent, useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function AcceptInvitationPage() {
  const [error, setError] = useState("");
  const [accepted, setAccepted] = useState(false);
  const [loading, setLoading] = useState(false);

  async function accept(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password"));
    if (password !== form.get("confirmPassword")) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${apiUrl}/api/v1/invitations/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: form.get("token"), password }),
      });
      if (!response.ok) throw new Error();
      setAccepted(true);
    } catch {
      setError("This invitation is invalid, expired, revoked, or already used.");
    } finally {
      setLoading(false);
    }
  }

  if (accepted) return <main className="login"><article className="card loginCard">
    <p className="eyebrow">DWCO Workforce</p>
    <h1>Invitation accepted</h1>
    <p>Your account is ready. You can now sign in using your work email.</p>
    <a href="/">Continue to sign in</a>
  </article></main>;

  return <main className="login"><form className="card loginCard" onSubmit={accept}>
    <p className="eyebrow">DWCO Workforce</p>
    <h1>Accept invitation</h1>
    <label>Invitation token<input name="token" required minLength={32} autoComplete="off" /></label>
    <label>Password<input name="password" type="password" required minLength={12} autoComplete="new-password" /></label>
    <label>Confirm password<input name="confirmPassword" type="password" required minLength={12} autoComplete="new-password" /></label>
    {error && <p role="alert" className="error">{error}</p>}
    <button className="primary" disabled={loading}>{loading ? "Accepting…" : "Accept invitation"}</button>
  </form></main>;
}
