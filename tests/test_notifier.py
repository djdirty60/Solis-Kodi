import os, sys, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT + '/script.solis.dashboard')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mock_homey
from resources.lib.notifier import Notifier, as_bool, as_int
from resources.lib import client

srv = mock_homey.start()
port = srv.server_address[1]
S = mock_homey.State
shown, logs = [], []
cfg = dict(enabled=True, seconds=8, quiet=False, warn_only=False)
playing = [False]
clock = [1000.0]
n = Notifier(lambda since: client.fetch_notifications('127.0.0.1', port, since),
             lambda t, x, k, s: shown.append((t, x, k, s)), lambda: cfg,
             playing=lambda: playing[0], log=logs.append, clock=lambda: clock[0])

def item(i, kind='info', title='T', text='x'):
    return {'id': i, 'at': 0, 'title': title, 'text': text, 'kind': kind}

# 1. eerste poll: oude meldingen NIET tonen
S.items = [item(1), item(2, 'warn', 'Oud')]
assert n.poll() == 0 and shown == [] and n.last == 2
assert '/meldingen.json' in S.hits[0] and 'since' not in S.hits[0]
# 2. alleen nieuwe, oplopend
S.items += [item(3, 'good', 'Negatieve prijs', 'Start de vaatwasser'), item(4, 'info', 'Wasmachine klaar')]
assert n.poll() == 2
assert [s[0] for s in shown] == ['Negatieve prijs', 'Wasmachine klaar'] and shown[0][3] == 8
assert 'since=2' in S.hits[-1]
assert n.poll() == 0 and len(shown) == 2          # niets dubbel
# 3. ongeldig: geen kind of lege titel wordt overgeslagen maar id schuift op
S.items += [item(5, None, 'Zonder kind'), item(6, 'info', ''), item(7, 'bogus', 'Onbekend'), item(8, 'warn', 'Echt')]
assert n.poll() == 1 and shown[-1][0] == 'Echt' and n.last == 8
# 4. alleen waarschuwingen
cfg['warn_only'] = True
S.items += [item(9, 'info', 'Info'), item(10, 'good', 'Goed'), item(11, 'warn', 'Let op')]
assert n.poll() == 2 and [s[0] for s in shown[-2:]] == ['Goed', 'Let op']
cfg['warn_only'] = False
# 5. niet tijdens video (alleen als ingesteld)
S.items.append(item(12, 'info', 'Tijdens film'))
playing[0] = True
assert n.poll() == 1 and shown[-1][0] == 'Tijdens film'      # quiet uit: wel tonen
cfg['quiet'] = True
S.items.append(item(13, 'info', 'Stil'))
assert n.poll() == 0 and shown[-1][0] == 'Tijdens film' and n.last == 13
cfg['quiet'] = False; playing[0] = False
# 6. fout: geen crash, maximaal een logregel per 10 min
S.down = True
for _ in range(5):
    assert n.poll() == 0
assert len(logs) == 1, logs
clock[0] += 601
n.poll(); assert len(logs) == 2
S.down = False
S.items.append(item(14, 'info', 'Na storing'))
assert n.poll() == 1 and shown[-1][0] == 'Na storing'
# 7. server opnieuw begonnen (ids kleiner): alleen onthouden
S.items = [item(1, 'info', 'Nieuw begin')]
assert n.poll() == 0 and n.last == 1
S.items.append(item(2, 'info', 'Daarna'))
assert n.poll() == 1 and shown[-1][0] == 'Daarna'
# 8. uitgezet: niets, en bij weer aanzetten geen oude meldingen
cfg['enabled'] = False
S.items.append(item(3, 'warn', 'Terwijl uit'))
count = len(shown); assert n.poll() == 0 and len(shown) == count
cfg['enabled'] = True
assert n.poll() == 0 and len(shown) == count and n.last == 3
# 9. rommel van de server
bad = Notifier(lambda s: ['nee'], lambda *a: shown.append(a), lambda: cfg, log=logs.append)
assert bad.poll() == 0
assert as_bool('true') and not as_bool('false') and as_bool('', True) and as_int('x', 8) == 8 and as_int('99', 8, 3, 30) == 30
print('notifier OK')
