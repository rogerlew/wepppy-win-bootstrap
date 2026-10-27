#!/usr/bin/env bash
set -eu
platform=$1
tag=$2
lane=$3
if [ "$platform" = windows ]; then
 export PATH=/c/tmp/winlibs-gcc133/mingw64/bin:/usr/bin:$PATH
 base=/c/tmp/native-parity-20261027
 fc=/c/tmp/winlibs-gcc133/mingw64/bin/gfortran
 ld='-mcmodel=medium -static'
 suffix=.exe
else
 base=/tmp/native-parity-20261027
 fc=/usr/bin/gfortran
 ld='-mcmodel=medium -no-pie'
 suffix=
fi
root=$base/$tag/$lane
mkdir -p "$root"
tar -xf "$base/$tag/source.tar" -C "$root"
if [[ "$lane" = observe* ]]; then
 if [ "$platform" = windows ]; then
  /c/Users/roger/miniconda3/python.exe C:/tmp/parity-observe.py "$(cygpath -w "$root")"
 else
  python /tmp/parity-observe.py "$root"
 fi
fi
if [[ "$lane" = crop* ]]; then
 if [ "$platform" = windows ]; then
  /c/Users/roger/miniconda3/python.exe C:/tmp/parity-crop-bounds.py "$(cygpath -w "$root")"
 else
  python /tmp/parity-crop-bounds.py "$root"
 fi
fi
if [ "$lane" = radtrig ]; then
 if [ "$platform" = windows ]; then
  /c/Users/roger/miniconda3/python.exe C:/tmp/parity-radtrig.py "$(cygpath -w "$root")"
 else
  python /tmp/parity-radtrig.py "$root"
 fi
fi
cd "$root/src"
flags='-c -fno-align-commons -mcmodel=medium -g -fbacktrace -O2 -ffpe-trap=invalid,zero,overflow -finit-local-zero -std=legacy'
if [[ "$lane" = diagnostic || "$lane" = crop-checked ]]; then flags="$flags -fcheck=all -Wall -Wextra -Wimplicit-interface"; fi
target=wepp_hill
if [ "$lane" = watershed ]; then target=wepp; fi
make -j4 FC="$fc" LINKER="$fc" FFLAGS="$flags -ffixed-form -ffixed-line-length-72" FFLAGS_F90="$flags" LDFLAGS="$ld" "$target" > "$root/build.log" 2>&1
artifact=wepp_${tag}_hill
if [ "$lane" = watershed ]; then artifact=wepp_${tag}; fi
cp "$target$suffix" "$root/$artifact$suffix"
"$fc" --version | head -1
sha256sum "$root/$artifact$suffix"
