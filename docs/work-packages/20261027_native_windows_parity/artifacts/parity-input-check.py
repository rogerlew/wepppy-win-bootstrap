import json,hashlib
from pathlib import Path
base=Path('C:/tmp/native-parity-20261027')
manifest=json.loads(Path('C:/tmp/parity-inputs.json').read_text());rows=[]
for tag in ['261010','261026']:
 for lane in ['plain','checked','crop-checked','radtrig','observe-radiation']:
  root=base/tag/(lane+'-cases')
  if not root.exists():continue
  bad=[];count=0
  for row in manifest:
   if not (root/row['case']).exists():continue
   p=root/row['case']/'runs'/row['file'];count+=1
   if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:bad.append(str(p))
  rows.append(dict(tag=tag,lane=lane,checked=count,mismatches=bad))
(base/'input-verification.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
raise SystemExit(any(r['mismatches'] for r in rows))
