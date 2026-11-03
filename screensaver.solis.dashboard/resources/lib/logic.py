# -*- coding: utf-8 -*-
"""Rekenwerk voor de schermbeveiliging. Geen Kodi nodig, dus te testen."""
import os

DEFAULT_PAGES = ['stroom', 'zon', 'meer', 'verbruik']
DIM_ON = '0x66FFFFFF'
DIM_OFF = '0xFFFFFFFF'


def pick_pages(setting, available=None):
    """Zet 'stroom, zon,verbruik' om naar een lijst. Onbekende pagina's vallen weg."""
    wanted = [p.strip().lower() for p in (setting or '').split(',') if p.strip()]
    if available:
        wanted = [p for p in wanted if p in available]
        if not wanted:
            wanted = [p for p in DEFAULT_PAGES if p in available] or list(available)
    return wanted or list(DEFAULT_PAGES)


def is_night(hour, start=23, end=6):
    return hour >= start or hour < end


def dim_color(hour, enabled=True):
    return DIM_ON if enabled and is_night(hour) else DIM_OFF


def image_path(tmp, number, ext='png'):
    """Elke afbeelding een eigen bestandsnaam: Kodi onthoudt anders de oude."""
    return os.path.join(tmp, 'solis_saver_%d.%s' % (number, ext))


def stale_numbers(current, keep=3):
    """Nummers van afbeeldingen die opgeruimd mogen worden."""
    return list(range(max(0, current - keep - 3), max(0, current - keep) + 1))
