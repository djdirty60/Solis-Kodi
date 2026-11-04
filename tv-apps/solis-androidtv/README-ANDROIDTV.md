# Solis voor Android TV

Een kleine app voor je Android TV of Google TV (zoals je TCL). Hij laat dezelfde pagina's zien als de Kodi-add-on: Zon, Stroom, Details, Inzicht, Overzicht, Dynamisch, enzovoort. Ook is er een schermbeveiliging die de pagina's laat zien als je niets kijkt.

**Eerlijk vooraf:** deze app is geschreven maar nog **niet gebouwd of op een echte tv geprobeerd**. In mijn werkomgeving is geen Android-gereedschap, dus de eerste keer bouwen kan een foutmelding geven. Plak die dan in de chat, dan los ik het op.

---

## Wat heb je nodig

- Een computer (je Mac) met **Android Studio** (gratis).
- Je tv op hetzelfde netwerk als de Mac en de Homey.
- In de Solis-app op de Homey moet het **dashboard aanstaan**. De standaardpoort is **8765**.
- Staat er een **wachtwoord** op het dashboard? Dan kan deze app de pagina's nog **niet** laden. Laat het wachtwoord voorlopig leeg.

---

## Stap 1: Android Studio installeren

1. Ga naar https://developer.android.com/studio en download Android Studio voor Mac (kies "Apple chip" voor een nieuwe Mac).
2. Open het gedownloade bestand, sleep Android Studio naar Programma's en start het.
3. Kies bij de eerste start gewoon **Standard** en laat alles downloaden. Dat duurt even.

## Stap 2: Het project openen

1. Start Android Studio en kies **Open**.
2. Kies de map `solis-androidtv` (de map waar dit bestand in staat).
3. Wacht tot onderin "Gradle sync" klaar is. De eerste keer downloadt hij onderdelen, dat kan enkele minuten duren.
4. Vraagt Android Studio om een SDK te installeren of een "Gradle plugin" bij te werken? Zeg **ja** bij installeren. Bij bijwerken kun je ook **Niet nu** kiezen.

## Stap 3: De tv klaarmaken

Je moet op de tv "foutopsporing" aanzetten.

1. Tv: **Instellingen → Apparaatvoorkeuren → Over** en druk 7 keer op **Build** (of Buildnummer). Er verschijnt "Je bent nu ontwikkelaar".
2. Ga terug naar **Apparaatvoorkeuren → Ontwikkelaarsopties** en zet **USB-foutopsporing** aan. Als er **Draadloze foutopsporing** staat, zet die ook aan.
3. Zoek het IP-adres van de tv: **Instellingen → Netwerk → je wifi** (bijvoorbeeld `192.168.178.50`).

## Stap 4: De tv koppelen met de Mac

Open Terminal op je Mac en plak (vervang het IP-adres door dat van jouw tv):

```
adb connect 192.168.178.50:5555
```

- Vraagt de tv "USB-foutopsporing toestaan?", kies dan **Altijd toestaan**.
- Werkt dit niet, en heb je **Draadloze foutopsporing** met een koppelcode? Kies dan in Android Studio rechtsboven bij het apparaat-menu **Pair Devices Using Wi-Fi** en volg de stappen, of gebruik `adb pair IP:POORT` met de code die de tv laat zien.
- Kent je Mac `adb` niet? Android Studio zet het hier: `~/Library/Android/sdk/platform-tools/adb`. Plak dan dat hele pad in plaats van `adb`.

## Stap 5: Draaien

1. Kies bovenin Android Studio je tv in het apparaat-menu.
2. Druk op de groene **Run**-knop (driehoek).
3. De app start op de tv. De eerste keer zie je het scherm **Solis - instellingen**.

---

## De app gebruiken

**Eerste keer (instellingen):**
- Druk op **Zoek zelf in mijn netwerk**. De app zoekt de Homey. Dat duurt maximaal een minuut.
- Of vul zelf in: het adres van je Homey (bijvoorbeeld `homey.local` of `192.168.178.20`) en de poort (`8765`).
- Druk op **Test de verbinding**. Er moet staan "Gelukt".
- Wil je dat de app zelf pagina's wisselt? Zet **Automatisch doorbladeren** aan en kies hoeveel seconden per pagina.
- Druk op **Opslaan**.

**Afstandsbediening:**

| Toets | Wat het doet |
|---|---|
| Links / Rechts | Vorige / volgende pagina |
| OK | Pagina nu vernieuwen |
| Omhoog (of Menu) | Instellingen |
| Omlaag | Doorbladeren aan of uit |
| Terug | De app sluiten |

De pagina ververst vanzelf elke 30 seconden. Valt de verbinding weg, dan zie je een duidelijke melding en probeert de app het na ongeveer 10 seconden zelf opnieuw. De app crasht daar niet van.

---

## Schermbeveiliging aanzetten

**Android TV:** Instellingen → Apparaatvoorkeuren → Schermbeveiliging → kies **Solis zonnepanelen**.

**Google TV (zoals veel TCL's):** daar staat de keuze vaak niet in het menu. Plak dan dit in Terminal (met je tv gekoppeld zoals in stap 4):

```
adb shell settings put secure screensaver_components nl.leek.solis.tv/.SolisDream
adb shell settings put secure screensaver_enabled 1
```

Probeer de schermbeveiliging meteen met:

```
adb shell am start -n "com.android.systemui/.Somnambulator"
```

Sommige tv's laten dit niet toe. Dan werkt de gewone app wel, maar de schermbeveiliging niet. Dat kan ik niet vooraf zien.

---

## Zonder Android Studio installeren (APK)

Je kunt van het project een los installatiebestand (APK) maken:

1. In Android Studio: **Build → Build Bundle(s) / APK(s) → Build APK(s)**.
2. Klik rechtsonder op **locate**. Het bestand heet `app-debug.apk` (in `app/build/outputs/apk/debug/`).

Installeren op de tv:

- **Met Terminal:** `adb install -r app-debug.apk` (met de tv gekoppeld zoals in stap 4).
- **Met een USB-stick of de app "Downloader":** zet het bestand ergens neer waar de tv bij kan (of in de Downloader-app via een link) en open het. Zet daarvoor eerst **Onbekende bronnen** aan voor die app. Dat staat bij Instellingen → Apparaatvoorkeuren → Beveiliging en beperkingen.

De app staat daarna in je lijst met apps op de tv, onder de naam **Solis**.

---

## Als het niet lukt

- **"Geen verbinding met de Solis-app":** zit de tv op hetzelfde netwerk als de Homey? Staat het dashboard aan in de Solis-app, en klopt de poort? Open `http://IP-van-de-Homey:8765/beeld/pages.json` in een browser op de Mac. Daar moet tekst met pagina's staan.
- **"Ik kan 'homey.local' niet vinden":** sommige tv's kennen dat adres niet. Gebruik het IP-adres van je Homey, of druk op **Zoek zelf**.
- **Zwart beeld met melding:** lees de melding, die zegt wat er mis is.
- **Android Studio geeft een rode foutmelding:** plak de tekst in de chat.

## Wat er in het project zit

- `app/src/main/java/nl/leek/solis/tv/MainActivity.kt`: het gewone scherm.
- `SolisViewer.kt`: toont de pagina's, ververst, bladert en toont meldingen.
- `SettingsActivity.kt`: het instelscherm met "Zoek zelf" en "Test".
- `SolisDream.kt`: de schermbeveiliging.
- `Net.kt`: het ophalen van pagina's en het zoeken in het netwerk.
- `Store.kt`: onthoudt je instellingen.

Er worden geen extra bibliotheken gebruikt. Alles is gewoon Android zelf. Er komen alleen aanvragen naar het adres dat je zelf invult.

## Niet getest

Alles hierboven is nog niet op een echte tv geprobeerd, ook niet in een emulator: bouwen, het zoeken in je netwerk, de afstandsbediening-toetsen en de schermbeveiliging. Het gedrag bij een weggevallen verbinding is wel doorgelopen in de code, maar niet uitgeprobeerd.
