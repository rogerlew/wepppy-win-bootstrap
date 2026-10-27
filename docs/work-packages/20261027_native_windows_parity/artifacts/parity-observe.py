from pathlib import Path
import sys
root=Path(sys.argv[1])/'src'
p=root/'winter.for'; s=p.read_text()
s=s.replace('         hrmlt(hour,iplane)  = wmelt(iplane)', '''         call wepp_observe('PAR_RAW',year,sdate,iplane,hour,0,
     1     wmelt(iplane),hrtemp)
         call wepp_observe('PAR_RAD',year,sdate,iplane,hour,0,
     1     hradmj,snodpt(iplane))
         hrmlt(hour,iplane)  = wmelt(iplane)''')
s=s.replace('           totmel = totmel + hrmlt(hour,iplane)', '''           call wepp_observe('PAR_FIN',year,sdate,iplane,hour,0,
     1       hrmlt(hour,iplane),hrrain(hour))
           totmel = totmel + hrmlt(hour,iplane)''')
s=s.replace('       call radcur(sdate,hour,radlat,dsunmp,cratio)', """       call wepp_observe('PAR_SUN',year,sdate,iplane,hour,0,
     1   radlat,dsunmp)
       call radcur(sdate,hour,radlat,dsunmp,cratio)
       call wepp_observe('PAR_RAT',year,sdate,iplane,hour,0,
     1   cratio,rpoth)
       call wepp_observe('PAR_EST',year,sdate,iplane,hour,0,
     1   estrad,halfdy)""")
p.write_text(s)
p=root/'wepp_observe.for' ; s=p.read_text(); old='      write (lun,1000) tag, year, sdate, ielmt, ichan, iseg, v1, v2'
assert old in s
s=s.replace('      lun = 99',"      if (tag(1:3).ne.'PAR') return\n      if (sdate.lt.50.or.sdate.gt.53) return\n      lun = 99")
s=s.replace(old,'''      if (tag(1:3).eq.'PAR') then
        write(lun,1001) tag,year,sdate,ielmt,ichan,iseg,
     1    transfer(v1,0),transfer(v2,0),v1,v2
      else
'''+old+'''
      endif''')
s=s.replace('      end\n', ''' 1001 format(a,5(1x,i8),2(1x,z8.8),2(1x,es24.16))
      end
''')
p.write_text(s)
