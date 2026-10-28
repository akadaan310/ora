# ORA 360 · First executable end-to-end attempt (0.3)

**Identity:** GLASS · ORA · ORA OS · ORA Space (web repository `akadaan310/ORASPACE`, engine repository `akadaan310/ORA`). Canonical spelling **ORA**, not alternate forms.

**Scope:** a running private/local reference, not the entire ORA OS ecosystem. Built on the existing `ORA` 0.2 engine and tested locally. Separate public hosting, OAuth, account creation, and Oracle VM deployment are pending: the connected Gateway currently reports **zero registered Oracle hosts**. Do not confuse screenshots with public availability.

## Run

```bash
# Work with both repositories cloned as siblings on the actual Oracle VM/host:
cd ORA
./scripts/check.sh
python3 -m unittest discover -s tests -v
python3 -m service.oraspace360 --host 127.0.0.1 --port 8767 --db data/ora.sqlite3 --db360 data/ora360.sqlite3 --web ../ORASPACE/web
# Open http://127.0.0.1:8767 from the SAME host.
```

The existing `ORA` service remains available and is **extended** with `/api/v1/360/*`. The consumer website is loaded from the sibling `ORASPACE/web`. New website resources are `index.html`, `style.css`, `scene.js`, and `app.js`. The new `ora360.py` module uses durable SQLite WAL. Its objects link to immutable ORA IDs created by the established `service.engine.Engine`.

**Security:** loopback-only is a single-owner development setting. For external use, put it behind HTTPS and a real authentication/reverse proxy; provide `ORA_ADMIN_TOKEN` (>=32 chars). A global admin Bearer token **is not** a production multi-user session. The login modal intentionally says so. Do not expose loopback development mode to the public. `ora360` provides owner roles only; real tenant isolation and per-account records are required before public launch.

## User story, with exact implementation boundary

1. Open ORA Space. The 2.5D painter displays stars, dusk, city, harbor, orbits, and responsive sphere/landing vessel. This is a **real Canvas rendering**, not a photo or complete hydrodynamic simulation. We have used actual source-like geometry to establish the experience. Add Three.js `Water` with WebGL for later physically based reflections; WebGPU needs `WaterMesh` and an explicit renderer decision.
2. Type one concept. `POST /api/v1/360/realize` creates an established ORA **proposal** and an ORA 360 artifact record in one HTTP workflow. Client/server share an explicit preview/live distinction; a logged-out visitor gets a local preview with no fake persistence.
3. Switch between eight different materializations: web, article, paper, app, SVG, email draft, storyboard, API. All derive from **one source intent**. These are bounded deterministic scaffolds with working independent renderers, **not** a polished full video, real published website or verified research paper.
4. Review and approve the artifact. Only local status changes to `REALIZED_LOCAL`; no external publishing, SMTP delivery, or commercial integration is performed.
5. Create an **ORA anchor URL** for Codex: `GET /o/{ora_id}/anchor/{anchor_id}` is safe and readable but never a grant. The owner receives a one-time secret in the creation POST, which must be supplied separately via secure process environment when Codex attaches. `POST /api/v1/360/anchors/{id}/attach` requires owner authentication, matching principal, token, expiry and one-time state. No background assistant session or remote shell is conjured by reading a link.
6. Offer a first redacted Baton: `POST /api/v1/360/batons`; `GET /b/{id}/capsule` is a read-only public summary. Version 0.3 does **not** implement the full two-way Baton protocol or machine-to-machine messaging; that belongs to the separate hardened Baton PR.
7. Poll `/api/v1/360/events?after=N` and verify SHA-256 event hashes. A local hash chain provides elementary tamper evidence, **not** independently anchored cryptographic proof.

## OS creation from ORAs

`GET /api/v1/360/catalog` exposes 12 candidate OS/department blueprints: ORA OS, World OS, Space OS, Life OS, Events OS, GLASS OS, MUSES, Academy, SUPER, HOMELESS, Courier and Creator. Each is an installable **candidate ORA package** with typed contracts, admitted capability prerequisites and independent lab/trace requirements. They are not 12 launched OSes or 12 real cloud agents.

The first production implementation should allow typed seeds to be proposed to ORA Sovereign, tested as package manifests, then promoted to their separate OS repo only after acceptance and evidence. Common continuity is a **portable event envelope**, not duplicate engines or authority inherited from URLs.

## Tool systems and primitive derivatives

`GET /api/v1/360/tools` exposes a schema-study catalogue for GitHub, Notion, Slack, Shopify, email, calendars, publishing, Make, n8n, Zapier, social/media, native ORA OS and Space OS. Nouns/verbs have different effect classes: read/draft can be local; publish/send/write require real provider grants; destructive actions and payments require stricter policy. These are **not live authenticated connectors** yet.

`study_workflow()` recognizes Make `flow`, n8n `nodes` and Zapier `steps` in deliberately bounded, sanitized samples and emits typed **proposals**; it refuses credential fields and marks unsupported node semantics. This is **not parity** with their full catalogues or a runnable import. n8n and Make exports require connection/credential handling independently. Provider semantics, plugin installation and per-account OAuth remain to build.

### Email is a transport, not a popup

The email derivative includes account identity, addresses, mailbox, MIME messages, drafts, attachments, delivery queues, SMTP submission, server-to-server transfer, authentication, JMAP/IMAP reads, spam control, and communication Batons. v0.3 implements **MIME drafts only**. For an owner-operated production mail server, research **Stalwart** (JMAP/IMAP/SMTP) as a connector, not a claim of deployment. DNS MX, SPF, DKIM, DMARC, TLS, reputation, abuse handling and the chosen domain are prerequisites. Do **not** invent a user `@ora` address before the owner controls the domain and receives actual mail.

## ORA / Codex anchoring API sample

```bash
# Only after service is running, over authenticated private transport:
# 1. create an ORA; note its ID from POST /api/v1/360/realize
# 2. owner POST /api/v1/360/anchors with {"ora_id":"...","principal":"codex-oracle","scope":"review-code"}
# 3. give Codex the resulting READ-ONLY URL, NOT the returned secret in the URL.
# 4. owner securely passes the secret to Codex's actual host process.
# 5. Codex POST /api/v1/360/anchors/{id}/attach with matching principal and secret.
# Attached means the handshake happened, not that ChatGPT silently gained SSH access.
```

## Performance and truth guardrails

The website's night sky and waterfront are procedural Canvas 2D with seeded stars and rendered skyline/harbor; CSS renders accessible controls and orbs. This release doesn't load Gaia data, run Julia/Octave, reconstruct physics, or synthesize 3D fluid dynamics. Event-driven ripples are tied to actual user transitions. Mobile reduced motion, foreground/background behavior, responsive layouts and security origin checks have a preliminary path; measure GPU/CPU frame times and user accessibility on a midrange Samsung device before calling it launch quality.

All copyright-sensitive content remains in the user's provided references, **not shipped as a background asset**. Source screenshots are design targets. The original GLASS/HOMELESS repos remain unchanged.

## Open source pointers checked

- Three.js Water documentation https://threejs.org/docs/pages/Water.html and WaterMesh https://threejs.org/docs/pages/WaterMesh.html.
- Make scenario blueprint format https://help.make.com/blueprints
- n8n workflow export/import https://github.com/n8n-io/n8n-docs/blob/main/docs/build/manage-workflows/export-and-import.md
- Zapier developer CLI https://github.com/zapier/zapier-platform/blob/main/packages/cli/docs/cli.md
- Stalwart mail protocol overview https://stalw.art/docs/email/

## Next increments

Full signed Baton handshake, time-anchored Codex session mounts, typed ORB manifests, package validators, per-account OAuth, multi-tenancy, proper mail server domain, actual registered OS subagents, advanced water optics, spatial projection, observational star tiles, and hardened public registration. Until those pass review, they are proposals rather than claims of completion.
