# Solis Dashboard for Kodi

A Kodi / CoreELEC add-on that puts your solar dashboard on the TV. It is the companion to the Homey app **Solis voor Homey** (Solis inverter, Homey Pro, P1 dongle, dynamic electricity prices).

Made by Wilfried van der Voort. The dashboard itself is in Dutch.

![Power flow page](docs/power.png)

## What it does

The Solis app on your Homey draws nine dashboard pages as images, in the same dark style as the web dashboard on a Mac. The add-on shows them full screen on the TV, refreshes them every few seconds, and lets you flip between pages with left and right on the remote. No computer, browser or extra server is needed.

| Page | What you see |
| --- | --- |
| **Zon** (Sun) | Sun arc for today, output per hour, big live wattage, today / price / advice / month tiles |
| **Stroom** (Power) | Panels, house and grid as three rings with flowing dots, plus today's yield sparkline, price, smart advice and month totals |
| **Details** | Generation versus consumption over the day, today's score, hourly price chart with cheap and expensive hours, tracked appliances, CO2 savings |
| **Inzicht** (Insight) | Last 14 days, 3-day forecast with weather icons, payback time, shade and dirt detection, feed-in value, charging tip |
| **Overzicht** (Overview) | Year totals, self-consumption ring, value of your solar power, month-by-month table, "what if" comparison, home battery estimate |
| **Dynamisch** (Dynamic) | Countdown to a dynamic contract, tomorrow's hourly prices, cheapest and most expensive 3 hours, what dynamic would cost you, smart shifting |
| **Verbruik** (Usage) | Consumption today, month and year, 30-day stacked chart (own solar versus grid), hourly usage, appliances |
| **Slim** (Smart) | Twelve smart cards: standby usage, yield versus normal, shade, monthly budget, live cost per hour, grid voltage, end of net metering, goal streak, CO2 |
| **Opties** (Settings) | Read-only overview of the app settings: contract, installation, notifications, control, connections |

<table>
  <tr>
    <td><img src="docs/sun.png" alt="Sun page"></td>
    <td><img src="docs/details.png" alt="Details page"></td>
  </tr>
  <tr>
    <td><img src="docs/insight.png" alt="Insight page"></td>
    <td><img src="docs/overview.png" alt="Overview page"></td>
  </tr>
  <tr>
    <td><img src="docs/dynamic.png" alt="Dynamic page"></td>
    <td><img src="docs/usage.png" alt="Usage page"></td>
  </tr>
  <tr>
    <td><img src="docs/smart.png" alt="Smart page"></td>
    <td><img src="docs/settings.png" alt="Settings page"></td>
  </tr>
</table>

Screenshots use sample data.

## Display modes

Choose one in the add-on settings under **Display**:

1. **Image from the Homey app** (default, recommended). Needs Solis voor Homey **3.35.0 or newer**. The app draws the pages itself, so nothing else has to run.
2. **Image from the image server.** The real web dashboard, pixel for pixel, rendered by a small Node.js server (folder `beeld-server`) on a computer that stays on. Use this if you want the exact web page.
3. **Built-in pages.** Seven simple native Kodi pages drawn with Kodi controls. Needs Solis voor Homey **3.34.0 or newer**.

## Requirements

- Kodi 19 or newer (tested on CoreELEC with Kodi 22), Python 3
- The Homey app **Solis voor Homey** on a Homey Pro, reachable from the TV on your local network (default port **8765**)

## Install (with automatic updates)

Install the **Solis Repository** once. After that Kodi fetches and updates the add-on by itself.

1. Download `repository.solis-1.0.0.zip` from this repository. Do not unzip it.
2. Put the file on your device, for example over SMB to the `Userdata` folder of CoreELEC.
3. In Kodi enable **Settings, System, Add-ons, Unknown sources**.
4. Choose **Add-ons, Install from zip file**, pick the file.
5. Choose **Add-ons, Install from repository, Solis Repository, Program add-ons, Solis Dashboard, Install**.
6. Open **Add-ons, Program add-ons, Solis Dashboard, Configure**.

On Fire TV or Android you can fetch the file with the **Downloader** app:
`https://github.com/djdirty60/Solis-Kodi/raw/main/repository.solis-1.0.0.zip`

## Settings

- **Display**: image from the Homey app, image from the image server, or built-in pages.
- **Dashboard address and port**: the IP address of your Homey and port 8765.
- **Image server address and port**: only for display mode 2.
- **Refresh every (seconds)**, **switch page automatically every (seconds, 0 = off)** and **start page**.

Controls: left and right change page, Back closes the add-on.

## How it works

The Solis app on Homey serves everything on its dashboard port:

- `/beeld/pages.json` lists the pages.
- `/beeld/page/<page>.png` returns a 1920 x 1080 image of a page, drawn by a small rendering module in the app (no browser, no native libraries).
- `/kodi.json` returns the data for the built-in pages.

You can open the image URLs in any browser to check them, for example `http://HOMEY-IP:8765/beeld/page/stroom.png`.

## Troubleshooting

- **"No connection to the image source"**: check the Homey address in the add-on settings, and that the Solis app is 3.35.0 or newer.
- **Old picture stays on screen**: update the add-on to 2.1.1 or newer.
- **Inverter shows "offline" at night**: that is normal. The inverter sleeps without sun.

## Security

The dashboard and the image server have no password and are read-only. Do not expose their ports to the internet; use them on your own network.

## Releasing a new version (for the maker)

1. Raise the version in `script.solis.dashboard/addon.xml` and add a line to `changelog.txt`.
2. Run `python3 tools/make_repo.py`.
3. Commit and push, including the `repo` folder. Kodi usually sees the update within the hour.

The image server (folder `beeld-server`) is not updated by Kodi; replace its files on your computer when there is a new version.

## License

MIT
