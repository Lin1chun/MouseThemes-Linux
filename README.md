# MouseThemes-Linux

Linux 光标主题与 Cerby 鼠标挂件：从 Cerber、Cerby Windows 光标包生成 Xcursor 主题，并提供一个基于 Cerby 小狗图案的 X11 跟随挂件。

## 中文使用说明

### 安装光标主题

```sh
./linux-cursors/install-cursor-theme.sh Cerber
# 或
./linux-cursors/install-cursor-theme.sh Cerby
```

然后在桌面环境的鼠标/光标设置中选择主题。GNOME 可使用：

```sh
gsettings set org.gnome.desktop.interface cursor-theme Cerber
```

安装脚本只复制主题文件，不会自行切换当前光标。

### 运行 Cerby 挂件

需要 Python 3、Tkinter、Pillow，以及提供 Shape 扩展的 X11 服务：

```sh
python3 linux-cursors/cerby-pendant.py
```

静态图案会跟随指针、按透明轮廓裁切，并且点击穿透。按 **Ctrl+C** 退出。
需要 X11 会话，不支持原生 Wayland 会话。

### 重新生成光标主题

安装 Python 包 `Pillow`、`dnfile` 和系统工具 `xcursorgen`，然后运行：

```sh
python3 linux-cursors/build-cursor-themes.py
```

该脚本会从随附 EXE 提取光标和挂件图案，并重建两个 Xcursor 主题。

原始程序及其内嵌图像遵循各自的来源和授权信息。

## English

Linux cursor themes converted from the Cerber and Cerby Windows cursor packs,
plus an X11 mouse-following pendant based on Cerby's embedded dog image.

### Install a cursor theme

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

### Run the Cerby pendant

Requires Python 3, Tkinter, Pillow, and an X11 server with the Shape extension:

```sh
python3 linux-cursors/cerby-pendant.py
```

The static image follows the pointer, uses its alpha silhouette as the window
shape, and is click-through. Stop it with **Ctrl+C**. It requires an X11
session; native Wayland sessions are not supported.

### Rebuild the cursor themes

Install `Pillow`, `dnfile`, and the system package `xcursorgen`, then run:

```sh
python3 linux-cursors/build-cursor-themes.py
```

This extracts the cursor and pendant assets from the supplied executables and
rebuilds both Xcursor themes. The original applications and embedded artwork
retain their respective attribution and licensing terms.
