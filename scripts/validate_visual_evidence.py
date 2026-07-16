#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from yaml_compat import yaml
ROOT=Path(__file__).resolve().parents[1]
DEFECTS={'gold_dominance','chrome_mirror_glossy','jewelry_baroque','missing_rim_light','noisy_texture','wrong_background_profile','alternate_dark_style_drift','photoreal_product_photo_drift','unreadable_silhouette','reference_identity_loss','final_asset_not_surfaced'}
STATUSES={'pass','expected_defect_confirmed','ambiguous'}

def load(path:Path): return yaml.safe_load(path.read_text(encoding='utf-8'))
def validate(root:Path):
    errors=[]
    paths={k:root/v for k,v in {'visual':'tests/cases/visual-regression-cases.yaml','workflows':'tests/cases/workflow-cases.yaml','triggers':'tests/cases/trigger-cases.yaml','matrix':'tests/cases/rejection-matrix.yaml','review':'docs/evidence/visual-manual-review.json'}.items()}
    for path in paths.values():
        if not path.is_file(): errors.append(f'missing required visual evidence file: {path.relative_to(root)}')
    if errors: return errors,{}
    visual={x['id']:x for x in load(paths['visual']).get('anchors',[])}
    workflows={x['id'] for x in load(paths['workflows']).get('cases',[])}
    triggers={x['id'] for x in load(paths['triggers']).get('cases',[])}
    matrix=load(paths['matrix']).get('cases',[])
    missing=DEFECTS-{x.get('defect') for x in matrix}
    if missing: errors.append(f'rejection matrix missing defects: {sorted(missing)}')
    if len(matrix)!=len({x.get('id') for x in matrix}): errors.append('rejection matrix ids must be unique')
    valid_types={'visual_anchor','workflow_rule','trigger_boundary','prompt_contract','rubric_rule'}
    for item in matrix:
        cid,kind,ref=item.get('id'),item.get('evidence_type'),item.get('evidence_ref')
        if item.get('expected_outcome')!='rejected': errors.append(f'rejection {cid}: outcome must be rejected')
        if kind not in valid_types: errors.append(f'rejection {cid}: invalid evidence type')
        elif kind=='visual_anchor' and ref not in visual: errors.append(f'rejection {cid}: missing visual anchor {ref}')
        elif kind=='workflow_rule' and ref not in workflows: errors.append(f'rejection {cid}: missing workflow {ref}')
        elif kind=='trigger_boundary' and ref not in triggers: errors.append(f'rejection {cid}: missing trigger {ref}')
        elif kind in {'prompt_contract','rubric_rule'} and not (root/str(ref)).is_file(): errors.append(f'rejection {cid}: missing evidence file {ref}')
    review=json.loads(paths['review'].read_text(encoding='utf-8'))
    if review.get('review_type')!='manual_visual' or review.get('subjective_visual_quality_assessed') is not True: errors.append('manual visual assessment declaration invalid')
    if review.get('production_visual_quality_claimed') is not False: errors.append('production visual quality must not be claimed')
    records={x.get('case_id'):x for x in review.get('records',[])}
    if set(records)!=set(visual): errors.append('manual review records must match anchors exactly')
    for cid,anchor in visual.items():
        record=records.get(cid)
        if not record: continue
        if record.get('reviewed_asset_sha256')!=anchor.get('sha256'): errors.append(f'manual review {cid}: hash mismatch')
        if record.get('final_outcome')!=anchor.get('expected_outcome'): errors.append(f'manual review {cid}: outcome mismatch')
        required={'accepted':'pass','rejected':'expected_defect_confirmed','ambiguous':'ambiguous'}[anchor['expected_outcome']]
        full,target=record.get('full_size',{}),record.get('target_size',{})
        if full.get('status') not in STATUSES or target.get('status') not in STATUSES or full.get('status')!=required or target.get('status')!=required: errors.append(f'manual review {cid}: status mismatch')
        if target.get('size_px')!=64 or not full.get('notes') or not target.get('notes'): errors.append(f'manual review {cid}: full-size/64px notes required')
    return errors,{'rejection_cases':len(matrix),'manual_review_records':len(records),'required_defects':len(DEFECTS)}
def main():
    p=argparse.ArgumentParser(); p.add_argument('root',nargs='?',default=str(ROOT)); p.add_argument('--json',action='store_true'); a=p.parse_args(); errors,details=validate(Path(a.root).resolve()); payload={'status':'fail' if errors else 'pass','errors':errors,'details':details}; print(json.dumps(payload,ensure_ascii=False,sort_keys=True) if a.json else f"visual evidence: {'FAIL' if errors else 'PASS'}\n"+'\n'.join(f'- {e}' for e in errors)+'\n'+json.dumps(details,sort_keys=True)); return 2 if errors else 0
if __name__=='__main__': raise SystemExit(main())
