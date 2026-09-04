import { secureTokenStore, StoredSession } from "./tokenStore";

const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export type CurrentUser = { id: string; email: string; tenant_id: string; permissions: string[] };
export type Employee = { id: string; user_id?: string; employee_number: string; full_name: string; work_email: string; title?: string; is_suspended: boolean };
export type PresenceStatus = "available" | "away" | "busy" | "offline";
export type Presence = { employee_id?: string; employee_name?: string; status: PresenceStatus; last_seen_at?: string; expires_at?: string };
export type Conversation = { id: string; participant_user_ids: string[]; peer_user_id: string; last_message_at?: string; created_at: string };
export type Message = { id: string; conversation_id: string; sender_user_id: string; client_message_id: string; sequence_number: number; body?: string; created_at: string; expires_at: string; deleted_at?: string; read_by_user_ids: string[] };
export type RealtimeTicket = { ticket: string; expires_in_seconds: number; websocket_path: string };
type TokenPair = { access_token: string; refresh_token: string };

async function errorFor(response: Response): Promise<Error> {
  if (response.status === 401) return new Error("Your session has expired.");
  if (response.status === 403) return new Error("You do not have permission for this action.");
  if (response.status === 404) return new Error("The requested record was not found.");
  return new Error("The server could not complete the request.");
}

async function refresh(session: StoredSession): Promise<StoredSession> {
  const response = await fetch(`${apiUrl}/api/v1/auth/refresh`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh_token: session.refreshToken }) });
  if (!response.ok) throw await errorFor(response);
  const tokens = await response.json() as TokenPair;
  const rotated = { accessToken: tokens.access_token, refreshToken: tokens.refresh_token, tenantId: session.tenantId };
  await secureTokenStore.save(rotated);
  return rotated;
}

export async function request<T>(path: string, session: StoredSession, init?: RequestInit): Promise<{data: T; session: StoredSession}> {
  const execute = (active: StoredSession) => fetch(`${apiUrl}/api/v1${path}`, { ...init, headers: { "Content-Type": "application/json", Authorization: `Bearer ${active.accessToken}`, "X-Tenant-ID": active.tenantId, ...init?.headers } });
  let active = session;
  let response = await execute(active);
  if (response.status === 401) { active = await refresh(active); response = await execute(active); }
  if (!response.ok) throw await errorFor(response);
  return { data: await response.json() as T, session: active };
}

export async function signIn(tenantId: string, email: string, password: string): Promise<{user: CurrentUser; session: StoredSession}> {
  const response = await fetch(`${apiUrl}/api/v1/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
  if (!response.ok) throw new Error("Sign-in failed. Check your credentials.");
  const tokens = await response.json() as TokenPair;
  const session = { accessToken: tokens.access_token, refreshToken: tokens.refresh_token, tenantId };
  try {
    const profile = await request<CurrentUser>("/auth/me", session);
    await secureTokenStore.save(profile.session);
    return { user: profile.data, session: profile.session };
  } catch (reason) {
    await signOut(session);
    throw reason;
  }
}

export async function signOut(session: StoredSession): Promise<void> {
  await fetch(`${apiUrl}/api/v1/auth/logout`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${session.accessToken}` }, body: JSON.stringify({ refresh_token: session.refreshToken }) }).catch(() => undefined);
  await secureTokenStore.clear();
}

export function realtimeUrl(path: string, ticket: string): string {
  const url = new URL(`${apiUrl}${path}`);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.searchParams.set("ticket", ticket);
  return url.toString();
}

export function newClientMessageId(): string {
  return `mobile-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}
