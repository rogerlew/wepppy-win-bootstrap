import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/wepp-windows-261021-20261026/tools')
from compare_wepp_raw_outputs import compare_raw_outputs
base=Path('/tmp/native-parity-20261027')
rows=[]
for tag in ['261010','261026']:
 for lane,path in [('windows-base',base/'windows/results'/tag/'plain-cases'),('linux-rebuild',base/tag/'baseline-cases'),('linux-observe',base/tag/'observe-cases'),('windows-observe',base/'windows/results'/tag/'observe-cases'),('linux-radtrig',base/tag/'radtrig-cases'),('windows-radtrig',base/'windows/results'/tag/'radtrig-cases')]:
  if not (path/'execution.json').exists():continue
  cases=json.loads((path/'execution.json').read_text())
  for case in cases:
   if not case['passed']:continue
   name=case['case']
   for domain,globs,tol in [('all',['H1.*'] if name=='single-daily' else ['*'],.01),('water',['*.wat.dat'],.01),('erosion',['*.ebe.dat','*.loss.dat'],.10)]:
    result=compare_raw_outputs(baseline_root=base/tag/'reference-cases'/name,candidate_root=path/name,output_subdir='output',exclude_globs=[],abs_tol=1e-9,top_n=3,include_globs=globs,rel_tol=tol)
    rows.append(dict(tag=tag,lane=lane,case=name,domain=domain,result=result))
    print(tag,lane,name,domain,result['strict_pass'])
Path('docs/work-packages/20261027_native_windows_parity/artifacts/comparisons.json').write_text(json.dumps(rows,indent=2)+'\n')
