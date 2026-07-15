#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
FIXED_TIME=(2026,1,1,0,0,0)

def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def contract(root:Path)->dict: return yaml.safe_load((root/'release/package-contract.yaml').read_text())
def excluded(rel:str)->bool:
    return rel.startswith(('docs/','tests/','release/','dist/','source-documents/')) or '/assets/examples/' in rel or '/assets/anchors/' in rel or '__pycache__' in rel or rel.endswith('.pyc')
def source_files(root:Path)->list[Path]:
    files=[root/'.codex-plugin/plugin.json',root/'LICENSE',root/'CHANGELOG.md',root/'NOTICE.md']
    skill=root/'skills/silver-gold-image-pipeline'
    files.extend(p for p in skill.rglob('*') if p.is_file() and not excluded(p.relative_to(root).as_posix()))
    return sorted(set(files),key=lambda p:p.relative_to(root).as_posix())
def git_sha(root:Path)->str|None:
    try:return subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:return None
def build(root:Path,out_dir:Path)->dict:
    cfg=contract(root); version=cfg['package_version']; out_dir.mkdir(parents=True,exist_ok=True)
    archive=out_dir/f'silver-gold-image-pipeline-{version}.zip'; records=[]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in source_files(root):
            rel=path.relative_to(root).as_posix(); data=path.read_bytes(); info=zipfile.ZipInfo(rel,FIXED_TIME); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16; z.writestr(info,data); records.append({'path':rel,'sha256':sha256(data),'size_bytes':len(data)})
    archive_hash=sha256(archive.read_bytes()); manifest={'schema_version':'1.0.0','package_version':version,'source_commit':git_sha(root),'archive':archive.name,'archive_sha256':archive_hash,'files':records}
    manifest_path=out_dir/f'{archive.name}.manifest.json'; manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    checksum_path=out_dir/f'{archive.name}.sha256'; checksum_path.write_text(f'{archive_hash}  {archive.name}\n')
    return {'archive':str(archive),'manifest':str(manifest_path),'checksum':str(checksum_path),'file_count':len(records),'archive_sha256':archive_hash}
def main()->int:
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,default=ROOT); p.add_argument('--out-dir',type=Path,default=ROOT/'dist'); p.add_argument('--json',action='store_true'); a=p.parse_args(); result=build(a.root.resolve(),a.out_dir.resolve()); print(json.dumps(result,sort_keys=True) if a.json else '\n'.join(f'{k}: {v}' for k,v in result.items())); return 0
if __name__=='__main__': raise SystemExit(main())
