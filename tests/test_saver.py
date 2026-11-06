import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE) + '/screensaver.solis.dashboard')
import mock_homey, kodistubs

srv = mock_homey.start(); port = srv.server_address[1]
S = mock_homey.State
settings = dict(host='127.0.0.1', port=str(port), seconds='5', pages='stroom, zon ,bestaatniet,verbruik', night_dim='true')
tmp, Addon = kodistubs.install(settings)
from resources.lib import logic
from resources.lib.saver import Screensaver
import resources.lib.saver as saver
saver.REFRESH = 0.3; saver.RETRY = 0.3

# --- logica ---
assert logic.pick_pages('stroom, zon,x', ['zon', 'stroom']) == ['stroom', 'zon']
assert logic.pick_pages('x,y', ['zon', 'stroom', 'meer', 'verbruik']) == ['stroom', 'zon', 'meer', 'verbruik']
assert logic.pick_pages('', None) == logic.DEFAULT_PAGES
assert logic.is_night(23) and logic.is_night(2) and not logic.is_night(6) and not logic.is_night(12)
assert logic.dim_color(1) == logic.DIM_ON and logic.dim_color(1, False) == logic.DIM_OFF and logic.dim_color(12) == logic.DIM_OFF
assert logic.image_path('/t/', 4) != logic.image_path('/t/', 5)

# --- scherm ---
w = Screensaver('x', 'p', 'default', '1080i'); w.addon = Addon(); w.onInit()
for _ in range(100):
    if w.ctls.get(20) and w.ctls[20].img: break
    time.sleep(0.05)
first = w.ctls[20].img
assert first and first[1] is False and open(first[0], 'rb').read(4) == b'\x89PNG', first
assert w.pages == ['stroom', 'zon', 'verbruik'], w.pages          # onbekende pagina valt weg
assert w.ctls[20].diffuse in (logic.DIM_ON, logic.DIM_OFF)
paths = set()
for _ in range(40):
    time.sleep(0.1)
    paths.add(w.ctls[20].img[0])
assert len(paths) >= 4, paths                                    # steeds een nieuw bestand
assert len([f for f in os.listdir(tmp) if f.startswith('solis_saver_')]) <= 8   # oude zijn opgeruimd
assert '/beeld/pages.json' in S.hits[0] or any('pages.json' in h for h in S.hits)
# elke toets sluit af
class Act:
    def getId(s): return 7
w.onAction(Act()); assert w.closed
time.sleep(0.8)
# --- Homey onbereikbaar: rustig bericht, geen crash, herstelt daarna ---
S.down = True
w2 = Screensaver('x', 'p', 'default', '1080i'); w2.addon = Addon(); w2.onInit()
time.sleep(1.8)
assert w2.ctls[14].label.startswith('T30006'), w2.ctls[14].label
assert w2.ctls[20].img is None or w2.ctls[20].img[0] == ''
S.down = False
for _ in range(60):
    if w2.ctls[20].img and w2.ctls[20].img[0].endswith('.png'): break
    time.sleep(0.1)
assert w2.ctls[20].img[0].endswith('.png') and w2.ctls[14].label == ''
w2.close_saver()
# --- ongeldige afbeelding wordt geweigerd ---
S.png_ok = False
w3 = Screensaver('x', 'p', 'default', '1080i'); w3.addon = Addon(); w3.onInit()
time.sleep(1.8)
assert w3.ctls[14].label.startswith('T30006')
w3.close_saver()
print('saver OK')
