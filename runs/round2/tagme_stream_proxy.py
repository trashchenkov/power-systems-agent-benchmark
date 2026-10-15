#!/usr/bin/env python3
"""Loopback OpenAI-compatible proxy to TagMe with SSE streaming pass-through.

Unlike <home>/tagme-relay/tagme_relay.py it keeps the requested model (restricted to an
allowlist) and streams responses, which OpenCode requires. Credentials never leave the
process and are never logged.
"""
from __future__ import annotations

import argparse
import http.client
import json
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, "<home>/tagme-relay")
from tagme_relay import Credentials, TagMeClient  # noqa: E402


def make_handler(client: TagMeClient, base_url: str, allowed: set[str], log_path: Path):
    target = urllib.parse.urlsplit(base_url)
    base_path = target.path.rstrip("/")

    def log(entry: dict) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_args) -> None:
            return

        def reply(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path in {"/models", "/v1/models"}:
                data = {"object": "list", "data": [{"id": m, "object": "model"} for m in sorted(allowed)]}
                self.reply(200, json.dumps(data).encode())
            else:
                self.reply(404, b'{"error":"not found"}')

        def do_POST(self) -> None:
            endpoint = {"/chat/completions": "chat/completions", "/v1/chat/completions": "chat/completions",
                        "/responses": "responses", "/v1/responses": "responses"}.get(self.path)
            if endpoint is None:
                self.reply(404, b'{"error":"not found"}')
                return
            raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                self.reply(400, b'{"error":"invalid json"}')
                return
            model = payload.get("model")
            if model not in allowed:
                self.reply(400, json.dumps({"error": f"model not allowed: {model}"}).encode())
                return
            body = json.dumps(payload).encode()
            for attempt in range(2):
                token = client.token()
                conn = http.client.HTTPSConnection(target.hostname, target.port or 443, timeout=600)
                conn.request("POST", f"{base_path}/{endpoint}", body=body, headers={
                    "Authorization": f"Bearer {token}", "Content-Type": "application/json"})
                resp = conn.getresponse()
                if resp.status == 401 and attempt == 0:
                    resp.read()
                    conn.close()
                    client.invalidate(token)
                    continue
                break
            log({"endpoint": endpoint, "model": model, "stream": bool(payload.get("stream")), "status": resp.status})
            self.send_response(resp.status)
            self.send_header("Content-Type", resp.getheader("Content-Type", "application/json"))
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                while True:
                    chunk = resp.read1(65536)
                    if not chunk:
                        break
                    self.wfile.write(f"{len(chunk):X}\r\n".encode() + chunk + b"\r\n")
                    self.wfile.flush()
                self.wfile.write(b"0\r\n\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                conn.close()

    return Handler


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file", type=Path, default=Path("<home>/secrets/tagme.env"))
    ap.add_argument("--port", type=int, default=30210)
    ap.add_argument("--allow", nargs="+", required=True)
    ap.add_argument("--log", type=Path, default=Path("<workdir>/tagme_proxy_requests.jsonl"))
    args = ap.parse_args()
    creds = Credentials.from_env_file(args.env_file)
    client = TagMeClient(creds, interface="eth0")
    server = ThreadingHTTPServer(("127.0.0.1", args.port),
                                 make_handler(client, creds.base_url, set(args.allow), args.log))
    print(f"tagme stream proxy on 127.0.0.1:{args.port} allow={sorted(args.allow)}", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
