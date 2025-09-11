import random
import pytest

from swARM_at.RAK3172 import RAK3172, VALID_BAUD_RATE, VALID_COM_PORT, VALIDE_BAND
from swARM_at.exceptions import InvalidBaudRateException, InvalidCOMPortException

from .mocking import mock
from .mocking.serial import MockSerial


@pytest.mark.parametrize('port', VALID_COM_PORT)
def test_create_RAK3172_with_valid_port(port):
    # Given

    # When
    rak = RAK3172(port)

    # Then
    assert rak.port == port
    assert rak.baud_rate == 9600
    assert rak.timeout == 1
    assert rak.serial_connection is None

def test_create_RAK3172_with_invalid_port():
    # Given
    port = 5

    # When/Then
    with pytest.raises(InvalidCOMPortException):
        RAK3172(port)

@pytest.mark.parametrize('baud_rate', VALID_BAUD_RATE)
def test_create_RAK3172_with_valid_baudrate(baud_rate):
    # Given
    port = "COM5"

    # When
    rak = RAK3172(port, baud_rate=baud_rate)

    # Then
    assert rak.port == port
    assert rak.baud_rate == baud_rate
    assert rak.timeout == 1
    assert rak.serial_connection is None

@pytest.mark.parametrize('baud_rate', (435, 222, 11850, 147852))
def test_create_RAK3172_with_invalid_baudrate(baud_rate):
    # Given
    port = "COM5"

    # When/Then
    with pytest.raises(InvalidBaudRateException):
        RAK3172(port, baud_rate=baud_rate)

def test_connect(monkeypatch, test_rak):
    # Given

    # When
    with mock(monkeypatch):
        test_rak.connect()

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)

def test_disconnect(monkeypatch, test_rak):
    # Given

    # When
    with mock(monkeypatch):
        test_rak.connect()
        test_rak.disconnect()

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not test_rak.serial_connection.is_open

def test_send_command_at_ok(monkeypatch, test_rak):
    # Given
    string_sent = "AT"

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.send_command(string_sent)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_send_command_at_param_error(monkeypatch, test_rak):
    # Given
    string_sent = "ATuiyho"

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.send_command(string_sent)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_send_command_at_param_other(monkeypatch, test_rak):
    # Given
    string_sent = "A Ttrujilo"

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.send_command(string_sent)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_network_mode_one(monkeypatch, test_rak):
    # Given

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_network_mode(True)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_network_mode_zero(monkeypatch, test_rak):
    # Given
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_network_mode(False)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_network_mode_anything(monkeypatch, test_rak):
    # Given
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_network_mode(1)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value == 1

def test_set_app_key_right(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010230405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value


def test_set_app_key_wrong(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010230405A6B8"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_app_key_wrong_hex(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010230405*6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_app_eui_right(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_app_eui_wrong(monkeypatch, test_rak):
    # Given
    appkey = "010230406B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_app_eui_hex(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6-7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_app_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_dev_eui_right(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_dev_eui_wrong(monkeypatch, test_rak):
    # Given
    appkey = "010230406B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_dev_eui_hex(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6-7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_eui(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value


def test_set_apps_key_right(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010230405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_apps_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_apps_key_wrong(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010230405A6B7F"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_apps_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_apps_key_hex(monkeypatch, test_rak):
    # Given
    appkey = "01020AFBA1CD4D20010--405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_apps_key(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_dev_addr_right(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6B7F88"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_addr(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_dev_addr_wrong(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6B7F"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_addr(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_dev_addr_hex(monkeypatch, test_rak):
    # Given
    appkey = "010230405A6B7F--"
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_dev_addr(appkey)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_join_mode_one(monkeypatch, test_rak):
    # Given

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_join_mode(True)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_join_mode_zero(monkeypatch, test_rak):
    # Given
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_join_mode(False)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value

def test_set_confirm_mode_one(monkeypatch, test_rak):
    # Given

    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_confirm_mode(True)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value

def test_set_confirm_mode_zero(monkeypatch, test_rak):
    # Given
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.set_confirm_mode(False)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert not ret_value


def test_join_network_ok(monkeypatch, test_rak):
    # Given
    # When
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.join_network(False)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value is False

TEST_CASES_SUCCESS_AT_JOIN = [
    (join, auto_join, reattempt_interval, join_attempts)
    for join in [1]
    for auto_join in (0, 1)
    for reattempt_interval in [7, 255]
    for join_attempts in [0, 255]
]

@pytest.mark.parametrize("join, auto_join, reattempt_interval, join_attempts", TEST_CASES_SUCCESS_AT_JOIN)
def test_join_network_ok2(monkeypatch, join, auto_join, reattempt_interval, join_attempts, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.join_network(join, auto_join, reattempt_interval, join_attempts)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value is True


TEST_CASES_FAILURE_AT_JOIN = [
    (join, auto_join, reattempt_interval, join_attempts)
    for join in (2,)
    for auto_join in (2,)
    for reattempt_interval in [0,1,2,3,4,5,6,256]
    for join_attempts in [256]
]

@pytest.mark.parametrize("join, auto_join, reattempt_interval, join_attempts", TEST_CASES_FAILURE_AT_JOIN)
def test_join_network_ko(monkeypatch, join, auto_join, reattempt_interval, join_attempts, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.join_network(join, auto_join, reattempt_interval, join_attempts)

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value is False

def test_check_join_status_ok(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value is True
    assert ret_value2 is True

def test_check_join_status_ko(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value2 = test_rak.check_join_status()

    # Then
    assert isinstance(test_rak.serial_connection, MockSerial)
    assert ret_value2 is False


def genererated_hexa_string(min_taille, max_taille):
    return [''.join(random.choices('0123456789ABCDEF', k=taille)) for taille in range(min_taille, max_taille + 1, 2)]

def genererated_hexa_string_odd(min_taille, max_taille):
    # Assurez-vous que min_taille est impaire
    if min_taille % 2 == 0:
        min_taille += 1

    # Générer des chaînes hexadécimales de taille impaire
    return [''.join(random.choices('0123456789ABCDEF', k=taille)) for taille in range(min_taille, max_taille + 1, 2)]

test_cases_success_at_send_lorawan_data = [
    (port, payload)
    for port in (1, 200)
    for payload in genererated_hexa_string(2, 244)
]

@pytest.mark.parametrize("port, payload", test_cases_success_at_send_lorawan_data)
def test_send_lorawan_data(monkeypatch, port, payload, test_rak,):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data( port, payload)
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True

test_cases_failure_at_send_lorawan_data = [
    (port, payload)
    for port in range(201,220)
    for payload in genererated_hexa_string_odd(2, 244)
]

@pytest.mark.parametrize("port, payload", test_cases_failure_at_send_lorawan_data)
def test_send_lorawan_data_ko(monkeypatch, port, payload, test_rak):

    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data( port, payload)
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is False

def test_check_last_frame_status_ok(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data(2,"FF")
        ret_value4 = test_rak.check_last_frame_status()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True
    assert ret_value4 is True

def test_check_last_frame_status_ko(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value4 = test_rak.check_last_frame_status()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value4 is False


def test_receive_data_ok_data(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data(2,"FF")
        port, payload = test_rak.receive_data()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True
    assert port is not None
    assert payload is not None


def test_receive_data_ok_no_data(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        port, payload = test_rak.receive_data()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert port is None
    assert payload is None

def test_check_adr_status(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.check_adr_status()
    # Then
    assert ret_value is False


def test_check_adr_status_disabled_or_not(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_adr(False)
        ret_value2  = test_rak.check_adr_status()
        ret_value3  = test_rak.set_adr(True)
        ret_value4  = test_rak.check_adr_status()
    # Then
    assert ret_value  is True
    assert ret_value2 is False
    assert ret_value3 is True
    assert ret_value4 is False

def test_set_adr(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.set_adr(True)
        ret_value2  = test_rak.set_adr(False)
        ret_value3  = test_rak.set_adr(None)
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True

def test_set_get_lorawan_class(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.set_lorawan_class("A")
        ret_value2  = test_rak.get_lorawan_class()
        ret_value3  = test_rak.set_lorawan_class("B")
        ret_value4  = test_rak.get_lorawan_class()
        ret_value5  = test_rak.set_lorawan_class("C")
        ret_value6  = test_rak.get_lorawan_class()
    # Then
    assert ret_value is True
    assert ret_value3 is True
    assert ret_value5 is True
    assert ret_value2 == "A"
    assert ret_value4 == "B"
    assert ret_value6 == "C"

def test_set_get_duty_cycle(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_duty_cycle(0)
        ret_value2  = test_rak.get_duty_cycle()
        ret_value3  = test_rak.set_duty_cycle(1)
        ret_value4  = test_rak.get_duty_cycle()
        ret_value5  = test_rak.set_duty_cycle(2)
        ret_value6  = test_rak.get_duty_cycle()
    # Then
    assert ret_value is True
    assert ret_value3 is True
    assert ret_value5 is False
    assert ret_value2 == "0"
    assert ret_value4 == "1"
    assert ret_value6 == "1"

@pytest.mark.parametrize('band', VALIDE_BAND)
def test_set_get_frequency_band(monkeypatch, test_rak, band):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_frequency_band(band)
        ret_value2  = test_rak.get_frequency_band()
    # Then
    assert ret_value is True
    assert ret_value2 == band

@pytest.mark.parametrize('link', [0, 1, 2])
def test_set_get_linkcheck(monkeypatch, test_rak, link):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_link_check(link)
        ret_value2  = test_rak.get_link_check()
    # Then
    assert ret_value is True
    assert ret_value2 == link

@pytest.mark.parametrize('pnm', ['0', '1'])
def test_set_get_public_network_mode(monkeypatch, test_rak, pnm):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_public_network_mode(pnm)
        ret_value2  = test_rak.get_public_network_mode()
    # Then
    assert ret_value is True
    assert ret_value2 == pnm

def test_get_local_time(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value2_1 = test_rak.request_utc_time()
        ret_value3 = test_rak.send_lorawan_data( 20, "FF07")
        port, payload = test_rak.receive_data()
        ret_value4  = test_rak.get_local_time()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value2_1 is True
    assert ret_value3 is True
    assert port is not None
    assert payload is not None
    assert ret_value4 == "03h56m52s on 09/18/2021"

def test_get_rssi(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data( 20, "FF07")
        ret_value4 = test_rak.get_rssi()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True
    assert isinstance(ret_value4, int) is True

def test_get_snr(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value  = test_rak.join_network(True)
        ret_value2 = test_rak.check_join_status()
        ret_value3 = test_rak.send_lorawan_data( 20, "FF07")
        ret_value4 = test_rak.get_snr()
    # Then
    assert ret_value is True
    assert ret_value2 is True
    assert ret_value3 is True
    assert isinstance(ret_value4, int) is True

@pytest.mark.parametrize('frequency', [150000000, 960000000])
def test_set_get_p2p_frequency(monkeypatch, test_rak, frequency):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_p2p_frequency(frequency)
        ret_value2  = test_rak.get_p2p_frequency()
    # Then
    assert ret_value is True
    assert ret_value2 == frequency

@pytest.mark.parametrize('sf', [6, 7, 8, 9, 10, 11, 12])
def test_set_get_pp_sf(monkeypatch, test_rak, sf):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_p2p_spreading_factor(sf)
        ret_value2  = test_rak.get_p2p_spreading_factor()
    # Then
    assert ret_value is True
    assert ret_value2 == sf

@pytest.mark.parametrize('bw', [125, 250, 500])
def test_set_get_pp_bw(monkeypatch, test_rak, bw):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_p2p_bandwidth(bw)
        ret_value2  = test_rak.get_p2p_bandwidth()
    # Then
    assert ret_value is True
    assert ret_value2 == bw

@pytest.mark.parametrize('cr', [0, 1, 2, 3])
def test_set_get_pp_cr(monkeypatch, test_rak, cr):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.set_p2p_coding_rate(cr)
        ret_value2  = test_rak.get_p2p_coding_rate()
    # Then
    assert ret_value is True
    assert ret_value2 == cr

# Définition des paramètres de test
params = [
    (150000000, 7, 125, 0, 10, 15),  # Paramètres valides
    (960000000, 12, 500, 3, 65535, 22),  # Autre ensemble de paramètres valides
    # Ajoutez d'autres cas de test si nécessaire, incluant des paramètres invalides pour tester la gestion des erreurs
]

@pytest.mark.parametrize('freq, sf, bw, cr, preamble, power', params)
def test_set_get_p2p_param(monkeypatch, test_rak, freq, sf, bw, cr, preamble, power):
    with mock(monkeypatch):
        test_rak.connect()
        # Test de set_p2p_parameters
        ret_value = test_rak.set_p2p_parameters(freq, sf, bw, cr, preamble, power)

        # Test de get_p2p_parameters
        ret_value2 = test_rak.get_p2p_parameters()

    # Vérification des résultats
    assert ret_value is True
    assert ret_value2 is not None, "get_p2p_parameters returned None"
    assert ret_value2 == [str(freq), str(sf), str(bw), str(cr), str(preamble), str(power)], "get_p2p_parameters values mismatch"


def test_send_p2p_data(monkeypatch, test_rak):
    with mock(monkeypatch):
        test_rak.connect()
        ret_value   = test_rak.send_p2p_data("123456789100")
    # Then
    assert ret_value is True


# Test cases: (timeout, expected_return)
test_cases = [
    (0, True),  # Cas limite inférieur
    (32768, True),  # Cas valide
    (65534, True),  # Cas limite spécial
    (65535, True),  # Cas limite supérieur
    (-1, False),  # Cas d'erreur
    (65536, False)  # Cas d'erreur
]

@pytest.mark.parametrize("timeout, expected_return", test_cases)
def test_set_p2p_receive_window(monkeypatch,test_rak, timeout, expected_return):
    with mock(monkeypatch):
        test_rak.connect()
        result = test_rak.set_p2p_receive_window(timeout)

    # Vérifier le résultat de la fonction et la sortie print
    assert result == expected_return
