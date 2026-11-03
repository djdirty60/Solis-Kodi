# -*- coding: utf-8 -*-
"""Crash-guard voor onderdelen die Kodi kunnen laten vastlopen (zonder Kodi-imports).

Bij het starten schrijven we een vlagbestand. Na 60 seconden zonder fout, of bij een nette
afsluiting, verwijderen we het. Staat het bestand bij de volgende start nog, dan is Kodi
vastgelopen en gebruiken we het onderdeel niet meer.
"""
import os
import time

OK_AFTER = 60


class CrashGuard(object):
    def __init__(self, path, clock=None):
        self.path = path
        self.clock = clock or time.time
        self.started = None

    def crashed_before(self):
        try:
            return os.path.exists(self.path)
        except Exception:  # noqa: BLE001
            return False

    def start(self):
        try:
            folder = os.path.dirname(self.path)
            if folder and not os.path.isdir(folder):
                os.makedirs(folder)
            with open(self.path, 'w') as fh:
                fh.write(str(int(self.clock())))
        except Exception:  # noqa: BLE001
            pass
        self.started = self.clock()

    def tick(self):
        """Wis het vlagbestand zodra het 60 seconden goed ging. Geeft True als het gewist is."""
        if self.started is not None and self.clock() - self.started >= OK_AFTER:
            self.clear()
            return True
        return False

    def clear(self):
        self.started = None
        try:
            if os.path.exists(self.path):
                os.remove(self.path)
        except Exception:  # noqa: BLE001
            pass
