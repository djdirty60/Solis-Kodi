# Plan: SolisCloud als verbinding (geparkeerd)

Status: **geparkeerd** (4 november 2026). Eerst afwachten wat de tester met de S3-WIFI-ST wil.

## Waarom
Veel Solis-gebruikers hebben geen S2-WL-ST maar een S3-WIFI-ST of andere stick. Die hebben geen lokale Modbus TCP. Via SolisCloud kunnen ze de app toch gebruiken.

## Wat kan
- **Uitlezen (monitoring-API, `/v1/api/inverterDetail` e.d.):** vermogen, opbrengst vandaag/maand/totaal, spanning, temperatuur, status, storingen. De stick stuurt eens per 5 minuten gegevens naar de cloud; limiet 10 vragen per seconde.
- **Toegang:** gebruiker vraagt via een ticket bij Solis "API Access" aan, activeert het in SolisCloud (Basisinstellingen, API-beheer) en krijgt Key ID en Secret.
- **Bedienen (control-API, `/v2/api/control`, lezen met `/v2/api/atRead`):** voor stringomvormers (getest met S6-GR1P in de Home Assistant-koppeling mkuthan/solis-cloud-control):
  - vermogen beperken: CID **15**, in **procenten** (0 tot 110 %)
  - aan: CID **48**, uit: CID **53**
  - werkt met S2-WL-ST en S3-WIFI-ST; DLS-W niet (fout B0115)

## Wat niet of moeilijk kan
- Bediening op afstand is **apart** van API-toegang; Solis moet dat per account aanzetten en keurt het misschien niet goed.
- Gegevens zijn tot 5 minuten oud: "geen export" (snel bijsturen) werkt niet; grof sturen (uit, vaste grens) wel.
- Te vaak vragen maakt de officiële Solis-app onbetrouwbaar; de cloud valt soms weg (opnieuw proberen nodig).
- Er is al een Homey-app "Solis Cloud Inverter" die alleen uitleest (onderhoud onduidelijk).

## Hoe bouwen (veilig)
1. Keuze bij Verbinding: "Lokaal (S2-WL-ST)" of "SolisCloud"; standaard lokaal, cloud-code draait alleen als gekozen.
2. Uitlezen eens per 5 minuten; bij wegvallen rustig opnieuw proberen, geen "niet bereikbaar" na één fout.
3. Bedienen alleen als het werkt: eerst testen; weigert Solis, dan alleen uitlezen en één melding.
4. Alleen CID 15, 48 en 53 schrijven, nooit iets anders.
5. Na elke opdracht teruglezen; daarna minstens 10 minuten niets veranderen.
6. "Geen export" uitschakelen bij cloud; "uit" en vaste grens wel.
7. Hybride omvormers (met batterij): alleen uitlezen.

Testen: tester met S3-stick nodig, die eerst API-toegang (en bediening) bij Solis aanvraagt.

## Bronnen
- SolisCloud Developer Platform, Data Access API: https://developer.soliscloud.com/guide/data-access-user.html
- Solis Service Center, Request API Access: https://solis-service.solisinverters.com/support/solutions/articles/44002212561-api-access-soliscloud
- mkuthan/solis-cloud-control: https://github.com/mkuthan/solis-cloud-control
- Homey-forum, Solis Cloud Inverter-app: https://community.homey.app/t/app-pro-solis-cloud-inverter-receive-realtime-data-from-your-solis-inverter/96591/131
- Homey-forum, Solis omvormer sturen via Modbus/API: https://community.homey.app/t/solis-omvormer-sturen-via-modbus-eh-api/133900/22
