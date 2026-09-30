#!/usr/bin/env python3
"""
webfetch.py - ambil satu URL dan tampilkan isinya sebagai markdown/text/html.

Pakai:
    python3 webfetch.py URL [-f markdown|text|html] [--max-chars 6000] [--timeout 30]

Contoh:
    python3 webfetch.py https://example.com
    python3 webfetch.py https://github.com/rafixxp -f text --max-chars 3000

Exit code: 0 = berhasil, 1 = gagal (pesan error dicetak).
Hanya butuh: pip install requests
"""

import re
import sys
import socket
import argparse
import ipaddress
from html.parser import HTMLParser
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import requests

MAX_BYTES = 5 * 1024 * 1024          # batas unduhan: 5 MB
MAX_REDIRECTS = 5
USER_AGENT = "Mozilla/5.0 (compatible; simple-webfetch/1.0)"
ROBOTS_TOKEN = "simple-webfetch"


# ------------------------------------------------------------
# HTML -> markdown / text
# ------------------------------------------------------------

class Converter(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template", "iframe"}
    BLOCK = {"p", "div", "br", "li", "tr", "section", "article", "header",
             "footer", "ul", "ol", "table", "pre", "blockquote"}
    HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self, base_url, markdown):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.markdown = markdown
        self.parts = []
        self.title = ""
        self._skip = 0
        self._in_title = False
        self._href = None

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
            return
        if tag == "title":
            self._in_title = True
        if tag in self.HEADINGS:
            self.parts.append("\n\n" + ("#" * int(tag[1]) + " " if self.markdown else ""))
        elif tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "li" and self.markdown:
            self.parts.append("- ")
        if tag == "a" and self.markdown:
            href = dict(attrs).get("href")
            if href and not href.startswith(("#", "javascript:", "mailto:")):
                self._href = urljoin(self.base_url, href)
                self.parts.append("[")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if tag == "title":
            self._in_title = False
        if tag in self.HEADINGS:
            self.parts.append("\n\n")
        elif tag in self.BLOCK:
            self.parts.append("\n")
        if tag == "a" and self._href:
            self.parts.append(f"]({self._href})")
            self._href = None

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.title += data
        else:
            self.parts.append(data)

    def result(self):
        text = "".join(self.parts)
        text = re.sub(r"[ \t\r\f\v]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


# ------------------------------------------------------------
# Keamanan dasar: IP privat + robots.txt
# ------------------------------------------------------------

def check_host(host):
    """Return pesan error kalau host tidak boleh diakses, atau None kalau aman."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return f"host tidak bisa di-resolve: {host}"

    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return "diblokir: URL mengarah ke alamat privat/lokal"
    return None


_robots = {}


def robots_allows(url, timeout):
    p = urlparse(url)
    origin = f"{p.scheme}://{p.netloc}"

    rp = _robots.get(origin)
    if rp is None:
        rp = robotparser.RobotFileParser()
        try:
            r = requests.get(origin + "/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=timeout)
            if r.status_code == 200:
                rp.parse(r.text.splitlines())
            elif r.status_code >= 500:
                rp.disallow_all = True      # RFC 9309: 5xx = anggap dilarang
            else:
                rp.allow_all = True         # 4xx = tidak ada aturan
        except requests.RequestException:
            rp.allow_all = True
        _robots[origin] = rp

    return rp.can_fetch(ROBOTS_TOKEN, url)


# ------------------------------------------------------------
# Fetch
# ------------------------------------------------------------

def fetch(url, timeout):
    """Return (final_url, response). Raise RuntimeError kalau gagal."""
    current = url

    for _ in range(MAX_REDIRECTS + 1):
        parsed = urlparse(current)

        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise RuntimeError("URL harus diawali http:// atau https://")

        problem = check_host(parsed.hostname)
        if problem:
            raise RuntimeError(problem)

        if not robots_allows(current, timeout):
            raise RuntimeError(f"robots.txt melarang pengambilan URL ini: {current}")

        try:
            resp = requests.get(
                current,
                headers={"User-Agent": USER_AGENT,
                         "Accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.5"},
                timeout=timeout, stream=True, allow_redirects=False,
            )
        except requests.RequestException as error:
            raise RuntimeError(str(error))

        location = resp.headers.get("Location")
        if resp.status_code in (301, 302, 303, 307, 308) and location:
            resp.close()
            current = urljoin(current, location)
            continue

        return current, resp

    raise RuntimeError("terlalu banyak redirect")


def read_body(resp):
    chunks, size = [], 0
    try:
        for chunk in resp.iter_content(65536):
            chunks.append(chunk)
            size += len(chunk)
            if size >= MAX_BYTES:
                break
    finally:
        resp.close()
    return b"".join(chunks)


def decode(raw, content_type):
    m = re.search(r"charset=([\w\-]+)", content_type or "", flags=re.I)
    if m:
        try:
            return raw.decode(m.group(1), errors="replace")
        except LookupError:
            pass
    return raw.decode("utf-8", errors="replace")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Ambil isi satu URL.")
    ap.add_argument("url")
    ap.add_argument("-f", "--format", choices=["markdown", "text", "html"], default="markdown")
    ap.add_argument("--max-chars", type=int, default=6000, help="batas karakter output (0 = tanpa batas)")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    try:
        final_url, resp = fetch(args.url.strip(), args.timeout)
    except RuntimeError as error:
        print(f"ERROR: {error}")
        return 1

    if resp.status_code >= 400:
        resp.close()
        print(f"ERROR: HTTP {resp.status_code} {resp.reason} untuk {final_url}")
        return 1

    content_type_header = resp.headers.get("Content-Type", "")
    content_type = content_type_header.split(";")[0].strip().lower()
    raw = read_body(resp)
    body = decode(raw, content_type_header)

    title = ""
    is_html = content_type in ("text/html", "application/xhtml+xml", "")

    if is_html and args.format != "html":
        conv = Converter(final_url, markdown=(args.format == "markdown"))
        conv.feed(body)
        text, title = conv.result(), " ".join(conv.title.split())
    elif is_html or content_type.startswith("text/") or content_type.endswith(("json", "xml")):
        text = body.strip()
    else:
        print(f"ERROR: tipe konten tidak didukung: {content_type} ({len(raw)} bytes)")
        return 1

    if args.max_chars and len(text) > args.max_chars:
        text = text[:args.max_chars] + f"\n\n[dipotong di {args.max_chars} karakter]"

    print(f"URL: {final_url}")
    print(f"Status: {resp.status_code} | Type: {content_type or 'unknown'}")
    if title:
        print(f"Title: {title}")
    print()
    print(text or "(tidak ada teks yang bisa dibaca)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
