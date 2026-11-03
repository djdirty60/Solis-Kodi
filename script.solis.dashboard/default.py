# -*- coding: utf-8 -*-
"""Solis Dashboard voor Kodi: startpunt van de add-on."""
import xbmcaddon

from resources.lib.window import SolisWindow


def run():
    addon = xbmcaddon.Addon()
    win = SolisWindow('script-solis-dashboard.xml', addon.getAddonInfo('path'), 'default', '1080i')
    win.addon = addon
    win.doModal()
    del win


if __name__ == '__main__':
    run()
