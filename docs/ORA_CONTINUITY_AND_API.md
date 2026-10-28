# ORA Continuity v0.2 · live reference API

This SDK implements a local HTTP service and programmable **read-only PURL-style URL interpreter**. It does not claim deployed public web addresses or the entirety of ACSP/seURL compatibility. All URL examples below use local loopback until the owner supplies a real domain and trusted HTTPS proxy.

## Identity & mission lifecycle

- Parent governor: `ora-sovereign` (service-owned; not a privileged shell).
- Created ORA: `ora-<18 hex digits>`; immutable ID, unique human slug, a parent, version and placement *intent*.
- An ORA is a service object with lifecycle `PROPOSED → READY → RUNNING → PAUSED / STOPPED` and independent `observation`, `execution`, `authority`, `continuity` state regions. `STOPPED` terminal in v0.2.
- Grants are selected from currently admitted local capabilities and must be a subset of parent's grants. Unknown adapters are shown as `missing`, not silently executed.
- Missions are `QUEUED → RUNNING → SUCCEEDED / FAILED`, with persistent inputs/outputs and event receipts. Repeated `Idempotency-Key` with different input is a conflict. Main worker is a single thread with resource-limited operations, not a general-purpose shell.
- `observe CAPABILITY_GAP` constructs an ORA *proposal* subject to review, not an automatically trusted launched child.

## HTTP contract

| Method | Endpoint | Effect |
|---|---|---|
| GET | `/api/v1/health` | Service diagnostics and ledger verification |
| GET | `/api/v1/tower` | Full 12-level Tower schema |
| GET | `/.well-known/ora.json` | ORA protocol and eight verb descriptions |
| GET | `/api/v1/capabilities` | Available and unsupported capability states |
| GET | `/api/v1/catalog?offset=0&limit=12` | The 160 named profile **candidates**, not running agents |
| GET | `/o/{id}` | Redacted public identity (no personal goal) |
| GET | `/o/{id}/manifest` | Redacted typed public manifest; capabilities only |
| GET | `/o/{id}/purl/v1/shift/{VERB}/input/{REF}/preview` | Pure typed AST preview; absolutely no effects |
| GET | `/api/v1/oras` | Owner-authenticated ORA constellation |
| GET | `/api/v1/events?after={seq}` | Owner-authenticated event polling (1–2s browser cadence) |
| GET | `/api/v1/missions/{id}` | Owner-authenticated mission status/results |
| POST | `/api/v1/oras` | Create a proposal, infer supported/missing capabilities |
| POST | `/api/v1/oras/{id}/transition` | Explicit owner review/start/stop/pause/resume |
| POST | `/api/v1/oras/{id}/missions` | Enqueue admitted mission after lifecycle and grants checks |
| POST | `/api/v1/observe` | Authoritative event-lane trigger (CAPABILITY_GAP or offline/online state) |

All POSTs use JSON and are rejected when `Origin` does not match the expected host. For non-loopback binding, `ORA_ADMIN_TOKEN` of at least 32 characters is mandatory. **The service provides no TLS, OIDC, signup, multi-tenancy or public rate-limiting**. Put it behind a trusted HTTPS reverse proxy and implement user sessions before opening it to consumers. The endpoint can serve an initial single-owner lab, not arbitrary public signups.

## URL shifting with seURL's operator language

```
/o/ora-1234abcd/purl/v1/shift/BUILD/input/candidate_X1/preview
```

A navigation shifts symbolic values between path segments, which the server compiles into `{ora_id, verb, input_ref, program_hash, effect: PREVIEW_ONLY}`. The verb may read `START SWITCH WRITE COMMIT BUILD TALK PERTURB WITNESS`. A path containing `COMMIT` is still a *preview*, not a committed operation. HTTPS GET is still the network method; it does not cause mutation. A trusted executor must follow the separately authenticated API mutation flow with grants, version checks and logged receipts.

The source PURL project uses manifests and continuity operations; this prototype's URI grammar deliberately remains an adapter until full compatibility verification is performed. PURL authorization is not inherited from a URL string.

## Example: Muse creates and runs a Language ORA

```bash
# On a machine running the ORA Engine; for a remote installation use its real HTTPS base.
python3 examples/muse_create_ora.py
```

Or through the SDK:

```python
from ora_client import ORAClient
client = ORAClient('http://127.0.0.1:8767')
ora = client.create('Study Arabic and Greek text patterns', name='Muse Language ORA')
ora = client.transition(ora['id'], 'review', ora['version'])
ora = client.transition(ora['id'], 'activate', ora['version'])
receipt = client.mission(ora['id'], 'language.inspect', {'text':'مرحبا and Γεια'})
print(client.manifest(ora['id']))
```

The returned URI is local until the service is publicly hosted; Muse and Codex must use a reachable, authorized deployment URL for remote collaboration. Per-tenant privacy and individual user tokens are future work.

## Reference negotiation to build next

The 2026-10-28 ORA Space foundation contains a **pure protocol lab** for `DISCOVER → OFFER → VALIDATE → ACCEPT/COUNTER → LEASED → RUN → VERIFY → RECEIPT` with three-round bounds and a twin-event merge demonstration. Those remain separate from this live service until independently tested under multi-ORA authority, crash recovery, signed requests and real resource constraints.
