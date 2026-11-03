# -*- coding: utf-8 -*-
"""Startpunt van de Solis-schermbeveiliging."""
import xbmcaddon

from resources.lib.saver import Screensaver


def run():
    addon = xbmcaddon.Addon()
    win = Screensaver('screensaver-solis.xml', addon.getAddonInfo('path'), 'default', '1080i')
    win.addon = addon
    win.doModal()
    del win


if __name__ == '__main__':
    run()
