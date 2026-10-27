"""Resolve bundled releases or explicit executable paths without shell lookup."""
import os
from pathlib import Path
import platform

BIN = Path(__file__).resolve().parents[1] / 'bin'


def select_executables(wepp_exec=None, wepp_hill_exec=None, *, system=None, machine=None):
    system = system or platform.system()
    machine = (machine or platform.machine()).lower()
    if wepp_exec is None:
        if system in ('Windows', 'Linux') and machine in ('amd64', 'x86_64'):
            wepp_exec = 'wepp_261027'
        elif system == 'Darwin' and machine == 'arm64':
            wepp_exec = 'wepp.arm64.mac'
        else:
            raise ValueError(f'No bundled default for {system} {machine}; supply --wepp_exec PATH')

    def resolve(value):
        path = Path(value).expanduser()
        if not path.is_absolute() and '/' not in value and '\\' not in value:
            name = str(path)
            if system == 'Windows' and not name.lower().endswith('.exe'):
                name += '.exe'
            path = BIN / name
        else:
            path = path.resolve()
        if not path.is_file():
            raise ValueError(f'WEPP executable not found: {path}')
        if system != 'Windows' and not os.access(path, os.X_OK):
            raise ValueError(f'WEPP executable is not executable: {path}')
        return path

    watershed = resolve(wepp_exec)
    if watershed.name in ('wepp_261027', 'wepp_261027.exe'):
        if system not in ('Windows', 'Linux') or machine not in ('amd64', 'x86_64'):
            raise ValueError('Bundled wepp_261027 requires Windows or Linux x86_64')
        suffix = '.exe' if watershed.suffix == '.exe' else ''
        hill = str(watershed.with_name('wepp_261027_hill' + suffix))
    else:
        # Legacy/custom executables can implement both modes.
        hill = str(watershed)
    return str(watershed), str(resolve(wepp_hill_exec or hill))
