# -*- coding: utf-8 -*-
"""Solis Dashboard voor Kodi: startpunt van de add-on."""
import sys

import xbmcaddon


def run():
    addon = xbmcaddon.Addon()
    if len(sys.argv) > 1 and sys.argv[1] == 'minikaart':   # RunScript(script.solis.dashboard,minikaart)
        from resources.lib import minikaart, tv
        minikaart.run(addon, tv.as_bool(addon.getSetting('big_text'), False))
        return
    path = addon.getAddonInfo('path')
    if (addon.getSetting('mode') or '2') == '1':
        from resources.lib.window import SolisWindow
        win = SolisWindow('script-solis-dashboard.xml', path, 'default', '1080i')
    else:
        from resources.lib.imagewindow import SolisImageWindow
        win = SolisImageWindow('script-solis-image.xml', path, 'default', '1080i')
    win.addon = addon
    win.doModal()
    del win


if __name__ == '__main__':
    run()
