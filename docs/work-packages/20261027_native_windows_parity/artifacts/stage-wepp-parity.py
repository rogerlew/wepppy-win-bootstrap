import csv, importlib.util, json, shutil
from pathlib import Path
src=Path('/tmp/wepp-windows-261021-20261026')
spec=importlib.util.spec_from_file_location('physical',src/'tools/physical_water_case.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root=Path('/tmp/wepp-parity-inputs-20261026'); root.mkdir()
cases=[]
for layout in ['single','equal','upper60','lower60','three']:
 for mode in ['daily','hourly']:
  name=f'{layout}-{mode}'
  m.prepare(root/name,layout,mode,years=4)
  cases.append({'name':name,'cards':[{'role':'hill','file':'p1.run'},{'role':'watershed','file':'pw0.run'}]})
for row in csv.DictReader((src/'docs/ablation/hillslope_watchlist.csv').open()):
 if not row['seed_id'] or row['seed_id'].startswith('#'): continue
 name='watch-'+row['seed_id']
 run=src/row['run_file']
 shutil.copytree(run.parent,root/name/'runs')
 (root/name/'output').mkdir()
 cases.append({'name':name,'cards':[{'role':'hill','file':run.name}]})
(root/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
print(len(cases), 'cases staged')
