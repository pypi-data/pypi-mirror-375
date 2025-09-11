from serial import Serial

class MockSerial:
    def __init__(self, *args, **kwargs):
        self._open = True
        self.cmd = None
        self.data_sent = False
        self.join_sent = False
        self.adr = False
        self.appkey = "01020afba1cd4d20010230405a6b7f88"
        self.appeui = "0080E11500004CF6"
        self.deveui = "1122334455667788"
        self.devaddr = "01020A0B"
        self.appskey = "01020AFBA1CD4D20010230405A6B7F88"
        self.nwkskey = "01020AFBA1CD4D20010230405A6B7F88"
        self.class_object = "A"
        self.dutycycle = "1"
        self.band = "4"
        self.cfm = 0
        self.njm = 1
        self.linkcheck = 0
        self.nwm = 0
        self.pnm = 0
        self.local_time = "LTIME:03h56m52s on 09/18/2021"
        self.rssi = -31
        self.snr = 8
        self.pfreq = 868000000
        self.psf = 7
        self.pbw = 125
        self.cr = 0
        self.preamble = 65534
        self.power = 14
    @property
    def is_open(self):
        return self._open
    
    def validate_p2p_params(self, partie_apres_egal):
        # Découper les paramètres en utilisant la virgule comme séparateur
        params = partie_apres_egal.split(':')
        
            
        # Vérifier si le nombre de paramètres est correct
        if len(params) != 6:
            return False

        # Extraire chaque paramètre
        freq, sf, bw, cr, preamble, power = params

        try:
            # Convertir les paramètres en entiers pour la validation
            freq = int(freq)
            sf = int(sf)
            bw = int(bw)
            cr = int(cr)
            preamble = int(preamble)
            power = int(power)

            # Vérifier les règles pour chaque paramètre
            if not (150000000 <= freq <= 525000000 or 525000000 < freq <= 960000000):
                print("oskour2")
                return False
            if not (5 <= sf <= 12):
                print("oskour3")
                return False
            if bw not in [125, 250, 500]:
                print("oskour4")
                return False
            if cr not in [0, 1, 2, 3]:
                print("oskour5")
                return False
            if not (2 <= preamble <= 65535):
                print("oskour6")
                return False
            if not (5 <= power <= 22):
                print("oskour7")
                return False
            self.pfreq = freq
            self.psf = sf
            self.pbw = bw
            self.cr = cr
            self.preamble = preamble
            self.power = power
        except ValueError:
            # Si la conversion en entier échoue, les paramètres ne sont pas valides
            return False
        # Tous les paramètres sont valides
        return True

    def close(self):
        self._open = False
    def write(self, cmd):
        self.cmd = cmd
    def is_only_hex(self, chaine):
        caracteres_hex = set('0123456789abcdefABCDEF')
        return all(caractere in caracteres_hex for caractere in chaine)
    def read_all(self):
        return b""
    def readline(self):
        if self.cmd == b'AT':
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+APPKEY=?'):
            return b""+self.appkey.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+APPKEY=') and len(self.cmd.decode()) == 44:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.appkey = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+APPEUI=?'):
            return b""+self.appeui.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+APPEUI=') and len(self.cmd.decode()) == 28:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.appeui = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+DEVEUI=?'):
            return b""+self.deveui.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+DEVEUI=') and len(self.cmd.decode()) == 28:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.deveui = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+APPSKEY=?'):
            return b""+self.appskey.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+NWKSKEY=?'):
            return b""+self.nwkskey.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+DEVADDR=?'):
            return b""+self.devaddr.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+APPSKEY=') and len(self.cmd.decode()) == 45:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.appskey = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+NWKSKEY=') and len(self.cmd.decode()) == 45:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.nwkskey = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+DEVADDR=') and len(self.cmd.decode()) == 29:
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal and self.is_only_hex(partie_apres_egal):
                self.devaddr = partie_apres_egal
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+NWM=?'):
            return b""+self.nwm.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+NWM='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal == "0" or partie_apres_egal == "1":
                self.nwm = int(partie_apres_egal)
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+NJS=?') and self.join_sent is True:
            return b"1"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+NJS=?') and self.join_sent is False:
            return b"0"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+CFM=?'):
            return b""+self.cfm.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+CFM='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal == "0" or partie_apres_egal == "1":
                self.cfm = int(partie_apres_egal)
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+NJM=?'):
            return b""+self.njm.encode('utf-8')+"\r\nOK"
        elif self.cmd.decode().startswith('AT+NJM='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal == "0" or partie_apres_egal == "1":
                self.njm = int(partie_apres_egal)
                return b"\r\nOK"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+JOIN='):
            self.join_sent = True
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+SEND='):
            self.data_sent = True
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+CFS=?') and self.data_sent is True:
            return b"1"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+CFS=?') and self.data_sent is False:
            return b"0"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+RECV=') and self.data_sent is True:
            return b"\r\n2:1055\r\nOK"
        elif self.cmd.decode().startswith('AT+RECV=') and self.data_sent is False:
            return b"\r\n0"
        elif self.cmd.decode().startswith('AT+ADR=?') and self.adr is True:
            return b"1"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+ADR=?') and self.adr is False:
            return b"0"+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+ADR=1'):
            self.adr is True
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+ADR=0'):
            self.adr is False
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+CLASS=?'):
            return b""+self.class_object.encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+CLASS=A'):
            self.class_object = "A"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+CLASS=B'):
            self.class_object = "B"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+CLASS=C'):
            self.class_object = "C"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+DCS=?'):
            return b""+self.dutycycle.encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+DCS=1'):
            self.dutycycle = "1"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+DCS=0'):
            self.dutycycle = "0"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=?'):
            return b""+self.band.encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+BAND=0'):
            self.band = "0"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=1'):
            self.band = "1"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=2'):
            self.band = "2"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=3'):
            self.band = "3"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=4'):
            self.band = "4"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=5'):
            self.band = "5"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=6'):
            self.band = "6"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=7'):
            self.band = "7"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=8\r\n'):
            self.band = "8"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=8-1-JP'):
            self.band = "8-1-JP"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=8-2'):
            self.band = "8-2"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=8-3'):
            self.band = "8-3"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+BAND=8-4'):
            self.band = "8-4"
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+LINKCHECK=?\r\n'):
            return b""+str(self.linkcheck).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+LINKCHECK=0'):
            self.linkcheck = 0
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+LINKCHECK=1'):
            self.linkcheck = 1
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+LINKCHECK=2'):
            self.linkcheck = 2
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+PNM=?\r\n'):
            return b""+str(self.pnm).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PNM=0'):
            self.pnm = 0
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+PNM=1'):
            self.pnm = 1
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+LTIME=?'):
            return b""+str(self.local_time).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+TIMEREQ=1'):
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+RSSI=?'):
            return b""+str(self.rssi).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+SNR=?'):
            return b""+str(self.snr).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PFREQ=?'):
            return b""+str(self.pfreq).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PFREQ='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal:
                valeur = int(partie_apres_egal)
                if 150000000 <= valeur <= 960000000:
                    self.pfreq = valeur
                    return b"\r\nOK"
                else:
                    return b"\r\nAT_PARAM_ERROR"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+PSF=?'):
            return b""+str(self.psf).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PSF='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal:
                valeur = int(partie_apres_egal)
                if 6 <= valeur <= 12:
                    self.psf = valeur
                    return b"\r\nOK"
                else:
                    return b"\r\nAT_PARAM_ERROR"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+PBW=?'):
            return b""+str(self.pbw).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PBW='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal:
                valeur = int(partie_apres_egal)
                if 125 == valeur or valeur == 250 or valeur == 500:
                    self.pbw = valeur
                    return b"\r\nOK"
                else:
                    return b"\r\nAT_PARAM_ERROR"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+PCR=?'):
            return b""+str(self.cr).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+PCR='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if partie_apres_egal:
                valeur = int(partie_apres_egal)
                if 0 <= valeur <= 3:
                    self.cr = valeur
                    return b"\r\nOK"
                else:
                    return b"\r\nAT_PARAM_ERROR"
            else:
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+P2P=?'):
            return b""+(str(self.pfreq)+":"+str(self.psf)+":"+str(self.pbw)+":"+str(self.cr)+":"+str(self.preamble)+":"+str(self.power)).encode('utf-8')+"\r\nOK".encode('utf-8')
        elif self.cmd.decode().startswith('AT+P2P='):
            partie_apres_egal = self.cmd.decode().split('=')[1] if '=' in self.cmd.decode() else None
            if self.validate_p2p_params(partie_apres_egal):
                return b"\r\nOK"
            else:
                print("oskour")
                return b"\r\nAT_PARAM_ERROR"
        elif self.cmd.decode().startswith('AT+PSEND='):
            return b"\r\nOK"
        elif self.cmd.decode().startswith('AT+PRECV='):
            return b"123456\r\nOK"
        else:
            return b"\r\nAT_PARAM_ERROR"


def mock_serial(*args, **kwargs):
    return MockSerial(*args, **kwargs)
