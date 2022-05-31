import logging, commands

REPORT_TIME = 15.0
RPI_NETWORK_INTERFACE = "wlan0"

class NetworkStatus:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        
        self.interface = config.get("interface", RPI_NETWORK_INTERFACE)

        self.printer.register_event_handler("klippy:connect",
                                            self.handle_connect)
        self.sample_timer = self.reactor.register_timer(self._get_pi_networkinfo)

    def handle_connect(self):
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def _get_pi_networkinfo(self, eventtime):
        try:
            self.hostname = commands.getoutput("hostname")
            self.ip = commands.getoutput("/sbin/ifconfig " + RPI_NETWORK_INTERFACE + " | grep -i mask | awk '{print $2}'| cut -f2 -d:")
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

