"""Create reproducible starter/docs zips, excluding local secrets and runtime data."""
import hashlib
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent
SUFFIX='2026-11-17'
EXCLUDED={'.venv','.git','__pycache__','.pytest_cache','.ruff_cache','.dart_tool',
          'local_data','build','coverage','.idea','.vscode'}


def eligible(path:Path)->bool:
    rel=path.relative_to(ROOT)
    return path.is_file() and not any(p in EXCLUDED or p.endswith('.egg-info') for p in rel.parts) \
        and not rel.name.startswith('.env') and rel.name!='SHA256SUMS.txt' and not rel.name.endswith('.db')


def checksum(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def create_zip(dest:Path, docs_only=False):
    all_files=sorted((x for x in ROOT.rglob('*') if eligible(x)),key=lambda p:p.as_posix())
    def included(p:Path):
        if not docs_only:
            return True
        r=p.relative_to(ROOT)
        return r.parts[0]=='docs' or r.as_posix() in {
            'README.md','AGENTS.md','CONTENT_LICENSE.md','LICENSE','CHANGELOG.md',
            'CONTRIBUTING.md','scripts/agent_bootstrap_prompt.txt',
        }
    files=[p for p in all_files if included(p)]
    manifest=''.join(f'{checksum(p.read_bytes())}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
    prefix='audioverse-starter' if not docs_only else 'AudioVerse_Documentation'
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for file in files:
            z.write(file,arcname=f'{prefix}/{file.relative_to(ROOT).as_posix()}')
        z.writestr(f'{prefix}/SHA256SUMS.txt',manifest)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(files)+1
    return len(files),dest.stat().st_size


if __name__=='__main__':
    for dest,docs in [(OUT/f'AudioVerse_Starter_{SUFFIX}.zip',False),
                      (OUT/f'AudioVerse_Documentation_{SUFFIX}.zip',True)]:
        count,size=create_zip(dest,docs)
        print(dest, 'files',count,'bytes',size)
