"use client";

import { FormEvent, useEffect, useState } from "react";

type Api = (path: string, init?: RequestInit) => Promise<unknown>;
type Role = { id: string; name: string; permissions: string[] };
type Invitation = { token?: string };

export function InvitationPanel({ api, reload }: { api: Api; reload: () => Promise<void> }) {
  const [roles, setRoles] = useState<Role[]>([]);
  const [token, setToken] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api("/invitations/available-roles")
      .then(data => setRoles(data as Role[]))
      .catch(() => setError("Unable to load tenant roles."));
  }, [api]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      const result = await api("/invitations", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          role_ids: form.get("roleId") ? [form.get("roleId")] : [],
        }),
      }) as Invitation;
      setToken(result.token ?? "");
      formElement.reset();
      await reload();
    } catch {
      setError("Unable to create invitation.");
    }
  }

  return <form className="card formGrid" onSubmit={submit}>
    <h2>Invite user</h2>
    <input aria-label="Invitation email" name="email" type="email" placeholder="Work email" required />
    <select aria-label="Invitation role" name="roleId" defaultValue="">
      <option value="">No initial role</option>
      {roles.map(role => <option key={role.id} value={role.id}>{role.name}</option>)}
    </select>
    <button className="primary">Create invitation</button>
    {error && <p role="alert" className="error">{error}</p>}
    {token && <p><strong>Copy once:</strong> <span className="mono">{token}</span></p>}
  </form>;
}
