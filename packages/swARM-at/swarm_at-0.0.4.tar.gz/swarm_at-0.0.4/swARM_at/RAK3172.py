from serial import Serial, SerialException
from .exceptions import InvalidBaudRateException, InvalidCOMPortException

VALID_BAUD_RATE = 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000
VALID_COM_PORT = (
    [f'COM{i}' for i in range(100)] +
    [f'/dev/tty{i}' for i in range(256)] +
    [f'/dev/ttyS{i}' for i in range(256)] +
    [f'/dev/ttyACM{i}' for i in range(256)]
)

EU433 = "0"
CN470 = "1"
RU864 = "2"
IN865 = "3"
EU868 = "4"
US915 = "5"
AU915 = "6"
KR920 = "7"
AS923_1 = "8"
AS923_1_JP = "8-1-JP"
AS923_2 = "8-2"
AS923_3 = "8-3"
AS923_4 = "8-4"

VALIDE_BAND = EU433 , CN470 , RU864 , IN865 , EU868 , US915 , AU915 , KR920 , AS923_1 , AS923_1_JP, AS923_2, AS923_3, AS923_4

class RAK3172:
    def __init__(self, port, baud_rate=9600, timeout=1):
        if port not in VALID_COM_PORT:
            raise InvalidCOMPortException('COM port invalid')
        self.port = port
        if baud_rate not in VALID_BAUD_RATE:
            raise InvalidBaudRateException('Baud rate invalid')
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None
        self.network_mode = None
        self.join_sent = False
        self.frame_sent = True

    def connect(self):
        try:
            self.serial_connection = Serial(self.port, self.baud_rate, timeout=self.timeout)
            print("Connected successfully to", self.port)
        except SerialException as e:
            print("Error connecting to", self.port, ":", e)

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from", self.port)

    def set_network_mode(self, lorawan=True):
        command = "AT+NWM=1\r\n" if lorawan else "AT+NWM=0\r\n"
        result = self.send_command(command)

        if result:
            print("Mode set to LoRaWAN" if lorawan else "Mode set to P2P")
            self.network_mode = lorawan
        else:
            print("Failed to set mode")
            self.network_mode = None
        return self.network_mode

    def send_command(self, command):
        response = self.serial_connection.read_all().decode().strip()
        asking_command = "=?"
        try:
            self.serial_connection.write(command.encode())
            if asking_command not in command :
                response = self.serial_connection.readline().decode().strip()
            elif "AT_PARAM_ERROR" in response:
                print("Parameter error with command:", command)
                return False
            return True
        except SerialException as e:
            print(f"Error with command: {command} Exception: {e}")
            return False

    def read_response(self):
        response = self.serial_connection.readline().decode().strip().replace("\r\n", "").replace("OK", "")
        #print("response is "+response)
        return response

    def set_app_key(self, app_key):
        command = f"AT+APPKEY={app_key}\r\n"
        if len(app_key) == 32 and self.is_only_hex(app_key) and self.send_command(command):
            print("AppKey set successfully")
            return True
        print("Failed to set AppKey")
        return False

    def get_app_key(self):
        command = "AT+APPKEY=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get AppKey")
        return None

    def set_app_eui(self, app_eui):
        command = f"AT+APPEUI={app_eui}\r\n"
        if len(app_eui) == 16 and self.is_only_hex(app_eui) and self.send_command(command):
            print("AppEUI set successfully")
            return True
        print("Failed to set AppEUI")
        return False

    def get_app_eui(self):
        command = "AT+APPEUI=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get AppEUI")
        return None

    def set_dev_eui(self, dev_eui):
        command = f"AT+DEVEUI={dev_eui}\r\n"
        if len(dev_eui) == 16 and self.is_only_hex(dev_eui) and self.send_command(command):
            print("DevEUI set successfully")
            return True
        print("Failed to set DevEUI")
        return False

    def get_dev_eui(self):
        command = "AT+DEVEUI=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get DevEUI")
        return None

    def get_nwks_key(self):
        command = "AT+NWKSKEY=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get NWKSKEY")
        return None

    def set_nwks_key(self, nwks_key):
        command = f"AT+NWKSKEY={nwks_key}\r\n"
        if len(nwks_key) == 32 and self.is_only_hex(nwks_key) and self.send_command(command):
            print("NWKSKEY set successfully")
            return True
        print("Failed to set NWKSKEY")
        return False

    def get_apps_key(self):
        command = "AT+APPSKEY=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get APPSKEY")
        return None

    def set_apps_key(self, apps_key):
        command = f"AT+APPSKEY={apps_key}\r\n"
        if len(apps_key) == 32 and self.is_only_hex(apps_key) and self.send_command(command):
            print("APPSKEY set successfully")
            return True
        print("Failed to set APPSKEY")
        return False

    def get_dev_addr(self):
        command = "AT+DEVADDR=?\r\n"
        if self.send_command(command):
            return self.read_response()
        print("Failed to get DEVADDR")
        return None

    def set_dev_addr(self, dev_addr):
        command = f"AT+DEVADDR={dev_addr}\r\n"
        if len(dev_addr) == 16 and self.is_only_hex(dev_addr) and self.send_command(command):
            print("DEVADDR set successfully")
            return True
        print("Failed to set DEVADDR")
        return False

    def set_join_mode(self, otaa=True):
        command = "AT+NJM=1\r\n" if otaa else "AT+NJM=0\r\n"
        if self.send_command(command):
            print("Join mode set to OTAA" if otaa else "Join mode set to ABP")
            return otaa
        print("Failed to set join mode")
        return None

    def set_confirm_mode(self, confirmed=True):
        command = "AT+CFM=1\r\n" if confirmed else "AT+CFM=0\r\n"
        if self.send_command(command):
            print("Payload mode set to confirmed" if confirmed else "Payload mode set to unconfirmed")
            return confirmed
        print("Failed to set payload mode")
        return None

    def join_network(self, join=1, auto_join=0, reattempt_interval=8, join_attempts=8):
        command = f"AT+JOIN={join}:{auto_join}:{reattempt_interval}:{join_attempts}\r\n"
        self.send_command(command)

        if join == 1 and auto_join in (0, 1) and 6 < reattempt_interval < 256 and join_attempts < 256:
            print("Join command sent successfully")
            self.join_sent = True
            return True
        print("Failed to send join command : AT_PARAM_ERROR")
        return False

    def check_join_status(self):
        command = "AT+NJS=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if response == "0" or self.join_sent is False:
            print("Not joined to network")
            return False
        print("Joined to network")
        return True

    def send_lorawan_data(self, port, payload):
        if not 0 < port <= 200:
            print("Error: Port number must be between 0 and 200")
            return False

        if len(payload) % 2 != 0 and  0 > len(payload) <= 444:
            print("Error: Payload length must be even (hexadecimal string) and 222 bytes max")
            return False

        command = f"AT+SEND={port}:{payload}\r\n"
        if self.send_command(command):
            print("Data sent successfully")
            self.frame_sent = True
            return True
        print("Failed to send data")
        return False

    def check_last_frame_status(self):
        command = "AT+CFS=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if "1" in response:
            print("Last frame was confirmed by the network")
            return True
        if "0"  in response :
            print("Last frame was not confirmed by the network")
            return False
        print("Error or unknown response: ", response)
        return None

    def receive_data(self):
        command = "AT+RECV=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if ":" in response:
            port, payload = response.split(":")
            print(f"Data received on port {port} with payload {payload}")
            return port, payload
        print("No data received or error: ", response)
        return None, None

    def check_adr_status(self):
        command = "AT+ADR=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if "1" in response :
            print("ADR is enabled")
            return True
        if "0" in response :
            print("ADR is disabled")
            return False
        print("Error or unknown response: ", response)
        return None

    def set_adr(self, enable):
        command = "AT+ADR=1\r\n" if enable else "AT+ADR=0\r\n"
        if self.send_command(command):
            print("ADR enabled" if enable else "ADR disabled")
            return True
        print("Failed to set ADR status")
        return False

    def set_lorawan_class(self, lorawan_class):
        valid_classes = ['A', 'B', 'C']
        if lorawan_class not in valid_classes:
            print(f"Invalid LoRaWAN class: {lorawan_class}. Valid options are 'A', 'B', or 'C'.")
            return False

        command = f"AT+CLASS={lorawan_class}\r\n"
        if self.send_command(command):
            print(f"LoRaWAN class set to {lorawan_class}")
            return True
        print("Failed to set LoRaWAN class")
        return False

    def get_lorawan_class(self):
        command = "AT+CLASS=?\r\n"
        self.send_command(command)

        response = self.read_response()
        class_info = response.split(",")[0]

        if "B" in class_info:
            print("Class B operational state:", response)
        else:
            print("Current LoRaWAN class:", class_info)

        return class_info

    def set_duty_cycle(self, enable):
        if enable not in [0, 1]:
            print("Invalid parameter. Use 0 to disable or 1 to enable the duty cycle.")
            return False
        command = f"AT+DCS={enable}\r\n"
        if self.send_command(command):
            print("Duty cycle set to", "enabled" if enable else "disabled")
            return True
        print("Failed to set duty cycle")
        return False

    def get_duty_cycle(self):
        command = "AT+DCS=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if "0" in response or "1" in response:
            print("Duty cycle is", "enabled" if "1" in response else "disabled")
            return response
        print("Error or unknown response:", response)
        return None

    def get_duty_cycle_time(self):
        command = "AT+DUTYTIME?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            duty_time = int(response)
            print(f"Duty cycle time: {duty_time} seconds")
            return duty_time
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_frequency_band(self, band):
        valid_bands = [EU433, CN470, RU864, IN865, EU868, US915, AU915, KR920, AS923_1, AS923_1_JP, AS923_2, AS923_3, AS923_4]
        if band not in valid_bands:
            print("Invalid band. Valid options are: EU433, CN470, RU864, etc.")
            return False

        command = f"AT+BAND={band}\r\n"
        if self.send_command(command):
            print(f"Frequency band set to {band}")
            return True
        print("Failed to set frequency band")
        return False

    def get_frequency_band(self):
        command = "AT+BAND=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            band = response.split("\r\n")[0]
            print(f"Current frequency band: {band}")
            return band
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_link_check(self, mode):
        if mode not in [0, 1, 2]:
            print("Invalid mode. Use 0 to disable, 1 for one-time check, or 2 for check after every uplink.")
            return False
        command = f"AT+LINKCHECK={mode}\r\n"
        if self.send_command(command):
            print(f"Link check mode set to {mode}")
            return True
        print("Failed to set link check mode")
        return False

    def get_link_check(self):
        command = "AT+LINKCHECK=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if response.split("\r\n")[0] in ["0", "1", "2"]:
            print(f"Current link check mode: {response}")
            return int(response.split("\r\n")[0])
        print("Error or unknown response:", response)
        return None

    def set_public_network_mode(self, mode):
        if mode not in ['0', '1']:
            print("Invalid mode. Use 0 for private network mode, 1 for public network mode.")
            return False

        command = f"AT+PNM={mode}\r\n"
        if self.send_command(command):
            print(f"Public network mode set to {'on' if mode else 'off'}")
            return True
        print("Failed to set public network mode")
        return False

    def get_public_network_mode(self):
        command = "AT+PNM=?\r\n"
        self.send_command(command)

        response = self.read_response()
        pnm = response.split("\r\n")[0]
        if pnm in ["0", "1"]:
            print(f"Current public network mode: {'on' if pnm == '1' else 'off'}")
            return pnm
        print("Error or unknown response:", response)
        return None

    def get_local_time(self):
        command = "AT+LTIME=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if response.startswith("LTIME:"):
            time_info = response.split("LTIME:")[1].strip()
            print(f"Local time in UTC format: {time_info}")
            return response.split("\r\n")[0].split(":")[1]
        print("Error or unknown response:", response)
        return None

    def get_rssi(self):
        command = "AT+RSSI=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            rssi_value = int(response.split("\r\n")[0])
            print(f"RSSI of the last received packet: {rssi_value} dBm")
            return rssi_value
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def get_snr(self):
        command = "AT+SNR=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            snr_value = int(response.split("\r\n")[0])
            print(f"SNR of the last received packet: {snr_value}")
            return snr_value
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def request_utc_time(self):
        command = "AT+TIMEREQ=1\r\n"
        if self.send_command(command):
            print("UTC time request sent. Use AT+LTIME to get the time.")
            return True
        print("Failed to send UTC time request")
        return False

    def set_p2p_frequency(self, frequency):
        # Plage de fréquence pour RAK3172(L) et RAK3172(H)
        if not 150000000 <= frequency <= 960000000:
            print("Invalid frequency. Frequency must be between 150000000 and 960000000 Hz.")
            return False

        command = f"AT+PFREQ={frequency}\r\n"
        if self.send_command(command):
            print(f"P2P frequency set to {frequency} Hz")
            return True
        print("Failed to set P2P frequency")
        return False

    def get_p2p_frequency(self):
        command = "AT+PFREQ=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            frequency = int(response.split("\r\n")[0])
            print(f"Current P2P frequency: {frequency} Hz")
            return frequency
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_p2p_spreading_factor(self, sf):
        if sf not in [6, 7, 8, 9, 10, 11, 12]:
            print("Invalid spreading factor. Must be between 6 and 12.")
            return False

        command = f"AT+PSF={sf}\r\n"
        if self.send_command(command):
            print(f"P2P spreading factor set to {sf}")
            return True
        print("Failed to set P2P spreading factor")
        return False

    def get_p2p_spreading_factor(self):
        command = "AT+PSF=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            sf = int(response.split("\r\n")[0])
            print(f"Current P2P spreading factor: {sf}")
            return sf
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_p2p_bandwidth(self, bw):
        valid_bandwidths = [125, 250, 500]
        if bw not in valid_bandwidths:
            print("Invalid bandwidth. Valid options are 125, 250, or 500 kHz.")
            return False

        command = f"AT+PBW={bw}\r\n"
        if self.send_command(command):
            print(f"P2P bandwidth set to {bw} kHz")
            return True
        print("Failed to set P2P bandwidth")
        return False

    def get_p2p_bandwidth(self):
        command = "AT+PBW=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            bw = int(response.split("\r\n")[0])
            print(f"Current P2P bandwidth: {bw} kHz")
            return bw
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_p2p_coding_rate(self, cr):
        valid_coding_rates = [0, 1, 2, 3]
        if cr not in valid_coding_rates:
            print("Invalid coding rate. Valid options are 0 (4/5), 1 (4/6), 2 (4/7), or 3 (4/8).")
            return False

        command = f"AT+PCR={cr}\r\n"
        if self.send_command(command):
            print(f"P2P coding rate set to {cr}")
            return True
        print("Failed to set P2P coding rate")
        return False

    def get_p2p_coding_rate(self):
        command = "AT+PCR=?\r\n"
        self.send_command(command)

        response = self.read_response()
        try:
            cr = int(response.split("\r\n")[0])
            print(f"Current P2P coding rate: {cr}")
            return cr
        except ValueError:
            print("Error or non-numeric response:", response)
            return None

    def set_p2p_parameters(self, freq, sf, bw, cr, preamble, power):
        if not (150000000 <= freq <= 960000000 and sf in range(5, 13) and
                bw in [125, 250, 500] and cr in [0, 1, 2, 3] and
                2 <= preamble <= 65535 and 5 <= power <= 22):
            print("Invalid P2P parameters.")
            return False

        command = f"AT+P2P={freq}:{sf}:{bw}:{cr}:{preamble}:{power}\r\n"
        if self.send_command(command):
            print(f"P2P parameters set to freq: {freq}, sf: {sf}, bw: {bw}, cr: {cr}, preamble: {preamble}, power: {power}")
            return True
        print("Failed to set P2P parameters")
        return False

    def get_p2p_parameters(self):
        command = "AT+P2P=?\r\n"
        self.send_command(command)

        response = self.read_response()
        if response:
            params = response.split(":")
            params[5] = params[5].split("\r\n")[0]
            print(
                f"Current P2P parameters: Freq: {params[0]}, SF: {params[1]}, BW: {params[2]}, "
                f"CR: {params[3]}, Preamble: {params[4]}, Power: {params[5]}"
            )
            return params
        print("Error or unknown response:", response)
        return None

    def send_p2p_data(self, payload):
        if len(payload) > 255:
            print("Payload size exceeds the maximum limit of 255 bytes.")
            return False

        command = f"AT+PSEND={payload}\r\n"
        if self.send_command(command):
            print("P2P data sent successfully")
            return True
        print("Failed to send P2P data")
        return False

    def set_p2p_receive_window(self, timeout):
        if not 0 <= timeout <= 65535:
            print("Invalid timeout. Must be between 0 and 65535 milliseconds.")
            return False

        command = f"AT+PRECV={timeout}\r\n"
        if self.send_command(command):
            mode_description = "continuous listening" if timeout == 65534 else \
                               "listen until packet received" if timeout == 65535 else \
                               "stop listening" if timeout == 0 else \
                               f"listen for {timeout} ms"
            print(f"P2P receive window set to {mode_description}")
            return True
        print("Failed to set P2P receive window")
        return False
    def is_only_hex(self, chaine):
        caracteres_hex = set('0123456789abcdefABCDEF')
        return all(caractere in caracteres_hex for caractere in chaine)
    