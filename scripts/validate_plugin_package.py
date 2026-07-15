#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re, zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
VERSIONS={'skill_version':'0.1.0','pipeline_core_version':'0.2.0','style_core_version':'0.1.0','background_profiles_version':'0.1.0','prompt_schema_version':'0.1.0','qa_schema_version':'0.1.0','manifest_schema_version':'0.1.0'}

def load(path:Path): return yaml.safe_load(path.read_text(encoding='utf-8'))
def hash_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def validate(root:Path,archive:Path|None=None)->tuple[list[str],dict]:
    errors=[]; manifest_path=root/'.codex-plugin/plugin.json'; contract_path=root/'release/package-contract.yaml'; skill=root/'skills/silver-gold-image-pipeline/SKILL.md'; agent=root/'skills/silver-gold-image-pipeline/agents/openai.yaml'
    for p in (manifest_path,contract_path,skill,agent,root/'LICENSE',root/'CHANGELOG.md',root/'NOTICE.md'):
        if not p.is_file():errors.append(f'missing required packaging file: {p.relative_to(root)}')
    if errors:return errors,{}
    plugin=json.loads(manifest_path.read_text()); contract=load(contract_path); openai=load(agent)
    expected={'schema_version':'1.0.0','id':'silver-gold-image-pipeline','version':'0.1.0','display_name':'Silver-Gold Image Pipeline','license':'MIT'}
    for k,v in expected.items():
        if plugin.get(k)!=v:errors.append(f'plugin manifest {k} mismatch')
    if plugin.get('skills')!=['skills/silver-gold-image-pipeline']:errors.append('plugin manifest must declare exactly one canonical skill path')
    if not str(plugin.get('repository','')).startswith('https://github.com/sevranty/silver-gold-image-pipeline'):errors.append('plugin repository metadata mismatch')
    interface=openai.get('interface',{})
    if interface.get('display_name')!=plugin.get('display_name'):errors.append('openai display name mismatch')
    text=' '.join(str(interface.get(k,'')) for k in ('short_description','default_prompt')).casefold()
    for marker in ('visual qa','user-visible','final delivery'):
        if marker not in text:errors.append(f'openai metadata missing delivery marker: {marker}')
    if any(x in text for x in ('finuslugi','moscow exchange','moex','finkit')):errors.append('brand-specific marker in agent metadata')
    front=re.match(r'^---\n(.*?)\n---',skill.read_text(),re.S)
    if not front or yaml.safe_load(front.group(1)).get('name')!=plugin.get('id'):errors.append('SKILL front matter name mismatch')
    if contract.get('package_version')!=plugin.get('version') or contract.get('plugin_manifest_version')!=plugin.get('schema_version'):errors.append('package/plugin version mismatch')
    if contract.get('versions')!=VERSIONS:errors.append('package contract versions mismatch')
    versioning=(root/'docs/style-versioning.md').read_text() if (root/'docs/style-versioning.md').is_file() else ''
    for key,value in VERSIONS.items():
        if f'{key}: {value}' not in versioning:errors.append(f'versioning document missing {key}: {value}')
    visual=load(root/'tests/cases/visual-regression-cases.yaml') if (root/'tests/cases/visual-regression-cases.yaml').is_file() else {}
    if visual.get('style_core_version')!='0.1.0' or visual.get('qa_schema_version')!='0.1.0':errors.append('visual regression contract versions mismatch')
    required=[root/p for p in contract.get('required_runtime_files',[])]
    for p in required:
        if not p.is_file():errors.append(f'missing required runtime file: {p.relative_to(root)}')
    details={'source_required_files':len(required)}
    if archive:
        from build_plugin_package import source_files
        expected_paths=[p.relative_to(root).as_posix() for p in source_files(root)]
        with zipfile.ZipFile(archive) as z:
            names=z.namelist()
            if names!=expected_paths:errors.append('archive file list mismatch')
            if any(n.startswith(('docs/','tests/','release/','source-documents/')) or '/assets/examples/' in n or '/assets/anchors/' in n for n in names):errors.append('archive includes excluded repository/evaluation content')
            for info in z.infolist():
                if info.filename in expected_paths:
                    source=(root/info.filename).read_bytes()
                    if hash_bytes(z.read(info.filename))!=hash_bytes(source):errors.append(f'archive byte mismatch: {info.filename}')
        details['archive_files']=len(names)
    return errors,details
def main()->int:
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--archive',type=Path);p.add_argument('--json',action='store_true');a=p.parse_args();errors,details=validate(a.root.resolve(),a.archive.resolve() if a.archive else None);payload={'status':'fail' if errors else 'pass','errors':errors,'details':details};print(json.dumps(payload,sort_keys=True) if a.json else f"plugin package: {'FAIL' if errors else 'PASS'}\n"+'\n'.join(f'- {e}' for e in errors)+'\n'+json.dumps(details,sort_keys=True));return 2 if errors else 0
if __name__=='__main__':raise SystemExit(main())
