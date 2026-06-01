#!/usr/bin/env python3
"""Extract clean plain-text from a complaint email file (.eml or .msg).

The "intelligent" work (analysis, classification) is done by Claude. This script
only translates what Claude cannot read on its own: MIME-encoded .eml and binary
.msg files. It prints clean text (headers + body) to stdout.

Usage:
    python extract_email.py <path-to-email>
    python extract_email.py <path-to-email> --output cleaned.txt

Supports:
    .eml  -> stdlib `email` (MIME parse, quoted-printable/base64 decode,
             prefers text/plain over a tag-stripped text/html)
    .msg  -> third-party `extract-msg` (sender, to, subject, date, body)

Exit codes: 0 ok, 1 usage/IO error, 2 unsupported format, 3 missing dependency.
"""

import argparse
import os
import re
import sys
from email import policy
from email.parser import BytesParser


def _eprint(msg):
    """Print an error message to stderr."""
    print(msg, file=sys.stderr)


def _strip_html(html):
    """Turn an HTML body into readable plain text (best-effort, no deps)."""
    # Drop script/style blocks entirely.
    text = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    # Line breaks for common block-level tags.
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|div|tr|li|h[1-6])>", "\n", text)
    # Remove all remaining tags.
    text = re.sub(r"(?s)<[^>]+>", "", text)
    # Decode the handful of entities we actually see in complaint emails.
    entities = {
        "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">",
        "&quot;": '"', "&#39;": "'", "&aacute;": "á", "&eacute;": "é",
        "&iacute;": "í", "&oacute;": "ó", "&uacute;": "ú", "&ntilde;": "ñ",
    }
    for ent, char in entities.items():
        text = text.replace(ent, char)
    # Collapse excess blank lines.
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _format_output(headers, body):
    """Build the final header-block + body string."""
    lines = []
    for label, value in headers:
        if value:
            lines.append(f"{label}: {value}")
    header_block = "\n".join(lines)
    body = (body or "").strip()
    if header_block:
        return f"{header_block}\n\n{body}\n"
    return f"{body}\n"


def extract_eml(path):
    """Parse a .eml file with the stdlib. Decodes quoted-printable/base64 and
    prefers text/plain; falls back to a tag-stripped text/html part."""
    with open(path, "rb") as fh:
        msg = BytesParser(policy=policy.default).parse(fh)

    headers = [
        ("From", msg.get("From", "")),
        ("To", msg.get("To", "")),
        ("Cc", msg.get("Cc", "")),
        ("Subject", msg.get("Subject", "")),
        ("Date", msg.get("Date", "")),
    ]

    plain_parts = []
    html_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            # Skip attachments; we only want the message body.
            if part.get_content_disposition() == "attachment":
                continue
            ctype = part.get_content_type()
            if ctype == "text/plain":
                plain_parts.append(part.get_content())
            elif ctype == "text/html":
                html_parts.append(part.get_content())
    else:
        ctype = msg.get_content_type()
        if ctype == "text/html":
            html_parts.append(msg.get_content())
        else:
            plain_parts.append(msg.get_content())

    if plain_parts:
        body = "\n\n".join(p.strip() for p in plain_parts if p)
    elif html_parts:
        body = "\n\n".join(_strip_html(h) for h in html_parts if h)
    else:
        body = ""

    return _format_output(headers, body)


def extract_msg(path):
    """Parse a .msg (Outlook binary) file using the extract-msg library."""
    try:
        import extract_msg
    except ImportError:
        _eprint(
            "ERROR: falta la librería 'extract-msg' para leer archivos .msg.\n"
            "Instálala con: pip install -r scripts/requirements.txt"
        )
        sys.exit(3)

    msg = extract_msg.Message(path)
    try:
        headers = [
            ("From", (msg.sender or "").strip()),
            ("To", (msg.to or "").strip()),
            ("Cc", (msg.cc or "").strip()),
            ("Subject", (msg.subject or "").strip()),
            ("Date", str(msg.date or "").strip()),
        ]
        body = msg.body or ""
        if not body.strip() and getattr(msg, "htmlBody", None):
            html = msg.htmlBody
            if isinstance(html, bytes):
                html = html.decode("utf-8", errors="replace")
            body = _strip_html(html)
        return _format_output(headers, body)
    finally:
        msg.close()


def main():
    parser = argparse.ArgumentParser(
        description="Extrae texto plano limpio de un correo de reclamo (.eml/.msg)."
    )
    parser.add_argument("path", help="Ruta al archivo de correo (.eml o .msg)")
    parser.add_argument(
        "--output", "-o", help="Ruta opcional de salida; si se omite, imprime a stdout"
    )
    args = parser.parse_args()

    path = args.path
    if not os.path.isfile(path):
        _eprint(f"ERROR: no existe el archivo: {path}")
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".eml":
            text = extract_eml(path)
        elif ext == ".msg":
            text = extract_msg(path)
        else:
            _eprint(
                f"ERROR: formato no soportado '{ext}'. Usa .eml o .msg "
                "(los .txt se leen directamente, sin este script)."
            )
            sys.exit(2)
    except Exception as exc:  # noqa: BLE001 - report any parse failure clearly
        _eprint(f"ERROR al procesar '{path}': {exc}")
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as out:
                out.write(text)
        except OSError as exc:
            _eprint(f"ERROR al escribir '{args.output}': {exc}")
            sys.exit(1)
        print(f"OK: texto extraído en {args.output}")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
