# Solis tv-apps

Twee kleine apps die de tv-pagina's van de Solis-app (Homey) tonen:

- `solis-androidtv/`: Android TV / Google TV (Kotlin). Zie `README-ANDROIDTV.md`.
- `solis-appletv/`: Apple TV (SwiftUI). Zie `README-APPLETV.md`.

Beide halen `/beeld/pages.json` en `/beeld/page/<id>.png` op van het dashboard van de Solis-app (standaard `homey.local:8765`).
Getest: Android TV-app gebouwd en gestart in de Android Studio-emulator; Apple TV-app gebouwd en als .ipa verpakt. Nog niet op een echte tv geprobeerd.
