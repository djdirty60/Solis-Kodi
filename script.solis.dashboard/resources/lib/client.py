# -*- coding: utf-8 -*-
"""Haalt de pagina's op bij het dashboard van Solis voor Homey."""
import json

try:
    from urllib.request import urlopen
except ImportError:  # pragma: no cover
    from urllib2 import urlopen


def url_for(host, port):
    host = (host or '').strip().replace('http://', '').replace('https://', '').strip('/')
    if ':' in host:
        return 'http://%s/kodi.json' % host
    return 'http://%s:%s/kodi.json' % (host, int(port or 8765))


def fetch(host, port, timeout=6):
    with urlopen(url_for(host, port), timeout=timeout) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    if not isinstance(data, dict) or not data.get('pages'):
        raise ValueError('onverwacht antwoord')
    return data
