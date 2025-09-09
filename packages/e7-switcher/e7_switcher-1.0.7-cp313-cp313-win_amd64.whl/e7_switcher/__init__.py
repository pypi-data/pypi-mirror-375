"""
E7 Switcher Python Client

A Python wrapper for the E7 Switcher library that allows controlling Switcher devices.
"""


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'e7_switcher.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from .client import E7SwitcherClient
from .enums import ACMode, ACFanSpeed, ACSwing, ACPower
from .version import __version__

__all__ = [
    'E7SwitcherClient',
    'ACMode',
    'ACFanSpeed',
    'ACSwing',
    'ACPower',
    '__version__',
]
