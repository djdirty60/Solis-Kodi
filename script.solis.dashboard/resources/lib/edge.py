# -*- coding: utf-8 -*-
"""Dunne gekleurde rand om het scherm (verkeerslicht). Geen focus, alleen kijken."""
import os

import xbmcgui

from . import tv


class EdgeWindow(xbmcgui.WindowDialog):
    def __init__(self, media_dir):
        xbmcgui.WindowDialog.__init__(self)
        try:
            self.setCoordinateResolution(0)   # 1920 x 1080
        except Exception:  # noqa: BLE001
            pass
        self.bars = []
        for (x, y, w, h) in tv.edge_rects(8):
            img = xbmcgui.ControlImage(x, y, w, h, os.path.join(media_dir, 'white.png'), colorDiffuse='FF000000')
            self.addControl(img)
            self.bars.append(img)
        self.shown = False

    def onAction(self, action):
        pass   # de rand eet geen toetsen op

    def paint(self, color):
        for b in self.bars:
            b.setColorDiffuse(color)
        if not self.shown:
            self.show()
            self.shown = True

    def clear(self):
        if self.shown:
            self.close()
            self.shown = False


class Edge(object):
    """Houdt één EdgeWindow bij; wordt pas gemaakt als de rand echt nodig is."""

    def __init__(self, addon):
        self.media = os.path.join(addon.getAddonInfo('path'), 'resources', 'skins', 'default', 'media')
        self.win = None

    def show(self, color):
        if self.win is None:
            self.win = EdgeWindow(self.media)
        self.win.paint(color)

    def hide(self):
        if self.win is not None:
            self.win.clear()
