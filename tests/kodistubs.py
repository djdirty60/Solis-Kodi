"""Nagemaakte Kodi-modules voor de tests."""
import sys, time, types, tempfile

LOG = []
NOTES = []


class Ctl:
    def __init__(s, i): s.id = i; s.label = ''; s.img = None; s.diffuse = None
    def setLabel(s, l='', **k): s.label = l
    def setImage(s, p, c=True): s.img = (p, c)
    def setColorDiffuse(s, c): s.diffuse = c


def install(settings, abort_after=None):
    xbmc = types.ModuleType('xbmc'); xbmc.LOGWARNING = 2; xbmc.log = lambda m, l=0: LOG.append(m)
    calls = [0]

    class Mon:
        def __init__(s, *a): pass
        def abortRequested(s): return abort_after is not None and calls[0] > abort_after
        def waitForAbort(s, t=0):
            calls[0] += 1
            time.sleep(min(t, 0.02))
            return s.abortRequested()
        def onScreensaverDeactivated(s): pass
    xbmc.Monitor = Mon
    xbmc.Player = lambda: types.SimpleNamespace(isPlayingVideo=lambda: False)
    xbmcgui = types.ModuleType('xbmcgui')

    class WX:
        def __init__(s, *a): s.ctls = {}; s.closed = False
        def getControl(s, i): return s.ctls.setdefault(i, Ctl(i))
        def close(s): s.closed = True
        def doModal(s): pass
    xbmcgui.WindowXML = WX
    xbmcgui.WindowXMLDialog = WX
    xbmcgui.Dialog = lambda: types.SimpleNamespace(notification=lambda *a: NOTES.append(a))
    xbmcvfs = types.ModuleType('xbmcvfs'); tmp = tempfile.mkdtemp() + '/'; xbmcvfs.translatePath = lambda p: tmp
    xbmcaddon = types.ModuleType('xbmcaddon')

    class Addon:
        def getSetting(s, k): return settings.get(k, '')
        def getLocalizedString(s, i): return 'T%d' % i
        def getAddonInfo(s, k): return '/icon.png' if k == 'icon' else '/addon'
    xbmcaddon.Addon = Addon
    sys.modules.update(xbmc=xbmc, xbmcgui=xbmcgui, xbmcvfs=xbmcvfs, xbmcaddon=xbmcaddon)
    return tmp, Addon
