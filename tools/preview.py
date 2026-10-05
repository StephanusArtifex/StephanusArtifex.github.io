#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="Build and preview the portfolio locally.")
parser.add_argument("--port", type=int, default=8000)
parser.add_argument("--drafts", action="store_true", help="Include draft Notes in the local preview.")
args = parser.parse_args()

cmd = [sys.executable, str(ROOT / "tools" / "build.py")]
if args.drafts:
    cmd.append("--include-drafts")
subprocess.run(cmd, cwd=ROOT, check=True)

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT / "_site"), **kw)

server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
print(f"Preview: http://127.0.0.1:{args.port}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    server.server_close()
