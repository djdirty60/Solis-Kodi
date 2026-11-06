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


def base_url(host, port):
    host = (host or '').strip().replace('http://', '').replace('https://', '').strip('/')
    if ':' in host:
        return 'http://%s' % host
    return 'http://%s:%s' % (host, int(port or 8780))


def fetch_pages(host, port, timeout=5, prefix=''):
    """Lijst met pagina's van de beeldserver (of van de Homey-app met prefix /beeld)."""
    with urlopen(base_url(host, port) + prefix + '/pages.json', timeout=timeout) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    pages = [p for p in data.get('pages', []) if isinstance(p, str)]
    if not pages:
        raise ValueError('geen pagina\'s')
    return pages


def download_page(host, port, page, path, timeout=45, prefix='', ext='jpg'):
    """Haalt de afbeelding van een pagina op en schrijft die naar path."""
    with urlopen('%s%s/page/%s.%s' % (base_url(host, port), prefix, page, ext), timeout=timeout) as resp:
        body = resp.read()
    if len(body) < 1000 or not (body[:2] == b'\xff\xd8' or body[:4] == b'\x89PNG'):
        raise ValueError('geen geldige afbeelding')
    with open(path, 'wb') as fh:
        fh.write(body)
    return path


def fetch_notifications(host, port, since=None, timeout=5):
    """Nieuwe meldingen uit de Solis-app op de Homey (/meldingen.json)."""
    url = base_url(host, port) + '/meldingen.json'
    if since is not None:
        url += '?since=%d' % int(since)
    with urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_json(host, port, path, timeout=5):
    """Haalt een JSON-antwoord op van de Solis-app op de Homey."""
    with urlopen(base_url(host, port) + path, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def fetch_data(host, port, timeout=5):
    """Alle gegevens van het dashboard (/data), o.a. het verkeerslicht."""
    return fetch_json(host, port, '/data', timeout)


def fetch_lucent(host, port, timeout=5):
    """Klein overzicht met de belangrijkste cijfers (/lucent.json)."""
    return fetch_json(host, port, '/lucent.json', timeout)


def fetch_day(host, port, date=None, timeout=6):
    """Terugblik op een dag (/dag?datum=JJJJ-MM-DD); zonder datum is het gisteren."""
    path = '/dag' + ('?datum=%s' % date if date else '')
    return fetch_json(host, port, path, timeout)


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
