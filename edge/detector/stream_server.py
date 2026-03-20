import time
import structlog
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from edge.config.settings import config

logger = structlog.get_logger(__name__)

class MJPEGRequestHandler(BaseHTTPRequestHandler):
    """
    Serves a continuous boundary-separated JPEG byte stream on a local port.
    To be consumed securely through the VPN by the CCC dashboard frontend.
    """

    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    time.sleep(0.1)
                    mock_frame_data = getattr(self.server, "latest_frame", b"MOCK_JPEG_BINARY_DATA")
                    # C4: Write per-frame headers as raw bytes — send_header after
                    # end_headers writes into the body and corrupts frames.
                    frame_header = (
                        b'--FRAME\r\n'
                        b'Content-Type: image/jpeg\r\n'
                        b'Content-Length: ' + str(len(mock_frame_data)).encode() + b'\r\n'
                        b'\r\n'
                    )
                    self.wfile.write(frame_header)
                    self.wfile.write(mock_frame_data)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logger.info("stream_client_disconnected", error=str(e))
        else:
            self.send_error(404)

class StreamServer:
    def __init__(self):
        self.port = config.timing.stream_port
        # SEC-C3/H8: bind to VPN interface only — not accessible on open LAN
        bind_addr = getattr(config.uplink, 'vpn_ip', '127.0.0.1') or '127.0.0.1'
        self.server = HTTPServer((bind_addr, self.port), MJPEGRequestHandler)
        self.server.latest_frame = b"MOCK_JPEG_BINARY_DATA"
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        logger.info("mjpeg_stream_start", port=self.port)
        self.thread.start()

    def stop(self):
        logger.info("mjpeg_stream_stop")
        self.server.shutdown()
