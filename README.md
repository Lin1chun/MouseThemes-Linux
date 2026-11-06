# MouseThemes-Linux

Linux Xcursor themes converted from the Cerber and Cerby Windows cursor packs,
plus an X11 mouse-following pendant based on Cerby's embedded dog image.

## Install a cursor theme

```sh
./linux-cursors/install-cursor-theme.sh Cerber
# or
./linux-cursors/install-cursor-theme.sh Cerby
```

Choose the theme in the desktop's cursor settings. On GNOME:

```sh
gsettings set org.gnome.desktop.interface cursor-theme Cerber
```

The installer copies the selected theme into the current user's icon directory
and does not change the active cursor setting.

## Run the Cerby pendant

Requires Python 3, Tkinter, Pillow, and an X11 server with the Shape extension:

```sh
python3 linux-cursors/cerby-pendant.py
```

The static image follows the pointer, uses its alpha silhouette as the window
shape, and is click-through. Stop it with **Ctrl+C**. It requires an X11
session; native Wayland sessions are not supported.

## Rebuild the cursor themes

Install `Pillow`, `dnfile`, and the system package `xcursorgen`, then run:

```sh
python3 linux-cursors/build-cursor-themes.py
```

This extracts the cursor and pendant assets from the supplied executables and
rebuilds both Xcursor themes.

The supplied applications and embedded artwork retain their original
attribution and licensing terms; see the original executable distributions.
