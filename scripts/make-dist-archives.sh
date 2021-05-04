#!/usr/bin/env bash
# This script is based on <https://github.com/dmitmel/cc-world-map-overhaul/blob/c0a51cf591088808aed7a0990a2466756740a6cf/.github/workflows/release.sh#L71-L73>.
# Also see <https://github.com/CCDirectLink/crosscode-ru/blob/af5403b4fd0be67225a6fe0c3e3bb0b62dfa7c1e/dist-archive/GNUmakefile>.
set -euo pipefail
shopt -s globstar

cd "$(dirname "$(dirname "${BASH_SOURCE[0]}")")"

log() {
  echo >&2 -E "$@"
}

PROJECT_DIR="$PWD"
WORK_DIR="${PROJECT_DIR}/dist"
LOCALIZE_ME_DOWNLOAD_COMMIT="6a7ec30756a0b742661936ee809d7b5f93ff359a"
LOCALIZE_ME_DIR="Localize-me-v1.x-${LOCALIZE_ME_DOWNLOAD_COMMIT}"
LOCALIZE_ME_DOWNLOAD_FILE="${LOCALIZE_ME_DIR}.tar.gz"
LOCALIZE_ME_DOWNLOAD_URL="https://github.com/L-Sherry/Localize-me/tarball/${LOCALIZE_ME_DOWNLOAD_COMMIT}"
CCLOADER3_DOWNLOAD_DATE="20210504225816"
CCLOADER3_DIR="ccloader3-${CCLOADER3_DOWNLOAD_DATE}"
CCLOADER3_DOWNLOAD_FILE="${CCLOADER3_DIR}.tgz"
CCLOADER3_DOWNLOAD_URL="https://stronghold.crosscode.ru/~dmitmel/ccloader3/${CCLOADER3_DOWNLOAD_DATE}/ccloader_3.0.0-alpha_quick-install.tar.gz"
ULTIMATE_UI_DIR="ultimate-localized-ui_v1.0.0"
ULTIMATE_UI_DOWNLOAD_FILE="${ULTIMATE_UI_DIR}.tgz"
ULTIMATE_UI_DOWNLOAD_URL="https://github.com/CCDirectLink/crosscode-ru/releases/download/v1.2.0/${ULTIMATE_UI_DOWNLOAD_FILE}"

mod_id="$(jq -r '.id' ccmod.json)"
mod_ver="$(jq -r '.version' ccmod.json)"
mod_files=(
  ccmod.json
  LICENSE*
  README.md
  packs-mapping.json
  src/*.js
  packs/**/*.json
  assets/**/*.png
)

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

download_file() {
  local url="$1" file="$2"
  if [[ -f "$file" ]]; then
    return
  fi
  log "downloading ${url}"
  # curl options were taken from Arch's default /etc/makepkg.conf
  curl \
    --globoff --disable --cookie "" --fail --location --retry 3 --retry-delay 3 \
    --output "$file" -- "$url"
  local code="$?"
  if (( code )); then
    rm -- "$file"
    exit "$code"
  fi
}

log "==> downloading dependencies"
download_file "$LOCALIZE_ME_DOWNLOAD_URL" "$LOCALIZE_ME_DOWNLOAD_FILE"
download_file "$CCLOADER3_DOWNLOAD_URL" "$CCLOADER3_DOWNLOAD_FILE"
download_file "$ULTIMATE_UI_DOWNLOAD_URL" "$ULTIMATE_UI_DOWNLOAD_FILE"

make_tar() {
  local output="$1"
  log "making ${output}"
  tar --create --gzip --file "$output" --dereference --numeric-owner --owner 0 --group 0 --files-from -
}

unpack_tar() {
  local archive="$1"
  shift
  log "unpacking ${archive}"
  tar --extract --gzip --no-same-owner "$@" --file "$archive"
}

make_zip() {
  local output="$1"
  log "making ${output}"
  if [[ -e "$output" ]]; then
    rm -- "$output"
  fi
  zip --quiet --must-match --no-wild -X --names-stdin "$output"
}

log "==> unpacking dependencies"
mkdir -p -- "$LOCALIZE_ME_DIR" "$ULTIMATE_UI_DIR" "$CCLOADER3_DIR"
unpack_tar "$LOCALIZE_ME_DOWNLOAD_FILE" --strip-components=1 --directory "$LOCALIZE_ME_DIR"
unpack_tar "$CCLOADER3_DOWNLOAD_FILE" --directory "$CCLOADER3_DIR"
unpack_tar "$ULTIMATE_UI_DOWNLOAD_FILE" --strip-components=1 --directory "$ULTIMATE_UI_DIR"

log "==> setting up the file structure for packaging"
ln_safe() {
  ln --symbolic --relative --force --no-target-directory -- "$@"
}
ln_safe "$PROJECT_DIR" "$mod_id"
ln_safe "${CCLOADER3_DIR}/package.json" "package.json"
ln_safe "${CCLOADER3_DIR}/ccloader" "ccloader"
mkdir -p -- "assets/mods"
ln_safe "$LOCALIZE_ME_DIR" "assets/mods/Localize-me"
ln_safe "$ULTIMATE_UI_DIR" "assets/mods/ultimate-localized-ui"
ln_safe "$PROJECT_DIR" "assets/mods/${mod_id}"

log "==> making mod-only packages"
list_mod_files() {
  local prefix="$1"
  shift
  local file; for file in "$@"; do
    if [[ ! -d "$file" ]]; then
      printf "%s%s\n" "$prefix" "$file"
    fi
  done
}
list_mod_files "${mod_id}/" "${mod_files[@]}" >main_package_file_list.txt
make_tar "${mod_id}_v${mod_ver}.tgz" <main_package_file_list.txt
make_zip "${mod_id}_v${mod_ver}.zip" <main_package_file_list.txt
{
  list_mod_files "" assets/mods/Localize-me/**/*
  list_mod_files "" assets/mods/ultimate-localized-ui/**/*
  list_mod_files "assets/mods/${mod_id}/" "${mod_files[@]}"
  list_mod_files "" ccloader/**/* package.json
} >quick_install_file_list.txt
make_tar "${mod_id}_quick-install_v${mod_ver}.tgz" <quick_install_file_list.txt
make_zip "${mod_id}_quick-install_v${mod_ver}.zip" <quick_install_file_list.txt

log "==> done!"
