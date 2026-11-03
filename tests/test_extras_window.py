import datetime, os, sys, time, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE) + '/script.solis.dashboard')
import mock_homey, kodistubs

srv = mock_homey.start(); port = srv.server_address[1]
S = mock_homey.State
yest = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
S.days = {yest: {'date': yest, 'kwh': 1.8, 'usageKwh': 6.0, 'importKwh': 4.5, 'exportKwh': 0.1, 'selfPct': 94, 'saved': 0.4, 'text': 'ok'}}
settings = dict(mode='2', host='127.0.0.1', port=str(port), refresh='3', rotate='0', startpage='0', big_text='true')
kodistubs.install(settings, abort_after=10 ** 9)
from resources.lib import imagewindow as iw, client

# client-functies tegen de nagebootste Homey
assert client.fetch_lucent('127.0.0.1', port)['solar_w'] == 1200
assert client.fetch_data('127.0.0.1', port)['light']['color'] == 'groen'
assert client.fetch_day('127.0.0.1', port, yest)['kwh'] == 1.8 and client.fetch_day('127.0.0.1', port).get('none')

Act = lambda i: types.SimpleNamespace(getId=lambda: i)
addon = kodistubs.xbmcaddon.Addon() if hasattr(kodistubs, 'xbmcaddon') else sys.modules['xbmcaddon'].Addon()
w = iw.SolisImageWindow('x.xml', '/p', 'default', '1080i')
w.addon = addon
w.onInit()
try:
    time.sleep(0.3)
    assert w.big is True and w.zoom == 0
    c20 = w.getControl(20)
    assert (c20.pos, c20.w, c20.h) == ((-144, -81), 2208, 1242)       # grote letters: standaardzoom 1.15
    w.onAction(Act(3)); assert w.zoom == 2 and c20.pos == (-576, 0) and c20.h == 1728
    w.onAction(Act(4)); assert w.zoom == 0
    w.onAction(Act(4)); assert w.zoom == 1 and c20.pos[1] == 1080 - 1728
    w.onAction(Act(3)); assert w.zoom == 0
    # kleurknoppen
    w.onAction(Act(216)); assert w.index == 1
    w.onAction(Act(218)); assert w.index == 6
    w.onAction(Act(215)); assert w.index == 0
    w.onAction(Act(2)); assert w.index == 1 and w.day is None
    # dag-terugblik
    w.onAction(Act(11)); assert w.day == yest and w.getControl(30).visible is True
    time.sleep(0.5)
    assert w.getControl(32).label == 'Opgewekt: 1,8 kWh', w.getControl(32).label
    assert w.getControl(37).label == 'Besparing: € 0,40'
    d0 = w.day
    w.onAction(Act(1)); assert w.day == (datetime.date.fromisoformat(d0) - datetime.timedelta(days=1)).isoformat()
    time.sleep(0.4)
    assert w.getControl(32).label == '' or w.getControl(32).label.startswith('Opgewekt')   # geen gegevens op die dag
    w.onAction(Act(2)); assert w.day == d0
    idx = w.index
    w.onAction(Act(2)); assert w.day == datetime.date.today().isoformat() and w.index == idx   # links/rechts wisselt geen pagina
    w.onAction(Act(10)); assert w.day is None and w.getControl(30).visible is False and not w.closed
    w.onAction(Act(10)); assert w.closed                                     # Terug sluit pas daarna het venster
    print('extras window OK')
finally:
    w._stop = True
