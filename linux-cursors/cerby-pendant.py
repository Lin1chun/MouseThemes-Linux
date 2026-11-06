#!/usr/bin/env python3
"""Show the extracted Cerby icon as a click-through X11 cursor pendant."""

import ctypes
import ctypes.util
import os
from pathlib import Path
import sys
import tkinter as tk

from PIL import Image
from PIL import ImageTk


ASSET = Path(__file__).resolve().parent / "assets" / "cerby-pendant.png"
SHAPE_BOUNDING = 0
SHAPE_INPUT = 2
SHAPE_SET = 0
UNSORTED = 0
ALPHA_THRESHOLD = 8
PENDANT_HOTSPOT_Y = 33


class XRectangle(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_short),
        ("y", ctypes.c_short),
        ("width", ctypes.c_ushort),
        ("height", ctypes.c_ushort),
    ]


def shape_rectangles(alpha: Image.Image) -> list[XRectangle]:
    rectangles = []
    for y in range(alpha.height):
        run_start = None
        for x in range(alpha.width + 1):
            visible = x < alpha.width and alpha.getpixel((x, y)) >= ALPHA_THRESHOLD
            if visible and run_start is None:
                run_start = x
            elif not visible and run_start is not None:
                rectangles.append(XRectangle(run_start, y, x - run_start, 1))
                run_start = None
    return rectangles


def configure_click_through(
    window_id: int,
    rectangles: list[XRectangle],
) -> tuple[ctypes.CDLL, ctypes.c_void_p]:
    x11_name = ctypes.util.find_library("X11")
    xext_name = ctypes.util.find_library("Xext")
    if not x11_name or not xext_name:
        raise RuntimeError("The X11 Shape extension libraries (libX11 and libXext) are required.")

    x11 = ctypes.CDLL(x11_name)
    xext = ctypes.CDLL(xext_name)
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XFlush.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XDefaultScreen.argtypes = [ctypes.c_void_p]
    x11.XDefaultScreen.restype = ctypes.c_int
    x11.XRootWindow.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x11.XRootWindow.restype = ctypes.c_ulong
    x11.XQueryTree.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.POINTER(ctypes.c_ulong)),
        ctypes.POINTER(ctypes.c_uint),
    ]
    x11.XQueryTree.restype = ctypes.c_int
    x11.XFree.argtypes = [ctypes.c_void_p]
    xext.XShapeQueryExtension.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    xext.XShapeQueryExtension.restype = ctypes.c_int
    xext.XShapeQueryVersion.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
    ]
    xext.XShapeQueryVersion.restype = ctypes.c_int
    xext.XShapeCombineRectangles.argtypes = [
        ctypes.c_void_p,
        ctypes.c_ulong,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(XRectangle),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]

    display = x11.XOpenDisplay(os.environ.get("DISPLAY", "").encode() or None)
    if not display:
        raise RuntimeError("Could not connect to X11. Run this pendant in an X11 session.")

    event_base = ctypes.c_int()
    error_base = ctypes.c_int()
    if not xext.XShapeQueryExtension(display, ctypes.byref(event_base), ctypes.byref(error_base)):
        x11.XCloseDisplay(display)
        raise RuntimeError("The current X11 server does not provide the Shape extension.")
    shape_major = ctypes.c_int()
    shape_minor = ctypes.c_int()
    if not xext.XShapeQueryVersion(display, ctypes.byref(shape_major), ctypes.byref(shape_minor)):
        x11.XCloseDisplay(display)
        raise RuntimeError("Could not query the X11 Shape extension version.")
    if (shape_major.value, shape_minor.value) < (1, 1):
        x11.XCloseDisplay(display)
        raise RuntimeError("The X11 Shape extension must be version 1.1 or newer for click-through.")

    root_window = x11.XRootWindow(display, x11.XDefaultScreen(display))
    shaped_window = window_id
    while True:
        tree_root = ctypes.c_ulong()
        parent = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        child_count = ctypes.c_uint()
        if not x11.XQueryTree(
            display,
            shaped_window,
            ctypes.byref(tree_root),
            ctypes.byref(parent),
            ctypes.byref(children),
            ctypes.byref(child_count),
        ):
            x11.XCloseDisplay(display)
            raise RuntimeError("Could not locate the pendant's top-level X11 window.")
        if children:
            x11.XFree(children)
        if parent.value == root_window:
            break
        if parent.value == 0:
            x11.XCloseDisplay(display)
            raise RuntimeError("The pendant's X11 window is not attached to the screen.")
        shaped_window = parent.value

    rect_array_type = XRectangle * len(rectangles)
    rect_array = rect_array_type(*rectangles)
    xext.XShapeCombineRectangles(
        display,
        shaped_window,
        SHAPE_BOUNDING,
        0,
        0,
        rect_array,
        len(rectangles),
        SHAPE_SET,
        UNSORTED,
    )
    input_windows = [shaped_window]
    for window in input_windows:
        tree_root = ctypes.c_ulong()
        parent = ctypes.c_ulong()
        children = ctypes.POINTER(ctypes.c_ulong)()
        child_count = ctypes.c_uint()
        if not x11.XQueryTree(
            display,
            window,
            ctypes.byref(tree_root),
            ctypes.byref(parent),
            ctypes.byref(children),
            ctypes.byref(child_count),
        ):
            x11.XCloseDisplay(display)
            raise RuntimeError("Could not locate the pendant's X11 child windows.")
        input_windows.extend(children[index] for index in range(child_count.value))
        if children:
            x11.XFree(children)

    for window in input_windows:
        xext.XShapeCombineRectangles(
            display,
            window,
            SHAPE_INPUT,
            0,
            0,
            None,
            0,
            SHAPE_SET,
            UNSORTED,
        )
    x11.XFlush(display)
    return x11, display


def main() -> int:
    if not os.environ.get("DISPLAY"):
        print("Cerby mouse pendant requires an X11 session (DISPLAY).", file=sys.stderr)
        return 1
    if not ASSET.is_file():
        print(f"Cerby image is missing: {ASSET}", file=sys.stderr)
        return 1

    image = Image.open(ASSET).convert("RGBA")
    alpha = image.getchannel("A")
    rectangles = shape_rectangles(alpha)

    root = tk.Tk()
    root.title("Cerby mouse pendant")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.geometry(f"{image.width}x{image.height}+0+0")
    canvas = tk.Canvas(
        root,
        width=image.width,
        height=image.height,
        borderwidth=0,
        highlightthickness=0,
        background="#000000",
        takefocus=False,
    )
    canvas.pack()
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, image=photo, anchor="nw")
    root.update_idletasks()
    root.update()

    try:
        x11, display = configure_click_through(root.winfo_id(), rectangles)
    except RuntimeError as error:
        root.destroy()
        print(str(error), file=sys.stderr)
        return 1

    def follow_pointer() -> None:
        pointer_x, pointer_y = root.winfo_pointerxy()
        left = pointer_x - image.width // 2
        top = pointer_y - PENDANT_HOTSPOT_Y
        root.geometry(f"+{left}+{top}")
        root.after(16, follow_pointer)

    root.after_idle(follow_pointer)
    try:
        root.mainloop()
    finally:
        x11.XCloseDisplay(display)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
