# ulauncher-plugin-windows
[Ulauncher](https://ulauncher.io) plugin for activating from a list of windows opened.

Purpose of this fork is to handle windows inside Gnome/Wayland environment.

## Dependencies

This plugin relies on `xdotool` and `xprop` packages, which needs to be installed prior. It also relies on the Python `memoization` package being available.

```sh
sudo apt install xdotool xprop -y
pip install memoization
```

## Usage

`w ` to get a list of windows. Selecting one will activate the window.
