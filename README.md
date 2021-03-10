pMusic
======

pMusic is a tiny minimalistic music player.
ASCII art impression of what it looks like:

        +----------+
        |          |
        |          |
        |          |
        |          |
        +----------+

It assumes your music is organized in directories; one album per directory.

It plays music:

- .mp3 files
- .ogg files
- .wav files

It displays albumart images if appropriated named:

- cover.jpg
- Folder.jpg
- folder.jpg
- cover.png
- AlbumArt.jpg
- AlbumArtSmall.jpg


Controls
--------
Hover over the app window to enable the buttons.

        +----------+
        |S        x|
        |          |
        |          |
        | < ==== > |
        +----------+

- left button : skip to previous track
- middle button : select directory to play
- right button : skip to next track
- S button : toggle shuffle
- X button : quits the app

Playback always loops.
Clicking the albumart pauses/resumes playback.
Click and drag the albumart to move the window.


Installation
------------
This app requires Python 3 and Qt5.

    sudo apt install python3-pyqt5 python3-pyqt5.qtmultimedia

And run `install.sh`.

    sudo ./install.sh

This app integrates with GNOME 3 (but may be used elsewhere too).
Search `pMusic` from the GNOME menu or run `pmusic` from a Terminal.


Window size
-----------
You can not resize the window. The window sizes itself according to
your display resolution. If it is too large/small for your tastes,
edit the source code. Near the end of `pmusic.py` there is a
line that reads:

    APP_DIV_SIZE = 12

meaning that the app window size is equal to display height divided by 12.
Increasing the value makes the window smaller, and a lower value results
in a larger window.

Why this convoluted way of changing window size? It's a frameless window
and therefore can not be resized. You are not really supposed to resize
the window.


Volume control
--------------
There is no volume control. Use the GNOME desktop volume control, or
turn a knob somewhere.



- - - 

Copyright 2021 by Walter de Jong <walter@heiho.net>

