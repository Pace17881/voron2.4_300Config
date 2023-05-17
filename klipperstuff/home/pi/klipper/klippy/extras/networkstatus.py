import logging
import subprocess

REPORT_TIME = 15.0
RPI_NETWORK_INTERFACE = "wlan0"

class NetworkStatus:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()

        self.interface = config.get("interface", RPI_NETWORK_INTERFACE)

        self.printer.register_event_handler("klippy:connect", self.handle_connect)
        self.sample_timer = self.reactor.register_timer(self._get_pi_networkinfo)

    def handle_connect(self):
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def _get_pi_networkinfo(self, eventtime):
        try:
            self.hostname = subprocess.check_output(['hostname']).decode().strip()
            ifconfig_output = subprocess.check_output(['/sbin/ifconfig', RPI_NETWORK_INTERFACE])
            self.ip = ifconfig_output.decode().split('\n')[1].split()[1][5:]
        except subprocess.CalledProcessError as e:
            logging.exception("networkstatus: Error running command: %s", e)
        except Exception:
            logging.exception("networkstatus: Error reading data")

        measured_time = self.reactor.monotonic()
        return measured_time + REPORT_TIME

    def get_status(self, eventtime):
        return {
            'ip': self.ip,
            'hostname': self.hostname
        }


def load_config(config):
    return NetworkStatus(config)

