#!/bin/bash
# Maakt Solis-AppleTV-v3.ipa voor Apple TV (zonder handtekening; de installatiedienst tekent hem zelf).
set -e
cd "$(dirname "$0")/appletv/solis-appletv"
rm -rf build Payload
echo "Bezig met bouwen, dit duurt een paar minuten..."
xcodebuild -project Solis.xcodeproj -scheme Solis -configuration Release -sdk appletvos \
  -derivedDataPath build CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" \
  build -quiet
APP=$(find build -name "Solis.app" -type d | head -1)
[ -z "$APP" ] && { echo "FOUT: Solis.app niet gevonden"; exit 1; }
if [ -f "$APP/Assets.car" ]; then echo "Icoon zit erin: ja"; else echo "Icoon zit erin: NEE (stuur me dit bericht)"; fi
mkdir Payload && cp -R "$APP" Payload/
rm -f ../../Solis-AppleTV-v3.ipa
zip -qrX ../../Solis-AppleTV-v3.ipa Payload
rm -rf Payload
echo "Klaar: Solis-AppleTV-v3.ipa staat naast dit script."
ls -la ../../Solis-AppleTV-v3.ipa
