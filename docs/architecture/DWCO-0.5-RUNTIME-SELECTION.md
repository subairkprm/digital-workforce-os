# DWCO 0.5 dependency and local runtime selection

SELECTION_STATUS=PROPOSED_FOR_SECURITY_QA_DEVOPS_APPROVAL

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
| Expo config plugin | `@config-plugins/react-native-webrtc@15.0.2` | npm integrity `sha512-sH4T7Z4P2RowV91k9CEwEr0unn+396NBexxCNZwRXuJXwguDU1qZWpE6fcwN0730B8uiS83F7+CLTyhpC7qRHQ==`; MIT | Peer range accepts Expo `>=56`; upstream compatibility table does not yet name SDK 57, so clean prebuild/build proof is mandatory |

The application must use an Expo development build. Expo Go is excluded because the selected bridge
contains custom native code. The config plugin must supply an explicit microphone permission message.
Camera permission and video capture are prohibited in this audio-only stage even if upstream defaults
or library capabilities include them. Any generated permission or manifest expansion outside this
contract is a review failure.

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
| Listener | Host loopback `13478` UDP/TCP; no host networking and no public STUN |
| Relay range | UDP `49160-49259`, bounded to the isolated voice-test project |
| Resource ceiling | 1 CPU, 256 MiB memory, 100 PIDs, 65,536 open files; Docker logs 10 MiB times three |
| Hardening proposal | Drop all capabilities, no-new-privileges, read-only root, bounded tmpfs, documented non-root UID where supported |
| Secret proposal | Fresh ignored `.env.dwco-voice-ci-turn-secret`, mounted read-only as a Docker secret and removed by scoped cleanup |
| Readiness | Fresh authenticated allocation plus bidirectional relay probe from a separate test peer; a process/port check alone fails |

The manifest digest was resolved without pulling or running the image. Resource, UID, read-only,
secret, allocation, port, and cleanup settings remain unproven until the implementation evidence gate.
TLS/TCP 5349, DNS, public ingress, certificates, staging, and production TURN remain excluded under
DEP-007 and DEP-012.

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
- [Expo WebRTC config plugin](https://github.com/expo/config-plugins/tree/main/packages/react-native-webrtc)
- [coturn 4.17.2 release](https://github.com/coturn/coturn/releases/tag/4.17.2)
- [Official coturn container tags](https://hub.docker.com/r/coturn/coturn/tags)
- [coturn licence](https://github.com/coturn/coturn/blob/4.17.2/LICENSE)

## Reviewer gate

| Reviewer | Required decision before closure |
|---|---|
| Mobile + Voice/WebRTC | Accept the package pair, permissions, effective OS/toolchain matrix, development-build workflow, and physical-device evidence plan |
| Identity/Security | Accept package licences, microphone-only permission boundary, digest pin, secret handling, credential TTL, relay-only policy, and residual upstream/supply-chain risk |
| QA/Validation | Accept the emulator/physical/cross-platform/audio-route matrix and define artifact ownership for every required result |
| DevOps/SRE | Accept the multi-architecture digest, collision-free ports, isolation, hardening, resources, readiness, failure injection, and scoped cleanup plan |
| Implementation Director | Accept the exact reviewed commit and separately authorize a bounded implementation branch |

Until those decisions are recorded, `VBL-04=OPEN`, `VBL-05=OPEN`, `DEP-007=OPEN`, and
`IMPLEMENTATION_AUTHORIZED=NO`.
