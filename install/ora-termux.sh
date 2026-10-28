#!/data/data/com.termux/files/usr/bin/sh
# ORA OS / ORA Space: audited, pinned, loopback-only Termux installer.
set -eu

if [ "${1:-}" = "--help" ]; then
  printf '%s\\n' 'ORA Space: curl installer for Termux' '  sh installer.sh [--install-only]' '  Starts locally at http://127.0.0.1:8767' 
  exit 0
fi
case "${1:-}" in ""|--install-only) ;; *) echo 'Invalid option' >&2; exit 2;; esac
if [ -z "${HOME:-}" ]; then echo 'HOME not set' >&2; exit 1; fi
if ! command -v python >/dev/null 2>&1; then
  if ! command -v pkg >/dev/null 2>&1; then
    echo 'This installer requires Termux (pkg) or Python 3.10+.' >&2; exit 1
  fi
  echo 'Installing Python in Termux (package download; no cloud GPU)...'
  pkg install -y python
fi
export ORA_PACKAGE_MODE="${1:-start}"
python - <<'ORA_INSTALL_PY'
from __future__ import annotations
from pathlib import Path, PurePosixPath
from hashlib import sha256
from base64 import b64decode
from zipfile import ZipFile
from contextlib import closing
from urllib.request import Request, urlopen
import io, os, shutil, subprocess, sys, json, tempfile

ORA_REV = '9995989149e8194f4cd699f902c3a6a565fda216'
SITE_REV = '15097494b9fe88e626bae934e2d75d6702717c60'
# Every shipped source and decoded WebP is verified against the original built package.
EXPECTED = {'web/app.js': 'bb2e0ab156bb44313f7456669e6068769b82731acfa7288e4100fa3455b808c9', 'web/assets/city-left.webp': 'ae7329152024b32a487b8f73c653d9247a6425d8b185890a1e1bb9333474baaa', 'web/assets/city-right.webp': 'dc145d4eb4bed1cfd02f72090d0bb7fbe53cd8dd67c09324d2ead426c5ad8ba9', 'web/assets/cosmos-texture.webp': '330c99468267e6762b5e6088ac32acc0c1af3cff9d6020ecd4a1c38f362e434d', 'web/assets/milkyway.webp': '86e75132ad94ab756da7edfb35dd6d454973309c0c2f42cf280d4fb9e2a4f637', 'web/assets/mobile-world.webp': 'a8e935b829d8f3336b16d8f5893299843bb4a8d98eff5d0534d7c17f8d025395', 'web/assets/orb-center.webp': 'eaa5d8cc3cc858e268679310e34cfd9b2e17a6796877466906d6d557d120cce3', 'web/assets/shore-world.webp': '6b49ada69b0f843c7ab5807a88b899079813a91fb6546d0d21f3c0582233469b', 'web/assets/water-source.webp': 'fa4485e892bcfa0e01d87f4e47c1d13929b785474c80395997c90bde046e47d7', 'web/gpu-water.js': '571e186197181778908e8730981fb53d1d497de049105dbd492a8c7f3beda35d', 'web/index.html': 'f88f74fa6373a357bab8c8c17b01efb7243ba23858792e55e9d8431bc277e52a', 'web/space-sky.js': 'c4888afc26224f0ff4301ea73754f79bbc6cafab9fafe674cb4d03bb098776bf', 'web/style.css': 'db3bc3f3091a7641069a20be9dd43d48a156718b6ff169eb8c2141b6b46e3e13', 'engine-overlays/service/ora360.py': '15dc812b7246824909360e239afffa0ae44215766e79e83c622f08c35d98a65c', 'engine-overlays/service/oraspace360.py': 'a0f8e5da6b5a930b95ffd46c173f8c7df442e05cef0da2aa5908b009b46d0414'}
ROOT = Path.home()/'.local'/'share'/'ora-space'
RELEASE = ROOT/'releases'/SITE_REV[:12]
ACTIVE = ROOT/'current'
DATA = ROOT/'data'
MAX_ARCHIVE_BYTES = 22_000_000

def fetch(repo, revision):
    url=f'https://codeload.github.com/akadaan310/{repo}/zip/{revision}'
    req=Request(url, headers={'User-Agent':'GLASS-ORA-Termux-Installer/0.4'})
    with closing(urlopen(req,timeout=45)) as r:
        data=r.read(MAX_ARCHIVE_BYTES+1)
    if len(data)>MAX_ARCHIVE_BYTES:
        raise ValueError('GitHub repository archive exceeds safe budget')
    return ZipFile(io.BytesIO(data))

def safe_zip_members(z):
    for member in z.infolist():
        pos=PurePosixPath(member.filename)
        if member.is_dir():continue
        if member.file_size>10_000_000 or pos.is_absolute() or '..' in pos.parts or len(pos.parts)<2:
            raise ValueError('Invalid archive entry')
        yield member, pos

def install():
    ROOT.mkdir(parents=True,exist_ok=True)
    DATA.mkdir(parents=True,exist_ok=True)
    if RELEASE.exists():
        try:
            verify(RELEASE)
            print('Already cached: verified ORA + ORA Space installation.')
            return
        except Exception:
            shutil.rmtree(RELEASE)
    temp=Path(tempfile.mkdtemp(prefix='ora-pending-',dir=ROOT))
    try:
        print('Downloading ORA engine from pinned GitHub revision...')
        with fetch('ORA',ORA_REV) as z:
            found=False
            for member,pos in safe_zip_members(z):
                tail=pos.parts[1:]
                if not tail:continue
                if tail==('service','engine.py'):found=True
                # source files only; no untrusted repo build hooks run
                dest=temp/'engine'/Path(*tail)
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(z.read(member))
            if not found:raise RuntimeError('Expected ORA engine missing')
        print('Downloading ORASPACE cinematic assets and ORA 360 module...')
        with fetch('ORASPACE',SITE_REV) as z:
            found=set()
            for member,pos in safe_zip_members(z):
                parts=pos.parts
                if len(parts)<5 or parts[1:3]!=('packages','celestial-preview'):
                    continue
                logical=PurePosixPath(*parts[3:])
                # *.b64 is an intentionally encoded binary WebP distributed through GitHub's text API.
                key=str(logical)
                raw=z.read(member)
                if key.endswith('.webp.b64'):
                    key=key[:-4]
                    raw=b64decode(raw,validate=True)
                if key not in EXPECTED:continue
                if sha256(raw).hexdigest()!=EXPECTED[key]:
                    raise RuntimeError('Integrity mismatch: '+key)
                if key.startswith('engine-overlays/'):
                    dest=temp/'engine'/key.removeprefix('engine-overlays/')
                else:
                    dest=temp/'website'/key.removeprefix('web/')
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(raw)
                found.add(key)
            missing=set(EXPECTED)-found
            if missing:raise RuntimeError('Missing asset(s): '+', '.join(sorted(missing)))
        (temp/'package.json').write_text(json.dumps({'ora_commit':ORA_REV,'oraspace_commit':SITE_REV,'expected':EXPECTED},indent=2))
        verify(temp)
        RELEASE.parent.mkdir(exist_ok=True,parents=True)
        temp.rename(RELEASE)
    finally:
        if temp.exists():shutil.rmtree(temp)

def verify(root):
    package=json.loads((root/'package.json').read_text())
    if package.get('ora_commit')!=ORA_REV or package.get('oraspace_commit')!=SITE_REV:
        raise RuntimeError('Unexpected package revision')
    for key,want in EXPECTED.items():
        if key.startswith('engine-overlays/'):
            path=root/'engine'/key.removeprefix('engine-overlays/')
        else:path=root/'website'/key.removeprefix('web/')
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=want:
            raise RuntimeError('Checksum mismatch: '+key)
    if not (root/'engine/service/app.py').is_file():raise RuntimeError('ORA host missing')
    if not (root/'website/index.html').is_file():raise RuntimeError('ORA Space site missing')

install()
if ACTIVE.is_symlink() or ACTIVE.is_file():ACTIVE.unlink()
elif ACTIVE.exists():raise RuntimeError('Active path is not a managed symlink')
ACTIVE.symlink_to(RELEASE, target_is_directory=True)
print('Verified release:',RELEASE)
print('ORA Space: http://127.0.0.1:8767')
print('ORA identity: http://127.0.0.1:8767/o/ora-sovereign/manifest')
print('Data persists in:',DATA)
if os.environ.get('ORA_PACKAGE_MODE')=='--install-only':sys.exit(0)
print('Starting ORA Sovereign + ORA 360 locally. Keep Termux running; Ctrl+C stops.')
os.chdir(ACTIVE/'engine')
os.execv(sys.executable,[sys.executable,'-m','service.oraspace360',
    '--host','127.0.0.1','--port','8767',
    '--db',str(DATA/'ora.sqlite3'),'--db360',str(DATA/'ora360.sqlite3'),
    '--web',str(ACTIVE/'website')])
ORA_INSTALL_PY
