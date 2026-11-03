"""Kleine nagebootste Homey-server voor de tests."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

PNG = b'\x89PNG\r\n\x1a\n' + b'x' * 2000


class State:
    items = []          # lijst van meldingen
    png_ok = True
    down = False
    hits = []
    data = {'light': {'color': 'groen', 'reason': 'x'}}
    lucent = {'solar_w': 1200, 'house_w': 900, 'grid_w': -300}
    days = {}           # datum -> antwoord van /dag


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        State.hits.append(self.path)
        if State.down:
            self.send_response(503); self.end_headers(); return
        if u.path == '/meldingen.json':
            since = parse_qs(u.query).get('since')
            items = State.items if not since else [i for i in State.items if i['id'] > int(since[0])]
            body = json.dumps({'now': 0, 'last': max([i['id'] for i in State.items] or [0]), 'items': items}).encode()
            ctype = 'application/json'
        elif u.path == '/data':
            body = json.dumps(State.data).encode(); ctype = 'application/json'
        elif u.path == '/lucent.json':
            body = json.dumps(State.lucent).encode(); ctype = 'application/json'
        elif u.path == '/dag':
            d = parse_qs(u.query).get('datum', ['gisteren'])[0]
            body = json.dumps(State.days.get(d, {'none': True})).encode(); ctype = 'application/json'
        elif u.path == '/beeld/pages.json':
            body = json.dumps({'pages': ['zon', 'stroom', 'meer', 'inzicht', 'overzicht', 'dynamisch', 'verbruik', 'slim', 'instel']}).encode()
            ctype = 'application/json'
        elif u.path.startswith('/beeld/page/') and u.path.endswith('.png'):
            body = PNG if State.png_ok else b'nee'
            ctype = 'image/png'
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.end_headers()
        self.wfile.write(body)


def start(port=0):
    srv = HTTPServer(('127.0.0.1', port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv
