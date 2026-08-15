#!/usr/bin/env python3
"""Black-box tests for fetch-harness-docs.py."""

import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
try:
    import resource
except ImportError:  # pragma: no cover - unavailable on Windows
    resource = None
import signal
import socketserver
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("fetch-harness-docs.py")
FETCHER_SPEC = importlib.util.spec_from_file_location("fetch_harness_docs", SCRIPT)
FETCHER = importlib.util.module_from_spec(FETCHER_SPEC)
FETCHER_SPEC.loader.exec_module(FETCHER)
CODEX_URL = "https://learn.chatgpt.com/docs/build-skills.md"
SOURCE_CASES = {
    "agent-skills": (
        "agentskills.io:443",
        "/specification.md",
        "https://agentskills.io/specification.md",
        "# Specification",
    ),
    "claude-code": (
        "code.claude.com:443",
        "/docs/en/skills.md",
        "https://code.claude.com/docs/en/skills.md",
        "# Extend Claude with skills",
    ),
    "codex": (
        "learn.chatgpt.com:443",
        "/docs/build-skills.md",
        CODEX_URL,
        "# Build skills",
    ),
    "grok": (
        "docs.x.ai:443",
        "/build/features/skills-plugins-marketplaces.md",
        "https://docs.x.ai/build/features/skills-plugins-marketplaces.md",
        "# Skills, Plugins & Marketplaces",
    ),
}
IDENTITY_PREAMBLES = {
    "agent-skills": (
        "> ## Documentation Index",
        "> Fetch the complete documentation index at: https://agentskills.io/llms.txt",
        "> Use this file to discover all available pages before exploring further.",
        "",
    ),
    "claude-code": (
        "> ## Documentation Index",
        "> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt",
        "> Use this file to discover all available pages before exploring further.",
        "",
    ),
    "codex": (),
    "grok": ("#### Features", ""),
}


class _TlsTunnelHandler(socketserver.StreamRequestHandler):
    def handle(self):
        connect_line = self.rfile.readline().decode("ascii").rstrip("\r\n")
        method, authority, _ = connect_line.split(" ", 2)
        if method != "CONNECT":
            return
        while self.rfile.readline() not in (b"\r\n", b"\n", b""):
            pass

        self.server.seen_authority = authority
        self.server.seen_authorities.append(authority)
        self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        self.wfile.flush()

        try:
            tls_socket = self.server.ssl_context.wrap_socket(
                self.connection, server_side=True
            )
        except ssl.SSLError:
            return

        with tls_socket:
            reader = tls_socket.makefile("rb")
            request_line = reader.readline().decode("ascii").rstrip("\r\n")
            _, path, _ = request_line.split(" ", 2)
            while reader.readline() not in (b"\r\n", b"\n", b""):
                pass
            self.server.seen_path = path

            body = self.server.body
            content_length = self.server.declared_content_length
            if content_length is None:
                content_length = len(body)
            response_head = (
                f"HTTP/1.1 {self.server.response_status}\r\n".encode("ascii")
                + f"Content-Type: {self.server.content_type}\r\n".encode("ascii")
                + b'ETag: "fixture-etag"\r\n'
                b"Last-Modified: Fri, 14 Aug 2026 10:00:00 GMT\r\n"
                + self.server.extra_headers
                + f"Content-Length: {content_length}\r\n".encode("ascii")
                + b"Connection: close\r\n\r\n"
            )
            try:
                tls_socket.sendall(response_head)
                if self.server.chunk_delay is None:
                    tls_socket.sendall(body)
                else:
                    for byte in body:
                        tls_socket.sendall(bytes((byte,)))
                        time.sleep(self.server.chunk_delay)
            except (BrokenPipeError, ConnectionResetError, ssl.SSLError):
                pass


class _TlsTunnelServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


@contextlib.contextmanager
def harness_origin(
    body,
    certificate,
    private_key,
    *,
    response_status="200 OK",
    content_type="text/markdown; charset=utf-8",
    declared_content_length=None,
    extra_headers=b"",
    chunk_delay=None,
):
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certificate, private_key)

    server = _TlsTunnelServer(("127.0.0.1", 0), _TlsTunnelHandler)
    server.ssl_context = ssl_context
    server.body = body
    server.response_status = response_status
    server.content_type = content_type
    server.declared_content_length = declared_content_length
    server.extra_headers = extra_headers
    server.chunk_delay = chunk_delay
    server.seen_authority = None
    server.seen_authorities = []
    server.seen_path = None
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class FetchHarnessDocsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certificate_dir = tempfile.TemporaryDirectory()
        cls.certificate = Path(cls.certificate_dir.name, "certificate.pem")
        cls.private_key = Path(cls.certificate_dir.name, "private-key.pem")
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-keyout",
                str(cls.private_key),
                "-out",
                str(cls.certificate),
                "-days",
                "1",
                "-subj",
                "/CN=learn.chatgpt.com",
                "-addext",
                "subjectAltName=DNS:agentskills.io,DNS:learn.chatgpt.com,"
                "DNS:code.claude.com,DNS:docs.x.ai",
                "-addext",
                "basicConstraints=critical,CA:TRUE",
            ],
            check=True,
            capture_output=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.certificate_dir.cleanup()

    def test_ambient_tls_trust_is_rejected_before_network_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            env = os.environ.copy()
            env.pop("SSLKEYLOGFILE", None)
            env.update(
                {
                    "HTTPS_PROXY": "http://127.0.0.1:9",
                    "https_proxy": "http://127.0.0.1:9",
                    "SSL_CERT_FILE": str(self.certificate),
                }
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "codex", "--output", str(bundle)],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )

        self.assertEqual(1, result.returncode)
        self.assertEqual(
            "trust: ambient SSL_CERT_FILE or SSL_CERT_DIR is not allowed; "
            "pass --ca-file explicitly\n",
            result.stderr,
        )
        self.assertFalse(bundle.exists())

    def test_ambient_tls_key_logging_is_rejected_before_network_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            key_log = Path(temp_dir, "tls-keys.log")
            env = os.environ.copy()
            env.pop("SSL_CERT_FILE", None)
            env.pop("SSL_CERT_DIR", None)
            env.update(
                {
                    "HTTPS_PROXY": "http://127.0.0.1:9",
                    "SSLKEYLOGFILE": str(key_log),
                }
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "codex", "--output", str(bundle)],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )

        self.assertEqual(1, result.returncode)
        self.assertEqual(
            "trust: ambient SSLKEYLOGFILE is not allowed\n", result.stderr
        )
        self.assertFalse(bundle.exists())
        self.assertFalse(key_log.exists())

    def run_fetch(
        self,
        source,
        bundle,
        proxy_url,
        *,
        ca_file=True,
        timeout=10,
        preexec_fn=None,
    ):
        env = os.environ.copy()
        env.update(
            {
                "HTTPS_PROXY": "http://127.0.0.1:9",
                "https_proxy": "http://127.0.0.1:9",
                "ALL_PROXY": "http://127.0.0.1:9",
                "all_proxy": "http://127.0.0.1:9",
                "NO_PROXY": "learn.chatgpt.com",
                "no_proxy": "learn.chatgpt.com",
            }
        )
        env.pop("SSL_CERT_FILE", None)
        env.pop("SSL_CERT_DIR", None)
        env.pop("SSLKEYLOGFILE", None)
        command = [
            sys.executable,
            str(SCRIPT),
            source,
            "--output",
            str(bundle),
            "--proxy",
            proxy_url,
        ]
        if ca_file:
            command.extend(["--ca-file", str(self.certificate)])
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout,
            preexec_fn=preexec_fn,
        )

    def test_proxy_credentials_are_rejected_before_network_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            env = os.environ.copy()
            env.pop("SSL_CERT_FILE", None)
            env.pop("SSL_CERT_DIR", None)
            env.pop("SSLKEYLOGFILE", None)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "codex",
                    "--output",
                    str(bundle),
                    "--proxy",
                    "http://user:secret@127.0.0.1:9",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )

        self.assertEqual(1, result.returncode)
        self.assertEqual("trust: proxy credentials are not allowed\n", result.stderr)
        self.assertFalse(bundle.exists())

    def test_malformed_proxy_is_a_handled_trust_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            env = os.environ.copy()
            env.pop("SSL_CERT_FILE", None)
            env.pop("SSL_CERT_DIR", None)
            env.pop("SSLKEYLOGFILE", None)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "codex",
                    "--output",
                    str(bundle),
                    "--proxy",
                    "http://[",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )

        self.assertEqual(1, result.returncode)
        self.assertTrue(result.stderr.startswith("trust: invalid proxy URL: "))
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(bundle.exists())

    def test_unverified_proxy_scheme_is_rejected_before_network_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            env = os.environ.copy()
            env.pop("SSL_CERT_FILE", None)
            env.pop("SSL_CERT_DIR", None)
            env.pop("SSLKEYLOGFILE", None)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "codex",
                    "--output",
                    str(bundle),
                    "--proxy",
                    "https://127.0.0.1:9",
                ],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )

        self.assertEqual(1, result.returncode)
        self.assertEqual(
            "trust: proxy must be an absolute http:// URL\n", result.stderr
        )
        self.assertFalse(bundle.exists())

    def test_codex_response_creates_verified_bundle(self):
        body = b"# Build skills\n\nCurrent official fixture.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("learn.chatgpt.com:443", origin.seen_authority)
            self.assertEqual("/docs/build-skills.md", origin.seen_path)
            self.assertEqual(body, Path(bundle, "payload.md").read_bytes())

            provenance = json.loads(Path(bundle, "provenance.json").read_text())
            self.assertEqual(1, provenance["schema_version"])
            self.assertEqual("1", provenance["tool_version"])
            self.assertEqual("codex", provenance["source_id"])
            self.assertEqual(CODEX_URL, provenance["requested_url"])
            self.assertEqual(CODEX_URL, provenance["final_url"])
            self.assertEqual(200, provenance["http_status"])
            self.assertEqual("text/markdown", provenance["content_type"])
            self.assertEqual(len(body), provenance["byte_count"])
            self.assertEqual(hashlib.sha256(body).hexdigest(), provenance["sha256"])
            self.assertEqual(
                "# Build skills", provenance["required_identity_heading"]
            )
            self.assertEqual([], provenance["required_identity_preamble"])
            self.assertEqual("none", provenance["transformation"])
            self.assertEqual('"fixture-etag"', provenance["etag"])
            self.assertEqual([], provenance["redirect_chain"])
            self.assertEqual(
                {
                    "proxy": proxy_url,
                    "tls_ca": {
                        "mode": "explicit",
                        "sha256": hashlib.sha256(
                            self.certificate.read_bytes()
                        ).hexdigest(),
                    },
                },
                provenance["transport_trust"],
            )
            self.assertEqual(
                {
                    "allowed_https_host": True,
                    "complete_transfer": True,
                    "content_type": True,
                    "identity_heading": True,
                    "identity_preamble": True,
                    "nul_free": True,
                    "size": True,
                    "status_200": True,
                    "utf8": True,
                },
                provenance["validations"],
            )
            self.assertTrue(provenance["retrieved_at_utc"].endswith("Z"))

    def test_each_built_in_source_targets_its_reviewed_document(self):
        for source_id, (authority, path, url, identity_heading) in SOURCE_CASES.items():
            with self.subTest(source_id=source_id):
                body = "\n".join(
                    (*IDENTITY_PREAMBLES[source_id], identity_heading, "", "Official fixture.")
                ).encode()
                with tempfile.TemporaryDirectory() as temp_dir:
                    bundle = Path(temp_dir, "bundle")
                    with harness_origin(
                        body, self.certificate, self.private_key
                    ) as origin:
                        proxy_url = (
                            f"http://127.0.0.1:{origin.server_address[1]}"
                        )
                        result = self.run_fetch(source_id, bundle, proxy_url)

                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual(authority, origin.seen_authority)
                    self.assertEqual(path, origin.seen_path)
                    provenance = json.loads(
                        bundle.joinpath("provenance.json").read_text()
                    )
                    self.assertEqual(source_id, provenance["source_id"])
                    self.assertEqual(url, provenance["requested_url"])
                    self.assertEqual(
                        identity_heading,
                        provenance["required_identity_heading"],
                    )
                    self.assertEqual(
                        list(IDENTITY_PREAMBLES[source_id]),
                        provenance["required_identity_preamble"],
                    )

    def test_wrong_identity_heading_fails_without_publishing_a_bundle(self):
        body = b"# Unrelated page\n\nThis is not the requested manual.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: identity line does not match after "
                "reviewed preamble: "
                "expected # Build skills, received # Unrelated page\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_identity_heading_in_body_does_not_authenticate_the_document(self):
        body = (
            b"# Sign in\n\n"
            b"Navigation mentions the expected page: # Build skills\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: identity line does not match after "
                "reviewed preamble: "
                "expected # Build skills, received # Sign in\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_heading_in_a_code_fence_does_not_authenticate_the_document(self):
        body = (
            b"```markdown\n"
            b"# Build skills\n"
            b"```\n\n"
            b"# Sign in\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: identity line does not match after "
                "reviewed preamble: expected # Build skills, "
                "received ```markdown\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_noncanonical_content_before_identity_line_is_rejected(self):
        cases = {
            "inline-comment": "# Sign in <!-- note -->\n# Build skills\n",
            "empty-atx": "#\n# Build skills\n",
            "tab-atx": "#\tSign in\n# Build skills\n",
            "setext": "Sign in\n=======\n# Build skills\n",
            "bom": "\ufeff# Sign in\n# Build skills\n",
            "raw-pre": "<pre>\n# Build skills\n</pre>\n# Sign in\n",
        }

        for label, text_payload in cases.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp_dir:
                bundle = Path(temp_dir, "bundle")
                with harness_origin(
                    text_payload.encode("utf-8"),
                    self.certificate,
                    self.private_key,
                ) as origin:
                    proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                    result = self.run_fetch("codex", bundle, proxy_url)

                self.assertNotEqual(0, result.returncode)
                self.assertTrue(
                    result.stderr.startswith(
                        "content_validation: identity line does not match after "
                        "reviewed preamble: expected # Build skills, received "
                    ),
                    result.stderr,
                )
                self.assertFalse(bundle.exists())

    def test_non_markdown_line_separators_cannot_split_the_identity_line(self):
        separators = {
            "bare-cr": ("\r", "bare CR"),
            "vertical-tab": ("\v", "VT"),
            "form-feed": ("\f", "FF"),
            "next-line": ("\x85", "NEL"),
            "line-separator": ("\u2028", "U+2028"),
            "paragraph-separator": ("\u2029", "U+2029"),
        }

        for label, (separator, diagnostic) in separators.items():
            payload = f"# Build skills{separator}# Sign in\n".encode("utf-8")
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temp_dir:
                bundle = Path(temp_dir, "bundle")
                with harness_origin(
                    payload, self.certificate, self.private_key
                ) as origin:
                    proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                    result = self.run_fetch("codex", bundle, proxy_url)

                self.assertNotEqual(0, result.returncode)
                self.assertEqual(
                    "content_validation: unsupported Markdown line separator: "
                    f"{diagnostic}\n",
                    result.stderr,
                )
                self.assertFalse(bundle.exists())

    def test_wrong_content_type_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n\nLogin page disguised as success.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                body,
                self.certificate,
                self.private_key,
                content_type="text/html; charset=utf-8",
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: unexpected content type: text/html\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_truncated_response_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n\ntruncated fixture\n"
        declared_length = len(body) + 20

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                body,
                self.certificate,
                self.private_key,
                declared_content_length=declared_length,
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: response ended before declared Content-Length: "
                f"expected {declared_length}, received {len(body)}\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_cross_host_redirect_is_rejected_before_contacting_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                b"",
                self.certificate,
                self.private_key,
                response_status="302 Found",
                extra_headers=b"Location: https://unexpected.example/manual.md\r\n",
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(["learn.chatgpt.com:443"], origin.seen_authorities)
            self.assertEqual(
                "content_validation: redirect is not allowed: "
                "https://unexpected.example/manual.md\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    def test_existing_output_is_rejected_before_network_access(self):
        body = b"# Build skills\n\nCurrent official fixture.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            bundle.mkdir()
            sentinel = bundle.joinpath("owned-by-caller.txt")
            sentinel.write_text("keep me\n")

            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], origin.seen_authorities)
            self.assertEqual(
                f"io: output directory already exists: {bundle}\n", result.stderr
            )
            self.assertEqual("keep me\n", sentinel.read_text())
            self.assertEqual([sentinel], list(bundle.iterdir()))

    def test_http_error_fails_without_publishing_a_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                b"temporary outage\n",
                self.certificate,
                self.private_key,
                response_status="503 Service Unavailable",
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("http: unexpected HTTP status: 503\n", result.stderr)
            self.assertFalse(bundle.exists())

    def test_malformed_http_status_fails_without_a_traceback_or_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                b"# Build skills\n",
                self.certificate,
                self.private_key,
                response_status="BOGUS",
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("http: malformed HTTP response\n", result.stderr)
            self.assertFalse(bundle.exists())

    def test_partial_content_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n\nOnly one range.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                body,
                self.certificate,
                self.private_key,
                response_status="206 Partial Content",
                extra_headers=b"Content-Range: bytes 0-34/100\r\n",
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual("http: unexpected HTTP status: 206\n", result.stderr)
            self.assertFalse(bundle.exists())

    def test_network_error_fails_without_publishing_a_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(
                b"# Build skills\n",
                self.certificate,
                self.private_key,
            ) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"

            result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertTrue(result.stderr.startswith("network_or_permission: "))
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(bundle.exists())

    def test_untrusted_certificate_is_reported_as_a_trust_error(self):
        body = b"# Build skills\n\nCurrent official fixture.\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch(
                    "codex", bundle, proxy_url, ca_file=False
                )

            self.assertNotEqual(0, result.returncode)
            self.assertTrue(
                result.stderr.startswith(
                    "trust: TLS certificate verification failed: "
                ),
                result.stderr,
            )
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(bundle.exists())

    def test_direct_certificate_verification_error_keeps_trust_classification(self):
        opener = mock.Mock()
        opener.open.side_effect = ssl.SSLCertVerificationError(
            1, "certificate expired"
        )

        with self.assertRaisesRegex(
            FETCHER.TrustConfigurationError,
            "TLS certificate verification failed: certificate expired",
        ):
            FETCHER.fetch(FETCHER.SOURCES["codex"], opener, None)

    def test_slow_trickle_is_cut_off_by_total_deadline(self):
        body = b"# Build skills\n\nSlow official fixture.\n"

        with harness_origin(
            body,
            self.certificate,
            self.private_key,
            chunk_delay=0.05,
        ) as origin:
            proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
            with mock.patch.dict(
                os.environ,
                {
                    "SSL_CERT_FILE": "",
                    "SSL_CERT_DIR": "",
                    "SSLKEYLOGFILE": "",
                },
            ):
                opener, proxy_target, _ = FETCHER.configure_transport(
                    proxy_url, self.certificate
                )
            started = time.monotonic()
            with self.assertRaisesRegex(
                FETCHER.NetworkAccessError,
                "response transfer exceeded 0.1-second deadline",
            ):
                FETCHER.fetch_with_deadline(
                    FETCHER.SOURCES["codex"],
                    opener,
                    proxy_target,
                    deadline_seconds=0.1,
                )
            elapsed = time.monotonic() - started

        self.assertLess(elapsed, 1)

    def test_cleanup_failure_reports_the_residual_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with mock.patch.object(
                Path, "write_bytes", side_effect=OSError("write denied")
            ), mock.patch.object(
                FETCHER.shutil,
                "rmtree",
                side_effect=OSError("cleanup denied"),
            ):
                with self.assertRaisesRegex(
                    FETCHER.OutputError,
                    rf"partial bundle cleanup failed at {bundle}: cleanup denied",
                ):
                    FETCHER.publish_bundle(bundle, b"payload", {})

            self.assertTrue(bundle.is_dir())

    def test_invalid_utf8_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n\ninvalid: \xff\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: response is not valid UTF-8\n", result.stderr
            )
            self.assertFalse(bundle.exists())

    def test_nul_byte_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n\nembedded: \x00\n"

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch("codex", bundle, proxy_url)

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: response contains a NUL byte\n", result.stderr
            )
            self.assertFalse(bundle.exists())

    def test_oversized_response_fails_without_publishing_a_bundle(self):
        body = b"# Build skills\n" + b"x" * (10 * 1024 * 1024)

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch(
                    "codex", bundle, proxy_url, timeout=20
                )

            self.assertNotEqual(0, result.returncode)
            self.assertEqual(
                "content_validation: response exceeds 10485760 bytes\n",
                result.stderr,
            )
            self.assertFalse(bundle.exists())

    @unittest.skipIf(
        resource is None or not hasattr(signal, "SIGXFSZ"),
        "requires POSIX file-size limits",
    )
    def test_write_failure_removes_partial_bundle(self):
        body = b"# Build skills\n\nCurrent official fixture.\n"

        def limit_output_file_size():
            signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
            resource.setrlimit(resource.RLIMIT_FSIZE, (64, 64))

        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = Path(temp_dir, "bundle")
            with harness_origin(body, self.certificate, self.private_key) as origin:
                proxy_url = f"http://127.0.0.1:{origin.server_address[1]}"
                result = self.run_fetch(
                    "codex",
                    bundle,
                    proxy_url,
                    preexec_fn=limit_output_file_size,
                )

            self.assertNotEqual(0, result.returncode)
            self.assertTrue(result.stderr.startswith("io: unable to publish bundle: "))
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse(bundle.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
