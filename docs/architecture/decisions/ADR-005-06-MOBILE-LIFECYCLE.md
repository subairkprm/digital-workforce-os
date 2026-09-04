# ADR-005-06: mobile lifecycle

STATUS=PROPOSED_BLOCKED_ON_NATIVE_DEPENDENCY_PROOF

DWCO 0.5 supports foreground iOS and Android development builds using a pinned, license-clean native
WebRTC dependency. Expo Go, background wake, push, CallKit, Android Telecom/ConnectionService,
lock-screen integration, and store release are excluded.

The initiating and first accepting devices generate 256-bit call-leg proof tokens before their
idempotent commands, retain them in memory, and present them in addition to normal authentication
for signaling and TURN credentials. A lost response retries with the same proof; proof loss cannot
rebind and requires authenticated end/timeout before a new call. Other user
devices receive lifecycle state only. Logout, tenant switch, permission loss, call end, timeout, app
background, or OS interruption closes tracks, peer connection, timers, and subscriptions. Foreground
resume obtains a fresh realtime ticket and authoritative HTTP catch-up; it never auto-answers or
claims a phantom active call.

The exact dependency/version, minimum OS matrix, native build commands, audio route controls, and
reproducible two-device proof remain Mobile and Voice/WebRTC approval blockers.
