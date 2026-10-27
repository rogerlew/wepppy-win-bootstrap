import json,shutil,sys
from pathlib import Path
base=Path(sys.argv[1]); source=base/'261026'/'baseline-cases'
tag,lane=sys.argv[2:4]
root=base/tag/(lane+'-cases')
assert not root.exists(),root
root.mkdir(parents=True)
rows=json.loads((source/'cases.json').read_text())
if lane.startswith('observe'): rows=[r for r in rows if r['name']=='single-daily']
(root/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:
 target=root/r['name']/'runs'
 shutil.copytree(source/r['name']/'runs',target)
 for name in ['wepp_observe.log','wepp_observe.on']:
  (target/name).unlink(missing_ok=True)
 if lane.startswith('observe'):(target/'wepp_observe.on').touch()
 (root/r['name']/'output').mkdir()
