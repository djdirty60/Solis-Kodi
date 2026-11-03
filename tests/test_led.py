import os, sys, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE) + '/script.solis.dashboard')
from resources.lib import led
from resources.lib.guard import CrashGuard

root = tempfile.mkdtemp()
def mk(name, mx, trig, br=0):
    d = os.path.join(root, name); os.makedirs(d)
    open(d + '/max_brightness', 'w').write(str(mx))
    open(d + '/trigger', 'w').write(trig)
    open(d + '/brightness', 'w').write(str(br))
def rd(n, f): return open(os.path.join(root, n, f)).read().strip()

mk('red:status', 255, 'none [heartbeat] timer', 7)
mk('green:status', 255, '[none] heartbeat timer')
mk('blue:heartbeat', 1, 'none [heartbeat] timer')
leds = led.list_leds(root)
assert [l['name'] for l in leds] == ['blue:heartbeat', 'green:status', 'red:status']
assert leds[0]['color'] == 'blue' and leds[2]['trigger'] == 'heartbeat'
assert led.list_leds('/nonexistent') == []
assert led.resolve('red', leds) == 'red:status' and led.resolve('x', leds) is None
assert led.light_name({'light': {'color': 'Groen'}}) == 'groen' and led.light_name({}) is None

# drie lampjes
cfg = dict(mode='drie', brightness=100, leds=leds, led_red='red:status', led_green='green:status')
p = led.plan('groen', cfg)
assert p['green:status']['value'] == 255 and p['red:status']['value'] == 0
saved = led.apply(p, root)
assert rd('green:status', 'brightness') == '255' and rd('red:status', 'trigger').startswith('none')
led.restore(saved, root)
assert rd('red:status', 'brightness') == '7' and 'heartbeat' in rd('red:status', 'trigger')

# een lampje: oranje = heartbeat, rood = timer
cfg = dict(mode='een', brightness=50, leds=leds, led_single='blue:heartbeat')
assert led.plan('oranje', cfg)['blue:heartbeat']['trigger'] == 'heartbeat'
assert led.plan('rood', cfg)['blue:heartbeat']['trigger'] == 'timer'
assert led.plan('groen', cfg)['blue:heartbeat']['value'] == 1
assert led.plan(None, cfg)['blue:heartbeat']['value'] == 0
assert led.plan('groen', dict(cfg, mode='uit')) == {}

# nacht
assert led.is_night(23) and led.is_night(3) and not led.is_night(12) and not led.is_night(3, False)

# controller: kleur volgt data, geen data en nacht = uit, stop herstelt
state = {'d': {'light': {'color': 'rood'}}, 'h': 12}
def fetch():
    if state['d'] is None: raise IOError('weg')
    return state['d']
c = led.LedController(fetch, lambda: dict(mode='drie', brightness=100, led_red='red:status', led_green='green:status'),
                      root=root, hour=lambda: state['h'])
assert c.tick() == 'rood' and rd('red:status', 'brightness') == '255' and rd('green:status', 'brightness') == '0'
state['d'] = None
assert c.tick() is None and rd('red:status', 'brightness') == '0'
state['d'] = {'light': {'color': 'groen'}}; state['h'] = 2
assert c.tick() is None and rd('green:status', 'brightness') == '0'
state['h'] = 12; assert c.tick() == 'groen'
c.stop(); assert rd('red:status', 'brightness') == '7'

# crash-guard
flag = os.path.join(root, 'sub', 'edge_started'); t = [1000.0]
g = CrashGuard(flag, clock=lambda: t[0])
assert not g.crashed_before(); g.start()
assert CrashGuard(flag).crashed_before()
t[0] += 30; assert not g.tick() and os.path.exists(flag)
t[0] += 31; assert g.tick() and not os.path.exists(flag)
g.start(); g.clear(); assert not CrashGuard(flag).crashed_before()
# lichtbalk: 15 witte puntjes
bar_root = tempfile.mkdtemp()
for i in range(1, 16):
    d = os.path.join(bar_root, 'led%d' % i); os.makedirs(d)
    open(d + '/max_brightness', 'w').write('255'); open(d + '/brightness', 'w').write('0')
bl = led.list_leds(bar_root)
assert led.bar_leds('led', bl) == ['led%d' % i for i in range(1, 16)]
cfg = dict(mode='balk', brightness=100, leds=bl, led_bar='led')
lit = lambda c: sorted(int(n[3:]) for n, w in led.plan(c, cfg).items() if w['value'] > 0)
assert lit('groen') == list(range(1, 16))
assert lit('oranje') == list(range(5, 12))
assert lit('rood') == [7, 8, 9]
assert lit(None) == []
sv = led.apply(led.plan('rood', cfg), bar_root)
assert open(bar_root + '/led8/brightness').read() == '255' and open(bar_root + '/led1/brightness').read() == '0'
assert led.bar_leds('x', bl) == []
shutil.rmtree(bar_root)
shutil.rmtree(root)
print('test_led OK')
