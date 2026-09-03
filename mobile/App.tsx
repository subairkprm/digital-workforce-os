import { useEffect, useState } from "react";
import { ActivityIndicator, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";

import { CurrentUser, Employee, Presence, PresenceStatus, request, signIn, signOut } from "./src/api";
import { secureTokenStore, StoredSession } from "./src/tokenStore";

type Workspace = { user: CurrentUser; profile: Employee | null; directory: Employee[]; presence: Presence; directoryPresence: Presence[] };

export default function App() {
  const [session, setSession] = useState<StoredSession | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  async function loadWorkspace(active: StoredSession, query = "") {
    const me = await request<CurrentUser>("/auth/me", active);
    let nextSession = me.session;
    const ownPresence = await request<Presence>("/presence/me", nextSession);
    nextSession = ownPresence.session;
    let profile: Employee | null = null;
    try {
      const result = await request<Employee>("/employees/me", nextSession);
      profile = result.data;
      nextSession = result.session;
    } catch (reason) {
      if (!(reason instanceof Error) || !reason.message.includes("not found")) throw reason;
    }
    let directory: Employee[] = [];
    let directoryPresence: Presence[] = [];
    if (me.data.permissions.includes("employee.read") || me.data.permissions.includes("tenant.owner")) {
      const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
      const result = await request<Employee[]>(`/employees${suffix}`, nextSession);
      directory = result.data;
      nextSession = result.session;
      const presenceResult = await request<Presence[]>(`/presence${suffix}`, nextSession);
      directoryPresence = presenceResult.data;
      nextSession = presenceResult.session;
    }
    setSession(nextSession);
    setWorkspace({ user: me.data, profile, directory, presence: ownPresence.data, directoryPresence });
  }

  useEffect(() => {
    secureTokenStore.load()
      .then(async stored => { if (stored) { const heartbeat = await request<Presence>("/presence/me/heartbeat", stored, { method: "POST", body: "{}" }); await loadWorkspace(heartbeat.session); } })
      .catch(async () => { await secureTokenStore.clear(); })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!session || !workspace || workspace.presence.status === "offline") return;
    const heartbeat = setInterval(() => {
      request<Presence>("/presence/me/heartbeat", session, { method: "POST", body: "{}" })
        .then(result => { setSession(result.session); setWorkspace(current => current ? { ...current, presence: result.data } : current); })
        .catch(() => undefined);
    }, 60_000);
    return () => clearInterval(heartbeat);
  }, [session, workspace?.presence.status]);

  async function login(tenantId: string, email: string, password: string) {
    setLoading(true); setError("");
    try {
      const authenticated = await signIn(tenantId.trim(), email.trim().toLowerCase(), password);
      const heartbeat = await request<Presence>("/presence/me/heartbeat", authenticated.session, { method: "POST", body: "{}" });
      await loadWorkspace(heartbeat.session);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Sign-in failed.");
    } finally { setLoading(false); }
  }

  async function logout() {
    if (session) {
      const offline = await request<Presence>("/presence/me", session, { method: "PUT", body: JSON.stringify({ status: "offline" }) }).catch(() => null);
      await signOut(offline?.session ?? session);
    }
    setSession(null); setWorkspace(null); setSearch("");
  }

  async function updatePresence(status: PresenceStatus) {
    if (!session || !workspace) return;
    setError("");
    try {
      const result = await request<Presence>("/presence/me", session, { method: "PUT", body: JSON.stringify({ status }) });
      setSession(result.session);
      setWorkspace({ ...workspace, presence: result.data });
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to update presence."); }
  }

  if (loading) return <SafeAreaView style={styles.screen}><ActivityIndicator size="large" /></SafeAreaView>;
  if (!session || !workspace) return <Login error={error} onLogin={login} />;
  const canReadDirectory = workspace.user.permissions.includes("employee.read") || workspace.user.permissions.includes("tenant.owner");

  return <SafeAreaView style={styles.screen}><ScrollView contentContainerStyle={styles.scroll}>
    <View style={styles.header}><Text style={styles.brand}>DWCO</Text><TouchableOpacity onPress={logout}><Text style={styles.link}>Sign out</Text></TouchableOpacity></View>
    <View style={styles.card}><Text style={styles.title}>My profile</Text><Text style={styles.name}>{workspace.profile?.full_name ?? workspace.user.email}</Text><Text>{workspace.profile?.title ?? "Employee profile not linked"}</Text>{workspace.profile && <Text style={styles.muted}>{workspace.profile.employee_number} · {workspace.profile.work_email}</Text>}</View>
    <View style={styles.card}><Text style={styles.title}>My presence</Text><Text style={styles.status}>{workspace.presence.status}</Text><View style={styles.presenceRow}>{(["available", "away", "busy", "offline"] as PresenceStatus[]).map(status => <TouchableOpacity key={status} style={[styles.statusButton, workspace.presence.status === status && styles.statusButtonActive]} onPress={() => updatePresence(status)}><Text style={workspace.presence.status === status ? styles.buttonText : styles.link}>{status}</Text></TouchableOpacity>)}</View></View>
    {canReadDirectory && <View style={styles.card}><Text style={styles.title}>Directory</Text><View style={styles.searchRow}><TextInput value={search} onChangeText={setSearch} placeholder="Search people" style={[styles.input, styles.search]} /><TouchableOpacity style={styles.smallButton} onPress={async () => { setLoading(true); try { await loadWorkspace(session, search); } catch { setError("Unable to load directory."); } finally { setLoading(false); } }}><Text style={styles.buttonText}>Search</Text></TouchableOpacity></View>{workspace.directory.length === 0 ? <Text style={styles.muted}>No employees found.</Text> : workspace.directory.map(employee => { const presence = workspace.directoryPresence.find(item => item.employee_id === employee.id); return <View style={styles.person} key={employee.id}><View style={styles.personHeading}><Text style={styles.name}>{employee.full_name}</Text><Text style={styles.status}>{presence?.status ?? "offline"}</Text></View><Text>{employee.title ?? "Team member"}</Text><Text style={styles.muted}>{employee.work_email}</Text></View>; })}</View>}
    {error && <Text style={styles.error}>{error}</Text>}
  </ScrollView></SafeAreaView>;
}

function Login({ error, onLogin }: { error: string; onLogin: (tenantId: string, email: string, password: string) => Promise<void> }) {
  const [tenantId, setTenantId] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  return <SafeAreaView style={styles.screen}><View style={styles.card}><Text style={styles.brand}>DWCO</Text><Text style={styles.title}>Workforce login</Text><TextInput autoCapitalize="none" value={tenantId} onChangeText={setTenantId} placeholder="Tenant ID" style={styles.input} /><TextInput autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="Work email" style={styles.input} /><TextInput secureTextEntry value={password} onChangeText={setPassword} placeholder="Password" style={styles.input} />{error && <Text style={styles.error}>{error}</Text>}<TouchableOpacity disabled={!tenantId || !email || password.length < 8} style={styles.button} onPress={() => onLogin(tenantId, email, password)}><Text style={styles.buttonText}>Sign in</Text></TouchableOpacity></View></SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#eef3f9", justifyContent: "center" }, scroll: { padding: 24, gap: 16 }, header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" }, card: { backgroundColor: "white", borderRadius: 16, padding: 24, gap: 12 }, brand: { fontSize: 14, fontWeight: "700", letterSpacing: 3, color: "#3165a5" }, title: { fontSize: 26, fontWeight: "700", color: "#142440" }, name: { fontSize: 17, fontWeight: "700", color: "#142440" }, muted: { color: "#5d6b7a" }, input: { borderColor: "#b8c5d5", borderWidth: 1, borderRadius: 8, padding: 12 }, button: { backgroundColor: "#1d4f8d", borderRadius: 8, padding: 14, alignItems: "center" }, smallButton: { backgroundColor: "#1d4f8d", borderRadius: 8, padding: 12 }, buttonText: { color: "white", fontWeight: "700" }, error: { color: "#a32020" }, link: { color: "#1d4f8d", fontWeight: "700" }, searchRow: { flexDirection: "row", gap: 8 }, search: { flex: 1 }, person: { borderTopColor: "#dbe3ed", borderTopWidth: 1, paddingTop: 12, gap: 3 }, personHeading: { flexDirection: "row", justifyContent: "space-between" }, presenceRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 }, status: { textTransform: "capitalize", color: "#3165a5", fontWeight: "700" }, statusButton: { borderColor: "#1d4f8d", borderWidth: 1, borderRadius: 8, padding: 10 }, statusButtonActive: { backgroundColor: "#1d4f8d" },
});
