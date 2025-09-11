import pytest

from swARM_at.RAK3172 import RAK3172

@pytest.fixture
def test_rak():
    yield RAK3172('COM5')
