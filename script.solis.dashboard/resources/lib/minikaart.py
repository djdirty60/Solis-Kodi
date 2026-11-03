# -*- coding: utf-8 -*-
"""Mini-kaart rechtsonder in beeld, ook tijdens een film (start met RunScript(script.solis.dashboard,minikaart))."""
import os

import xbmc
import xbmcgui

from . import client, tv

ACTIONS_CLOSE = (10, 92, 7, 9, 13)   # terug, menu, OK, ...


class MiniKaart(xbmcgui.WindowDialog):
    def __init__(self, media_dir, big=False):
        xbmcgui.WindowDialog.__init__(self)
        try:
            self.setCoordinateResolution(0)   # 1920 x 1080
        except Exception:  # noqa: BLE001
            pass
        self.closed = False
        k = tv.BIG_TEXT_FACTOR if big else 1.0
        w, h = int(560 * k), int(210 * k)
        x, y = 1920 - w - 50, 1080 - h - 50
        self.addControl(xbmcgui.ControlImage(x, y, w, h, os.path.join(media_dir, 'white.png'), colorDiffuse='E6161B2E'))
        font = 'font14' if big else 'font13'
        self.labels = []
        for i in range(3):
            lab = xbmcgui.ControlLabel(x + 28, y + 18 + i * int(60 * k), w - 56, int(56 * k), '', font=font, textColor='FFF2F4FB')
            self.addControl(lab)
            self.labels.append(lab)

    def onAction(self, action):
        if action.getId() in ACTIONS_CLOSE:
            self.closed = True

    def set_lines(self, lines):
        for lab, text in zip(self.labels, lines):
            lab.setLabel(text)


def run(addon, big=False):
    from .notifier import as_int
    host = addon.getSetting('host') or 'homey.local'
    port = as_int(addon.getSetting('port'), 8765, 1, 65535)
    seconds = as_int(addon.getSetting('mini_seconds'), 8, 3, 60)
    media = os.path.join(addon.getAddonInfo('path'), 'resources', 'skins', 'default', 'media')
    win = MiniKaart(media, big)
    win.show()
    mon = xbmc.Monitor()
    try:
        tv.run_minikaart(lambda: client.fetch_lucent(host, port), win.set_lines,
                         lambda: win.closed or mon.abortRequested(), lambda s: mon.waitForAbort(s), seconds)
    finally:
        win.close()
