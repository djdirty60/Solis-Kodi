#!/bin/bash
# Bouwt de Android TV-app (Solis-AndroidTV-v3.apk) op de Mac.
# Nodig: Android Studio (een keer geopend, zodat de Android SDK er staat).
set -e
cd "$(dirname "$0")"
DIR="$(pwd)"
PROJ="$DIR/android/solis-androidtv"
[ -d "$PROJ" ] || PROJ="$DIR/solis-androidtv"
SDK="$HOME/Library/Android/sdk"
[ -d "$SDK" ] || { echo "Android SDK niet gevonden in $SDK. Open Android Studio een keer en probeer opnieuw."; exit 1; }

# Gradle 8 werkt niet met Java 25 (die zit in de nieuwste Android Studio). Zoek daarom Java 21 of 17.
versie() { [ -f "$1/release" ] && sed -n 's/^JAVA_VERSION="\([0-9]*\).*/\1/p' "$1/release"; }
JH=""
for v in 21 17; do
  c=$(/usr/libexec/java_home -v "$v" 2>/dev/null || true)
  if [ -n "$c" ] && [ "$(versie "$c")" = "$v" ]; then JH="$c"; break; fi
done
if [ -z "$JH" ]; then
  for c in "$HOME"/Library/Java/JavaVirtualMachines/*/Contents/Home /Library/Java/JavaVirtualMachines/*/Contents/Home "$DIR"/.jdk/*/Contents/Home; do
    v=$(versie "$c"); if [ "$v" = "21" ] || [ "$v" = "17" ]; then JH="$c"; break; fi
  done
fi
if [ -z "$JH" ]; then
  echo "Geen Java 21 gevonden. Ik download Java 21 (Eclipse Temurin, gratis, ongeveer 200 MB) in de map .jdk hiernaast..."
  ARCH=$(uname -m); [ "$ARCH" = "arm64" ] && ARCH=aarch64 || ARCH=x64
  mkdir -p "$DIR/.jdk"
  curl -fL# "https://api.adoptium.net/v3/binary/latest/21/ga/mac/$ARCH/jdk/hotspot/normal/eclipse" -o "$DIR/.jdk/jdk21.tar.gz"
  tar -xzf "$DIR/.jdk/jdk21.tar.gz" -C "$DIR/.jdk"
  JH=$(ls -d "$DIR"/.jdk/*/Contents/Home | head -1)
fi
export JAVA_HOME="$JH"
echo "Java: $JAVA_HOME (versie $(versie "$JAVA_HOME"))"
cd "$PROJ"
echo "sdk.dir=$SDK" > local.properties
chmod +x gradlew
echo "Bezig met bouwen. De eerste keer duurt dit een paar minuten..."
./gradlew --no-daemon -q assembleDebug
cp app/build/outputs/apk/debug/app-debug.apk "$DIR/Solis-AndroidTV-v3.apk"
echo "Klaar: Solis-AndroidTV-v3.apk staat naast dit script."
ls -la "$DIR/Solis-AndroidTV-v3.apk"
