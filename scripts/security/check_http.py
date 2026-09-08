"""Comprobacion HTTP real de S-04/S-05/E-06; solo usa la biblioteca estandar.

Uso: python scripts/security/check_http.py --base-url http://localhost:8081
No autentica, no modifica datos y no imprime cuerpos ni cabeceras sensibles.
"""

import argparse
import re
import sys
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8081")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    failures = []

    def request(path, *, method="GET", headers=None):
        req = urllib.request.Request(base + path, method=method, headers=headers or {})
        try:
            response = urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def check(condition, label):
        if not condition:
            failures.append(label)

    status, _, body = request("/")
    check(status == 200, "HTML publico disponible")
    asset = re.search(rb'(?:src|href)="(/assets/[^\"]+\.js)"', body)
    paths = [
        ("/", False), ("/articulos", False), ("/admin", True),
        ("/admin/login?prueba=018", True), ("/admin/inexistente", True),
        ("/administer", False), ("/api/v1/posts", True),
        ("/api/v1/admin/auth/me", True), ("/api/v1/inexistente", True),
        ("/sitemap.xml", False), ("/robots.txt", False), ("/favicon.svg", False),
        ("/health", True), ("/ready", True),
    ]
    check(asset is not None, "HTML referencia bundle real")
    if asset:
        paths.append((asset[1].decode("ascii"), False))
    for path, noindex in paths:
        status, headers, _ = request(path)
        check(headers.get("X-Content-Type-Options") == "nosniff", f"nosniff {path}")
        check(headers.get("X-Frame-Options") == "DENY", f"antiframe {path}")
        check(headers.get("Referrer-Policy") == "no-referrer", f"referrer {path}")
        check(bool(headers.get("Permissions-Policy")), f"permisos {path}")
        csp = headers.get("Content-Security-Policy", "")
        check("frame-ancestors 'none'" in csp, f"CSP {path}")
        check("unsafe-inline" not in csp and "unsafe-eval" not in csp, f"CSP sin bypass {path}")
        check(("noindex" in headers.get("X-Robots-Tag", "")) == noindex, f"indexacion {path}")
        if base.startswith("http:"):
            check(not headers.get("Strict-Transport-Security"), f"sin HSTS en HTTP {path}")
        if path.startswith("/api/v1/admin/") or path.startswith("/admin/") or path == "/admin":
            check(headers.get("Cache-Control") == "no-store", f"no-store {path}")
        print(f"HTTP {status} {path}: inspeccionado")

    for origin, expected in [(base, True), ("https://ajeno.example.test", False)]:
        status, headers, _ = request("/api/v1/admin/auth/login", method="OPTIONS", headers={
            "Origin": origin, "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-request-id",
        })
        check((headers.get("Access-Control-Allow-Origin") == origin) == expected, "CORS origen")
        check(status == (200 if expected else 400), "CORS estado preflight")
        check(bool(headers.get("X-Request-ID")), "CORS correlacion")
        check("*" not in headers.get("Access-Control-Allow-Methods", ""), "CORS metodos")
    for failure in failures:
        print(f"FAIL: {failure}")
    print(f"FALLOS={len(failures)}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
