# GLASS Render Foundry ORA — Recorded Architecture

## Why this is an ORA and not an operating system

World OS owns world geometry and geography; Space OS owns astronomical events and light-source models; HOMELESS owns gameplay and interactive physical rules. **Render Foundry is a reusable generator-agent**: it compiles approved world-cell recipes into meshes, cache entries, baked pass requests and receipts, then makes the output usable in many scene viewers. A GPU is an optional tool invoked by this ORA, not its parent or ontological level.

`input recipe → typecheck → stable fingerprint → materialize reusable asset graph → (optional authorized bake) → quality/rights verify → artifact registry → ORA Space/HOMELESS`

**Typed operators**: `SELECT_TEMPLATE`, `PLACE_INSTANCE`, `SHARE_MESH`, `PARAMETERIZE_MATERIAL`, `PLAN_BAKE`, `VERIFY_CACHE`, `PUBLISH_ASSET_REF`. The first three and cache verification are implemented; GPU baking and deployment remain non-executable proposals.

**Cost model**: first render base geometry locally for free; only submit expensive light/water/orb pass jobs after benchmarking frame time. Cloud GPU bill can be zero if never invoked; actual service hosting, data storage, network egress and paid GPU time have independent constraints. Never use the owner's $30 allowance without a budgeted, approved job.

**Optimization principle**: expensive textures, reflections, lightmaps and distant impostor views are *baked once*; near interactive geometry is instanced and shaded on device. Determinism means frozen geometry/seed/renderer-version/source. Photorealistic pixels require high-quality materials and actual GPU baking not in this baseline.

**Identity**: `ora-render-foundry` is a provisional research ORA. A stable `recipe digest` identifies the desired cell, distinct from an immutable `gltf SHA-256` identifying the actual output. The same mesh can appear in several positions; this is actual spatial instancing, not a table-cell metaphor alone.
