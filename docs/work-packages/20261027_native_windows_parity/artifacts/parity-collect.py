import zipfile,sys
from pathlib import Path
base=Path('C:/tmp/native-parity-20261027')
with zipfile.ZipFile(base/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
 for tag in ['261010','261026']:
  for lane in sys.argv[1:]:
   root=base/tag/(lane+'-cases')
   if not root.exists():continue
   for p in root.rglob('*'):
    if p.is_file() and ('runs' not in p.relative_to(root).parts or p.name=='wepp_observe.log'):
     z.write(p,p.relative_to(base))
