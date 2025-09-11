import pytest
from unittest.mock import patch, MagicMock

from swARM_at.RAK4270 import RAK4270, VALID_BAUD_RATE, VALID_COM_PORT, VALID_BAND
from swARM_at.exceptions import InvalidBaudRateException, InvalidCOMPortException


@pytest.mark.parametrize('port', VALID_COM_PORT[:5])  # Limit to first 5 for faster testing
def test_create_RAK4270_with_valid_port(port):
    # Given/When
    rak = RAK4270(port)

    # Then
    assert rak.port == port
    assert rak.baud_rate == 9600
    assert rak.timeout == 1
    assert rak.serial_connection is None

def test_create_RAK4270_with_invalid_port():
    # Given
    port = 5

    # When/Then
    with pytest.raises(InvalidCOMPortException):
        RAK4270(port)

@pytest.mark.parametrize('baud_rate', VALID_BAUD_RATE[:3])  # Limit for faster testing
def test_create_RAK4270_with_valid_baud_rate(baud_rate):
    # Given
    port = VALID_COM_PORT[0]

    # When
    rak = RAK4270(port, baud_rate)

    # Then
    assert rak.baud_rate == baud_rate

def test_create_RAK4270_with_invalid_baud_rate():
    # Given
    port = VALID_COM_PORT[0]
    baud_rate = 5

    # When/Then
    with pytest.raises(InvalidBaudRateException):
        RAK4270(port, baud_rate)

def test_create_RAK4270_with_valid_timeout():
    # Given
    port = VALID_COM_PORT[0]
    timeout = 5

    # When
    rak = RAK4270(port, timeout=timeout)

    # Then
    assert rak.timeout == timeout

@patch('swARM_at.RAK4270.Serial')
def test_connect(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_serial.return_value = mock_instance

    # When
    rak.connect()

    # Then
    assert rak.serial_connection is not None

@patch('swARM_at.RAK4270.Serial')
def test_disconnect(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    rak.disconnect()

    # Then
    mock_instance.close.assert_called_once()

@patch('swARM_at.RAK4270.Serial')
def test_send_command(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    command = "at+version"
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    response = rak.send_command(command)

    # Then
    assert response == "OK"

def test_send_command_without_connection():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    command = "at+version"

    # When
    response = rak.send_command(command)

    # Then
    assert response == False

@patch('swARM_at.RAK4270.Serial')
def test_get_version(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"RAK4270 Version:1.0.3 OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    version = rak.get_version()

    # Then
    assert version is not None

@patch('swARM_at.RAK4270.Serial')
def test_restart_device(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.restart_device()

    # Then
    assert isinstance(result, bool)

@patch('swARM_at.RAK4270.Serial')
def test_set_network_mode_lorawan(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_network_mode(lorawan=True)

    # Then
    assert rak.network_mode == "LoRaWAN"

@patch('swARM_at.RAK4270.Serial')
def test_set_network_mode_p2p(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_network_mode(lorawan=False)

    # Then
    assert rak.network_mode == "P2P"

@patch('swARM_at.RAK4270.Serial')
def test_set_dev_eui_valid(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    dev_eui = "1133557799224466"

    # When
    result = rak.set_dev_eui(dev_eui)

    # Then
    assert isinstance(result, bool)

def test_set_dev_eui_invalid_format():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    dev_eui = "invalid_eui"

    # When
    result = rak.set_dev_eui(dev_eui)

    # Then
    assert result == False

def test_set_dev_eui_invalid_length():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    dev_eui = "1133557799"  # Too short

    # When
    result = rak.set_dev_eui(dev_eui)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_set_app_eui_valid(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    app_eui = "1000000000000009"

    # When
    result = rak.set_app_eui(app_eui)

    # Then
    assert isinstance(result, bool)

def test_set_app_eui_invalid():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    app_eui = "invalid"

    # When
    result = rak.set_app_eui(app_eui)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_set_join_mode_otaa(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_join_mode(otaa=True)

    # Then
    assert isinstance(result, bool)

@patch('swARM_at.RAK4270.Serial')
def test_set_join_mode_abp(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_join_mode(otaa=False)

    # Then
    assert isinstance(result, bool)

@pytest.mark.parametrize('lora_class', ['A', 'B', 'C'])
@patch('swARM_at.RAK4270.Serial')
def test_set_lora_class_valid(mock_serial, lora_class):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_lora_class(lora_class)

    # Then
    assert isinstance(result, bool)

def test_set_lora_class_invalid():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    lora_class = "D"

    # When
    result = rak.set_lora_class(lora_class)

    # Then
    assert result == False

@pytest.mark.parametrize('region', VALID_BAND[:3])  # Limit for faster testing
@patch('swARM_at.RAK4270.Serial')
def test_set_region_valid(mock_serial, region):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_region(region)

    # Then
    assert isinstance(result, bool)

def test_set_region_invalid():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    region = "INVALID"

    # When
    result = rak.set_region(region)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_join_network(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.join_network()

    # Then
    assert isinstance(result, bool)
    assert rak.join_sent == True

@patch('swARM_at.RAK4270.Serial')
def test_send_lorawan_data_valid(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    lora_port = 2
    payload = "1234567890"

    # When
    result = rak.send_lorawan_data(lora_port, payload)

    # Then
    assert isinstance(result, bool)
    assert rak.frame_sent == True

def test_send_lorawan_data_invalid_port():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    lora_port = 0  # Invalid port
    payload = "1234567890"

    # When
    result = rak.send_lorawan_data(lora_port, payload)

    # Then
    assert result == False

def test_send_lorawan_data_invalid_payload():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    lora_port = 2
    payload = "invalid_hex"

    # When
    result = rak.send_lorawan_data(lora_port, payload)

    # Then
    assert result == False

def test_is_only_hex_valid():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    hex_string = "1234ABCD"

    # When
    result = rak.is_only_hex(hex_string)

    # Then
    assert result == True

def test_is_only_hex_invalid():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    hex_string = "invalid_hex"

    # When
    result = rak.is_only_hex(hex_string)

    # Then
    assert result == False

# Additional tests for error handling and missing coverage

@patch('swARM_at.RAK4270.Serial')
def test_connect_serial_exception(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    from serial import SerialException
    mock_serial.side_effect = SerialException("Port not found")

    # When
    rak.connect()

    # Then
    assert rak.serial_connection is None

@patch('swARM_at.RAK4270.Serial')
def test_send_command_exception(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    command = "at+version"
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.write.side_effect = OSError("Serial error")
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    response = rak.send_command(command)

    # Then
    assert response is None

@patch('swARM_at.RAK4270.Serial')
def test_read_response_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Response data\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    response = rak.read_response()

    # Then
    assert response == "Response data"

def test_read_response_no_connection():
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)

    # When
    response = rak.read_response()

    # Then
    assert response is None

@patch('swARM_at.RAK4270.Serial')
def test_read_response_exception(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.side_effect = OSError("Read error")
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    response = rak.read_response()

    # Then
    assert response is None

@patch('swARM_at.RAK4270.Serial')
def test_get_version_no_ok_response(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    version = rak.get_version()

    # Then
    assert version is None

@patch('swARM_at.RAK4270.Serial')
def test_set_network_mode_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_network_mode(lorawan=True)

    # Then
    assert result == False
    assert rak.network_mode == "LoRaWAN"

@patch('swARM_at.RAK4270.Serial')
def test_get_lora_status(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Status OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    status = rak.get_lora_status()

    # Then
    assert status == "Status OK"

@patch('swARM_at.RAK4270.Serial')
def test_set_dev_eui_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    dev_eui = "1133557799224466"

    # When
    result = rak.set_dev_eui(dev_eui)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_dev_eui_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:dev_eui:1133557799224466\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    dev_eui = rak.get_dev_eui()

    # Then
    assert "1133557799224466" in dev_eui and "OK" in dev_eui

@patch('swARM_at.RAK4270.Serial')
def test_get_dev_eui_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    dev_eui = rak.get_dev_eui()

    # Then
    assert dev_eui is None

@patch('swARM_at.RAK4270.Serial')
def test_set_app_eui_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    app_eui = "1000000000000009"

    # When
    result = rak.set_app_eui(app_eui)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_app_eui_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:app_eui:1000000000000009\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    app_eui = rak.get_app_eui()

    # Then
    assert "1000000000000009" in app_eui and "OK" in app_eui

@patch('swARM_at.RAK4270.Serial')
def test_get_app_eui_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    app_eui = rak.get_app_eui()

    # Then
    assert app_eui is None

@patch('swARM_at.RAK4270.Serial')
def test_set_app_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    app_key = "04FA4E626EF5CF227C969601176275C2"

    # When
    result = rak.set_app_key(app_key)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_app_key_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:app_key:04FA4E626EF5CF227C969601176275C2\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    app_key = rak.get_app_key()

    # Then
    assert "04FA4E626EF5CF227C969601176275C2" in app_key and "OK" in app_key

@patch('swARM_at.RAK4270.Serial')
def test_get_app_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    app_key = rak.get_app_key()

    # Then
    assert app_key is None

@patch('swARM_at.RAK4270.Serial')
def test_set_dev_addr_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    dev_addr = "260BDE80"

    # When
    result = rak.set_dev_addr(dev_addr)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_dev_addr_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:dev_addr:260BDE80\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    dev_addr = rak.get_dev_addr()

    # Then
    assert "260BDE80" in dev_addr and "OK" in dev_addr

@patch('swARM_at.RAK4270.Serial')
def test_get_dev_addr_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    dev_addr = rak.get_dev_addr()

    # Then
    assert dev_addr is None

@patch('swARM_at.RAK4270.Serial')
def test_set_nwks_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    nwks_key = "433C7A924F7F6947778FE821525F183A"

    # When
    result = rak.set_nwks_key(nwks_key)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_nwks_key_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:nwks_key:433C7A924F7F6947778FE821525F183A\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    nwks_key = rak.get_nwks_key()

    # Then
    assert "433C7A924F7F6947778FE821525F183A" in nwks_key and "OK" in nwks_key

@patch('swARM_at.RAK4270.Serial')
def test_get_nwks_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    nwks_key = rak.get_nwks_key()

    # Then
    assert nwks_key is None

@patch('swARM_at.RAK4270.Serial')
def test_set_apps_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    apps_key = "A585653A949C2B2D44B55E99E94CB533"

    # When
    result = rak.set_apps_key(apps_key)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_apps_key_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:apps_key:A585653A949C2B2D44B55E99E94CB533\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    apps_key = rak.get_apps_key()

    # Then
    assert "A585653A949C2B2D44B55E99E94CB533" in apps_key and "OK" in apps_key

@patch('swARM_at.RAK4270.Serial')
def test_get_apps_key_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    apps_key = rak.get_apps_key()

    # Then
    assert apps_key is None

@patch('swARM_at.RAK4270.Serial')
def test_set_join_mode_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_join_mode(otaa=True)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_join_mode_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:join_mode:0\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    join_mode = rak.get_join_mode()

    # Then
    assert "0" in join_mode and "OK" in join_mode

@patch('swARM_at.RAK4270.Serial')
def test_get_join_mode_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    join_mode = rak.get_join_mode()

    # Then
    assert join_mode is None

@patch('swARM_at.RAK4270.Serial')
def test_set_lora_class_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_lora_class("A")

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_lora_class_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:class:0\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    lora_class = rak.get_lora_class()

    # Then
    assert "0" in lora_class and "OK" in lora_class

@patch('swARM_at.RAK4270.Serial')
def test_get_lora_class_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    lora_class = rak.get_lora_class()

    # Then
    assert lora_class is None

@patch('swARM_at.RAK4270.Serial')
def test_set_region_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_region("EU868")

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_region_success(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"lora:region:EU868\r\nOK"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    region = rak.get_region()

    # Then
    assert "EU868" in region and "OK" in region

@patch('swARM_at.RAK4270.Serial')
def test_get_region_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    region = rak.get_region()

    # Then
    assert region is None

@patch('swARM_at.RAK4270.Serial')
def test_join_network_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.join_network()

    # Then
    assert result == False
    assert rak.join_sent == True  # Flag is set regardless of result

@patch('swARM_at.RAK4270.Serial')
def test_check_join_status_joined(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Status joined OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.check_join_status()

    # Then
    assert result == True

@patch('swARM_at.RAK4270.Serial')
def test_check_join_status_not_joined(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Status not connected\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.check_join_status()

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_send_lorawan_data_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    lora_port = 2
    payload = "1234567890"

    # When
    result = rak.send_lorawan_data(lora_port, payload)

    # Then
    assert result == False
    assert rak.frame_sent == True  # Flag is set regardless of result

@patch('swARM_at.RAK4270.Serial')
def test_set_p2p_config_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.set_p2p_config(869525000, 7, 0, 1, 5, 5)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_send_p2p_data_failure(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"ERROR\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()
    payload = "FF112233"

    # When
    result = rak.send_p2p_data(payload)

    # Then
    assert result == False

@patch('swARM_at.RAK4270.Serial')
def test_get_device_status(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Device status OK\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.get_device_status()

    # Then
    assert result == "Device status OK"

@patch('swARM_at.RAK4270.Serial')
def test_get_help(mock_serial):
    # Given
    port = VALID_COM_PORT[0]
    rak = RAK4270(port)
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.readline.return_value = b"Help information\r\n"
    mock_serial.return_value = mock_instance
    rak.connect()

    # When
    result = rak.get_help()

    # Then
    assert result == "Help information"