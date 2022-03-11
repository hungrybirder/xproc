# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from xproc import pidstatus


def test_pidstatus():
    pid1 = pidstatus.PIDStatus(1)
    assert pid1
    assert pid1.get(pidstatus.PS_PPID) == 0
