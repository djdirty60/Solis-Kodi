import json, os, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + '/script.solis.dashboard')
from resources.lib import remote

class St:
    pin_set = True; status = 200; body = {'ok': True, 'text': 'Wasmachine staat klaar.'}; posts = []

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, obj):
        b = json.dumps(obj).encode(); self.send_response(code)
        self.send_header('Content-Type', 'application/json'); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == '/apparaten.json':
            self._send(200, {'pin': St.pin_set, 'items': [{'name': 'Wasmachine', 'armed': True, 'info': 'klaar om 13:00'},
                                                            {'name': 'Droger', 'armed': False, 'info': ''}]})
        else: self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0)); St.posts.append((self.path, self.headers.get('Content-Type'), json.loads(self.rfile.read(n))))
        self._send(St.status, St.body)

srv = HTTPServer(('127.0.0.1', 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

d = remote.fetch_devices('127.0.0.1', port)
assert d['pin'] and [remote.label(i) for i in d['items']] == ['Wasmachine (staat klaar, klaar om 13:00)', 'Droger']
St.pin_set = False
assert remote.fetch_devices('127.0.0.1', port)['pin'] is False       # pin=false
St.pin_set = True

ok, t = remote.arm('127.0.0.1', port, 'Wasmachine', 'klaar', '1234')
assert ok and t == 'Wasmachine staat klaar.'
assert St.posts[-1] == ('/arm', 'application/json', {'apparaat': 'Wasmachine', 'actie': 'klaar', 'pin': '1234'})
St.status, St.body = 403, {'ok': False, 'error': 'pin'}
assert remote.arm('127.0.0.1', port, 'Wasmachine', 'klaar', '0') == (False, 'Foute pincode')
for code in (423, 429):
    St.status, St.body = code, {'ok': False, 'error': 'wacht', 'seconds': 300}
    assert remote.arm('127.0.0.1', port, 'Wasmachine', 'klaar', '0') == (False, 'Even wachten, te veel foute pogingen')
St.status, St.body = 404, {'ok': False, 'error': 'onbekend apparaat'}
assert remote.arm('127.0.0.1', port, 'X', 'klaar', '1') == (False, 'onbekend apparaat')
St.status, St.body = 400, {}
assert remote.arm('127.0.0.1', port, 'X', 'klaar', '1')[0] is False
srv.shutdown(); srv.server_close()
assert remote.arm('127.0.0.1', port, 'W', 'klaar', '1') == (False, 'Geen verbinding')
try:
    remote.fetch_devices('127.0.0.1', port, timeout=1); assert False
except AssertionError: raise
except Exception: pass
print('test_remote OK')
