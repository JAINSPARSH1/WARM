# WARM/core/tls_whois.py
"""
tls_whois.py — Gather TLS cert info, DNS A records, and WHOIS metadata
"""

import ssl
import socket
import hashlib
import datetime
from urllib.parse import urlparse
import whois
import tldextract

# optional dnspython dependency
try:
    import dns.resolver
except ImportError:
    dns = None

def get_tls_info(hostname: str) -> dict:
    """
    Connects to <hostname>:443, retrieves CERT and TLS version.
    Returns: issuer CN, valid_from/date, valid_until/date,
             days_left, protocol version, fingerprint (SHA256).
    """
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(5)
            s.connect((hostname, 443))
            cert_bin = s.getpeercert(binary_form=True)
            cert    = s.getpeercert()
            proto   = s.version()
        # parse validity strings to datetime
        nb = datetime.datetime.strptime(
            cert["notBefore"], "%b %d %H:%M:%S %Y %Z"
        ).replace(tzinfo=datetime.timezone.utc)
        na = datetime.datetime.strptime(
            cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
        ).replace(tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        days_left = (na - now).days
        # SHA256 fingerprint of raw DER
        fp_sha256 = hashlib.sha256(cert_bin).hexdigest().upper()
        issuer_cn = dict(x[0] for x in cert["issuer"])["commonName"]
        return {
            "tls_issuer": issuer_cn,
            "tls_valid_from": nb.date(),
            "tls_valid_until": na.date(),
            "tls_days_left": days_left,
            "tls_protocol": proto,
            "tls_fingerprint_sha256": fp_sha256,
        }
    except Exception as e:
        # on error, log and return placeholders
        print(f"[yellow]TLS lookup failed for {hostname}: {e}[/]")
        return {
            "tls_issuer": "ERR",
            "tls_valid_from": None,
            "tls_valid_until": None,
            "tls_days_left": None,
            "tls_protocol": "ERR",
            "tls_fingerprint_sha256": "ERR",
        }

def get_dns_info(hostname: str) -> dict:
    """
    Resolves A records for hostname and retrieves TTL.
    Falls back to socket.gethostbyname_ex if dnspython missing.
    """
    try:
        if dns:
            ans = dns.resolver.resolve(hostname, "A")
            ips = [rdata.to_text() for rdata in ans]
            ttl = ans.rrset.ttl
        else:
            _, _, ips = socket.gethostbyname_ex(hostname)
            ttl = None
        return {
            "dns_ips": ", ".join(ips) if ips else "-",
            "dns_ttl": ttl if ttl is not None else "-",
        }
    except Exception as e:
        print(f"[yellow]DNS lookup failed for {hostname}: {e}[/]")
        return {"dns_ips": "-", "dns_ttl": "-"}

def get_whois_info(domain: str) -> dict:
    """
    Queries WHOIS for the domain.
    Returns: registrar, created_on (with age), expiry_date, days_to_expiry,
             registrant_org, registrant_country.
    """
    try:
        w = whois.whois(domain)
        # creation / expiration may be lists
        created = w.creation_date
        if isinstance(created, list):
            created = created[0]
        expires = w.expiration_date
        if isinstance(expires, list):
            expires = expires[0]
        # compute age and days to expiry
        now = datetime.datetime.now()
        age = (now - created).days // 365 if created else None
        days_to_expiry = (expires - now).days if expires else None
        org     = w.org or w.organization or "-"
        country = w.country or w.c or "-"
        return {
            "whois_registrar": w.registrar or "-",
            "whois_created_on": f"{created.date()} ({age}y)" if created else "-",
            "whois_expiry_date": str(expires.date()) if expires else "-",
            "whois_days_to_expiry": days_to_expiry if days_to_expiry else "-",
            "whois_org": org,
            "whois_country": country,
        }
    except Exception as e:
        print(f"[yellow]WHOIS lookup failed for {domain}: {e}[/]")
        return {
            "whois_registrar": "ERR",
            "whois_created_on": "ERR",
            "whois_expiry_date": "ERR",
            "whois_days_to_expiry": "ERR",
            "whois_org": "ERR",
            "whois_country": "ERR",
        }

def get_tls_whois_dns_summary(url: str) -> dict:
    """
    Parses hostname & registrable domain, then calls the three lookup functions.
    """
    # strip scheme/path → host
    hostname = urlparse(url).netloc.split(":")[0]
    # extract domain for WHOIS
    dom = tldextract.extract(hostname)
    domain = f"{dom.domain}.{dom.suffix}" if dom.suffix else hostname

    out = {}
    out.update(get_tls_info(hostname))
    out.update(get_dns_info(hostname))
    out.update(get_whois_info(domain))
    return out

