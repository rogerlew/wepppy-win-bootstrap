program probe
implicit none
real :: lat, decl, ratio, pi, dfact, slrtm, hasun, haset, harise, rdsun
integer :: hr
lat=transfer(int(z'3F450A6C'),lat)
decl=transfer(int(z'BE421E86'),decl)
pi=3.141593
dfact=((2*pi)*(52-81))/365
slrtm=(0.1645*sin(2*dfact))-(0.1255*cos(dfact))-(0.025*sin(dfact))
call emit('dfact',dfact)
call emit('sin2dfact',sin(2*dfact))
call emit('cosdfact',cos(dfact))
call emit('sindfact',sin(dfact))
call emit('slrtm',slrtm)
do hr=9,10
hasun=((hr+slrtm)-12)*(pi/12)
haset=hasun-pi/24
harise=hasun+pi/24
call radcur(52,hr,lat,decl,ratio)
call emit('ratio',ratio)
call emit('haset',haset)
call emit('harise',harise)
call emit('sinharise',sin(harise))
call emit('sinhaset',sin(haset))
enddo
contains
subroutine emit(name,x)
character(*),intent(in)::name
real,intent(in)::x
write(*,'(a,1x,z8.8,1x,es24.16)') name,transfer(x,0),x
end subroutine
end program
