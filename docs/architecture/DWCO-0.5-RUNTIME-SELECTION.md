# DWCO 0.5 dependency and local runtime selection

SELECTION_STATUS=CORRECTED_PROPOSAL_FOR_SECURITY_QA_DEVOPS_APPROVAL

SELECTION_AS_OF=2026-09-05

IMPLEMENTATION_AUTHORIZED=NO

DEPLOYMENT_AUTHORIZED=NO

This record closes ambiguity about the candidate native WebRTC packages and local coturn artifact.
It does not add dependencies, generate native projects, start a TURN service, authorize product code,
or approve any shared or production environment. Required reviewers must accept this selection against
an exact commit before VBL-04 or VBL-05 may close.

## Repository baseline

| Item | Observed value |
|---|---|
| Product baseline | Merged `main` at `9188adc` |
| Mobile framework | Expo `~57.0.20`, React Native `0.86.3`, React `19.2.3` |
| Package manager | pnpm `11.19.0` |
| Local host | Apple Silicon (`arm64`), macOS `26.6.2` |
| Native tools | Xcode `26.6` present; Java, Android `adb`, and CocoaPods not detected |
| Container runtime | Docker `29.7.2` |

The host inventory is evidence about this workstation only. It is not a reproducible build attestation.
Java/Android SDK and CocoaPods readiness must be established without changing the machine implicitly.

## Proposed native WebRTC selection

| Component | Exact proposal | Integrity and licence | Compatibility decision |
|---|---|---|---|
| WebRTC bridge | `react-native-webrtc@124.0.8` | npm integrity `sha512-uuQxvmk+mvnk5U0tr+1N42sKZqgm41fJrBA+fmCvML9J9P4roSh2So82t5RHAlu/vE9vxu5AKgivAiH61clCBg==`; MIT | Peer range accepts React Native `>=0.60.0`; native build and device proof still required |
| WebRTC native configuration | Project-owned `mobile/plugins/withDwcoAudioWebRtc.js`; no additional runtime package | Repository-reviewed source under the project licence | Must allowlist only approved audio/network configuration and remove prohibited merged-library surfaces; clean prebuild/build proof is mandatory |
| Rejected plugin | `@config-plugins/react-native-webrtc@15.0.2` | npm integrity `sha512-sH4T7Z4P2RowV91k9CEwEr0unn+396NBexxCNZwRXuJXwguDU1qZWpE6fcwN0730B8uiS83F7+CLTyhpC7qRHQ==`; MIT | Rejected: it unconditionally adds camera, overlay, wake-lock, Bluetooth, and iOS camera-description entries outside this contract |

The application must use an Expo development build. Expo Go is excluded because the selected bridge
contains custom native code. The checked-in project plugin must supply only an explicit microphone
usage description on iOS. On Android it must add only `INTERNET`, `ACCESS_NETWORK_STATE`,
`CHANGE_NETWORK_STATE`, `MODIFY_AUDIO_SETTINGS`, and `RECORD_AUDIO`, plus API-scoped
`BLUETOOTH`/`BLUETOOTH_ADMIN` through API 30 and runtime `BLUETOOTH_CONNECT` for approved Bluetooth
audio routing. The only added hardware feature is the microphone; it must not add camera, overlay,
wake-lock, media-projection, video, background-call, or unrelated foreground-service privileges.

The project plugin must also place an Android manifest merge removal for
`com.oney.WebRTCModule.MediaProjectionService`, which the selected bridge otherwise contributes for
screen sharing. No application code may expose video, screen capture, or `getDisplayMedia`. A clean
prebuild assertion must inventory generated Android permissions, features, services, providers, and
iOS usage descriptions/entitlements; any item outside the reviewed allowlist fails before compilation.
Generated native directories remain disposable CNG output and must not become hand-edited authority.

### Supported build and device matrix

| Dimension | Required selection or proof |
|---|---|
| iOS deployment floor | iOS `16.4+`, inherited from Expo SDK 57; this is stricter than the bridge's iOS 12 floor |
| iOS toolchain | Xcode `26.4+`; clean local development build on the approved version |
| Android deployment floor | Android 7 / API 24+, common to Expo SDK 57 and the bridge |
| Android build SDK | `compileSdkVersion=36`, `targetSdkVersion=36` |
| JavaScript toolchain | Node `22.13.x` minimum per Expo SDK 57 and pnpm `11.19.0`; exact CI image/version must be pinned before implementation evidence |
| Simulator/emulator | iOS 16.4+ simulator and Android API 24 plus API 36 emulator build/smoke evidence |
| Physical devices | At least one supported iPhone and one supported Android phone with microphone permission deny/grant/revoke and route interruption evidence |
| Cross-platform | iOS-to-Android and Android-to-iOS two-device, relay-only, foreground audio calls |
| Audio routes | Earpiece, speaker, wired route when available, Bluetooth when available, interruption, background termination, and cleanup |

Simulator/emulator checks do not replace the physical two-device media proof. Versions above the
minimum floor are sampled, but this bounded stage does not claim exhaustive handset compatibility.

## Proposed local coturn selection

| Item | Exact proposal |
|---|---|
| Image | `docker.io/coturn/coturn:4.17.2-r0@sha256:aa68aab64a3b929d57fc2924c98ea447bf996cf8dade2508e7b71eaf23f1f14e` |
| Source release | coturn `4.17.2`, source commit `de0c9b28f22281a0251d7e98aa8a097895a5b185` |
| Licence | BSD 3-Clause terms in the upstream `LICENSE` file |
| Platforms resolved | `linux/amd64` and `linux/arm64` are present in the pinned multi-architecture manifest |
| Compose project | `dwco-voice-ci`, isolated from development, governance, and normal `dwco-ci` |
| Listener | Selected private test-LAN host interface on `13478` UDP/TCP; never loopback, wildcard, public, or host networking |
| Relay range | UDP `49160-49259`, bounded to the isolated voice-test project |
| Resource ceiling | 1 CPU, 256 MiB memory, 100 PIDs, 65,536 open files; Docker logs 10 MiB times three |
| Container network | Static isolated bridge `172.31.250.0/29`; coturn relay address `172.31.250.2`; preflight fails on collision |
| Advertised address | Explicit `${DWCO_TURN_HOST_LAN_IP}/172.31.250.2`; automatic public-IP detection is disabled |
| Hardening proposal | Exact user `65534:65534`, drop all capabilities, no-new-privileges, read-only root, and bounded UID-owned tmpfs only |
| Secret proposal | Fresh 32-byte random ignored `.env.dwco-voice-ci-turn-secret`, host mode `0600`, mounted read-only and removed by an interruption-safe scoped wrapper |
| Readiness | Fresh authenticated allocation plus bidirectional relay probe from a separate test peer; a process/port check alone fails |

The pinned image declares `USER nobody:nogroup` and `/var/lib/coturn` as its writable volume. Compose
must enforce numeric `65534:65534`; `/var/lib/coturn` and `/run/dwco` are the only writable tmpfs
mounts, each `uid=65534,gid=65534,mode=0700`. Any different resolved identity or writable path fails
the preflight. The command must override the image default so `detect-external-ip` never runs and no
external DNS/public-address discovery occurs.

### Physical-peer and Docker/NAT topology

Physical evidence runs only on a dedicated, private, IPv4 test LAN containing the development host
and the two named test devices, with no WAN uplink or public ingress. Before start, the operator must
freeze `DWCO_TURN_HOST_LAN_IP` and the two peer `/32` addresses in the raw, non-committed evidence.
Preflight fails unless they are RFC1918, are on the same dedicated interface/subnet, are not loopback
or wildcard, and the interface has no public address. Published mappings bind only to the selected
host address:

```text
${DWCO_TURN_HOST_LAN_IP}:13478 -> 172.31.250.2:3478/tcp+udp
${DWCO_TURN_HOST_LAN_IP}:49160-49259 -> 172.31.250.2:49160-49259/udp
```

Coturn must use `relay-ip=172.31.250.2` and
`external-ip=${DWCO_TURN_HOST_LAN_IP}/172.31.250.2`, preserving each relay port across Docker's NAT.
It must also set `min-port=49160`, `max-port=49259`, `no-stun`, `no-cli`, `no-tls`, `no-dtls`,
`fingerprint`, `lt-cred-mech`, `use-auth-secret`, `no-multicast-peers`, and the approved local realm.
Raw allocation evidence must prove the XOR relayed address is the selected private host address and
that both devices exchange packets bidirectionally; committed evidence contains only hashes and
pass/fail, never IP addresses. Loopback-only smoke checks may supplement but cannot replace this test.

### Secret creation and cleanup

The DevOps-owned voice-test wrapper must set `umask 077`, create exactly 32 random bytes as 64
lowercase hexadecimal characters in `.env.dwco-voice-ci-turn-secret`, verify current-user ownership
and host mode `0600`, and never echo, export, interpolate into Compose, or pass the value as a process
argument. The file is mounted read-only at `/run/secrets/dwco_turn_secret`.

Running without shell tracing, the container wrapper reads that file and writes the final coturn
configuration to UID-owned `/run/dwco/turnserver.conf` with mode `0600`; the coturn process receives
only the configuration path. Host traps for normal exit, error, interrupt, and termination run
project-scoped `docker compose --project-name dwco-voice-ci down --volumes --remove-orphans` and
unlink only the named secret file. The postcondition requires the host secret, project containers,
network, volumes, and generated in-container configuration to be absent. Failure of any cleanup
assertion fails the gate and requires manual review; no broad Docker prune is allowed.

The manifest digest was resolved without pulling or running the image. Resource, numeric-user,
read-only, secret, allocation, NAT, port, and cleanup settings remain unproven until the executable
evidence gate. TLS/TCP 5349, DNS, public ingress, certificates, staging, and production TURN remain
excluded under DEP-007 and DEP-012.

## Verification and provenance

Selection metadata was obtained read-only using:

```text
npm view react-native-webrtc@124.0.8 ... --json
npm view @config-plugins/react-native-webrtc@15.0.2 ... --json
docker buildx imagetools inspect coturn/coturn:4.17.2-r0
git ls-remote https://github.com/coturn/coturn.git refs/tags/4.17.2 refs/tags/4.17.2^{}
```

Primary references:

- [Expo SDK 57 compatibility and platform table](https://docs.expo.dev/versions/v57.0.0/)
- [Expo custom native-code workflow](https://docs.expo.dev/workflow/customizing/)
- [React Native WebRTC repository and supported architectures](https://github.com/react-native-webrtc/react-native-webrtc)
- [React Native WebRTC iOS installation](https://github.com/react-native-webrtc/react-native-webrtc/blob/master/Documentation/iOSInstallation.md)
- [React Native WebRTC Android installation](https://github.com/react-native-webrtc/react-native-webrtc/blob/master/Documentation/AndroidInstallation.md)
- [Rejected Expo WebRTC config plugin source](https://github.com/expo/config-plugins/tree/main/packages/react-native-webrtc)
- [React Native WebRTC Android manifest](https://github.com/react-native-webrtc/react-native-webrtc/blob/124.0.8/android/src/main/AndroidManifest.xml)
- [coturn 4.17.2 release](https://github.com/coturn/coturn/releases/tag/4.17.2)
- [Official coturn container tags](https://hub.docker.com/r/coturn/coturn/tags)
- [coturn licence](https://github.com/coturn/coturn/blob/4.17.2/LICENSE)

## Reviewer gate

| Reviewer | Required decision before closure |
|---|---|
| Mobile + Voice/WebRTC | Accept the bridge, project-owned minimal CNG plugin design, permissions, effective OS/toolchain matrix, development-build workflow, and physical-device evidence plan |
| Identity/Security | Accept package licences, microphone-only permission boundary, digest pin, secret handling, credential TTL, relay-only policy, and residual upstream/supply-chain risk |
| QA/Validation | Accept the emulator/physical/cross-platform/audio-route matrix and define artifact ownership for every required result |
| DevOps/SRE | Accept the multi-architecture digest, collision-free ports, isolation, hardening, resources, readiness, failure injection, and scoped cleanup plan |
| Implementation Director | Accept the exact reviewed commit and separately authorize a bounded implementation branch |

Until those decisions are recorded, `VBL-04=OPEN`, `VBL-05=OPEN`, `DEP-007=OPEN`, and
`IMPLEMENTATION_AUTHORIZED=NO`.
