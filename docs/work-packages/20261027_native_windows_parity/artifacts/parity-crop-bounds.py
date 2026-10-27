from pathlib import Path
import sys
root=Path(sys.argv[1])/'src'
p=root/'ccrpet.inc'; s=p.read_text(); assert 'kcb(mxcrop),rawp(mxcrop)' in s
p.write_text(s.replace('kcb(mxcrop),rawp(mxcrop)','kcb(ntype),rawp(ntype)'))
p=root/'pmetcoef.for'; s=p.read_text(); assert "      include 'pntype.inc'" not in s
p.write_text(s.replace("      include 'pmxcrp.inc'","      include 'pmxcrp.inc'\n      include 'pntype.inc'"))
