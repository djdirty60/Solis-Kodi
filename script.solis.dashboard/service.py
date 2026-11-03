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
    if monitor.waitForAbort(15):   # even wachten: netwerk komt na het opstarten pas op
        return
    while not monitor.abortRequested():
        notifier.poll()
        if cfg.get('edge') and edge_ctl is None:   # pas maken als de rand echt aan staat
            from resources.lib.edge import Edge
            from resources.lib.tv import EdgeController
            edge = Edge(xbmcaddon.Addon())
            edge_ctl = EdgeController(lambda: client.fetch_data(cfg['host'], cfg['port']), edge.show, edge.hide,
                                      lambda: cfg.get('edge', False))
        if edge_ctl is not None:
            edge_ctl.tick()
        if monitor.waitForAbort(INTERVAL):
            break
    if edge is not None:
        edge.hide()


if __name__ == '__main__':
    run()
