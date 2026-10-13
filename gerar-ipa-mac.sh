#!/bin/bash
# Compila a exportação da Unity sem conta Apple; Sideloadly assina na instalação.
set -euo pipefail
if [[ "$(uname -s)" != Darwin ]]; then
    echo "A compilação nativa exige macOS com Xcode." >&2
    exit 1
fi
projeto="${1:?Informe a pasta exportada pela Unity}"
saida="${2:?Informe a pasta de saída}"
mkdir -p "$saida"
projeto="$(cd "$projeto" && pwd)"
saida="$(cd "$saida" && pwd)"
temporario="$(mktemp -d)"
xcodebuild -version > "$saida/xcode.log"
if ! xcodebuild -project "$projeto/Unity-iPhone.xcodeproj" -scheme Unity-iPhone \
    -configuration Release -sdk iphoneos -destination 'generic/platform=iOS' \
    -derivedDataPath "$temporario/DerivedData" -jobs 2 \
    CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY='' \
    DEVELOPMENT_TEAM='' build > "$saida/build.log" 2>&1; then
    tail -n 100 "$saida/build.log"
    exit 1
fi
app="$temporario/DerivedData/Build/Products/Release-iphoneos/Moltz.app"
if [[ ! -d "$app" ]]; then
    echo "Moltz.app não foi gerado no caminho esperado." >&2
    exit 1
fi
executavel="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$app/Info.plist")"
file "$app/$executavel" | tee "$saida/binario.log"
lipo "$app/$executavel" -verify_arch arm64
mkdir -p "$temporario/Payload"
ditto "$app" "$temporario/Payload/Moltz.app"
(cd "$temporario" && zip -qry "$saida/Moltz-Sideloadly.ipa" Payload)
unzip -tq "$saida/Moltz-Sideloadly.ipa"
shasum -a 256 "$saida/Moltz-Sideloadly.ipa" > "$saida/SHA256.txt"
echo "IPA gerado: $saida/Moltz-Sideloadly.ipa"
