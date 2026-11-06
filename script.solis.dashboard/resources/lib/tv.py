# -*- coding: utf-8 -*-
"""Rekenwerk voor de extra's op de tv (zonder Kodi, dus te testen):
mini-kaart, gekleurde rand, kleurknoppen, dag-terugblik, zoom en grote letters."""
import datetime

SCREEN_W, SCREEN_H = 1920, 1080

# ---------- kleurknoppen ----------
# Kodi: ACTION_TELETEXT_RED=215, GREEN=216, YELLOW=217, BLUE=218
ACTION_RED, ACTION_GREEN, ACTION_YELLOW, ACTION_BLUE = 215, 216, 217, 218
BUTTONS = {ACTION_RED: ('key_red', 'zon'), ACTION_GREEN: ('key_green', 'stroom'),
           ACTION_YELLOW: ('key_yellow', 'dynamisch'), ACTION_BLUE: ('key_blue', 'verbruik')}


def button_page(action_id, get_setting, pages):
    """Index van de pagina waar een kleurknop naartoe springt, of None."""
    if action_id not in BUTTONS:
        return None
    key, default = BUTTONS[action_id]
    wanted = (get_setting(key) or default).strip().lower() or default
    return pages.index(wanted) if wanted in pages else None


# ---------- verkeerslicht-rand ----------
LIGHT_COLORS = {'groen': 'FF1FAE6B', 'oranje': 'FFFF9F1C', 'rood': 'FFE5484D'}


def light_color(data):
    """Kleurcode (AARRGGBB) volgens het verkeerslicht in /data, of None als er geen is."""
    light = data.get('light') if isinstance(data, dict) else None
    name = light.get('color') if isinstance(light, dict) else None
    return LIGHT_COLORS.get(str(name or '').lower())


def edge_rects(thickness=8, w=SCREEN_W, h=SCREEN_H):
    """De vier randen als (x, y, breedte, hoogte): boven, onder, links, rechts."""
    t = max(1, int(thickness))
    return [(0, 0, w, t), (0, h - t, w, t), (0, t, t, h - 2 * t), (w - t, t, t, h - 2 * t)]


class EdgeController(object):
    """Zet de gekleurde rand aan of uit. Alles komt van buiten, zodat het testbaar is."""

    def __init__(self, fetch, show, hide, enabled):
        self.fetch, self.show, self.hide, self.enabled = fetch, show, hide, enabled
        self.current = None

    def tick(self):
        color = None
        if self.enabled():
            try:
                color = light_color(self.fetch())
            except Exception:  # noqa: BLE001
                color = None
        if color == self.current:
            return color
        self.current = color
        if color:
            self.show(color)
        else:
            self.hide()
        return color


# ---------- zoom ----------
ZOOM_FACTOR = 1.6
BIG_TEXT_FACTOR = 1.25
BIG_IMAGE_ZOOM = 1.15


def as_bool(value, default=False):
    if value is None or value == '':
        return default
    return str(value).strip().lower() in ('true', '1', 'yes', 'ja')


def zoom_rect(state, base=1.0, w=SCREEN_W, h=SCREEN_H, factor=ZOOM_FACTOR):
    """Plek en maat (x, y, breedte, hoogte) van de afbeelding.
    state 0 = passen (eventueel iets groter met base), 1 = inzoomen op onderkant, 2 = op bovenkant."""
    if state == 0:
        f = max(1.0, base)
        return (int(round(-(w * f - w) / 2)), int(round(-(h * f - h) / 2)), int(round(w * f)), int(round(h * f)))
    f = max(factor, base)
    x = int(round(-(w * f - w) / 2))
    ww, hh = int(round(w * f)), int(round(h * f))
    return (x, 0 if state == 2 else h - hh, ww, hh)


def step_zoom(state, direction):
    """direction 'up' of 'down'. Vanuit passen: omhoog = bovenkant, omlaag = onderkant."""
    if direction == 'up':
        return {0: 2, 1: 0, 2: 2}.get(state, 0)
    return {0: 1, 2: 0, 1: 1}.get(state, 0)


# ---------- mini-kaart ----------
def _w(v):
    return '–' if v is None else '{:,.0f}'.format(v).replace(',', '.')


def minikaart_lines(lucent):
    """Drie korte regels: zon, huis, net."""
    d = lucent if isinstance(lucent, dict) else {}
    solar = d.get('solar_w')
    house = d.get('house_w')
    grid = d.get('grid_w')
    if grid is None:
        net = 'Net  –'
    elif grid < 0:
        net = 'Terug  %s W' % _w(-grid)
    else:
        net = 'Van het net  %s W' % _w(grid)
    return ['Zon  %s W' % _w(solar), 'Huis  %s W' % _w(house), net]


def run_minikaart(fetch, show_lines, is_closed, sleep, seconds, interval=2.0, clock=None):
    """Ververst elke `interval` seconden en stopt na `seconds` of als het venster dicht is."""
    import time
    clock = clock or time.time
    end = clock() + seconds
    shown = 0
    while not is_closed() and clock() < end:
        try:
            show_lines(minikaart_lines(fetch()))
        except Exception:  # noqa: BLE001
            show_lines(['Zon  –', 'Huis  –', 'Geen verbinding'])
        shown += 1
        sleep(interval)
    return shown


# ---------- dag-terugblik ----------
def _kwh(v):
    return '–' if v is None else ('%.1f' % v).replace('.', ',') + ' kWh'


def day_lines(day):
    """(titel, zes regels, tekst) voor het dag-venster; bij geen gegevens een melding."""
    if not isinstance(day, dict) or day.get('none') or 'kwh' not in day:
        return ('Dag', [], 'Geen gegevens voor deze dag.')
    pct = day.get('selfPct')
    saved = day.get('saved')
    lines = [
        'Opgewekt: ' + _kwh(day.get('kwh')),
        'Verbruik: ' + _kwh(day.get('usageKwh')),
        'Ingekocht: ' + _kwh(day.get('importKwh')),
        'Teruggeleverd: ' + _kwh(day.get('exportKwh')),
        'Eigen gebruik: ' + ('–' if pct is None else '%d %%' % pct),
        'Besparing: ' + ('–' if saved is None else ('€ %.2f' % saved).replace('.', ',')),
    ]
    return (str(day.get('date') or 'Dag'), lines, str(day.get('text') or ''))


def shift_date(date_str, step, today=None):
    """Een dag(en) verder of terug; nooit na vandaag, nooit meer dan een jaar terug."""
    today = today or datetime.date.today()
    try:
        d = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        d = today - datetime.timedelta(days=1)
    d = d + datetime.timedelta(days=step)
    d = min(d, today)
    d = max(d, today - datetime.timedelta(days=366))
    return d.strftime('%Y-%m-%d')


# ---------- grote letters ----------
# Lettertypen uit de skin zelf: Kodi gebruikt geen lettertypen uit een add-on, dus namen die elke skin heeft.
SKIN = {'sd_small': 'font12', 'sd_text': 'font13', 'sd_title': 'font14', 'sd_head': 'font30', 'sd_big': 'font45'}
FONTS = {'sd_small': 'font14', 'sd_text': 'font27', 'sd_title': 'font30',
         'sd_head': 'font37', 'sd_big': 'font52'}


def font_for(name, big):
    """Naam van het lettertype, groter als 'grote letters' aan staat."""
    return FONTS.get(name, name) if big else SKIN.get(name, name)
