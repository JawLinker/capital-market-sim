import os
import socket
import threading
import webbrowser

import uvicorn

from app.main import app


def _lan_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _open_browser() -> None:
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    lan_ip = _lan_ip()
    print("=" * 62)
    print("Capital Market Simulator")
    print(f"  Local:    http://127.0.0.1:8000")
    print(f"  LAN:      http://{lan_ip}:8000")
    print("  Host account: host / 123456  (first player to register owns the host)")
    print("=" * 62)
    if os.environ.get("CMS_NO_BROWSER") != "1":
        threading.Timer(1.2, _open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
