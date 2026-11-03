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


def download_page(host, port, page, path, timeout=20):
    with urlopen('%s/beeld/page/%s.png' % (base_url(host, port), page), timeout=timeout) as resp:
        body = resp.read()
    if len(body) < 1000 or body[:4] != b'\x89PNG':
        raise ValueError('geen geldige afbeelding')
    with open(path, 'wb') as fh:
        fh.write(body)
    return path
