#!/bin/bash
# Bouwt de Android TV-app (Solis-AndroidTV.apk) op de Mac. Nodig: Android Studio (eenmaal geopend, zodat de SDK er staat).
set -e
cd "$(dirname "$0")"
DIR="$(pwd)"
PROJ="$DIR/android/solis-androidtv"
[ -d "$PROJ" ] || PROJ="$DIR/solis-androidtv"
export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
[ -d "$JAVA_HOME" ] || { echo "Android Studio niet gevonden in Programma's."; exit 1; }
SDK="$HOME/Library/Android/sdk"
[ -d "$SDK" ] || { echo "Android SDK niet gevonden in $SDK. Open Android Studio een keer."; exit 1; }
cd "$PROJ"
echo "sdk.dir=$SDK" > local.properties
chmod +x gradlew
./gradlew --no-daemon -q assembleDebug
cp app/build/outputs/apk/debug/app-debug.apk "$DIR/Solis-AndroidTV-v3.apk"
echo "Klaar: Solis-AndroidTV-v3.apk staat naast dit script."
