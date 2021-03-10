#! /bin/bash
#
#   pMusic install.sh
#

DESTDIR=${DESTDIR:-/usr}

if [ ! -e pmusic.py ]
then
    echo "error: pMusic source files not found"
    echo "please chdir to source directory"
    exit 1
fi

install -o root -g root -m 755 pmusic.py $DESTDIR/bin/pmusic
install -o root -g root -m 644 -D pMusic.png $DESTDIR/share/pmusic/pMusic.png
install -o root -g root -m 644 -D pMusicIcon.png $DESTDIR/share/pmusic/pMusicIcon.png
install -o root -g root -m 644 -D pmusic.desktop $DESTDIR/share/applications/pmusic.desktop
install -o root -g root -m 644 -D LICENSE $DESTDIR/share/doc/pmusic/README.md
install -o root -g root -m 644 -D LICENSE $DESTDIR/share/doc/pmusic/LICENSE

# EOB
