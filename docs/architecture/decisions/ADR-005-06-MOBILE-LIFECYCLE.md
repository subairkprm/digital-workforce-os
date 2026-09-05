# ADR-005-06: mobile lifecycle

STATUS=PROPOSED_DEPENDENCIES_SELECTED_APPROVAL_AND_PROOF_OPEN

DWCO 0.5 supports foreground iOS and Android development builds using a pinned, licence-clean native
WebRTC dependency and a checked-in, minimal project config plugin. The third-party Expo WebRTC plugin
is rejected because it expands camera, overlay, wake-lock, Bluetooth, and iOS camera-description
surfaces. The project plugin must remove the bridge's media-projection service and allowlist only the
reviewed audio/network and API-scoped Bluetooth configuration. Expo Go, background wake, push,
CallKit, Android Telecom/ConnectionService,
lock-screen integration, and store release are excluded.

The initiating and first accepting devices generate 256-bit call-leg proof tokens before their
idempotent commands, retain them in memory, and present them in addition to normal authentication
for signaling and TURN credentials. A lost response retries with the same proof; proof loss cannot
rebind and requires authenticated end/timeout before a new call. Other user
devices receive lifecycle state only. Logout, tenant switch, permission loss, call end, timeout, app
background, or OS interruption closes tracks, peer connection, timers, and subscriptions. Foreground
resume obtains a fresh realtime ticket and authoritative HTTP catch-up; it never auto-answers or
claims a phantom active call.

The candidate bridge, project configuration path, and effective platform matrix are fixed in
[`../DWCO-0.5-RUNTIME-SELECTION.md`](../DWCO-0.5-RUNTIME-SELECTION.md). Mobile and Voice/WebRTC must
still approve the corrected proposal. Clean-prebuild manifest assertions, native builds, audio-route
controls, permissions, and reproducible two-device relay-only calls remain mandatory evidence.
