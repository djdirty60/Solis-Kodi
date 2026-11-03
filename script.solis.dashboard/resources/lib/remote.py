# -*- coding: utf-8 -*-
"""Apparaten klaarzetten vanaf de tv (zonder Kodi-imports, dus testbaar)."""
import json
import urllib.error
import urllib.request

from .client import base_url

TEXT_PIN = 'Foute pincode'
TEXT_WAIT = 'Even wachten, te veel foute pogingen'
TEXT_OFFLINE = 'Geen verbinding'
TEXT_NO_PIN = 'Stel eerst een pincode in bij de Solis-app (Instellingen, Dashboard)'


def fetch_devices(host, port, timeout=6):
    """Geeft {'pin': bool, 'items': [...]}. Gooit een uitzondering bij geen verbinding."""
    with urllib.request.urlopen(base_url(host, port) + '/apparaten.json', timeout=timeout) as r:
        data = json.loads(r.read().decode('utf-8'))
    items = [i for i in (data.get('items') or []) if isinstance(i, dict) and i.get('name')]
    return {'pin': bool(data.get('pin')), 'items': items}


def label(item):
    """Tekst in het keuzemenu: 'Wasmachine' of 'Wasmachine (staat klaar, klaar om 13:00)'."""
    if not item.get('armed'):
        return item['name']
    info = (item.get('info') or '').strip()
    return '%s (staat klaar%s)' % (item['name'], ', ' + info if info else '')


def error_text(status, body):
    """Vertaalt een foutantwoord van de server naar leesbare tekst."""
    err = body.get('error') if isinstance(body, dict) else None
    if status == 403 or err == 'pin':
        return TEXT_PIN
    if status in (423, 429) or err == 'wacht':
        return TEXT_WAIT
    return str(err) if err and err not in ('pin', 'wacht') else 'Mislukt'


def arm(host, port, apparaat, actie, pin, timeout=6):
    """Stuurt de opdracht. Geeft (ok, tekst); de pincode wordt nooit gelogd."""
    req = urllib.request.Request(
        base_url(host, port) + '/arm',
        data=json.dumps({'apparaat': apparaat, 'actie': actie, 'pin': str(pin)}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode('utf-8') or '{}')
            return True, body.get('text') or 'Gelukt'
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode('utf-8') or '{}')
        except Exception:  # noqa: BLE001
            body = {}
        return False, error_text(e.code, body)
    except Exception:  # noqa: BLE001
        return False, TEXT_OFFLINE
