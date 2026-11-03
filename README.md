# Solis Dashboard voor Kodi

Kodi-add-on voor de Homey-app **Solis voor Homey**. Toont je zonnepanelen op de tv, in twee varianten:

1. **Echt dashboard als beeld (standaard)**: precies hetzelfde als op de Mac of in de browser, alle pagina's. Hiervoor draait op een computer die aan blijft staan de **Solis beeldserver** (map `beeld-server`).
2. **Ingebouwde pagina's**: 7 eigen Kodi-pagina's, zonder extra computer. Vereist Solis voor Homey **3.34.0 of nieuwer**.

Gemaakt door Wilfried van der Voort.

## Stappen
1. Zet de beeldserver aan op je Mac: zie [beeld-server/README.md](beeld-server/README.md).
2. Installeer de add-on in Kodi (hieronder).
3. Vul bij de instellingen van de add-on het adres van je Mac in.
4. Start de add-on. Links en rechts wisselt van pagina, Terug sluit af.

## Installeren op CoreELEC / Kodi
1. Download `script.solis.dashboard-2.0.0.zip` uit deze repository en pak hem **niet** uit.
2. Zet het bestand op je CoreELEC, bijvoorbeeld via Finder: **Ga → Verbind met server** → `smb://coreelec` → map **Userdata**.
3. Zet in Kodi **Instellingen → Systeem → Add-ons → Onbekende bronnen** aan.
4. Kies **Add-ons → Installeren vanuit zip-bestand → Home-map → Userdata** en kies het zip-bestand.
5. Ga naar **Add-ons → Programma-add-ons → Solis Dashboard → Configureren**.

Op een Fire TV of Android-apparaat kun je het bestand ook ophalen met de app **Downloader**:
`https://github.com/djdirty60/Solis-Kodi/raw/main/script.solis.dashboard-2.0.0.zip`

## Instellingen
- **Weergave**: echt dashboard als beeld of ingebouwde pagina's.
- **Adres en poort van de beeldserver** (voor het beeld).
- **Adres en poort van het dashboard** (alleen voor de ingebouwde pagina's; poort 8765).
- **Verversen** in seconden, **automatisch wisselen** (0 = uit), **startpagina**.

## Veiligheid
Het dashboard en de beeldserver hebben geen wachtwoord. Zet geen poorten open op internet; gebruik alles op je eigen netwerk.
