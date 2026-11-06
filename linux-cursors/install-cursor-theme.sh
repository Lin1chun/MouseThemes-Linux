#!/bin/sh
set -eu

APP_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
THEME=${1:-}
case "$THEME" in
    Cerber|Cerby) ;;
    *)
        printf '%s\n' "Usage: $0 Cerber|Cerby" >&2
        exit 2
        ;;
esac

SOURCE=$APP_DIR/themes/$THEME
if [ ! -f "$SOURCE/index.theme" ] || [ ! -d "$SOURCE/cursors" ]; then
    printf '%s\n' "Cursor theme is missing. Build it first with build-cursor-themes.py." >&2
    exit 1
fi

DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
DEST=$DATA_HOME/icons/$THEME
mkdir -p "$DEST/cursors"
cp -a "$SOURCE/cursors/." "$DEST/cursors/"
cp "$SOURCE/index.theme" "$DEST/index.theme"
printf 'Installed %s to %s\n' "$THEME" "$DEST"
printf "To apply it in GNOME, run: gsettings set org.gnome.desktop.interface cursor-theme '%s'\n" "$THEME"
printf '%s\n' "Or select it in your desktop's mouse/cursor settings."
