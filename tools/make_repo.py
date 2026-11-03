#!/usr/bin/env python3
"""Bouwt de Kodi-repository: repo/addons.xml, repo/addons.xml.md5 en de zip-bestanden.

Gebruik na elke wijziging (en na het ophogen van het versienummer in addon.xml):
    python3 tools/make_repo.py
Commit daarna de map repo en push. Kodi ziet de nieuwe versie vanzelf.
"""
import hashlib
import os
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDONS = ['repository.solis', 'script.solis.dashboard', 'screensaver.solis.dashboard']
OUT = os.path.join(ROOT, 'repo')
SKIP_DIRS = {'__pycache__', '.git'}


def build():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, 'zips'))
    parts = []
    for aid in ADDONS:
        src = os.path.join(ROOT, aid)
        xml_path = os.path.join(src, 'addon.xml')
        root = ET.parse(xml_path).getroot()
        if root.get('id') != aid:
            sys.exit('id in %s klopt niet' % xml_path)
        version = root.get('version')
        dest = os.path.join(OUT, 'zips', aid)
        os.makedirs(dest)
        zpath = os.path.join(dest, '%s-%s.zip' % (aid, version))
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for base, dirs, files in os.walk(src):
                dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
                for f in sorted(files):
                    full = os.path.join(base, f)
                    z.write(full, os.path.join(aid, os.path.relpath(full, src)))
        for extra in ('icon.png', 'fanart.jpg'):
            if os.path.exists(os.path.join(src, extra)):
                shutil.copy(os.path.join(src, extra), os.path.join(dest, extra))
        text = open(xml_path, encoding='utf-8').read()
        parts.append(re.sub(r'^<\?xml[^>]*\?>\s*', '', text).strip())
        print('%s %s' % (aid, version))
    xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n' + '\n'.join(parts) + '\n</addons>\n'
    with open(os.path.join(OUT, 'addons.xml'), 'w', encoding='utf-8') as fh:
        fh.write(xml)
    with open(os.path.join(OUT, 'addons.xml.md5'), 'w') as fh:
        fh.write(hashlib.md5(xml.encode('utf-8')).hexdigest())
    # losse repository-zip in de hoofdmap, om één keer te installeren
    repo_zip = [f for f in os.listdir(os.path.join(OUT, 'zips', 'repository.solis')) if f.endswith('.zip')][0]
    for old in [f for f in os.listdir(ROOT) if f.startswith('repository.solis-') and f.endswith('.zip')]:
        os.remove(os.path.join(ROOT, old))
    shutil.copy(os.path.join(OUT, 'zips', 'repository.solis', repo_zip), os.path.join(ROOT, repo_zip))


if __name__ == '__main__':
    build()
