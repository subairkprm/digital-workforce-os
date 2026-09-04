import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, AppState, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";

import { Conversation, CurrentUser, Employee, Message, Presence, PresenceStatus, RealtimeTicket, newClientMessageId, realtimeUrl, request, signIn, signOut } from "./src/api";
import { secureTokenStore, StoredSession } from "./src/tokenStore";

type Workspace = { user: CurrentUser; profile: Employee | null; directory: Employee[]; presence: Presence; directoryPresence: Presence[]; conversations: Conversation[] };

export default function App() {
  const [session, setSession] = useState<StoredSession | null>(null);
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageBody, setMessageBody] = useState("");
  const [realtimeState, setRealtimeState] = useState<"offline" | "connecting" | "live">("offline");
  const activeConversationIdRef = useRef<string | null>(null);

  useEffect(() => { activeConversationIdRef.current = activeConversationId; }, [activeConversationId]);

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
    const conversationResult = await request<Conversation[]>("/messaging/conversations", nextSession);
    nextSession = conversationResult.session;
    setSession(nextSession);
    setWorkspace({ user: me.data, profile, directory, presence: ownPresence.data, directoryPresence, conversations: conversationResult.data });
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

  useEffect(() => {
    if (!session || !workspace) return;
    let socket: WebSocket | null = null;
    let stopped = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    const scheduleReconnect = () => {
      if (stopped || AppState.currentState !== "active") return;
      reconnectTimer = setTimeout(connect, 3_000);
    };
    const connect = async () => {
      if (stopped || AppState.currentState !== "active") return;
      if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) return;
      setRealtimeState("connecting");
      try {
        const result = await request<RealtimeTicket>("/realtime/tickets", session, { method: "POST", body: "{}" });
        if (stopped) return;
        setSession(result.session);
        socket = new WebSocket(realtimeUrl(result.data.websocket_path, result.data.ticket));
        socket.onmessage = event => {
          const payload = JSON.parse(String(event.data)) as { type?: string; presence?: Presence; message?: Message; receipt?: { message_id: string; user_id: string } };
          if (payload.type === "realtime.ready") setRealtimeState("live");
          if (payload.type === "presence.updated" && payload.presence) {
            setWorkspace(current => current ? { ...current, directoryPresence: [...current.directoryPresence.filter(item => item.employee_id !== payload.presence?.employee_id), payload.presence!] } : current);
          }
          if ((payload.type === "message.created" || payload.type === "message.redacted") && payload.message?.conversation_id === activeConversationIdRef.current) {
            setMessages(current => [...current.filter(item => item.id !== payload.message?.id), payload.message!].sort((left, right) => left.sequence_number - right.sequence_number));
          }
          if (payload.type === "message.read" && payload.receipt) {
            setMessages(current => current.map(item => item.id === payload.receipt?.message_id && !item.read_by_user_ids.includes(payload.receipt.user_id) ? { ...item, read_by_user_ids: [...item.read_by_user_ids, payload.receipt.user_id] } : item));
          }
        };
        socket.onerror = () => setRealtimeState("offline");
        socket.onclose = () => { setRealtimeState("offline"); scheduleReconnect(); };
      } catch {
        setRealtimeState("offline");
        scheduleReconnect();
      }
    };
    const subscription = AppState.addEventListener("change", state => {
      if (state === "active") void connect();
      else { socket?.close(); socket = null; setRealtimeState("offline"); }
    });
    void connect();
    return () => { stopped = true; if (reconnectTimer) clearTimeout(reconnectTimer); socket?.close(); subscription.remove(); };
  }, [session?.accessToken, session?.refreshToken, session?.tenantId, workspace?.user.id]);

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
    setSession(null); setWorkspace(null); setSearch(""); setMessages([]); setActiveConversationId(null);
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

  async function openConversation(conversationId: string, active = session) {
    if (!active || !workspace) return;
    setError("");
    try {
      const result = await request<Message[]>(`/messaging/conversations/${conversationId}/messages`, active);
      setSession(result.session); setActiveConversationId(conversationId); setMessages(result.data);
      const latestUnread = [...result.data].reverse().find(message => message.sender_user_id !== workspace.user.id && !message.read_by_user_ids.includes(workspace.user.id));
      if (latestUnread) await request(`/messaging/conversations/${conversationId}/messages/${latestUnread.id}/read`, result.session, { method: "POST", body: "{}" });
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load messages."); }
  }

  async function startConversation(participantUserId: string) {
    if (!session || !workspace) return;
    try {
      const result = await request<Conversation>("/messaging/conversations/direct", session, { method: "POST", body: JSON.stringify({ participant_user_id: participantUserId }) });
      setSession(result.session);
      setWorkspace({ ...workspace, conversations: [result.data, ...workspace.conversations.filter(item => item.id !== result.data.id)] });
      await openConversation(result.data.id, result.session);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to start conversation."); }
  }

  async function sendCurrentMessage() {
    if (!session || !activeConversationId || !messageBody.trim()) return;
    try {
      const result = await request<Message>(`/messaging/conversations/${activeConversationId}/messages`, session, { method: "POST", body: JSON.stringify({ client_message_id: newClientMessageId(), body: messageBody.trim() }) });
      setSession(result.session); setMessageBody("");
      setMessages(current => [...current.filter(item => item.id !== result.data.id), result.data].sort((left, right) => left.sequence_number - right.sequence_number));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to send message."); }
  }

  if (loading) return <SafeAreaView style={styles.screen}><ActivityIndicator size="large" /></SafeAreaView>;
  if (!session || !workspace) return <Login error={error} onLogin={login} />;
  const canReadDirectory = workspace.user.permissions.includes("employee.read") || workspace.user.permissions.includes("tenant.owner");
  const activeConversation = workspace.conversations.find(item => item.id === activeConversationId);
  const displayNameFor = (userId: string) => workspace.directory.find(employee => employee.user_id === userId)?.full_name ?? userId.slice(0, 8);

  return <SafeAreaView style={styles.screen}><ScrollView contentContainerStyle={styles.scroll}>
    <View style={styles.header}><Text style={styles.brand}>DWCO</Text><View style={styles.headerActions}><Text style={styles.realtime}>{realtimeState}</Text><TouchableOpacity onPress={logout}><Text style={styles.link}>Sign out</Text></TouchableOpacity></View></View>
    <View style={styles.card}><Text style={styles.title}>My profile</Text><Text style={styles.name}>{workspace.profile?.full_name ?? workspace.user.email}</Text><Text>{workspace.profile?.title ?? "Employee profile not linked"}</Text>{workspace.profile && <Text style={styles.muted}>{workspace.profile.employee_number} · {workspace.profile.work_email}</Text>}</View>
    <View style={styles.card}><Text style={styles.title}>My presence</Text><Text style={styles.status}>{workspace.presence.status}</Text><View style={styles.presenceRow}>{(["available", "away", "busy", "offline"] as PresenceStatus[]).map(status => <TouchableOpacity key={status} style={[styles.statusButton, workspace.presence.status === status && styles.statusButtonActive]} onPress={() => updatePresence(status)}><Text style={workspace.presence.status === status ? styles.buttonText : styles.link}>{status}</Text></TouchableOpacity>)}</View></View>
    <View style={styles.card}><Text style={styles.title}>Messages</Text>{workspace.conversations.length === 0 ? <Text style={styles.muted}>Start a direct conversation from the directory.</Text> : <View style={styles.conversationRow}>{workspace.conversations.map(conversation => <TouchableOpacity key={conversation.id} style={[styles.statusButton, activeConversationId === conversation.id && styles.statusButtonActive]} onPress={() => openConversation(conversation.id)}><Text style={activeConversationId === conversation.id ? styles.buttonText : styles.link}>{displayNameFor(conversation.peer_user_id)}</Text></TouchableOpacity>)}</View>}{activeConversation && <View style={styles.thread}><Text style={styles.name}>{displayNameFor(activeConversation.peer_user_id)}</Text>{messages.length === 0 ? <Text style={styles.muted}>No messages yet.</Text> : messages.map(message => <View key={message.id} style={[styles.message, message.sender_user_id === workspace.user.id && styles.ownMessage]}><Text>{message.body ?? "Message deleted"}</Text><Text style={styles.messageMeta}>{message.sender_user_id === workspace.user.id ? "You" : displayNameFor(message.sender_user_id)} · #{message.sequence_number}{message.read_by_user_ids.length ? " · Read" : ""}</Text></View>)}<View style={styles.searchRow}><TextInput value={messageBody} onChangeText={setMessageBody} placeholder="Write a message" maxLength={4000} multiline style={[styles.input, styles.search]} /><TouchableOpacity disabled={!messageBody.trim()} style={styles.smallButton} onPress={sendCurrentMessage}><Text style={styles.buttonText}>Send</Text></TouchableOpacity></View></View>}</View>
    {canReadDirectory && <View style={styles.card}><Text style={styles.title}>Directory</Text><View style={styles.searchRow}><TextInput value={search} onChangeText={setSearch} placeholder="Search people" style={[styles.input, styles.search]} /><TouchableOpacity style={styles.smallButton} onPress={async () => { setLoading(true); try { await loadWorkspace(session, search); } catch { setError("Unable to load directory."); } finally { setLoading(false); } }}><Text style={styles.buttonText}>Search</Text></TouchableOpacity></View>{workspace.directory.length === 0 ? <Text style={styles.muted}>No employees found.</Text> : workspace.directory.map(employee => { const presence = workspace.directoryPresence.find(item => item.employee_id === employee.id); return <View style={styles.person} key={employee.id}><View style={styles.personHeading}><Text style={styles.name}>{employee.full_name}</Text><Text style={styles.status}>{presence?.status ?? "offline"}</Text></View><Text>{employee.title ?? "Team member"}</Text><View style={styles.personHeading}><Text style={styles.muted}>{employee.work_email}</Text>{employee.user_id && employee.user_id !== workspace.user.id && <TouchableOpacity onPress={() => startConversation(employee.user_id!)}><Text style={styles.link}>Message</Text></TouchableOpacity>}</View></View>; })}</View>}
    {error && <Text style={styles.error}>{error}</Text>}
  </ScrollView></SafeAreaView>;
}

function Login({ error, onLogin }: { error: string; onLogin: (tenantId: string, email: string, password: string) => Promise<void> }) {
  const [tenantId, setTenantId] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState("");
  return <SafeAreaView style={styles.screen}><View style={styles.card}><Text style={styles.brand}>DWCO</Text><Text style={styles.title}>Workforce login</Text><TextInput autoCapitalize="none" value={tenantId} onChangeText={setTenantId} placeholder="Tenant ID" style={styles.input} /><TextInput autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="Work email" style={styles.input} /><TextInput secureTextEntry value={password} onChangeText={setPassword} placeholder="Password" style={styles.input} />{error && <Text style={styles.error}>{error}</Text>}<TouchableOpacity disabled={!tenantId || !email || password.length < 8} style={styles.button} onPress={() => onLogin(tenantId, email, password)}><Text style={styles.buttonText}>Sign in</Text></TouchableOpacity></View></SafeAreaView>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#eef3f9", justifyContent: "center" }, scroll: { padding: 24, gap: 16 }, header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" }, headerActions: { flexDirection: "row", gap: 16, alignItems: "center" }, card: { backgroundColor: "white", borderRadius: 16, padding: 24, gap: 12 }, brand: { fontSize: 14, fontWeight: "700", letterSpacing: 3, color: "#3165a5" }, title: { fontSize: 26, fontWeight: "700", color: "#142440" }, name: { fontSize: 17, fontWeight: "700", color: "#142440" }, muted: { color: "#5d6b7a" }, input: { borderColor: "#b8c5d5", borderWidth: 1, borderRadius: 8, padding: 12 }, button: { backgroundColor: "#1d4f8d", borderRadius: 8, padding: 14, alignItems: "center" }, smallButton: { backgroundColor: "#1d4f8d", borderRadius: 8, padding: 12, justifyContent: "center" }, buttonText: { color: "white", fontWeight: "700" }, error: { color: "#a32020" }, link: { color: "#1d4f8d", fontWeight: "700" }, searchRow: { flexDirection: "row", gap: 8 }, search: { flex: 1 }, person: { borderTopColor: "#dbe3ed", borderTopWidth: 1, paddingTop: 12, gap: 3 }, personHeading: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" }, presenceRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 }, conversationRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 }, status: { textTransform: "capitalize", color: "#3165a5", fontWeight: "700" }, realtime: { textTransform: "capitalize", color: "#5d6b7a" }, statusButton: { borderColor: "#1d4f8d", borderWidth: 1, borderRadius: 8, padding: 10 }, statusButtonActive: { backgroundColor: "#1d4f8d" }, thread: { borderTopColor: "#dbe3ed", borderTopWidth: 1, paddingTop: 12, gap: 8 }, message: { backgroundColor: "#eef3f9", borderRadius: 10, padding: 10, alignSelf: "flex-start", maxWidth: "88%" }, ownMessage: { backgroundColor: "#dceaff", alignSelf: "flex-end" }, messageMeta: { color: "#5d6b7a", fontSize: 11, marginTop: 4 },
});
