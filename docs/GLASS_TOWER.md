# The GLASS Tower: ORA's constitutional hierarchy (working science v0.2)

**GLASS company → Substrate University research → Delphi evidence → Unison and ORA implementation.**

The Tower is a *typed dependency graph*, not a mystical proof that every layer is implemented, or an assertion of scientific novelty. An alphabet is not a compiler; a compiler is not a generator; a generator is not an autonomous agent. Every capability has dependencies and an evidence status.

## Twelve levels — what each produces

| L | Name | Input → output | Examples | v0.2 status |
|---:|---|---|---|---|
| 0 | Observation | physical/logical event → typed record | bytes, timestamp, source digest, clock tick | SQLite event ledger, SHA-256 chain |
| 1 | Letter | code point/lexeme → identified symbol | Latin, Greek, Arabic hijāʾī/abjad, Unison glyphs | C++ symbol/alphabet registry; full canonical packs pending |
| 2 | Form | symbols + features → typed representations | Arabic root/pattern, AST node shape, musical interval form | C++ `Form` declaration only |
| 3 | Grammar | productions + constraints → parsable expressions | mission syntax, article headings, PURL paths | limited Unison compiler, wiki syntax parser |
| 4 | Operator | typed expression → typed effect/result | OBSERVE, ANALYZE, GENERATE, PURL shift verbs | C++ operator registry and review gates |
| 5 | Compiler | source → tokens/AST/IR → checked output | constrained AST, URL preview compiler | minimal C++ mission compiler and Python URL compiler |
| 6 | Machine | state + event + guards → next state/evidence | lifecycle; authority; clock; continuity | orthogonal C++ FSM, persisted service regions |
| 7 | Generator | grammar + seed + parameters → artifact + witness | reproducible starfield, candidate lexical rules | C++ seeded star output; lexical proposal |
| 8 | Oracle | domain data + rules + evidence → bounded answer | Language, Wikipedia text, Cosmos | working limited text/scene oracles; not full corpora |
| 9 | ORB | versioned admitted capability packs → portable composition | Language ORB; Scene ORB | contract only; signed bundles pending |
| 10 | ORA | identity + delegated rights + missions + runtime → operating specialist | Wikipedia ORA, Scene ORA | real persisted instances, 5 mission types (plus delegate request) |
| 11 | ORA Sovereign | tenant-level registry + policy + receipts → governed constellation | parent ORA; placement and delegation | launched with service; NOT an unrestricted root shell |

**Naming:** `GLASSACLE` is the earlier source concept for the *highest Unison Oracle* (knowledge/operator layer). **ORA Sovereign** is the *runtime governor of ORA identities* (agent/orchestration layer). They are not synonyms. `ORA` is always written O-R-A. `ORA Space` is the consumer app and website; `ORA` repository is the engine and SDK. The user's corrected founder/credit spelling is **Abed Kadaan**.

## Typed mathematical contracts

Let `Σ` be a versioned alphabet, `Γ` a grammar, `Ω` the admitted operators, `S` a machine's product state, `K` a versioned knowledge corpus and `P` a continuity protocol.

A typing judgment marks side effects:

`Γ; Ω ⊢ e : τ ! ε` where `τ` is output type and `ε ∈ {PURE, OBSERVE, LOCAL_WRITE, NETWORK, PRIVILEGED}`.

Compile a supported expression using a versioned route:

`C_(Σ,Γ,Ω)(e) = lower(typecheck(parse(tokenize(e))))`.

Parsing success **is not permission to execute**. A successful parse produces a typed AST and effect obligations. The current C++ reference understands only `OBSERVE <subject>`, `ANALYZE <text>`, `GENERATE <recipe>`; arbitrary English appears as a proposed ORA goal, not a proven AST.

A machine with orthogonal state regions has

`S = S_lifecycle × S_execution × S_observation × S_authority × S_continuity`.

At a tick an event may update multiple regions; every guard reads a common prior snapshot, write conflicts reject the batch, and a successful commit produces a receipt. The C++ `Machine` implements snapshot-based atomicity within one in-process ORA; the Python service persists separate regions and serializes writes. *Distributed state-machine synchronization is not implemented.*

A generator is

`G : (Γ, Ω, inputs, seed, budget) → (candidate_artifact, test_evidence)`.

Its outputs are not automatically admitted. Registration requires distinguishability, explicit semantics/axioms, unfolding, independent fixtures and review. Failed candidates persist in the research catalogue.

An ORA can be formalized as

`O=(id,K,Σ,Γ,Ω,S,G,M,A,R,E,P)`

with `M` missions, `A` authority, `R` replicas, `E` evidence. A **mission** is a goal and success contract, whereas a **machine** is a transition mechanism used to accomplish goals. `ORA Sovereign` does not bypass authority: `grants(child) ⊆ grants(parent)`.

## An alphabet of forms, compilers and generators

The user's phrase *"alphabets of what?"* is resolved as a family of **typed namespaces** rather than treating all domains as letters:

- **Letter alphabets:** canonical script symbols, codepoints, graphemes and their historical register forms; Arabic abjad and hijāʾī have distinct orderings. QITṬ is GLASS's modern computational interpretation, not an ancient executable CPU.
- **Form alphabets:** AST node kinds; root-and-pattern morphology features; vector geometry shapes; musical modes/interval features; event forms. A form can contain compound values, not just a single glyph.
- **Operator alphabets:** typed verbs and laws, including Unison and seURL-inspired `START SWITCH WRITE COMMIT BUILD TALK PERTURB` and proposed `WITNESS`.
- **Compiler alphabets:** admissible tokens, parsing productions, AST node signatures, typing rules, IR instructions and emission targets. A compiler *consumes an alphabet* and transforms representations; it is not literally a letter.
- **Machine alphabets:** allowed state names, event kinds, guards, resource effects and transition labels.
- **Generator alphabets:** recipe grammar, allowed combinators, parameters, constraints, evaluation fixtures and outputs.
- **Oracle alphabets:** domain-specific accepted primitives (e.g. citations/sections, sky catalog identity/epoch, musical notes/time signatures).
- **Continuity alphabet:** identifiers, authority scopes, effect-bearing candidate programs, receipts, branches and replay heads.

Every namespace is versioned and has its own provenance. The same glyph used in two alphabets does **not** imply equal semantics. An extensible namespace is operationally finite at any moment; it is not an actually materialized infinity.

## Building up the first actual ORAs

| ORA | Bundled domain interfaces | Actually executable today |
|---|---|---|
| `ORA Sovereign` | lifecycle, delegation, event ledger | Govern instances, issue proposals, dispatch admitted local missions |
| `Language ORA` | Unicode source, scripts, tokenization | Inspect script distributions and token counts |
| `Wikipedia ORA` | Section grammar, wikilinks and source fingerprints | Parse user-provided article text only; no live Wikipedia fetch |
| `Scene ORA` | SURFACE star generator and clock | Generate deterministic seeded scene manifests |
| `Grammar ORA` | Unison candidate lexical grammar | Propose lexical rules; not self-admit |
| `Clock ORA` | Wall clock observation | Sample current time with explicit nondeterminism |
| `Music ORA`, `Shopify ORA`, `Browser ORA` | Research-defined but unadmitted adapters | Cannot yet do actual specialist work |

The attached catalogue enumerates **160 candidate profiles**, not 160 running ORAs. Product UI may preview these profiles with `SPECIFIED_NOT_IMPLEMENTED` labels.

## Reproducibility and trust boundaries

- Native scene generator: identical seed + count + same supported compiled environment → identical scene JSON within the demonstrated test profile. Floating-point portability across systems must be independently checked.
- Real text analysis: identical supplied Unicode input and same engine → same structured counts/source digest; not guaranteed semantic truth.
- Event ledger: SHA-256 **tamper-evidence against ordinary accidental edits**, but no independent witness/signature yet. A malicious DB administrator can rewrite an unsigned chain.
- Optional text/image/speech models: future isolated plugins. Stochastic output must be captured; never label model observations deterministic without frozen inputs/settings and controlled execution.
- URL previews: parsing must have no side effects. A user clicking a link is not proof of authorization.

## Source genealogy

Grounded in the owner's ORA Space founding constitution, 160-profile catalogue, HOMELESS World 001 mathematical rendering and GLASS repositories. PURL resource manifests and seURL's seven URL verbs are references; full production protocol compatibility remains an explicit test requirement. Before declaring ACSP/ASPS compliance, read and verify the actual current specification.

