# Solis tv-apps

Twee kleine apps die de tv-pagina's van de Solis-app (Homey) tonen:

- `solis-androidtv/`: Android TV / Google TV (Kotlin). Zie `README-ANDROIDTV.md`.
- `solis-appletv/`: Apple TV (SwiftUI). Zie `README-APPLETV.md`.

Beide halen `/beeld/pages.json` en `/beeld/page/<id>.png` op van het dashboard van de Solis-app (standaard `homey.local:8765`).
Getest: Android TV-app gebouwd en gestart in de Android Studio-emulator; Apple TV-app gebouwd en als .ipa verpakt. Android TV-app draait op een TCL Google TV, Apple TV-app op een Apple TV. Nieuw in deze versies: de vraag op de Kids-pagina beantwoorden met de afstandsbediening (OK, links/rechts, OK).

## Downloads (testversies)

- `downloads/Solis-AndroidTV.apk` (versie 1.2.0, werkt zichzelf bij): installeren met de app Downloader of `adb install`. Installeert over eerdere versies heen (zelfde handtekening). Bouwen op de Mac: `maak-apk.sh`.
- `downloads/Solis-AppleTV-v4.ipa`: **niet getekend**, bedoeld voor een installatiedienst die zelf tekent (bundle id `nl.solisvoorhomey.solis`).
