import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE) + '/script.solis.dashboard')
import mock_homey, kodistubs

srv = mock_homey.start(); port = srv.server_address[1]
S = mock_homey.State
S.items = [{'id': 1, 'title': 'Oud', 'text': '', 'kind': 'info'}]
settings = dict(host='127.0.0.1', port=str(port), notify_enabled='true', notify_seconds='5', notify_quiet='false', notify_warn_only='false')
kodistubs.install(settings, abort_after=60)
import service
service.INTERVAL = 0.01
# de eerste wachttijd (15 s) is ook een waitForAbort; de stub slaapt kort
import threading
threading.Timer(0.1, lambda: S.items.append({'id': 2, 'title': 'Wasmachine klaar', 'text': 'Haal de was eruit', 'kind': 'good'})).start()
service.run()
assert [n[0] for n in kodistubs.NOTES] == ['Wasmachine klaar'], kodistubs.NOTES
n = kodistubs.NOTES[0]
assert n[1] == 'Haal de was eruit' and n[2] == '/icon.png' and n[3] == 5000, n
# uitgezet: niets tonen
kodistubs.NOTES.clear(); settings['notify_enabled'] = 'false'
S.items.append({'id': 3, 'title': 'Uit', 'text': '', 'kind': 'warn'})
kodistubs.install(settings, abort_after=30)
import importlib; importlib.reload(service); service.INTERVAL = 0.01
service.run()
assert kodistubs.NOTES == []
print('service OK')
