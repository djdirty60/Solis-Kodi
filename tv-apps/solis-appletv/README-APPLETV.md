# Solis voor Apple TV

Een kleine Apple TV-app die de pagina's van je Solis-app (dezelfde plaatjes als in Kodi) schermvullend op de tv toont.

**Eerlijk vooraf:** deze app is geschreven zonder dat ik hem kon bouwen of op een Apple TV kon proberen. Ik had geen Xcode tot mijn beschikking. De code is nauwkeurig nagekeken, maar het kan zijn dat Xcode bij de eerste keer een foutmelding geeft. Meld dan de tekst van de fout, dan los ik die op.

## Wat je nodig hebt
- Een Mac met **Xcode** (gratis in de App Store, groot: ongeveer 10 GB en dat duurt even).
- Een Apple TV (4K of HD, tvOS 16 of nieuwer) op **hetzelfde wifi** als de Mac en de Homey.
- Een gratis **Apple ID** (het account waar je mee inlogt in de App Store).
- De Solis-app op je Homey (versie 3.40 of nieuwer) met het dashboard aan.

## Stap 1: Project openen
1. Pak de map `solis-appletv` uit.
2. Dubbelklik op **Solis.xcodeproj**. Xcode opent.
3. Mocht dit bestand niet goed openen, dan kun je het project ook opnieuw laten maken. Open Terminal en plak:
   ```
   brew install xcodegen
   cd ~/Desktop/solis-appletv
   xcodegen
   ```
   (Pas het pad aan naar waar je de map hebt neergezet.) Daarna dubbelklik je op het nieuwe **Solis.xcodeproj**.

## Stap 2: Je Apple ID instellen
1. Klik links in Xcode op **Solis** (bovenaan, blauw icoontje).
2. Kies onder *Targets* **Solis** en ga naar het tabblad **Signing & Capabilities**.
3. Kies bij **Team** je eigen naam (Personal Team). Staat er niets? Kies *Add an Account…* en log in met je Apple ID.
4. Bij **Bundle Identifier** staat `nl.solisvoorhomey.solis`. Zegt Xcode dat die al bezet is, verander dan een stukje, bijvoorbeeld `nl.wilfried.solis`.

## Stap 3: Apple TV koppelen
1. Zet de Apple TV aan. Ga op de Apple TV naar *Instellingen → Afstandsbedieningen en apparaten → Afstandsbediening-app en apparaten*. Laat dit scherm open staan.
2. Kies in Xcode in het menu **Window → Devices and Simulators**.
3. Je Apple TV staat links onder *Discovered*. Klik erop en kies **Pair**.
4. Op de tv verschijnt een **code van 6 cijfers**. Typ die in Xcode.
5. Wacht tot de Apple TV in de lijst staat zonder waarschuwing.

## Stap 4: De app starten
1. Kies bovenin Xcode, naast de knop met de driehoek, je **Apple TV** als apparaat.
2. Druk op de driehoek (**Run**) of op `⌘R`.
3. Is de Apple TV vergrendeld, ontgrendel hem dan. De eerste keer kan Xcode vragen om je Mac-wachtwoord (voor de sleutelhanger): kies *Altijd toestaan*.
4. Op de Apple TV moet je soms toestaan dat de ontwikkelaar wordt vertrouwd. Dat staat in *Instellingen → Algemeen → Beheer van apparaat*.
5. De app **Solis** start. De eerste keer zie je het instelscherm.

## De app gebruiken
- **Eerste keer:** vul het adres van je Homey in (`homey.local` of het IP-adres, bijvoorbeeld `192.168.1.20`) en de poort (standaard `8765`). Druk eerst op **Test verbinding**, dan op **Opslaan en starten**.
- **Links of rechts vegen** (of klikken op de rand van het touchpad) op de Siri Remote: vorige of volgende pagina.
- **Indrukken (Select):** de pagina meteen verversen. Verder ververst hij zichzelf elke 30 seconden.
- **Menu-knop:** opent een klein menu met *Doorgaan*, *Ververs nu* en *Instellingen*. Druk je **nog een keer** op Menu, dan sluit de app.
- Gaat er iets mis (Homey niet bereikbaar, dashboard uit), dan staat er onderin een rode melding in gewoon Nederlands. De app blijft dan het laatste plaatje tonen en probeert het na 30 seconden opnieuw.

## Belangrijk om te weten
- **Met een gratis Apple ID verloopt de app na 7 dagen.** Dan start hij niet meer en moet je hem opnieuw installeren door in Xcode weer op Run te drukken. Met een betaald Apple Developer-account (99 euro per jaar) duurt dat een jaar.
- De app heeft nog **geen eigen icoon** (je ziet een leeg vlak op het beginscherm). Dat is gewoon een uiterlijk puntje.
- De app praat via gewoon `http` met je Homey. Dat staat in de instellingen van de app uitdrukkelijk toegestaan voor je thuisnetwerk. Op dit adres staat geen wachtwoord: als je in de Solis-app een dashboard-wachtwoord hebt ingesteld, kan deze app (net als de Kodi-add-on) er nog niet mee inloggen. Laat het token dan leeg.
- Het eerste keer vraagt de Apple TV mogelijk of de app het lokale netwerk mag gebruiken. Kies **Sta toe**.

## Wat niet is getest
- Bouwen in Xcode en draaien op een echte Apple TV: **niet getest**.
- De bediening met de Siri Remote (vegen, indrukken, Menu): **niet getest**. Werkt een knop anders, meld het dan.
- Wel gecontroleerd: dat de server `{"pages": [...]}` en de PNG-plaatjes levert zoals de app ze verwacht.

## Bestanden
- `Solis/SolisApp.swift`: start van de app, kiest instelscherm of pagina's.
- `Solis/SetupView.swift`: het instelscherm.
- `Solis/ViewerView.swift`: de schermvullende weergave en de bediening.
- `Solis/SolisClient.swift`: haalt pagina's en plaatjes op en geeft Nederlandse foutmeldingen.
- `Solis/Info.plist`: toestemmingen en netwerkinstellingen.
- `project.yml`: beschrijving om het project met XcodeGen opnieuw te maken.
