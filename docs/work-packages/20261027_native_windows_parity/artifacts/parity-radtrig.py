from pathlib import Path
import re,sys
p=Path(sys.argv[1])/'src'/'radcur.for';s=p.read_text()
s=re.sub(r'\bsin\(', 'parsin(', s);s=re.sub(r'\bcos\(', 'parcos(', s)
s=s.replace('      real     ratio,rdlat,decl','      real     ratio,rdlat,decl\n      real parsin,parcos\n      external parsin,parcos')
s+='''
      real function parsin(x)
      real x
      parsin = real(dsin(dble(x)))
      end
      real function parcos(x)
      real x
      parcos = real(dcos(dble(x)))
      end
'''
p.write_text(s)
