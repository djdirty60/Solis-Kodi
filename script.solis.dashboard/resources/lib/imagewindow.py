# -*- coding: utf-8 -*-
"""Toont het echte dashboard als beeld, geleverd door de Solis beeldserver."""
import os
import threading
import time

import xbmc
import xbmcgui
import xbmcvfs

from . import client, remote, tv

ACTION_MOVE_LEFT = 1
ACTION_MOVE_RIGHT = 2
ACTION_MOVE_UP = 3
ACTION_MOVE_DOWN = 4
ACTION_SELECT_ITEM = 7
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
ACTION_NAV_BACK = 92

DEFAULT_PAGES = ['zon', 'stroom', 'meer', 'inzicht', 'overzicht', 'dynamisch', 'verbruik', 'slim', 'instel']
NAMES = {'zon': 'Zon', 'stroom': 'Stroom', 'meer': 'Details', 'inzicht': 'Inzicht', 'overzicht': 'Overzicht',
         'dynamisch': 'Dynamisch', 'verbruik': 'Verbruik', 'slim': 'Slim', 'instel': 'Opties'}


class SolisImageWindow(xbmcgui.WindowXML):
    addon = None
    pages = None
    index = 0
    _stop = False

    def onInit(self):
        s = self.addon
        self._lock = threading.RLock()
        self._stop = False
        self._flip = 0
        self._want = True        # er moet een nieuwe afbeelding komen
        self._hint_until = 0.0
        self.big = tv.as_bool(self._opt('big_text'), False)
        self.zoom = 0            # 0 = passen, 1 = onderkant groot, 2 = bovenkant groot
        self.day = None          # datum als het dag-venster open is
        self.homey = (s.getSetting('mode') or '2') == '2'
        if self.homey:   # beeld rechtstreeks uit de Homey-app
            self.host = s.getSetting('host') or 'homey.local'
            self.port = int(s.getSetting('port') or 8765)
            self.prefix, self.ext = '/beeld', 'png'
        else:            # beeld van de beeldserver op een computer
            self.host = s.getSetting('render_host')
            self.port = int(s.getSetting('render_port') or 8780)
            self.prefix, self.ext = '', 'jpg'
        self.refresh = max(3, int(s.getSetting('refresh') or 10))
        self.rotate = max(0, int(s.getSetting('rotate') or 0))
        self.pages = list(DEFAULT_PAGES)
        self.index = min(max(0, int(s.getSetting('startpage') or 0)), len(self.pages) - 1)
        self._tmp = xbmcvfs.translatePath('special://temp/')
        self._set(14, '' if self.host else s.getLocalizedString(30012))
        self._show_day_group(False)
        self._apply_zoom()
        threading.Thread(target=self._loop, daemon=True).start()

    def onAction(self, action):
        aid = action.getId()
        if self.day is not None:      # dag-terugblik is open
            if aid in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_SHOW_INFO):
                self.day = None
                self._show_day_group(False)
            elif aid == ACTION_MOVE_LEFT:
                self._open_day(-1)
            elif aid == ACTION_MOVE_RIGHT:
                self._open_day(1)
            return
        if aid in (ACTION_PREVIOUS_MENU, ACTION_NAV_BACK):
            self._stop = True
            self.close()
        elif aid == ACTION_MOVE_RIGHT:
            self._go(1)
        elif aid == ACTION_MOVE_LEFT:
            self._go(-1)
        elif aid == ACTION_MOVE_UP:
            self.zoom = tv.step_zoom(self.zoom, 'up')
            self._apply_zoom()
        elif aid == ACTION_MOVE_DOWN:
            self.zoom = tv.step_zoom(self.zoom, 'down')
            self._apply_zoom()
        elif aid == ACTION_SHOW_INFO and self.host:
            self._open_day(None)
        elif aid in tv.BUTTONS:
            nr = tv.button_page(aid, self._opt, self.pages)
            if nr is not None:
                with self._lock:
                    self.index = nr
                    self._want = True
                    self._last_rotate = time.time()
        elif aid == ACTION_SELECT_ITEM and self.host:
            threading.Thread(target=self._apparaten, daemon=True).start()

    # ---------- zoom ----------
    def _apply_zoom(self):
        base = tv.BIG_IMAGE_ZOOM if (self.big and self.homey) else 1.0
        x, y, w, h = tv.zoom_rect(self.zoom, base)
        try:
            ctl = self.getControl(20)
            ctl.setPosition(x, y)
            ctl.setWidth(w)
            ctl.setHeight(h)
        except Exception:  # noqa: BLE001
            pass

    # ---------- dag-terugblik ----------
    def _show_day_group(self, visible):
        try:
            self.getControl(30).setVisible(bool(visible))
        except Exception:  # noqa: BLE001
            pass

    def _open_day(self, step):
        """step None = openen (gisteren); -1/1 = een dag terug/verder."""
        if step is None:
            date = tv.shift_date(None, 0)
        else:
            date = tv.shift_date(self.day, step)
        self.day = date
        self._set(31, date, tv.font_for('sd_head', self.big))
        threading.Thread(target=self._load_day, args=(date,), daemon=True).start()
        self._show_day_group(True)

    def _load_day(self, date):
        try:
            title, lines, text = tv.day_lines(client.fetch_day(self.host, self.port, date))
        except Exception:  # noqa: BLE001
            title, lines, text = date, [], self.addon.getLocalizedString(30012)
        if self.day != date:
            return   # intussen een andere dag gekozen
        self._set(31, date, tv.font_for('sd_head', self.big))
        for i in range(6):
            self._set(32 + i, lines[i] if i < len(lines) else '', tv.font_for('sd_title', self.big))
        try:
            self.getControl(38).setText(text)
        except Exception:  # noqa: BLE001
            pass

    def _opt(self, key):
        """Instelling lezen; een ontbrekende instelling geeft '' (dan geldt de standaardwaarde)."""
        try:
            return self.addon.getSetting(key)
        except Exception:  # noqa: BLE001
            return ''

    def _apparaten(self):
        """OK-knop: menu om apparaten klaar te zetten (met pincode)."""
        if getattr(self, '_busy', False):
            return
        self._busy = True
        try:
            dlg = xbmcgui.Dialog()
            try:
                data = remote.fetch_devices(self.host, self.port)
            except Exception:  # noqa: BLE001
                dlg.notification('Solis', remote.TEXT_OFFLINE)
                return
            if not data['pin']:
                dlg.ok('Solis', remote.TEXT_NO_PIN)
                return
            items = data['items']
            if not items:
                return
            nr = dlg.select('Apparaten', [remote.label(i) for i in items])
            if nr < 0:
                return
            item = items[nr]
            actie = 'klaar'
            if item.get('armed'):
                if not dlg.yesno('Solis', 'Annuleren?'):
                    return
                actie = 'annuleer'
            pin = self.addon.getSetting('pin') or ''
            if not pin:
                pin = dlg.input('PIN', type=xbmcgui.INPUT_NUMERIC, option=xbmcgui.ALPHANUM_HIDE_INPUT)
                if not pin:
                    return
            ok, text = remote.arm(self.host, self.port, item['name'], actie, pin)
            dlg.notification('Solis', text, xbmcgui.NOTIFICATION_INFO if ok else xbmcgui.NOTIFICATION_WARNING, 6000)
        finally:
            self._busy = False

    def _go(self, step):
        with self._lock:
            self.index = (self.index + step) % len(self.pages)
            self._want = True
            self._last_rotate = time.time()

    def _set(self, cid, text, font=None):
        try:
            if font:
                self.getControl(cid).setLabel(text, font=font)
            else:
                self.getControl(cid).setLabel(text)
        except Exception:  # noqa: BLE001
            pass

    def _opruimen(self, nr):
        """Verwijdert oude tijdelijke afbeeldingen."""
        for n in range(max(0, nr - 2), nr + 1):
            try:
                os.remove(os.path.join(self._tmp, 'solis_beeld_%d.%s' % (n, self.ext)))
            except OSError:
                pass

    def _page_title(self):
        p = self.pages[self.index]
        return '%s  (%d/%d)' % (NAMES.get(p, p), self.index + 1, len(self.pages))

    def _loop(self):
        monitor = xbmc.Monitor()
        last = 0.0
        self._last_rotate = time.time()
        listed = False
        while not self._stop and not monitor.abortRequested():
            now = time.time()
            if self.host and not listed:
                try:
                    pages = client.fetch_pages(self.host, self.port, prefix=self.prefix)
                    with self._lock:
                        self.pages = pages
                        self.index = min(self.index, len(pages) - 1)
                    listed = True
                except Exception as exc:  # noqa: BLE001
                    xbmc.log('Solis dashboard: paginalijst mislukt bij %s:%s: %s' % (self.host, self.port, client.why(exc)), xbmc.LOGWARNING)
            if self.rotate and now - self._last_rotate >= self.rotate:
                self._go(1)
            if self.host and (self._want or now - last >= self.refresh):
                with self._lock:
                    page = self.pages[self.index]
                    self._want = False
                last = now
                self._flip += 1   # elke afbeelding een eigen bestandsnaam: Kodi onthoudt anders de oude
                path = os.path.join(self._tmp, 'solis_beeld_%d.%s' % (self._flip, self.ext))
                try:
                    client.download_page(self.host, self.port, page, path, prefix=self.prefix, ext=self.ext)
                    with self._lock:
                        still = page == self.pages[self.index]
                    if still:
                        self.getControl(20).setImage(path, False)
                        self._opruimen(self._flip - 3)
                    self._set(14, '')
                except Exception as exc:  # noqa: BLE001
                    reden = client.why(exc)
                    xbmc.log('Solis dashboard: beeld ophalen mislukt bij %s:%s: %s' % (self.host, self.port, reden), xbmc.LOGWARNING)
                    self._set(14, 'Geen beeld van %s:%s\n%s' % (self.host, self.port, reden))
                    if not getattr(self, '_told', False):
                        self._told = True
                        try:
                            xbmcgui.Dialog().notification('Solis', '%s:%s - %s' % (self.host, self.port, reden), self.addon.getAddonInfo('icon'), 10000)
                        except Exception:  # noqa: BLE001
                            pass
                self._hint_until = max(self._hint_until, now + 3) if self._hint_until == 0 else now + 3
                self._set(13, self._page_title() + '   ' + self.addon.getLocalizedString(30070), tv.font_for('sd_text', self.big))
            if self._hint_until and now > self._hint_until:
                self._hint_until = 0
                self._set(13, '')
            if monitor.waitForAbort(0.5):
                break
