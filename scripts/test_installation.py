#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,tempfile,zipfile
from pathlib import Path
import yaml
from build_plugin_package import build
from validate_plugin_package import validate
ROOT=Path(__file__).resolve().parents[1]
def smoke(root:Path)->tuple[list[str],dict]:
    errors=[]
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp); result=build(root,tmp); archive=Path(result['archive']); package_errors,_=validate(root,archive); errors.extend(package_errors)
        install=tmp/'installed'; install.mkdir()
        with zipfile.ZipFile(archive) as z:z.extractall(install)
        plugin=json.loads((install/'.codex-plugin/plugin.json').read_text()); skill=install/plugin['skills'][0]/'SKILL.md'; agent=install/plugin['skills'][0]/'agents/openai.yaml'
        if not skill.is_file() or not agent.is_file():errors.append('installed skill or agent metadata missing')
        else:
            match=re.match(r'^---\n(.*?)\n---',skill.read_text(),re.S); front=yaml.safe_load(match.group(1)) if match else {}
            if front.get('name')!=plugin.get('id'):errors.append('installed skill id mismatch')
            for rel in re.findall(r'`(references/[^`]+)`',skill.read_text()):
                if not (skill.parent/rel).is_file():errors.append(f'installed reference missing: {rel}')
        return errors,{'archive_sha256':result['archive_sha256'],'installed_files':result['file_count']}
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--json',action='store_true');a=p.parse_args();errors,details=smoke(a.root.resolve());payload={'status':'fail' if errors else 'pass','errors':errors,'details':details};print(json.dumps(payload,sort_keys=True) if a.json else f"installation smoke: {'FAIL' if errors else 'PASS'}\n"+'\n'.join(f'- {e}' for e in errors)+'\n'+json.dumps(details,sort_keys=True));return 2 if errors else 0
if __name__=='__main__':raise SystemExit(main())
