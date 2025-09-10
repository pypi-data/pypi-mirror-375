# Pyrrot

This is a collection of scripts I use to manage my wallpapers.
This is made for my usage in mind, and hasn't been tested much by others, but it might interest you.
If you've got any suggestion or issue, please let me know.

I personnally use Archlinux, and more importantly i3wm and Sway.
These scripts may not work on other window managers.

## What does it do ?

The `wallpaper.py` script sets you wallpaper from a json file listing all your wallpapers with a few attributes.
Wallpapers may be any file supported by feh (jpeg and non-animated png and gif) on X11, and Swaymsg on Sway (Wayland).
Animated gif or vidéo support for live-wallpapers will be supported later using xwinwrap for X11.
(I should also make a script to aut-generate such a json file if you just want to use a list of images without selection by tags or colors for instance.)

`mpd-wallpaper` will allow you to set your wallpaper with the cover of the current music you're listening to with your mpd server.
It requires `wallpaper.py`.

## Usage

1. Edit wallpaper.conf according to your needs.
2. Setup a cron job to run wallpaper.py to change the wallpaper regularly. Mine is `*/5 * * * * DISPLAY=:0 /home/user/scripts/wallpaper/wallpaper.py` for X11, and `SWAYSOCK=/run/user/$(id -u)/sway-ipc.$(id -u).$(pgrep -x sway).sock /home/inazu    ma/scripts/pyrrot/pyrrot-wrapper.sh` for Wayland.
3. Setup a systemd task for the mpd part (optional). See the `mpd-wallpaper.service.example`.
 Of course if you prefer not to run the scripts with cron or systemd, you're free to use them as you want.

## Prerequisites

Python 3.7 for the mpd script, Python 3.5 for the wallpaper.py, pywal and either feh and i3wm or Sway.
Linux (it might work on some BSD or macOS but it may need some tweaks, and it hasn't been tested at all)

## Development

This software uses `pytest` to run automated test, checking that it functions well.
Below is a list of commands useful for checking everything is allright.

```sh
pip install -e .
coverage run -m pytest --junitxml=report.xml
coverage report
pylint src/
```
