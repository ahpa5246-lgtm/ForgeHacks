"""Confirm Render can discover the listening port when HOST is not provided."""
import json
import os
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.request import urlopen


class RenderBootTests(unittest.TestCase):
    def test_server_binds_public_interface_without_host_env(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        env = os.environ.copy()
        env.pop("HOST", None)
        env["PORT"] = str(port)
        proc = subprocess.Popen(
            [sys.executable, "-u", "offerproof.py"],
            cwd=str(Path(__file__).resolve().parents[1]),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            deadline = time.monotonic() + 6
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    self.fail("Server stopped before ready; exit status "+str(proc.returncode))
                try:
                    with urlopen("http://127.0.0.1:"+str(port)+"/health", timeout=.5) as response:
                        self.assertEqual(response.status, 200)
                        self.assertTrue(json.load(response)["ok"])
                        return
                except OSError:
                    time.sleep(.1)
            self.fail("Render-like startup did not open the requested port")
        finally:
            proc.terminate()
            try:
                proc.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()


if __name__ == "__main__":
    unittest.main()
