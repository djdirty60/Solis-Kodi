# Solis Dashboard voor Kodi

Kodi-add-on die het dashboard van de Homey-app **Solis voor Homey** toont op je tv: opwek nu, vandaag, jaar, uurprijzen, slimme tips, plan en instellingen.

Gemaakt door Wilfried van der Voort.

## Wat heb je nodig
- Homey Pro met de app *Solis voor Homey* **versie 3.34.0 of nieuwer** (die levert `/kodi.json`).
- Kodi 19 of nieuwer (gemaakt voor Kodi 22) op een apparaat in hetzelfde netwerk als je Homey.
- Het IP-adres van je Homey en de poort van het dashboard (standaard `8765`).

## Installeren op een Fire TV
1. Installeer de app **Downloader** op de Fire TV.
2. Open Downloader en voer het adres van de zip in: `https://github.com/djdirty60/Solis-Kodi/raw/main/script.solis.dashboard-1.0.0.zip`
3. Laat het bestand downloaden en kies *Annuleren* of *Verwijderen* bij de vraag over installeren; het is geen app.
4. Open Kodi, ga naar *Add-ons*, kies *Installeren vanuit zip-bestand* en kies het bestand in de map Downloads.
5. Open *Add-ons → Programma-add-ons → Solis Dashboard → Configureren* en vul het IP-adres van je Homey in.
6. Start de add-on. Links en rechts wisselt van pagina, Terug sluit af.

## Installeren op een computer
Zet het zip-bestand op je computer, open in Kodi *Add-ons → Installeren vanuit zip-bestand* en kies het bestand.

## Instellingen
- **Adres en poort** van het dashboard.
- **Verversen**: elke hoeveel seconden de gegevens worden opgehaald.
- **Automatisch wisselen**: laat de pagina's vanzelf doorlopen (0 = uit).
- **Startpagina**: 0 = Nu, 1 = Overzicht, 2 = Prijzen, 3 = Slim, 4 = Verbruik, 5 = Plan, 6 = Opties.

## Hoe werkt het
De add-on haalt elke paar seconden `http://<homey>:8765/kodi.json` op. Alle berekeningen doet de Homey-app. De add-on tekent alleen. Het is alleen-lezen: er kan niets worden aangepast.

## Veiligheid
Het dashboard heeft geen wachtwoord. Zet de poort dus niet open op internet; gebruik het alleen op je eigen netwerk.
