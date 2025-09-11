from contextlib import contextmanager

from .serial import mock_serial
from swARM_at import RAK3172

@contextmanager
def mock(m):
    with m.context() as mc:
        mc.setattr(RAK3172, 'Serial', mock_serial)
        yield m
