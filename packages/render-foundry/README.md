# GLASS Render Foundry ORA v0.1

**Correct product spelling: ORA (O-R-A)**. This is an implemented **bounded ORA research package**, not a new OS, not admitted to the public ORA runtime, not a cloud renderer, and not deployed on the Oracle VM.

It compiles reusable World Cell recipes for World OS, HOMELESS and ORA Space. Each recipe has version, seed, node identities, spatial transforms, GPU target and a hash for cache reuse. It emits an actual *glTF 2.0 file* containing shared geometry and multiple nodes, rather than storing a separately generated mesh for each building. GPU baking is a future adapter with explicit budget limits; the public website and game consume the same *asset* contracts but may render using different camera/physics constraints.

## Source and proof

- `render_foundry.py`: typed recipe compiler, glTF2 exporter, cache validator and ORA manifest.
- `server.py`: read-only ORA manifest URL plus authorized local compile/build endpoints.
- `examples/waterfront-cell.json`: an eight-instance waterfront using shared building, road, plaza, lamp and water templates.
- `tests/`: CLI/cache and full HTTP route tests. No external packages or cloud spend.

## Start the ORA locally

```sh
python3 render_foundry.py manifest
python3 render_foundry.py plan --recipe examples/waterfront-cell.json
python3 render_foundry.py build --recipe examples/waterfront-cell.json --output render-cache
python3 -m unittest discover -s tests -v
python3 server.py --host 127.0.0.1 --port 8877
```

Then open `http://127.0.0.1:8877/o/ora-render-foundry/manifest`. An authorized Codex process can read that address on the **same host** while the service runs, and can call `POST /api/v1/render-foundry/plan` or `/build` with the typed recipe. A URL alone does not attach this assistant to a VM or grant privileged access. A public URL requires TLS, session authorization and a managed server deployment.

## Status and provenance

| Function | Actual state |
|---|---|
| World Cell recipe/type validation | **Implemented** |
| Reusable glTF mesh/node export | **Implemented** |
| Deterministic cache keys & verification | **Implemented** |
| Addressable local ORA manifest/HTTP API | **Implemented** |
| Blender Cycles GPU baking | **Not integrated** |
| Modal L4/L40S GPU execution | **Not integrated** |
| HDR/EXR lightmaps, water FFT and KTX2 output | **Not integrated** |
| Live ORA OS service/tenant authorization | **Not integrated** |
| Shared sky integration for HOMELESS | **Contract only** |

Future ORA admissions: add an `ORA/` capability registry integration, `render.gpu.bake` provider adapter, content-addressed artifact/object store, strict cost cap and renderer-version checks, signed asset licensing records, mobile performance benchmarks, and true GPU-side baking. No fake performance or $0 perpetual hosting claim.
