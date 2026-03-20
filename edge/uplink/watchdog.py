import structlog
import time
import requests
from edge.config.settings import config
from edge.signal.fallback import FallbackController
from edge.hardware.simulated.signal_sim import SignalSim

logger = structlog.get_logger(__name__)

import threading

class WatchdogDaemon:
    """Supervises the health of network and hardware components over time."""
    def __init__(self, sender=None, signal_controller=None, signal_backend=None):
        self.ping_interval = config.timing.watchdog_ping_interval
        self.fail_threshold = config.timing.watchdog_fail_threshold
        self.fail_count = 0
        self.fallback = FallbackController(signal_controller or signal_backend or SignalSim())
        self._fallback_active = False
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def ping_ccc(self) -> bool:
        """Ping the Control Center VPN IP."""
        try:
            res = requests.get(f"{config.uplink.ccc_url}/health", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def run(self):
        while self._running:
            if not self.ping_ccc():
                self.fail_count += 1
                logger.warning("watchdog_ping_failed", count=self.fail_count)
                if self.fail_count >= self.fail_threshold and not self._fallback_active:
                    logger.error("watchdog_threshold_met", action="activating_fallback")
                    self.fallback.activate_fallback()
                    self._fallback_active = True
            else:
                if self._fallback_active:
                    logger.info("watchdog_ccc_recovered", action="fallback_deactivated")
                self.fail_count = 0
                self._fallback_active = False

            time.sleep(self.ping_interval)

