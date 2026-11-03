import os, sys, threading, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE) + '/script.solis.dashboard')
import mock_homey, kodistubs

srv = mock_homey.start(); port = srv.server_address[1]
S = mock_homey.State
S.items = []
settings = dict(host='127.0.0.1', port=str(port), notify_enabled='true', notify_seconds='5', edge_light='true', mini_seconds='3')
kodistubs.install(settings, abort_after=80)
import service
from resources.lib import edge as edgemod
service.INTERVAL = 0.01
wins = []
orig = edgemod.EdgeWindow.__init__
def spy(self, *a):
    orig(self, *a); wins.append(self)
edgemod.EdgeWindow.__init__ = spy
threading.Timer(0.3, lambda: setattr(S, 'down', True)).start()    # later valt de verbinding weg
service.run()
assert len(wins) == 1, 'een enkele rand, geen nieuwe bij elke ronde'
w = wins[0]
assert len(w.bars) == 4
assert w.bars[0].diffuse == 'FF1FAE6B', w.bars[0].diffuse         # groen
assert w.shown is False and w.closed is True                        # na weggevallen verbinding of afsluiten weg
S.down = False

# rand uit: geen venster
wins.clear(); settings['edge_light'] = 'false'
kodistubs.install(settings, abort_after=20)
import importlib; importlib.reload(service); service.INTERVAL = 0.01
service.run()
assert wins == []

# mini-kaart
kodistubs.install(settings, abort_after=10 ** 9)
from resources.lib import minikaart
addon = sys.modules['xbmcaddon'].Addon()
import resources.lib.tv as tv
shown = []
orig_run = tv.run_minikaart
def fast(fetch, show, closed, sleep, seconds, interval=2.0, clock=None):
    shown.append(seconds)
    return orig_run(fetch, show, closed, lambda s: None, 0.05, 0.01, clock=None)
tv.run_minikaart = fast
captured = []
oc = minikaart.MiniKaart.__init__
def spy2(self, *a, **k):
    oc(self, *a, **k); captured.append(self)
minikaart.MiniKaart.__init__ = spy2
minikaart.run(addon, False)
assert shown == [3]                                               # uit de instelling
m = captured[0]
assert m.labels[0].label == 'Zon  1.200 W' and m.labels[1].label == 'Huis  900 W' and m.labels[2].label == 'Terug  300 W'
assert m.shown is False and m.closed is True                       # na afloop weer dicht
print('edge + mini OK')

# crash-guard: vlagbestand van een vorige vastloper => geen rand
wins.clear(); settings['edge_light'] = 'true'
tmp, _ = kodistubs.install(settings, abort_after=20)
open(tmp + 'edge_started', 'w').write('1')
importlib.reload(service); service.INTERVAL = 0.01
service.run()
assert wins == [], 'na een vastloper blijft de rand uit'
print('edge guard OK')
