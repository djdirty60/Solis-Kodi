# Solis Dashboard voor Kodi

Kodi-add-on voor de Homey-app **Solis voor Homey**. Toont je zonnepanelen op de tv, in drie varianten:

1. **Beeld uit de Homey-app (standaard)**: de Solis-app op je Homey tekent het dashboard zelf als afbeelding, in dezelfde stijl als op de Mac. Geen computer nodig. Vereist Solis voor Homey **3.35.0 of nieuwer**.
2. **Beeld van de beeldserver**: het echte webdashboard als beeld, pixel voor pixel. Hiervoor draait op een computer die aan blijft de **Solis beeldserver** (map `beeld-server`).
3. **Ingebouwde pagina's**: 7 eigen Kodi-pagina's. Vereist Solis voor Homey **3.34.0 of nieuwer**.

Gemaakt door Wilfried van der Voort.

## Stappen
1. Installeer Solis voor Homey 3.35.0 of nieuwer op je Homey.
2. Installeer de add-on in Kodi (hieronder).
3. Zet bij de instellingen van de add-on het adres van je Homey (poort 8765).
4. Start de add-on. Links en rechts wisselt van pagina, Terug sluit af.

## Installeren op CoreELEC / Kodi (met automatische updates)
Je installeert één keer de **Solis Repository**. Daarna haalt Kodi de add-on zelf op en werkt hem vanzelf bij.

1. Download `repository.solis-1.0.0.zip` uit deze repository en pak hem **niet** uit.
2. Zet het bestand op je CoreELEC, bijvoorbeeld via Finder: **Ga → Verbind met server** → `smb://coreelec` → map **Userdata**.
3. Zet in Kodi **Instellingen → Systeem → Add-ons → Onbekende bronnen** aan.
4. Kies **Add-ons → Installeren vanuit zip-bestand → Home-map → Userdata** en kies `repository.solis-1.0.0.zip`.
5. Kies **Add-ons → Installeren vanuit repository → Solis Repository → Programma-add-ons → Solis Dashboard → Installeren**.
6. Ga naar **Add-ons → Programma-add-ons → Solis Dashboard → Configureren**.

Updates komen daarna vanzelf. Wil je meteen kijken of er een nieuwe versie is? Ga naar **Add-ons**, open het menu en kies **Controleer op updates** (of ga naar Instellingen, Add-ons, Automatisch bijwerken).

Op een Fire TV of Android-apparaat kun je het bestand ook ophalen met de app **Downloader**:
`https://github.com/djdirty60/Solis-Kodi/raw/main/repository.solis-1.0.0.zip`

## Instellingen
- **Weergave**: echt dashboard als beeld of ingebouwde pagina's.
- **Adres en poort van de beeldserver** (voor het beeld).
- **Adres en poort van het dashboard** (alleen voor de ingebouwde pagina's; poort 8765).
- **Verversen** in seconden, **automatisch wisselen** (0 = uit), **startpagina**.

## Veiligheid
Het dashboard en de beeldserver hebben geen wachtwoord. Zet geen poorten open op internet; gebruik alles op je eigen netwerk.

## Een nieuwe versie uitbrengen (voor de maker)
1. Verhoog het versienummer in `script.solis.dashboard/addon.xml` en voeg een regel toe in `changelog.txt`.
2. Draai `python3 tools/make_repo.py`.
3. Commit en push, inclusief de map `repo`. Binnen ongeveer een uur ziet Kodi de update, meestal sneller.

De beeldserver (map `beeld-server`) wordt niet door Kodi bijgewerkt. Die draait op je computer; vervang daar de bestanden als er een nieuwe versie is.
