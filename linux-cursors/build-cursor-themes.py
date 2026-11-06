#!/usr/bin/env python3
"""Convert the embedded Windows CUR packs into Xcursor themes."""

from io import BytesIO
from pathlib import Path
import shutil
import struct
import subprocess
import zipfile

from PIL import Image
import dnfile


ROOT = Path(__file__).resolve().parent.parent
THEMES = Path(__file__).resolve().parent / "themes"
PENDANT_ICON = Path(__file__).resolve().parent / "assets" / "cerby-pendant.png"
PACKS = (
    ("Cerber", ROOT / "Cerber鼠标指针v1.1.exe"),
    ("Cerby", ROOT / "Cerby鼠标挂件v1.1.exe"),
)
ALIASES = {
    "Normal.cur": ("left_ptr", "default", "arrow"),
    "Help.cur": ("question_arrow", "help"),
    "Working.cur": ("progress",),
    "Busy.cur": ("watch", "wait"),
    "Precision.cur": ("crosshair", "cross"),
    "Text.cur": ("xterm", "text"),
    "Handwriting.cur": ("pencil",),
    "Unavailable.cur": ("not-allowed", "crossed_circle"),
    "Vertical.cur": ("size_ver", "sb_v_double_arrow", "n-resize", "s-resize"),
    "Horizontal.cur": ("size_hor", "sb_h_double_arrow", "e-resize", "w-resize"),
    "Diagonal1.cur": ("size_fdiag", "fd_double_arrow", "nwse-resize", "se-resize"),
    "Diagonal2.cur": ("size_bdiag", "bd_double_arrow", "nesw-resize", "sw-resize"),
    "Move.cur": ("fleur", "move", "all-scroll"),
    "Alternate.cur": ("up-arrow",),
    "Link.cur": ("hand2", "pointer", "hand1"),
    "Person.cur": ("person",),
    "Pin.cur": ("pin",),
}


def embedded_cursor_pack(executable: Path) -> bytes:
    try:
        with zipfile.ZipFile(executable) as bundle:
            return bundle.read("cursor/EmbeddedCursorPack.zip")
    except (zipfile.BadZipFile, KeyError):
        pass

    pe = dnfile.dnPE(str(executable))
    for resource in pe.net.resources:
        if "EmbeddedCursorPack.zip" in str(resource.name):
            return resource.data
    raise ValueError(f"No embedded cursor pack found in {executable.name}")


def embedded_pendant_icon(executable: Path) -> bytes:
    pe = dnfile.dnPE(str(executable))
    for resource in pe.net.resources:
        if "GeneratedPicIcon.png" in str(resource.name):
            image_data = resource.data
            with Image.open(BytesIO(image_data)) as image:
                image.verify()
            return image_data
    raise ValueError(f"No embedded pendant icon found in {executable.name}")


def cursor_frame(data: bytes, png_path: Path) -> tuple[int, int, int]:
    reserved, image_type, count = struct.unpack_from("<HHH", data)
    if reserved != 0 or image_type != 2 or count < 1:
        raise ValueError("Invalid CUR file header")
    width = data[6] or 256
    height = data[7] or 256
    hot_x, hot_y = struct.unpack_from("<HH", data, 10)
    if hot_x >= width or hot_y >= height:
        raise ValueError("CUR hotspot is outside the cursor image")
    with Image.open(BytesIO(data)) as image:
        image.convert("RGBA").save(png_path)
    return width, hot_x, hot_y


def main() -> None:
    if shutil.which("xcursorgen") is None:
        raise SystemExit("xcursorgen is required; install the xcursorgen package.")

    THEMES.mkdir(parents=True, exist_ok=True)
    PENDANT_ICON.parent.mkdir(parents=True, exist_ok=True)
    PENDANT_ICON.write_bytes(embedded_pendant_icon(ROOT / "Cerby鼠标挂件v1.1.exe"))
    for theme_name, executable in PACKS:
        target = THEMES / theme_name
        if target.exists():
            shutil.rmtree(target)
        cursor_dir = target / "cursors"
        cursor_dir.mkdir(parents=True)

        with zipfile.ZipFile(BytesIO(embedded_cursor_pack(executable))) as pack:
            for source_name, aliases in ALIASES.items():
                image_data = pack.read(source_name)
                png_path = target / f"{source_name}.png"
                size, hot_x, hot_y = cursor_frame(image_data, png_path)
                config = target / f"{source_name}.conf"
                config.write_text(
                    f"{size} {hot_x} {hot_y} {png_path} 0\n",
                    encoding="utf-8",
                )
                primary = cursor_dir / aliases[0]
                subprocess.run(
                    ["xcursorgen", str(config), str(primary)],
                    check=True,
                )
                for alias in aliases[1:]:
                    (cursor_dir / alias).symlink_to(primary.name)
                png_path.unlink()
                config.unlink()

        (target / "index.theme").write_text(
            "[Icon Theme]\n"
            f"Name={theme_name}\n"
            f"Comment={theme_name} cursor theme converted from the supplied Windows cursor pack\n"
            "Inherits=Adwaita\n",
            encoding="utf-8",
        )
        print(f"Built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
