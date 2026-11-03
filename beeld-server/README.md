# Solis beeldserver

Maakt van het echte Solis-dashboard een afbeelding per pagina, zodat de Kodi-add-on het **precies hetzelfde** laat zien als op de Mac of in de browser.

Het draait op een computer die aan blijft staan (bijvoorbeeld je Mac). Kodi haalt de afbeeldingen daar op.

## Installeren (Mac)
1. Zet de map `beeld-server` op je Bureaublad en hernoem hem naar `solis-beeld`.
2. Open **Terminal**.
3. Typ `cd ~/Desktop/solis-beeld` en druk op Enter.
4. Typ `npm install` en druk op Enter.
5. Typ `npx playwright install chromium` en druk op Enter. Dit haalt een onzichtbare browser op en duurt even.

## Starten
Typ in Terminal (vervang het IP door dat van je Homey):

    caffeinate -i node solis-beeld.js http://192.168.178.20:8765

Je ziet: *Solis beeldserver draait op poort 8780*. Laat dit venster open. `caffeinate` zorgt dat de Mac niet in slaap valt zolang de server draait.

Test in je browser: `http://localhost:8780/page/slim.jpg` toont de Slim-pagina.

## Instellen in Kodi
Vul bij de add-on *Solis Dashboard* → Configureren in:
- **Adres van de computer met de beeldserver**: het IP-adres van je Mac (Systeeminstellingen → Netwerk).
- **Poort van de beeldserver**: `8780`.

## Opties
| Variabele | Standaard | Betekenis |
|---|---|---|
| `POORT` | 8780 | poort van deze server |
| `VERS` | 8 | hoeveel seconden een afbeelding vers blijft |
| `DONKER_VAN` | 18 | vanaf dit uur donkere weergave |
| `DONKER_TOT` | 7 | tot dit uur |

Voorbeeld: `POORT=8790 VERS=5 node solis-beeld.js http://192.168.178.20:8765`

## Let op
- De computer moet aan staan en op hetzelfde netwerk zitten. Staat hij uit, dan toont Kodi de melding dat de beeldserver niet bereikbaar is.
- Het dashboard heeft geen wachtwoord. Gebruik dit alleen op je eigen netwerk.
