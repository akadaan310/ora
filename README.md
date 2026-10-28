# ORA Engine & SDK 0.2 — launchable model-free foundation

**Company:** GLASS · **Product:** ORA Space · **Core repository destination:** `ORA` (not GLASS) · **Website repository destination:** `ORASPACE` (not HOMELESS). **Root runtime ORA:** ORA Sovereign. **Highest Unison source oracle:** GLASSACLE. Founder's spelling **Abed Kadaan**. ORA is O-R-A, never A-U-R-A.

**This version can actually run on a machine.** It starts a persistent ORA service, exposes a website and HTTP API, creates ORAs with immutable URLs, activates them, executes a handful of honest model-free missions, and records hash-chained events. It does **not** establish global internet service, user signups, public HTTPS, installed Android workers or unrestricted agents. Its full scope is recorded in `docs/GLASS_TOWER.md`.

## Run together with ORA Space web

Keep two directories beside each other (after owner creates corresponding repositories):

```
workspace/
  ORA/             <-- this SDK / backend
  ORASPACE/       <-- site and mobile client source
```

Build and test on **the Oracle ARM64 VM itself**:

```bash
cd ORA
./scripts/check.sh
./scripts/run_local.sh
```

For the current downloadable folder names, the same script autodetects `../ORASPACE/web`.
Open **http://127.0.0.1:8767** from a browser on the *same host*; for phone access, a trusted HTTPS reverse proxy and auth/session setup are required. Don't assume that `127.0.0.1` on your Android phone points to the Oracle VM. `ORA_ADMIN_TOKEN` (at least 32 characters) is required before binding non-loopback. Public deployment requires additional authentication, TLS and hardening; do not simply change `--host` to 0.0.0.0 and call it safe.

## SDK and actual capabilities

- C++20 `libora.so` built from `include/ora/tower.hpp`, `src/tower.cpp`, `src/c_api.cpp`; C ABI `ora_version`, `ora_inspect`, `ora_scene`, `ora_compile`. Portable *source*; compiled `.so` target-specific.
- Python 3.11+ server and SDK client `sdk/python/ora_client.py` using the standard library. TypeScript transport example at `sdk/typescript/ora.ts`.
- SQLite WAL persistent ORA identities, five orthogonal regions, missions, event chain, capability grants and proposed types; one background worker.
- Working capabilities: `language.inspect`, `article.structure`, `scene.generate`, `grammar.propose`, `clock.sample`, and `ora.delegate` (delegation proposals only).
- **Not working in v0.2:** Wikimedia retrieval, full morphology, open-ended web navigation, model integrations, generated compiler production, marketplace, full self-directed agent planning, signed ORB installation, actual Android/cloud sync. The 160 founding ORAs are *candidates* in `catalog/160_candidates.json`.
- The event listener can propose ORAs from an authorized `CAPABILITY_GAP` event and mark logical `NETWORK_DISCONNECTED/NETWORK_RECONNECTED` states; it **cannot perform offline/cloud synchronization yet**.

## Example for Muse, Codex, or another script

```bash
# With local engine already running
python3 examples/muse_create_ora.py
```

It creates one language ORA, explicitly reviews/activates it, executes a Unicode script-inspection mission, and returns an actual stable local `/o/{id}` URL. No credentials embedded in the source. For remote use, set `ORA_BASE_URL` to an actually deployed and authorized HTTPS host and pass `ORA_ADMIN_TOKEN` securely through the process environment.

## Two dimensions of repeatability

- Deterministic: seeded star geometry and pinned text analysis under defined engine/profile; C++ and service tests verify sample fixtures.
- Reproducible event history: SHA-256 chain verifies logged transitions. Because no independent signed checkpoint exists, malicious database administrators could rewrite history; do not claim tamper-proof provenance.

## Audit commands

```bash
./scripts/check.sh
curl http://127.0.0.1:8767/api/v1/health
curl http://127.0.0.1:8767/api/v1/tower
curl http://127.0.0.1:8767/.well-known/ora.json
```

## Documents

- [`docs/GLASS_TOWER.md`](docs/GLASS_TOWER.md): names, hierarchy, maths, distinction between form/letter/operator/compiler/machine/generator/oracle/ORB/ORA.
- [`docs/ORA_CONTINUITY_AND_API.md`](docs/ORA_CONTINUITY_AND_API.md): REST and PURL-style path protocol, examples, negotiation boundary.
- [`docs/CODEX_SINGLE_COMMISSION.md`](docs/CODEX_SINGLE_COMMISSION.md): one full Codex continuation including Oracle VM verification and service deployment gates.

**Deployment truth:** This code was compiled and tested in this conversation's working container, *not on the Oracle VM*. The Gateway connector returned no registered servers. The exact repositories `akadaan310/ORA` and `akadaan310/ORASPACE` were verified as existing and writable on October 28, 2026; public HTTPS deployment is a separate step. Do not claim the service is live on Oracle until the host and HTTPS endpoint are actually verified.
