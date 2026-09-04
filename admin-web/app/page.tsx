"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { InvitationPanel } from "./InvitationPanel";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
type Section = "Dashboard" | "Employees" | "Departments" | "Presence" | "Messaging" | "Invitations" | "Roles" | "Sessions" | "Audit";
type CurrentUser = { email: string; tenant_id: string; permissions: string[] };
type Employee = { id: string; employee_number: string; full_name: string; work_email: string; title?: string; is_suspended: boolean };
type Department = { id: string; name: string; description?: string; manager_employee_id?: string };
type Role = { id: string; name: string; permissions: string[] };
type Membership = { id: string; user_id: string; role_ids: string[] };
type AuditEvent = { id: string; action: string; resource_type: string; created_at: string };
type Invitation = { id: string; email: string; role_ids: string[]; expires_at: string; accepted_at?: string; revoked_at?: string; token?: string };
type Session = { id: string; created_at: string; expires_at: string; revoked_at?: string };
type Presence = { employee_id?: string; employee_name?: string; status: "available" | "away" | "busy" | "offline"; last_seen_at?: string };
type MessagingMetrics = { conversation_count: number; active_message_count: number; expired_message_count: number; oldest_active_message_at?: string; newest_message_at?: string };
const sectionPermission: Record<Section, string | null> = { Dashboard: null, Employees: "employee.read", Departments: "employee.read", Presence: "employee.read", Messaging: "message.metadata.read", Invitations: "membership.manage", Roles: "role.manage", Sessions: null, Audit: "audit.read" };

export default function AdminShell() {
  const [token, setToken] = useState<string | null>(null), [refreshToken, setRefreshToken] = useState<string | null>(null), [tenantId, setTenantId] = useState(""), [me, setMe] = useState<CurrentUser | null>(null);
  const [section, setSection] = useState<Section>("Dashboard"), [items, setItems] = useState<unknown[]>([]), [loading, setLoading] = useState(false), [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const api = useCallback(async (path: string, init?: RequestInit) => {
    const response = await fetch(`${apiUrl}/api/v1${path}`, { ...init, headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, "X-Tenant-ID": tenantId, ...init?.headers } });
    if (!response.ok) throw new Error(response.status === 403 ? "You do not have permission for this action." : "The server could not complete the request.");
    return response.status === 204 ? null : response.json();
  }, [tenantId, token]);
  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setLoading(true); const form = new FormData(event.currentTarget); const selectedTenant = String(form.get("tenantId"));
    try {
      const response = await fetch(`${apiUrl}/api/v1/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: form.get("email"), password: form.get("password") }) });
      if (!response.ok) throw new Error("Sign-in failed. Check your credentials."); const tokens = await response.json() as { access_token: string; refresh_token: string };
      const profileResponse = await fetch(`${apiUrl}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${tokens.access_token}`, "X-Tenant-ID": selectedTenant } });
      if (!profileResponse.ok) {
        await fetch(`${apiUrl}/api/v1/auth/logout`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${tokens.access_token}` }, body: JSON.stringify({ refresh_token: tokens.refresh_token }) }).catch(() => null);
        throw new Error("This account does not belong to that tenant.");
      }
      setTenantId(selectedTenant); setToken(tokens.access_token); setRefreshToken(tokens.refresh_token); setMe(await profileResponse.json());
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Sign-in failed."); } finally { setLoading(false); }
  }
  const can = useCallback((permission: string) => Boolean(me && (me.permissions.includes(permission) || me.permissions.includes("tenant.owner"))), [me]);
  const visibleSections = useMemo(() => (Object.keys(sectionPermission) as Section[]).filter(name => !sectionPermission[name] || can(sectionPermission[name]!)), [can]);
  const loadSection = useCallback(async () => {
    if (!token || !me || section === "Dashboard") { setItems([]); return; }
    const paths = { Employees: "/employees", Departments: "/departments", Presence: "/presence", Messaging: "/messaging/admin/metrics", Invitations: "/invitations", Roles: "/roles", Sessions: "/auth/sessions", Audit: "/audit-events" };
    const query = (section === "Employees" || section === "Departments") && search ? `?q=${encodeURIComponent(search)}` : "";
    setLoading(true); setError(""); try { const result = await api(`${paths[section]}${query}`); setItems(section === "Messaging" ? [result] : result as unknown[]); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load data."); } finally { setLoading(false); }
  }, [api, me, search, section, token]);
  useEffect(() => { void loadSection(); }, [loadSection]);
  async function create(event: FormEvent<HTMLFormElement>, path: string, fields: string[]) {
    event.preventDefault(); setError(""); const form = new FormData(event.currentTarget); const body: Record<string, unknown> = Object.fromEntries(fields.map(field => [field, form.get(field)]).filter(([, value]) => value !== ""));
    if (path === "/roles") body.permissions = String(form.get("permissions") ?? "").split(",").map(value => value.trim()).filter(Boolean);
    try { await api(path, { method: "POST", body: JSON.stringify(body) }); event.currentTarget.reset(); await loadSection(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to save."); }
  }
  if (!token || !me) return <main className="login"><form className="card loginCard" onSubmit={login}><p className="eyebrow">DWCO Admin</p><h1>Sign in</h1><p className="muted">Use your tenant UUID from the local bootstrap output.</p><label>Tenant ID<input name="tenantId" required /></label><label>Work email<input name="email" type="email" required /></label><label>Password<input name="password" type="password" minLength={8} required /></label>{error && <p role="alert" className="error">{error}</p>}<button disabled={loading} className="primary">{loading ? "Signing in…" : "Sign in"}</button></form></main>;
  return <main className="shell"><aside><h1>DWCO Admin</h1><nav aria-label="Administration">{visibleSections.map(name => <button className={section === name ? "active" : ""} onClick={() => { setSection(name); setSearch(""); }} key={name}>{name}</button>)}</nav></aside><section className="content"><header><div><strong>{section}</strong><span>{me.email}</span></div><button onClick={async () => { if (refreshToken) await api("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }).catch(() => null); setToken(null); setRefreshToken(null); setMe(null); setItems([]); }}>Sign out</button></header>{(section === "Employees" || section === "Departments") && <label className="card">Search<input aria-label={`Search ${section}`} value={search} onChange={event => setSearch(event.target.value)} placeholder="Name, email, or number" /></label>}{error && <p role="alert" className="error banner">{error}</p>}{loading ? <p className="state">Loading…</p> : <Workspace section={section} items={items} can={can} create={create} api={api} reload={loadSection} />}</section></main>;
}

function Workspace({ section, items, can, create, api, reload }: { section: Section; items: unknown[]; can: (p: string) => boolean; create: (e: FormEvent<HTMLFormElement>, p: string, f: string[]) => Promise<void>; api: (p: string, i?: RequestInit) => Promise<unknown>; reload: () => Promise<void> }) {
  if (section === "Dashboard") return <article className="card"><p className="eyebrow">Tenant workspace</p><h2>Workforce administration</h2><p>Choose a permitted area. Every mutation is authorized and audited by the API.</p></article>;
  if (section === "Messaging") { const metrics = items[0] as MessagingMetrics | undefined; return <article className="card"><p className="eyebrow">Privacy-preserving operations</p><h2>Messaging metadata</h2>{!metrics ? <p className="state">No messaging metrics available.</p> : <ul className="records"><li><div><strong>{metrics.conversation_count}</strong><span>Direct conversations</span></div></li><li><div><strong>{metrics.active_message_count}</strong><span>Active messages</span></div></li><li><div><strong>{metrics.expired_message_count}</strong><span>Expired messages awaiting purge</span></div></li></ul>}<p className="muted">Administrators cannot view message content from this area.</p></article>; }
  return <div className="workspace">{section === "Employees" && can("employee.create") && <form className="card formGrid" onSubmit={e => create(e, "/employees", ["employee_number", "full_name", "work_email", "title"])}><h2>Add employee</h2><input aria-label="Employee number" name="employee_number" placeholder="Employee number" required /><input aria-label="Full name" name="full_name" placeholder="Full name" required /><input aria-label="Work email" name="work_email" type="email" placeholder="Work email" required /><input aria-label="Title" name="title" placeholder="Title" /><button className="primary">Create</button></form>}{section === "Departments" && can("department.manage") && <form className="card formGrid" onSubmit={e => create(e, "/departments", ["name", "description"])}><h2>Add department</h2><input aria-label="Department name" name="name" placeholder="Name" required /><input aria-label="Description" name="description" placeholder="Description" /><button className="primary">Create</button></form>}{section === "Invitations" && <InvitationPanel api={api} reload={reload} />}{section === "Roles" && can("role.manage") && <form className="card formGrid" onSubmit={e => create(e, "/roles", ["name", "permissions"])}><h2>Add role</h2><input aria-label="Role name" name="name" placeholder="Name" required /><input aria-label="Permissions" name="permissions" placeholder="employee.read, employee.update" /><button className="primary">Create</button></form>}<div className="card"><h2>{section}</h2>{items.length === 0 ? <p className="state">No records yet.</p> : <ul className="records">{items.map((raw, index) => { const record = raw as { id?: string; employee_id?: string }; return <RecordRow key={record.id ?? record.employee_id ?? index} section={section} item={raw as Employee & Department & Role & AuditEvent & Invitation & Session & Presence} can={can} api={api} reload={reload} />; })}</ul>}</div>{section === "Roles" && <MembershipRoles api={api} roles={items as Role[]} />}</div>;
}
function RecordRow({ section, item, can, api, reload }: { section: Section; item: Employee & Department & Role & AuditEvent & Invitation & Session & Presence; can: (p:string) => boolean; api: (p:string,i?:RequestInit)=>Promise<unknown>; reload:()=>Promise<void> }) {
  const title = section === "Employees" ? `${item.employee_number} · ${item.full_name}` : section === "Presence" ? item.employee_name ?? "Unlinked member" : section === "Audit" ? item.action : section === "Invitations" ? item.email : section === "Sessions" ? `Session ${item.id.slice(0, 8)}` : item.name;
  const detail = section === "Employees" ? item.work_email : section === "Presence" ? `${item.status}${item.last_seen_at ? ` · Last seen ${new Date(item.last_seen_at).toLocaleString()}` : ""}` : section === "Roles" ? item.permissions.join(", ") || "No permissions" : section === "Audit" ? `${item.resource_type} · ${new Date(item.created_at).toLocaleString()}` : section === "Invitations" ? (item.accepted_at ? "Accepted" : item.revoked_at ? "Revoked" : `Expires ${new Date(item.expires_at).toLocaleString()}`) : section === "Sessions" ? (item.revoked_at ? "Revoked" : `Expires ${new Date(item.expires_at).toLocaleString()}`) : item.description;
  return <li><div><strong>{title}</strong><span>{detail}</span></div><div className="actions">
    {section === "Employees" && can("employee.update") && <button onClick={async()=>{const value=prompt("New job title",item.title??"");if(value!==null){await api(`/employees/${item.id}`,{method:"PATCH",body:JSON.stringify({title:value})});await reload();}}}>Edit</button>}
    {section === "Employees" && can("employee.suspend") && !item.is_suspended && <button onClick={async()=>{await api(`/employees/${item.id}/suspend`,{method:"POST"});await reload();}}>Suspend</button>}
    {section === "Employees" && can("employee.suspend") && item.is_suspended && <button onClick={async()=>{await api(`/employees/${item.id}/reactivate`,{method:"POST"});await reload();}}>Reactivate</button>}
    {section === "Departments" && can("department.manage") && <button onClick={async()=>{const value=prompt("Department description",item.description??"");if(value!==null){await api(`/departments/${item.id}`,{method:"PATCH",body:JSON.stringify({description:value})});await reload();}}}>Edit</button>}
    {section === "Departments" && can("department.manage") && <button onClick={async()=>{const value=prompt("Manager employee ID",item.manager_employee_id??"");if(value!==null){await api(`/departments/${item.id}`,{method:"PATCH",body:JSON.stringify({manager_employee_id:value||null})});await reload();}}}>Set manager</button>}
    {section === "Invitations" && !item.accepted_at && !item.revoked_at && <button onClick={async()=>{await api(`/invitations/${item.id}`,{method:"DELETE"});await reload();}}>Revoke</button>}
    {section === "Sessions" && !item.revoked_at && <button onClick={async()=>{await api(`/auth/sessions/${item.id}`,{method:"DELETE"});await reload();}}>Revoke</button>}
    {section === "Roles" && can("role.manage") && <button onClick={async()=>{const value=prompt("Comma-separated permissions",item.permissions.join(", "));if(value!==null){await api(`/roles/${item.id}`,{method:"PATCH",body:JSON.stringify({permissions:value.split(",").map(v=>v.trim()).filter(Boolean)})});await reload();}}}>Edit</button>}
    {section === "Roles" && can("role.manage") && <button onClick={async()=>{if(confirm(`Delete role ${item.name}?`)){await api(`/roles/${item.id}`,{method:"DELETE"});await reload();}}}>Delete</button>}
  </div></li>;
}
function MembershipRoles({ api, roles }: { api:(p:string,i?:RequestInit)=>Promise<unknown>; roles:Role[] }) {
  const [memberships,setMemberships]=useState<Membership[]>([]); useEffect(()=>{api("/memberships").then(data=>setMemberships(data as Membership[])).catch(()=>setMemberships([]));},[api]);
  return <div className="card"><h2>Membership roles</h2>{memberships.length===0?<p className="state">No memberships available.</p>:<ul className="records">{memberships.map(m=><li key={m.id}><span className="mono">{m.user_id}</span><select aria-label={`Role for ${m.user_id}`} value={m.role_ids[0]??""} onChange={async e=>{await api(`/memberships/${m.id}/roles`,{method:"PUT",body:JSON.stringify({role_ids:e.target.value?[e.target.value]:[]})});setMemberships(await api("/memberships") as Membership[]);}}><option value="">No role</option>{roles.map(r=><option key={r.id} value={r.id}>{r.name}</option>)}</select></li>)}</ul>}</div>;
}
