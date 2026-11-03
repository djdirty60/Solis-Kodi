# -*- coding: utf-8 -*-
"""Achtergrondservice: toont meldingen van Solis voor Homey als Kodi-melding op de tv."""
import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import client
from resources.lib.notifier import Notifier, as_bool, as_int

INTERVAL = 30  # seconden tussen twee ronden


def read_settings():
    a = xbmcaddon.Addon()
    return {
        'enabled': as_bool(a.getSetting('notify_enabled'), True),
        'seconds': as_int(a.getSetting('notify_seconds'), 8, 3, 30),
        'quiet': as_bool(a.getSetting('notify_quiet'), False),
        'warn_only': as_bool(a.getSetting('notify_warn_only'), False),
        'host': a.getSetting('host') or 'homey.local',
        'port': as_int(a.getSetting('port'), 8765, 1, 65535),
        'icon': a.getAddonInfo('icon'),
        'edge': as_bool(a.getSetting('edge_light'), False),
        'led': {
            'mode': a.getSetting('led_mode') or 'uit',
            'brightness': as_int(a.getSetting('led_brightness'), 50, 5, 100),
            'night_off': as_bool(a.getSetting('led_night_off'), True),
            'led_red': a.getSetting('led_red'), 'led_green': a.getSetting('led_green'),
            'led_yellow': a.getSetting('led_yellow'), 'led_r': a.getSetting('led_r'),
            'led_g': a.getSetting('led_g'), 'led_b': a.getSetting('led_b'),
            'led_single': a.getSetting('led_single'),
        },
    }


def run():
    monitor = xbmc.Monitor()
    player = xbmc.Player()
    cfg = {}

    def settings():
        cfg.update(read_settings())
        return cfg

    def fetch(since):
        return client.fetch_notifications(cfg['host'], cfg['port'], since)

    def show(title, text, kind, seconds):
        xbmcgui.Dialog().notification(title, text, cfg['icon'], int(seconds) * 1000, False)

    notifier = Notifier(fetch, show, settings, playing=lambda: player.isPlayingVideo(),
                        log=lambda t: xbmc.log(t, xbmc.LOGWARNING))
    edge = None
    edge_ctl = None
    edge_dead = False
    guard = None
    try:
        import xbmcvfs
        from resources.lib.guard import CrashGuard
        folder = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
        guard = CrashGuard(folder.rstrip('/\\') + '/edge_started')
        if guard.crashed_before():       # vorige keer vastgelopen: rand blijft uit
            edge_dead = True
            xbmc.log('Solis: kleurrand staat uit omdat Kodi eerder vastliep', xbmc.LOGWARNING)
    except Exception as exc:  # noqa: BLE001
        xbmc.log('Solis: crash-guard niet beschikbaar: %s' % exc, xbmc.LOGWARNING)
    from resources.lib.led import LedController
    leds = LedController(lambda: client.fetch_data(cfg['host'], cfg['port']), lambda: cfg.get('led') or {})
    if monitor.waitForAbort(15):   # even wachten: netwerk komt na het opstarten pas op
        return
    while not monitor.abortRequested():
        notifier.poll()
        try:
            leds.tick()
        except Exception as exc:  # noqa: BLE001
            xbmc.log('Solis: lampje: %s' % exc, xbmc.LOGWARNING)
        if cfg.get('edge') and not edge_dead and edge_ctl is None:   # pas maken als de rand echt aan staat
            try:
                from resources.lib.edge import Edge
                from resources.lib.tv import EdgeController
                if guard is not None:
                    guard.start()
                edge = Edge(xbmcaddon.Addon())
                edge_ctl = EdgeController(lambda: client.fetch_data(cfg['host'], cfg['port']), edge.show, edge.hide,
                                          lambda: cfg.get('edge', False))
            except Exception as exc:  # noqa: BLE001
                edge_dead = True
                xbmc.log('Solis: kleurrand mislukt: %s' % exc, xbmc.LOGWARNING)
        if edge_ctl is not None:
            try:
                edge_ctl.tick()
                if guard is not None:
                    guard.tick()
            except Exception as exc:  # noqa: BLE001
                edge_dead = True
                edge_ctl = None
                xbmc.log('Solis: kleurrand uitgezet na fout: %s' % exc, xbmc.LOGWARNING)
        if monitor.waitForAbort(INTERVAL):
            break
    leds.stop()
    if edge is not None:
        try:
            edge.hide()
        except Exception:  # noqa: BLE001
            pass
    if guard is not None:
        guard.clear()   # nette afsluiting: geen crash


if __name__ == '__main__':
    run()
