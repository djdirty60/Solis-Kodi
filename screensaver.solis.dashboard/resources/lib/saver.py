# -*- coding: utf-8 -*-
"""De schermbeveiliging: toont de dashboardafbeeldingen uit de Solis-app volledig scherm."""
import os
import threading
import time

import xbmc
import xbmcgui
import xbmcvfs

from . import client, logic

REFRESH = 8        # seconden tussen twee nieuwe afbeeldingen van dezelfde pagina
RETRY = 5          # seconden tussen pogingen als de Homey niet bereikbaar is


class Screensaver(xbmcgui.WindowXMLDialog):
    addon = None
    _stop = False

    class _Exit(xbmc.Monitor):
        def __init__(self, callback):
            xbmc.Monitor.__init__(self)
            self.callback = callback

        def onScreensaverDeactivated(self):
            self.callback()

    def onInit(self):
        s = self.addon
        self._stop = False
        self._exit = self._Exit(self.close_saver)
        self.hosts = self._hosts()
        self.hi = 0
        self.host, self.port = self.hosts[0]
        self._told = False
        try:
            self.seconds = max(5, int(s.getSetting('seconds') or 20))
        except ValueError:
            self.seconds = 20
        self.pages = logic.pick_pages(s.getSetting('pages'))
        self.night = (s.getSetting('night_dim') or 'true').lower() != 'false'
        self.msg_off = s.getLocalizedString(30006)
        self._tmp = xbmcvfs.translatePath('special://temp/')
        self._n = 0
        self.index = 0
        threading.Thread(target=self._loop, daemon=True).start()

    def _hosts(self):
        """Waar de Homey te vinden is. Eigen instelling, en anders die van het Solis Dashboard (daar staat vaak al het IP-adres).
        'homey.local' werkt op CoreELEC vaak niet; dan gaat het IP-adres van het dashboard voor."""
        def port_of(v):
            try:
                return int(v or 8765)
            except ValueError:
                return 8765
        own = ((self.addon.getSetting('host') or '').strip(), port_of(self.addon.getSetting('port')))
        other = ('', 8765)
        try:
            import xbmcaddon
            d = xbmcaddon.Addon('script.solis.dashboard')
            other = ((d.getSetting('host') or '').strip(), port_of(d.getSetting('port')))
        except Exception:  # noqa: BLE001
            pass
        out = []
        weak = lambda h: (not h) or h.lower() == 'homey.local'
        order = [other, own] if weak(own[0]) and not weak(other[0]) else [own, other]
        for h, p in order + [('homey.local', 8765)]:
            if h and (h, p) not in out:
                out.append((h, p))
        return out

    def onAction(self, action):
        self.close_saver()

    def close_saver(self):
        if self._stop:
            return
        self._stop = True
        self._exit = None
        self.close()

    def _set(self, cid, text):
        try:
            self.getControl(cid).setLabel(text)
        except Exception:  # noqa: BLE001
            pass

    def _cleanup(self):
        for nr in logic.stale_numbers(self._n):
            try:
                os.remove(logic.image_path(self._tmp, nr))
            except OSError:
                pass

    def _loop(self):
        monitor = xbmc.Monitor()
        listed = False
        fails = 0
        last_shot = 0.0
        last_flip = time.time()
        while not self._stop and not monitor.abortRequested():
            now = time.time()
            if not listed:
                try:
                    self.pages = logic.pick_pages(self.addon.getSetting('pages'), client.fetch_pages(self.host, self.port))
                    listed = True
                except Exception as exc:  # noqa: BLE001
                    xbmc.log('Solis schermbeveiliging: paginalijst mislukt: %s' % exc, xbmc.LOGWARNING)
            if now - last_flip >= self.seconds:
                self.index = (self.index + 1) % len(self.pages)
                last_flip = now
                last_shot = 0.0
            wait = REFRESH if fails == 0 else RETRY
            if now - last_shot >= wait:
                last_shot = now
                self._n += 1
                path = logic.image_path(self._tmp, self._n)
                try:
                    client.download_page(self.host, self.port, self.pages[self.index % len(self.pages)], path)
                    if not self._stop:
                        ctl = self.getControl(20)
                        ctl.setColorDiffuse(logic.dim_color(time.localtime().tm_hour, self.night))
                        ctl.setImage(path, False)
                    self._set(14, '')
                    fails = 0
                    self._cleanup()
                except Exception as exc:  # noqa: BLE001
                    fails += 1
                    if fails == 1:
                        xbmc.log('Solis schermbeveiliging: beeld ophalen mislukt bij %s:%s: %s' % (self.host, self.port, exc), xbmc.LOGWARNING)
                    if len(self.hosts) > 1:   # volgende adres proberen
                        self.hi = (self.hi + 1) % len(self.hosts)
                        self.host, self.port = self.hosts[self.hi]
                        listed = False
                    if fails == 2 * len(self.hosts) and not self._told:
                        self._told = True
                        try:
                            xbmcgui.Dialog().notification('Solis', 'Homey niet bereikbaar (%s). Vul het IP-adres van je Homey in bij deze schermbeveiliging.' % ', '.join('%s:%s' % hp for hp in self.hosts), self.addon.getAddonInfo('icon'), 8000)
                        except Exception:  # noqa: BLE001
                            pass
                    if fails >= 2:
                        try:
                            self.getControl(20).setImage('', False)
                        except Exception:  # noqa: BLE001
                            pass
                        self._set(14, self.msg_off)
            if monitor.waitForAbort(0.5):
                break
