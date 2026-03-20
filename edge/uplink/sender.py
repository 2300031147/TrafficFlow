import structlog
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
import requests

from edge.config.settings import config
from edge.aggregator.buffer import SQLiteBuffer

logger = structlog.get_logger(__name__)

# H6: Thread pool for non-blocking network I/O — prevents blocking the main decision loop
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sender")


class CCSender:
    """Handles POST requests strictly and securely to CCC Server from Edge."""
    def __init__(self):
        self.url = f"{config.uplink.ccc_url}/api/v1/ingest"
        self.token = config.uplink.api_token
        self.junction_id = config.junction.junction_id
        self.buffer = SQLiteBuffer()
        self.seq_num = 0
        self.last_send_duration = 0.0

    def _do_send_task(self, payload: Dict[str, Any], seq_num: int):
        wrapped = {
            "junction_id": self.junction_id,
            "sequence_number": seq_num,
            "data": payload
        }
        headers = {
            "X-Device-Token": self.token,
            "Content-Type": "application/json"
        }
        start_time = time.time()
        try:
            resp = requests.post(self.url, json=wrapped, headers=headers, timeout=5)
            duration = time.time() - start_time
            if duration > 3.0:
                logger.warning("slow_network", duration=duration)
            resp.raise_for_status()
            
            try:
                update_avail = resp.json().get("model_update_available", False)
            except ValueError:
                update_avail = False
            
            logger.info("sent_successfully", seq_num=seq_num, update_available=update_avail, duration=duration)
            self.flush_buffer()
        except requests.exceptions.RequestException as e:
            logger.warning("send_failed", error=str(e), seq_num=seq_num)
            self.buffer.push(payload)
        except Exception as e:
            logger.error("unexpected_send_error", error=str(e), seq_num=seq_num)
            self.buffer.push(payload)

    def send(self, payload: Dict[str, Any]) -> bool:
        self.seq_num += 1
        _executor.submit(self._do_send_task, payload, self.seq_num)
        return True

    def flush_buffer(self):
        pairs = self.buffer.peek_batch(limit=10)
        if not pairs:
            return
            
        logger.info("buffer_flush_attempt", count=len(pairs))
        sent_ids = []
        
        for row_id, item in pairs:
            self.seq_num += 1
            wrapped = {
                "junction_id": self.junction_id,
                "sequence_number": self.seq_num,
                "data": item
            }
            headers = {"X-Device-Token": self.token, "Content-Type": "application/json"}
            try:
                resp = requests.post(self.url, json=wrapped, headers=headers, timeout=5)
                resp.raise_for_status()
                sent_ids.append(row_id)
            except Exception as e:
                logger.warning("flush_send_failed", error=str(e), seq_num=self.seq_num)
                break
                
        if sent_ids:
            self.buffer.delete_ids(sent_ids)
            logger.info("buffer_flush_confirmed", deleted=len(sent_ids))
