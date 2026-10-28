# ORA Sovereign + ORA Space — single end-to-end Codex continuation commission

**Date:** 2026-10-28 · **Owner:** Abed Kadaan · **Company:** GLASS · **Product spelling:** ORA (O-R-A) · **Runtime governor:** ORA Sovereign · **Top Unison Oracle:** GLASSACLE · **Repository split:** `ORA` = engine/SDK/service; `ORASPACE` = consumer web/mobile UI. **Do not put the new app in `GLASS` or `HOMELESS`.**

## Absolute premise

**You, Codex, are already running on the owner's Oracle ARM64 VM.** Before asking for host/SSH details or claiming Gateway is available, run `uname -m`, `hostnamectl`/kernel checks, `pwd`, `git status`, `ss -ltn`, and inspect actual user services and installed reverse-proxy configuration. Obtain domain names, DNS and TLS facts *from authorized local configuration* only; never print passwords, keys, tokens or private user files. Your execution environment and this chat's Gateway connector are independent. The ChatGPT Gateway connection returned zero registered servers; do not infer that means your own Codex shell lacks access to the VM. If you are not actually on the Oracle VM, record the discrepancy and stop the deployment portion, but continue local tests.

## Source packages you receive

- `ORA_ENGINE_001` (C++20, Python stdlib service, documented 12-level GLASS Tower, REST/PURL-aligned URL previews, candidate catalogue, C++ and service tests, sample ORB definitions, example SDK clients).
- `ORASPACE` (functional ORA Space web client, center-field creation, lifespan controls and real mission receipts).

These are **verified executable seeds**, not production-complete. Preserve source files and audit receipts; integrate into the two owner-created GitHub repositories using commits to `main` once confirmed and permitted. If either repo does not exist, do not push to GLASS as a fallback. Keep package contents separately, ask owner to create intended repos through GitHub's UI if necessary, and report precise blockers. No Railway; no GitHub Actions.

## Phase 1 — Preserve and verify

1. Inspect both repository remotes and any owner changes; don't overwrite or force-push. Record heads and tree states.
2. Compile `ORA` with `make all` on **ARM64**, and run `python3 -m unittest discover -s tests -v` (20 service tests plus C++ test when package was prepared). Report exact results and architecture. No x86 `.so` should be reused on ARM64; build from source.
3. Run `./scripts/run_local.sh` with `ORA_SPACE_WEB_DIR` pointing to sibling website. Verify `GET /api/v1/health`, `GET /api/v1/tower`, `GET /.well-known/ora.json`, manifest URL, safe shifted URL, and authenticated instance/missions APIs.
4. Make a test ORA from the web and from `sdk/python/ora_client.py`; review, activate, execute `language.inspect`, `article.structure`, `scene.generate`, `grammar.propose` against controlled fixtures; assert that unknown `model.text`, `wiki.fetch`, `browser.navigate` and music synthesis remain **not implemented**, not fake success.
5. Run a mobile browser Playwright (or Chrome remote debugging) visual/interactive test in 390px portrait and 1536px landscape; ensure center input, create, review, activate and mission receipt are all clickable, scrolling works, reduced motion obeyed, no detached result element or overflow. Match owner's chosen approved screenshots only when supplied; the current web visual is a functional placeholder.

## Phase 2 — Harden source of truth and Tower semantics

1. Convert the local executable capability registry and ORB manifest entries into one validated schema-controlled source, with version pinning and content hashing; build admission tests for every operator.
2. Preserve the `GLASSACLE`/Unison knowledge layer as the highest Oracle source, independent of ORA Sovereign tenant policy. Expand explicit script/glyph registry, form alphabet, productions, type effects, AST/IR, operator algebra and generated machine recipes **one bounded language at a time** (Latin, Greek, Arabic hijāʾī/abjad and QITṬ profile names). No unsupported claims about sacred etymology or historical computational machines.
3. Stabilize orthogonal FSM region transitions with atomic snapshots and transactional DB commits; model authority grants, lease/version conflicts, cancellation, mission checkpoints, resource/time budgets, crash recovery and idempotency.
4. Use SQLite for single-VM lab only; migrate to Postgres when multi-worker, multi-tenant workloads require it. Append signed ledger checkpoints (crypto and key rotation), owner/tenant ACLs, secrets vault, per-user session isolation and audit log retention.
5. Implement `ORA-N` bounded specialist negotiation as described in the owner foundation: `DISCOVER → OFFER → VALIDATE → ACCEPT/COUNTER → LEASED → RUN → VERIFY → RECEIPT`. Allow Wikipedia ORA to call Language ORA using typed artifact references and a continuation handle. Deny unsupported schemas and permissions.
6. Preserve PURL's resource manifest semantics and seURL's seven verbs. `WITNESS` is a new proposed ORA extension; do not silently modify the original protocols. URL path shifts remain **pure previews**—link crawlers/LLM browsers may inspect, but only explicit authenticated commands mutate. Add invalid path, expired nonce, replay, 409/412 version-conflict tests.

## Phase 3 — Real runtime/SDK deployment

1. Introduce a bounded worker host for ORAs with supervisor/watchdog, declared resource quotas, worker heartbeats, runtime placement (`oracle`, Android/Termux later, HOMELESS adapter later), and safe execution. Child grants may only be attenuated: `grants(child) ⊆ grants(parent)`. Do not give arbitrary internet access or shell tools to all ORAs.
2. Make `CAPABILITY_GAP` a governed listener: can propose a child ORA, install a **candidate** ORB and request explicit review; cannot self-approve or spawn infinite agents.
3. Compile native `libora.so` and expose stable C ABI with forward-compatible versioning; include Python and TypeScript SDK transports; build test harness for Android NDK shared object in a separate scoped target, never ship x86 binary to mobile. Package as `libora`, `ora-engine` service, `ora-space` front end.
4. Optional LLM, speech, image and web/browser tools remain individually declared adapters with gated network, cost limits, receipts, MIME/HTML sanitization and provider authorization. The model is a **fuel stop** at explicitly detected insufficiency, not the foundation. Never claim a small model fits a fixed 2 GB without measuring context and runtime.
5. Reserve near-term specialist bootstrap ORAs: Language (Unicode/grammar), Wikipedia (source-respecting article AST and revisioned MediaWiki access when approved), Scene (SURFACE geometry), Clock, Continuity, Generator Forge (reviewed proposals), and HOMELESS connector. The 160 candidate profiles are **unimplemented** until each passes independent fixtures.
6. Implement a Web / Android offline Continuity Twin later using local append-only events, cloud assigned missions and bounded sync. Do not imply a device without network service is online. Reconnection merges independent events and exposes noncommutative conflicts for review.

## Phase 4 — Real consumer ORA Space launch

1. Inspect existing `ORASPACE` repo before changing it. Keep it separate from engine. Use approved screenshot art direction with premium calm orbital light, translucent central field, atmospheric water and real state-bound orb clusters. Three.js is optional for water/rendering; use geometry/detail streaming/LOD rather than overbuild a game engine. Respect mobile FPS, memory, accessibility and reduced-motion.
2. Center is universal ORA mediator: every nav/orb/selector action updates the center composer/context; all running ORAs get status from actual server events. No fake status counts or fabricated 'training' claims.
3. For multi-user public signup, add real account authentication, password/passkey/OAuth as needed, ownership, quotas, privacy policy, consent, transport TLS and tamper controls. **Do not expose the temporary single-owner API to the public.** The default app requires no arbitrary identity documents.
4. Use verified DNS and a tested HTTPS reverse proxy (Caddy/nginx) to expose frontend and authenticated API from Oracle VM; no secrets or auth tokens in publicly copyable ORA URL paths. Test a public read-only capsule from a disconnected browser, confirm that no side effects occur, then test owner-authenticated commands.
5. Provide runbook, service health endpoint, restart policy, backup/recovery and exact live URL only after actually verifying them. If blocked, state what is functioning and what is not; do not ask the owner for secrets in chat.

## Definition of done for first service

- `ORA` and `ORASPACE` each exist as distinct repositories on the appropriate branches; neither overwrites GLASS.
- C++ shared library builds on Oracle ARM64; all automated tests pass, including negative permission and concurrency tests.
- Real service installed as user-level systemd/managed service on Oracle VM; survives restart and reports health.
- One owner can enter a goal, propose ORA, inspect limited admitted capabilities, review/activate it, run a real typed mission and observe a receipt from Android browser over a verified HTTPS URL.
- Both URL shifting and resource manifest can be read by an external agent without executing state changes; delegated execution requires authorization.
- Source/protocol science is documented; each unsupported feature clearly marked as such. Real device-worker networking, full model stack and 160 specialists remain later milestones.

**Owner priorities:** one comprehensive commission; evidence before claims; no unnecessary repo duplication; no Railway or GitHub Actions; Git main current after verified commits; user-facing design target is owner's approved ORA Space imagery, not a conventional dashboard; keep ORA spelling exactly O-R-A.
