# -*- coding: utf-8 -*-
"""Haalt dashboardafbeeldingen op uit de Solis-app op de Homey."""
import json

try:
    from urllib.request import urlopen
except ImportError:  # pragma: no cover
    from urllib2 import urlopen


def base_url(host, port):
    host = (host or '').strip().replace('http://', '').replace('https://', '').strip('/')
    if ':' in host:
        return 'http://%s' % host
    return 'http://%s:%s' % (host, int(port or 8765))


def fetch_pages(host, port, timeout=5):
    with urlopen(base_url(host, port) + '/beeld/pages.json', timeout=timeout) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    pages = [p for p in data.get('pages', []) if isinstance(p, str)]
    if not pages:
        raise ValueError('geen pagina\'s')
    return pages


def download_page(host, port, page, path, timeout=45):
    with urlopen('%s/beeld/page/%s.png' % (base_url(host, port), page), timeout=timeout) as resp:
        body = resp.read()
    if len(body) < 1000 or body[:4] != b'\x89PNG':
        raise ValueError('geen geldige afbeelding')
    with open(path, 'wb') as fh:
        fh.write(body)
    return path


def why(exc):
    """Korte, begrijpelijke reden van een mislukte opvraag (voor in beeld)."""
    try:
        code = getattr(exc, 'code', None)
        if code:
            body = ''
            try:
                body = exc.read().decode('utf-8', 'replace').strip()[:120]
            except Exception:  # noqa: BLE001
                pass
            return 'Homey gaf fout %s%s' % (code, (': ' + body) if body else '')
        reason = getattr(exc, 'reason', None) or exc
        txt = str(reason)
        if 'timed out' in txt or 'timeout' in txt.lower():
            return 'Homey reageert te traag (time-out)'
        if 'refused' in txt.lower():
            return 'Homey weigert de verbinding (draait de Solis-app?)'
        if 'Name or service not known' in txt or 'nodename' in txt or 'resolve' in txt.lower():
            return 'adres niet gevonden'
        return txt[:120]
    except Exception:  # noqa: BLE001
        return 'onbekende fout'
