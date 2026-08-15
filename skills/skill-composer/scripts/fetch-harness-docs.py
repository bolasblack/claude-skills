#!/usr/bin/env python3
"""Fetch one official source document into a provenance-bearing bundle."""

import argparse
from datetime import datetime, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import queue
import shutil
import ssl
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request


SCHEMA_VERSION = 1
TOOL_VERSION = "1"
# Bound one untrusted document before it can exhaust process memory.
MAX_BYTES = 10 * 1024 * 1024
TRANSFER_DEADLINE_SECONDS = 30
UNSUPPORTED_LINE_SEPARATORS = (
    ("\r", "bare CR"),
    ("\v", "VT"),
    ("\f", "FF"),
    ("\x85", "NEL"),
    ("\u2028", "U+2028"),
    ("\u2029", "U+2029"),
)
SOURCES = {
    "agent-skills": {
        "url": "https://agentskills.io/specification.md",
        "host": "agentskills.io",
        "content_type": "text/markdown",
        "identity_preamble": (
            "> ## Documentation Index",
            "> Fetch the complete documentation index at: https://agentskills.io/llms.txt",
            "> Use this file to discover all available pages before exploring further.",
            "",
        ),
        "identity_heading": "# Specification",
    },
    "codex": {
        "url": "https://learn.chatgpt.com/docs/build-skills.md",
        "host": "learn.chatgpt.com",
        "content_type": "text/markdown",
        "identity_preamble": (),
        "identity_heading": "# Build skills",
    },
    "claude-code": {
        "url": "https://code.claude.com/docs/en/skills.md",
        "host": "code.claude.com",
        "content_type": "text/markdown",
        "identity_preamble": (
            "> ## Documentation Index",
            "> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt",
            "> Use this file to discover all available pages before exploring further.",
            "",
        ),
        "identity_heading": "# Extend Claude with skills",
    },
    "grok": {
        "url": "https://docs.x.ai/build/features/skills-plugins-marketplaces.md",
        "host": "docs.x.ai",
        "content_type": "text/markdown",
        "identity_preamble": ("#### Features", ""),
        "identity_heading": "# Skills, Plugins & Marketplaces",
    },
}


class ContentValidationError(ValueError):
    pass


class OutputError(ValueError):
    pass


class NetworkAccessError(OSError):
    pass


class TrustConfigurationError(ValueError):
    pass


class HttpStatusError(ValueError):
    def __init__(self, status):
        super().__init__(f"unexpected HTTP status: {status}")
        self.status = status


class HttpProtocolError(ValueError):
    pass


class RejectRedirects(urllib.request.HTTPRedirectHandler):
    """Require source relocation to be re-authorized before contacting a new URL."""

    def redirect_request(self, request, response, code, message, headers, new_url):
        target = urllib.parse.urljoin(request.full_url, new_url)
        raise ContentValidationError(f"redirect is not allowed: {target}")


def validate_document_identity(text, source):
    """Require one reviewed preamble followed by one line-exact identity heading."""
    normalized = text.replace("\r\n", "\n")
    for separator, diagnostic in UNSUPPORTED_LINE_SEPARATORS:
        if separator in normalized:
            raise ContentValidationError(
                f"unsupported Markdown line separator: {diagnostic}"
            )
    lines = normalized.split("\n")
    position = 0
    while position < len(lines) and lines[position] == "":
        position += 1

    preamble = source["identity_preamble"]
    received_preamble = tuple(lines[position : position + len(preamble)])
    if received_preamble != preamble:
        received = lines[position] if position < len(lines) else "none"
        raise ContentValidationError(
            "reviewed identity preamble does not match: "
            f"received {received}"
        )

    position += len(preamble)
    received = lines[position] if position < len(lines) else "none"
    if received != source["identity_heading"]:
        raise ContentValidationError(
            "identity line does not match after reviewed preamble: "
            f"expected {source['identity_heading']}, received {received}"
        )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch one official source document into a new evidence bundle."
    )
    parser.add_argument("source", choices=sorted(SOURCES))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--proxy",
        help="Explicit HTTP CONNECT proxy URL; ambient proxy settings are ignored.",
    )
    parser.add_argument(
        "--ca-file",
        type=Path,
        help="Explicit PEM/DER CA bundle; ambient CA settings are rejected.",
    )
    return parser.parse_args(argv)


def configure_transport(proxy, ca_file):
    if os.environ.get("SSLKEYLOGFILE"):
        raise TrustConfigurationError("ambient SSLKEYLOGFILE is not allowed")
    if ca_file is None:
        if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
            raise TrustConfigurationError(
                "ambient SSL_CERT_FILE or SSL_CERT_DIR is not allowed; "
                "pass --ca-file explicitly"
            )
        context = ssl.create_default_context()
        tls_ca = {"mode": "platform-default"}
    else:
        try:
            ca_bytes = ca_file.read_bytes()
        except OSError as error:
            raise TrustConfigurationError(f"unable to read CA file: {error}") from error
        try:
            ca_data = ca_bytes.decode("ascii")
        except UnicodeDecodeError:
            ca_data = ca_bytes
        try:
            context = ssl.create_default_context(cadata=ca_data)
        except (ssl.SSLError, ValueError) as error:
            raise TrustConfigurationError(f"invalid CA file: {error}") from error
        tls_ca = {
            "mode": "explicit",
            "sha256": hashlib.sha256(ca_bytes).hexdigest(),
        }

    proxy_target = None
    if proxy is not None:
        if any(ord(character) <= 32 or ord(character) == 127 for character in proxy):
            raise TrustConfigurationError(
                "invalid proxy URL: whitespace and control characters are not allowed"
            )
        try:
            parsed = urllib.parse.urlsplit(proxy)
            hostname = parsed.hostname
            username = parsed.username
            password = parsed.password
            parsed.port
        except ValueError as error:
            raise TrustConfigurationError(f"invalid proxy URL: {error}") from error
        if parsed.scheme != "http" or hostname is None:
            raise TrustConfigurationError("proxy must be an absolute http:// URL")
        if username is not None or password is not None:
            raise TrustConfigurationError("proxy credentials are not allowed")
        if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
            raise TrustConfigurationError("proxy URL cannot contain a path or query")
        proxy_target = (parsed.netloc, parsed.scheme)

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPSHandler(context=context),
        RejectRedirects(),
    )
    return opener, proxy_target, {
        "proxy": proxy,
        "tls_ca": tls_ca,
    }


def fetch(source, opener, proxy_target):
    request = urllib.request.Request(
        source["url"],
        headers={"User-Agent": f"skill-composer-harness-docs/{TOOL_VERSION}"},
    )
    if proxy_target is not None:
        proxy_authority, proxy_scheme = proxy_target
        request.set_proxy(proxy_authority, proxy_scheme)
    try:
        with opener.open(request, timeout=TRANSFER_DEADLINE_SECONDS) as response:
            status = response.status
            # 206 may be partial and 203 explicitly transformed; either would make a
            # complete, unmodified source-snapshot provenance claim dishonest.
            if status != 200:
                raise HttpStatusError(status)
            declared_length_header = response.headers.get("Content-Length")
            if declared_length_header is None:
                declared_length = None
            else:
                try:
                    declared_length = int(declared_length_header)
                except ValueError as error:
                    raise ContentValidationError(
                        f"invalid Content-Length: {declared_length_header}"
                    ) from error
                if declared_length < 0:
                    raise ContentValidationError(
                        f"invalid Content-Length: {declared_length_header}"
                    )
                if declared_length > MAX_BYTES:
                    raise ContentValidationError(
                        f"response exceeds {MAX_BYTES} bytes"
                    )
            try:
                body = response.read(MAX_BYTES + 1)
            except http.client.IncompleteRead as error:
                raise ContentValidationError(
                    "response ended before the HTTP transfer completed"
                ) from error
            except http.client.HTTPException as error:
                raise ContentValidationError(
                    "HTTP transfer did not complete cleanly"
                ) from error
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
    except urllib.error.HTTPError:
        raise
    except http.client.HTTPException as error:
        raise HttpProtocolError("malformed HTTP response") from error
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        if isinstance(reason, ssl.SSLCertVerificationError):
            raise TrustConfigurationError(
                f"TLS certificate verification failed: {reason}"
            ) from error
        raise NetworkAccessError(str(reason)) from error
    except ssl.SSLCertVerificationError as error:
        raise TrustConfigurationError(
            f"TLS certificate verification failed: {error}"
        ) from error
    except (TimeoutError, OSError) as error:
        reason = getattr(error, "reason", error)
        raise NetworkAccessError(str(reason)) from error

    parsed_final_url = urllib.parse.urlsplit(final_url)
    if parsed_final_url.scheme != "https" or parsed_final_url.hostname != source["host"]:
        raise ContentValidationError("response left the source's allowed HTTPS host")
    if content_type != source["content_type"]:
        raise ContentValidationError(f"unexpected content type: {content_type}")
    if len(body) > MAX_BYTES:
        raise ContentValidationError(f"response exceeds {MAX_BYTES} bytes")
    if declared_length is not None and len(body) != declared_length:
        raise ContentValidationError(
            "response ended before declared Content-Length: "
            f"expected {declared_length}, received {len(body)}"
        )
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContentValidationError("response is not valid UTF-8") from error
    if "\x00" in text:
        raise ContentValidationError("response contains a NUL byte")
    validate_document_identity(text, source)

    return body, {
        "final_url": final_url,
        "http_status": status,
        "content_type": content_type,
        "etag": etag,
        "last_modified": last_modified,
    }


def fetch_with_deadline(
    source,
    opener,
    proxy_target,
    deadline_seconds=TRANSFER_DEADLINE_SECONDS,
):
    """Bound retrieval and content validation with one wall-clock deadline.

    The worker is a daemon because this module is a CLI: after a deadline the
    command reports failure and exits, which also terminates an in-flight socket
    operation instead of waiting for its per-operation timeout.
    """
    outcome = queue.Queue(maxsize=1)

    def run_fetch():
        try:
            outcome.put((True, fetch(source, opener, proxy_target)))
        except Exception as error:
            outcome.put((False, error))

    worker = threading.Thread(target=run_fetch, daemon=True)
    worker.start()
    try:
        succeeded, value = outcome.get(timeout=deadline_seconds)
    except queue.Empty as error:
        raise NetworkAccessError(
            "response transfer exceeded "
            f"{deadline_seconds:g}-second deadline"
        ) from error
    if succeeded:
        return value
    raise value


def publish_bundle(output, body, provenance):
    created = False
    try:
        output.mkdir()
        created = True
        output.joinpath("payload.md").write_bytes(body)
        output.joinpath("provenance.json").write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        if created:
            try:
                shutil.rmtree(output)
            except OSError as cleanup_error:
                raise OutputError(
                    f"unable to publish bundle: {error}; "
                    f"partial bundle cleanup failed at {output}: {cleanup_error}"
                ) from error
        raise OutputError(f"unable to publish bundle: {error}") from error


def main(argv=None):
    args = parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        raise OutputError(f"output directory already exists: {args.output}")
    opener, proxy_target, transport_trust = configure_transport(
        args.proxy, args.ca_file
    )
    source = SOURCES[args.source]
    body, response = fetch_with_deadline(source, opener, proxy_target)

    provenance = {
        "schema_version": SCHEMA_VERSION,
        "source_id": args.source,
        "requested_url": source["url"],
        "final_url": response["final_url"],
        "http_status": response["http_status"],
        "content_type": response["content_type"],
        "etag": response["etag"],
        "last_modified": response["last_modified"],
        "retrieved_at_utc": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "retrieval_method": "fetch-harness-docs.py",
        "tool_version": TOOL_VERSION,
        "byte_count": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "required_identity_heading": source["identity_heading"],
        "required_identity_preamble": list(source["identity_preamble"]),
        "redirect_chain": [],
        "transformation": "none",
        "transport_trust": transport_trust,
        "validations": {
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
    }
    publish_bundle(args.output, body, provenance)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TrustConfigurationError as error:
        print(f"trust: {error}", file=sys.stderr)
        raise SystemExit(1)
    except ContentValidationError as error:
        print(f"content_validation: {error}", file=sys.stderr)
        raise SystemExit(1)
    except OutputError as error:
        print(f"io: {error}", file=sys.stderr)
        raise SystemExit(1)
    except urllib.error.HTTPError as error:
        print(f"http: unexpected HTTP status: {error.code}", file=sys.stderr)
        raise SystemExit(1)
    except HttpStatusError as error:
        print(f"http: unexpected HTTP status: {error.status}", file=sys.stderr)
        raise SystemExit(1)
    except HttpProtocolError:
        print("http: malformed HTTP response", file=sys.stderr)
        raise SystemExit(1)
    except NetworkAccessError as error:
        print(f"network_or_permission: {error}", file=sys.stderr)
        raise SystemExit(1)
