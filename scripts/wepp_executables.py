"""Select a registered release as an indivisible, checksum-verified pair."""
import hashlib
import os
from pathlib import Path
import platform

BIN = Path(__file__).resolve().parents[1] / 'bin'

# Register both validated artifacts together. User paths and independent hill
# overrides are deliberately unsupported: matching filenames are not provenance.
RELEASES = {
    ('wepp_261027', 'Windows', 'x86_64'): (
        ('wepp_261027.exe', 'ad4a14e56ff5da4670c8c40dbfbd187299d6ee54e9b0a76ddf6df3cde4ab880f'),
        ('wepp_261027_hill.exe', '50e650645b4784aca9175c55aa9b508d8b2214b597409b466b2c084dd9408f0b')),
    ('wepp_261027', 'Linux', 'x86_64'): (
        ('wepp_261027', 'ed309dd19e4b44f88b6aa9df4d2a883aa6ea5dd3baeeb8b30fc142886665f27b'),
        ('wepp_261027_hill', '6be5ce1fc8bc9cad71f1d5d849a13d90baa3b8df821416e917ad94e611750e5a')),
    # These legacy releases implement both modes in the same executable.
    ('wepp_reveg', 'Windows', 'x86_64'): (
        ('wepp_reveg.exe', '7cc9c3aa57d841810ef50d8303abb342612962fa85569c9f25209942c9580831'),) * 2,
    ('wepp.arm64.mac', 'Darwin', 'arm64'): (
        ('wepp.arm64.mac', 'ed9d1931941338f2a78e478476bbbb832773438187d6f20ced16ef34e060d483'),) * 2,
}


def select_executables(wepp_exec=None, *, system=None, machine=None):
    system = system or platform.system()
    machine = (machine or platform.machine()).lower()
    if machine == 'amd64':
        machine = 'x86_64'
    if wepp_exec is None:
        wepp_exec = 'wepp.arm64.mac' if (system, machine) == ('Darwin', 'arm64') else 'wepp_261027'
    pair = RELEASES.get((wepp_exec, system, machine))
    if pair is None:
        available = sorted(name for name, host, arch in RELEASES if (host, arch) == (system, machine))
        raise ValueError(f'Unsupported WEPP release {wepp_exec!r} for {system} {machine}. '
                         f'Available releases: {", ".join(available) or "none"}. '
                         'Select a registered release name, not an executable path.')
    paths = []
    for name, expected_hash in pair:
        path = BIN / name
        if not path.is_file():
            raise ValueError(f'Matched WEPP release is incomplete: missing {path}')
        if system != 'Windows' and not os.access(path, os.X_OK):
            raise ValueError(f'WEPP executable is not executable: {path}')
        with path.open('rb') as stream:
            digest = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != expected_hash:
            raise ValueError(f'WEPP release checksum mismatch: {path}; restore the matched release')
        paths.append(str(path))
    return tuple(paths)
