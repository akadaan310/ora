# ORA package installer · Termux v0.4

This is an ORA OS package bootstrap: a single curl downloads pinned ORA and ORASPACE revisions, checksum-verifies the cinematic website, decodes its WebP assets, installs ORA 360 locally and starts the same-origin service on 127.0.0.1:8767.

## One command

```sh
curl -fsSL https://raw.githubusercontent.com/akadaan310/ORA/main/install/ora-termux.sh | sh
```

## Inspect before running

```sh
curl -fsSL https://raw.githubusercontent.com/akadaan310/ORA/main/install/ora-termux.sh -o ora-termux.sh
less ora-termux.sh
sh ora-termux.sh
```

Keep Termux running, then browse http://127.0.0.1:8767 on the same device. For cached restart, re-run installer (downloaded script still needs network) or run the installed service manually as described below.

**Limitations:** This is a loopback-only single-owner prototype. The server has no independent multi-user auth. Do not expose port 8767 to the public internet or embed other account credentials. Production HTTPS, authentic per-user ORA identities, automatic OS package installs and Modal GPU rendering are separate milestones. No paid cloud rendering is used. The installer does not use GitHub Actions or Railway.

**Security:** ORA and ORASPACE source revisions are pinned by full commit hashes, the 15 website/overlay files have fixed SHA-256 fingerprints, and downloads are compared before launching.
