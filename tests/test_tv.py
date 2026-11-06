import datetime, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE) + '/script.solis.dashboard')
from resources.lib import tv

PAGES = ['zon', 'stroom', 'meer', 'inzicht', 'overzicht', 'dynamisch', 'verbruik', 'slim', 'instel']

# kleurknoppen: standaard en eigen keuze
S = {}
get = lambda k: S.get(k, '')
assert tv.button_page(215, get, PAGES) == 0 and tv.button_page(216, get, PAGES) == 1
assert tv.button_page(217, get, PAGES) == 5 and tv.button_page(218, get, PAGES) == 6
S['key_red'] = 'slim'; assert tv.button_page(215, get, PAGES) == 7
S['key_red'] = 'bestaatniet'; assert tv.button_page(215, get, PAGES) is None
assert tv.button_page(1, get, PAGES) is None

# verkeerslicht-rand
assert tv.light_color({'light': {'color': 'groen'}}) == 'FF1FAE6B'
assert tv.light_color({'light': {'color': 'ROOD'}}) == 'FFE5484D'
assert tv.light_color({'light': {}}) is None and tv.light_color({}) is None and tv.light_color(None) is None
r = tv.edge_rects(8)
assert len(r) == 4 and r[0] == (0, 0, 1920, 8) and r[1] == (0, 1072, 1920, 8)

ev = []; state = {'on': True, 'data': {'light': {'color': 'groen'}}}
def fetch():
    if state['data'] is None: raise IOError('weg')
    return state['data']
c = tv.EdgeController(fetch, lambda col: ev.append(('show', col)), lambda: ev.append('hide'), lambda: state['on'])
c.tick(); c.tick()                                   # tweede keer niets nieuws
assert ev == [('show', 'FF1FAE6B')], ev
state['data'] = {'light': {'color': 'rood'}}; c.tick()
assert ev[-1] == ('show', 'FFE5484D')
state['data'] = None; c.tick()                       # geen verbinding: rand weg
assert ev[-1] == 'hide'
state['data'] = {'light': {'color': 'oranje'}}; c.tick(); state['on'] = False; c.tick()
assert ev[-1] == 'hide' and c.current is None

# zoom
assert tv.zoom_rect(0) == (0, 0, 1920, 1080)
x, y, w, h = tv.zoom_rect(0, 1.15)
assert w == 2208 and h == 1242 and x == -144 and y == -81
x, y, w, h = tv.zoom_rect(2); assert y == 0 and w == 3072 and x == -576
x, y, w, h = tv.zoom_rect(1); assert y == 1080 - 1728 and y + h == 1080
assert tv.step_zoom(0, 'up') == 2 and tv.step_zoom(0, 'down') == 1
assert tv.step_zoom(2, 'down') == 0 and tv.step_zoom(1, 'up') == 0
assert tv.step_zoom(2, 'up') == 2 and tv.step_zoom(1, 'down') == 1

# mini-kaart
assert tv.minikaart_lines({'solar_w': 1234, 'house_w': 457, 'grid_w': -300}) == ['Zon  1.234 W', 'Huis  457 W', 'Terug  300 W']
assert tv.minikaart_lines({'solar_w': 0, 'house_w': 157, 'grid_w': 157})[2] == 'Van het net  157 W'
assert tv.minikaart_lines({})[0] == 'Zon  – W' and tv.minikaart_lines({})[2] == 'Net  –'
t = [0.0]; shown = []
n = tv.run_minikaart(lambda: {'solar_w': 5, 'house_w': 6, 'grid_w': 1}, shown.append, lambda: False,
                     lambda s: t.__setitem__(0, t[0] + s), 8, 2.0, clock=lambda: t[0])
assert n == 4 and len(shown) == 4                    # 8 s met elke 2 s verversen
closed = [False]; t[0] = 0.0; shown.clear()
def sl(s): t[0] += s; closed[0] = t[0] >= 4
assert tv.run_minikaart(lambda: {}, shown.append, lambda: closed[0], sl, 60, 2.0, clock=lambda: t[0]) == 2
shown.clear(); t[0] = 0.0
def boom(): raise IOError('x')
tv.run_minikaart(boom, shown.append, lambda: False, lambda s: t.__setitem__(0, t[0] + 10), 5, clock=lambda: t[0])
assert shown == [['Zon  –', 'Huis  –', 'Geen verbinding']]

# dag-terugblik
day = {'date': '2026-11-02', 'kwh': 1.8, 'usageKwh': 6.25, 'importKwh': 4.5, 'exportKwh': 0.12, 'selfPct': 93, 'saved': 0.41, 'text': 'Gisteren: 1,8 kWh opgewekt.'}
title, lines, text = tv.day_lines(day)
assert title == '2026-11-02' and len(lines) == 6 and lines[0] == 'Opgewekt: 1,8 kWh' and lines[4] == 'Eigen gebruik: 93 %' and lines[5] == 'Besparing: € 0,41'
assert text.startswith('Gisteren')
assert tv.day_lines({'none': True})[1] == [] and 'Geen gegevens' in tv.day_lines({'none': True})[2]
assert tv.day_lines(None)[1] == []
assert tv.day_lines({'date': 'x', 'kwh': 1, 'usageKwh': None, 'importKwh': None, 'exportKwh': 0, 'selfPct': None, 'saved': None})[1][1] == 'Verbruik: –'
today = datetime.date(2026, 11, 3)
assert tv.shift_date(None, 0, today) == '2026-11-02'
assert tv.shift_date('2026-11-02', -1, today) == '2026-11-01'
assert tv.shift_date('2026-11-02', 1, today) == '2026-11-03' and tv.shift_date('2026-11-03', 1, today) == '2026-11-03'
assert tv.shift_date('2024-01-01', -1, today) == '2025-11-02'

# grote letters
assert tv.font_for('sd_text', False) == 'font13' and tv.font_for('sd_text', True) == 'font27'
assert tv.font_for('onbekend', True) == 'onbekend'
assert tv.as_bool('true') and not tv.as_bool('false') and tv.as_bool('', True)
print('tv OK')
