# -*- coding: utf-8 -*-
"""Lampje van het kastje (LED) als verkeerslicht, voor CoreELEC en andere Linux-boxen.

Zonder Kodi-imports, dus te testen met een nagemaakte /sys/class/leds. Niets in deze module
gooit een fout naar buiten: ontbrekende LED's, geen schrijfrechten en rare bestanden worden
stil overgeslagen.
"""
import os

DEFAULT_ROOT = '/sys/class/leds'
RGB_COLORS = {'groen': (0, 255, 0), 'oranje': (255, 120, 0), 'rood': (255, 0, 0)}
COLOR_WORDS = (('red', 'red'), ('green', 'green'), ('blue', 'blue'), ('white', 'white'),
               ('yellow', 'yellow'), ('amber', 'amber'), ('orange', 'orange'))
NIGHT_FROM, NIGHT_TO = 23, 7


def _read(path):
    try:
        with open(path, 'r') as fh:
            return fh.read().strip()
    except Exception:  # noqa: BLE001
        return None


def _write(path, value):
    try:
        with open(path, 'w') as fh:
            fh.write(str(value))
        return True
    except Exception:  # noqa: BLE001
        return False


def color_of(name):
    """Kleurnaam afgeleid uit de naam van de LED (bijvoorbeeld 'blue:heartbeat' geeft 'blue')."""
    low = (name or '').lower()
    for word, color in COLOR_WORDS:
        if word in low:
            return color
    return 'onbekend'


def parse_triggers(text):
    """('none [heartbeat] timer' geeft (['none', 'heartbeat', 'timer'], 'heartbeat'))."""
    names, active = [], None
    for tok in (text or '').split():
        if tok.startswith('[') and tok.endswith(']'):
            tok = tok[1:-1]
            active = tok
        names.append(tok)
    return names, active


def list_leds(root=DEFAULT_ROOT):
    """Alle LED's: [{name, max, color, triggers (aantal), trigger_names, trigger}]."""
    out = []
    try:
        names = sorted(os.listdir(root))
    except Exception:  # noqa: BLE001
        return out
    for name in names:
        base = os.path.join(root, name)
        if not os.path.isdir(base):
            continue
        mx = _read(os.path.join(base, 'max_brightness'))
        try:
            mx = int(mx)
        except (TypeError, ValueError):
            mx = 1
        tnames, active = parse_triggers(_read(os.path.join(base, 'trigger')))
        out.append({'name': name, 'max': mx, 'color': color_of(name), 'triggers': len(tnames),
                    'trigger_names': tnames, 'trigger': active})
    return out


def describe(leds):
    """Leesbare regels voor de dialoog en het logboek."""
    return ['%s   max %d   kleur: %s   triggers: %d' % (l['name'], l['max'], l['color'], l['triggers']) for l in leds]


def resolve(name, leds):
    """Zoekt de LED bij een ingevulde naam: exact, anders de enige LED waar de naam in voorkomt."""
    want = (name or '').strip().lower()
    if not want:
        return None
    for l in leds:
        if l['name'].lower() == want:
            return l['name']
    part = [l['name'] for l in leds if want in l['name'].lower()]
    return part[0] if len(part) == 1 else None


def is_night(hour, enabled=True):
    return bool(enabled) and (hour >= NIGHT_FROM or hour < NIGHT_TO)


def _scaled(max_value, pct, factor=255):
    value = int(round(max_value * (max(1, min(100, pct)) / 100.0) * factor / 255.0))
    return max(1, value) if factor > 0 else 0


def light_name(data):
    """'groen', 'oranje' of 'rood' volgens het verkeerslicht in /data; anders None."""
    light = data.get('light') if isinstance(data, dict) else None
    name = str(light.get('color') or '').lower() if isinstance(light, dict) else ''
    return name if name in ('groen', 'oranje', 'rood') else None


def plan(color, cfg):
    """Wat er per LED moet gebeuren: {ledname: {'value': int, 'trigger': 'none'|'heartbeat'|'timer'}}.

    cfg: mode, brightness (1-100), leds (lijst uit list_leds) en de namen led_red, led_green,
    led_yellow, led_r, led_g, led_b, led_single.
    """
    mode = (cfg.get('mode') or 'uit').lower()
    leds = cfg.get('leds') or []
    by = dict((l['name'], l) for l in leds)
    pct = cfg.get('brightness', 50)
    res = {}
    if mode == 'uit':
        return res

    def off(n):
        if n:
            res[n] = {'value': 0, 'trigger': 'none'}

    def on(n, factor=255):
        if n:
            res[n] = {'value': _scaled(by[n]['max'], pct, factor), 'trigger': 'none'}

    if mode == 'drie':
        names = {'rood': resolve(cfg.get('led_red'), leds), 'groen': resolve(cfg.get('led_green'), leds),
                 'oranje': resolve(cfg.get('led_yellow'), leds)}
        for c, n in names.items():
            if n:
                off(n)
        if color in names and names[color]:
            on(names[color])
    elif mode == 'rgb':
        chans = [resolve(cfg.get('led_r'), leds), resolve(cfg.get('led_g'), leds), resolve(cfg.get('led_b'), leds)]
        rgb = RGB_COLORS.get(color, (0, 0, 0))
        for n, f in zip(chans, rgb):
            if n:
                if f > 0:
                    on(n, f)
                else:
                    off(n)
    elif mode == 'een':
        n = resolve(cfg.get('led_single'), leds)
        if n:
            trig = by[n]['trigger_names']
            if color == 'groen':
                on(n)
            elif color == 'oranje':
                t = 'heartbeat' if 'heartbeat' in trig else ('timer' if 'timer' in trig else None)
                if t:
                    res[n] = {'value': _scaled(by[n]['max'], pct), 'trigger': t}
                else:
                    on(n, 128)   # zonder knipper-trigger: half licht
            elif color == 'rood':
                t = 'timer' if 'timer' in trig else ('heartbeat' if 'heartbeat' in trig else None)
                if t:
                    res[n] = {'value': _scaled(by[n]['max'], pct), 'trigger': t}
                else:
                    off(n)
            else:
                off(n)
    return res


def apply(the_plan, root=DEFAULT_ROOT, saved=None):
    """Schrijft het plan naar de LED's. `saved` onthoudt de oorspronkelijke trigger en helderheid."""
    saved = saved if saved is not None else {}
    for name, what in the_plan.items():
        try:
            base = os.path.join(root, name)
            if name not in saved:
                tnames, active = parse_triggers(_read(os.path.join(base, 'trigger')))
                try:
                    old_b = int(_read(os.path.join(base, 'brightness')))
                except (TypeError, ValueError):
                    old_b = None
                saved[name] = {'trigger': active, 'brightness': old_b}
            _write(os.path.join(base, 'trigger'), what['trigger'])
            _write(os.path.join(base, 'brightness'), what['value'])
        except Exception:  # noqa: BLE001
            pass
    return saved


def restore(saved, root=DEFAULT_ROOT):
    """Zet de LED's terug zoals ze waren (trigger en helderheid)."""
    for name, old in list((saved or {}).items()):
        try:
            base = os.path.join(root, name)
            if old.get('trigger'):
                _write(os.path.join(base, 'trigger'), old['trigger'])
            if old.get('brightness') is not None:
                _write(os.path.join(base, 'brightness'), old['brightness'])
        except Exception:  # noqa: BLE001
            pass
    if isinstance(saved, dict):
        saved.clear()


class LedController(object):
    """Elke ronde: licht uit /data lezen en de LED's goed zetten. Alles komt van buiten (testbaar)."""

    def __init__(self, fetch, get_cfg, root=DEFAULT_ROOT, hour=None):
        self.fetch, self.get_cfg, self.root = fetch, get_cfg, root
        self.hour = hour or (lambda: __import__('datetime').datetime.now().hour)
        self.saved = {}
        self.last = None

    def tick(self):
        try:
            cfg = dict(self.get_cfg())
            mode = (cfg.get('mode') or 'uit').lower()
            if mode == 'uit':
                self.stop()
                return None
            cfg['leds'] = list_leds(self.root)
            color = None
            try:
                color = light_name(self.fetch())
            except Exception:  # noqa: BLE001
                color = None
            if is_night(self.hour(), cfg.get('night_off', True)):
                color = None
            the_plan = plan(color, cfg)
            key = repr(sorted(the_plan.items()))
            if key != self.last:
                self.last = key
                apply(the_plan, self.root, self.saved)
            return color
        except Exception:  # noqa: BLE001
            return None

    def stop(self):
        try:
            restore(self.saved, self.root)
        except Exception:  # noqa: BLE001
            pass
        self.last = None
