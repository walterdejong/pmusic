#! /usr/bin/env python3
#
#   pmusic.py   WJ121
#

'''pico music player'''

import sys
import os
import inspect

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QEvent, QPoint, QRect, QUrl, QDirIterator
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QHBoxLayout,
                             QLabel, QPushButton, QToolButton, QStyle, QFileDialog)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent


DEBUG = True
DEBUG_COLOR = True


def debug(msg: str) -> None:
    '''print debug message (if in debug mode)'''

    if not DEBUG:
        return

    funcname = inspect.stack()[1][3]

    if DEBUG_COLOR:
        print('\x1b[32m% {}():\x1b[0m {}'.format(funcname, msg))
    else:
        print('% {}(): {}'.format(funcname, msg))


class PImage(QLabel):
    '''clickable image'''

    clicked = pyqtSignal()

    def __init__(self, parent, pixmap=None):
        '''initialize instance'''

        super().__init__(parent)

        self.aspect_ration = 0.0

        if pixmap is not None:
            self.setPixmap(pixmap)
        
    def setPixmap(self, pixmap):
        '''assign pixmap image'''

        super().setPixmap(pixmap)

        self.setScaledContents(True)

        if pixmap is not None:
            img_width, img_height = pixmap.size().width(), pixmap.size().height()
            self.aspect_ratio = img_width / img_height
        else:
            self.aspect_ratio = 0.0
        debug('img aspect ratio == {}'.format(self.aspect_ratio))

    def mousePressEvent(self, event):
        '''onclick event'''

        super().mousePressEvent(event)
        self.clicked.emit()

    def resizeEvent(self, event):
        '''resize event'''

        super().resizeEvent(event)

        debug('resizeEvent: {}x{}'.format(self.width(), self.height()))

        l = min(self.width(), self.height())
        self.resize(l, l * self.aspect_ratio)



class PButtonBar(QWidget):
    '''bar with three main buttons'''

    clicked_left = pyqtSignal()
    clicked_mid = pyqtSignal()
    clicked_right = pyqtSignal()

    def __init__(self, parent):
        '''initialize instance'''

        super().__init__(parent)

        layout = QHBoxLayout()
        layout.addStretch(1)

        self.left_button = QToolButton(self)
        self.left_button.setArrowType(Qt.LeftArrow)
        self.left_button.clicked.connect(self.onclick_left)
        layout.addWidget(self.left_button, 1)

        self.mid_button = QPushButton('', self)
        self.mid_button.clicked.connect(self.onclick_mid)
        layout.addWidget(self.mid_button, 10)

        self.right_button = QToolButton(self)
        self.right_button.setArrowType(Qt.RightArrow)
        self.right_button.clicked.connect(self.onclick_right)
        layout.addWidget(self.right_button, 1)

        self.setLayout(layout)
        self.resize(parent.width(), self.height())

    @pyqtSlot()
    def onclick_left(self):
        '''left button clicked'''

        self.clicked_left.emit()

    @pyqtSlot()
    def onclick_mid(self):
        '''mid button clicked'''

        self.clicked_mid.emit()

    @pyqtSlot()
    def onclick_right(self):
        '''right button clicked'''

        self.clicked_right.emit()



class PMusic(QWidget):
    '''central widget'''

    DEFAULT_IMG = 'appImage.png'
    QUITBUTTON_SIZE = 24

    def __init__(self, parent):
        '''initialize instance'''

        super().__init__(parent)

        self.player = QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.onmedia_status_changed)
        self.playlist = QMediaPlaylist()
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        self.current_albumart = ''

        self.player.setVolume(100)

        self.resize(parent.width(), parent.height())

        pixmap = QPixmap(PMusic.DEFAULT_IMG)
        self.img_label = PImage(self, pixmap)
        self.img_label.resize(self.width(), self.height())
        self.img_label.clicked.connect(self.onclick_img_label)

        self.buttonbar = PButtonBar(self)
        self.buttonbar.hide()
        # position: at the bottom
        self.buttonbar.move(0, self.height() - self.buttonbar.height())
        self.buttonbar.clicked_left.connect(self.onclick_prev)
        self.buttonbar.clicked_mid.connect(self.onclick_main)
        self.buttonbar.clicked_right.connect(self.onclick_next)

        self.quitbutton = QPushButton(self)
        self.quitbutton.hide()
        self.quitbutton.setStyleSheet('color: rgb(240, 0, 0)')      # red
        self.quitbutton.setFont(QFont('webdings', 10))
        self.quitbutton.setText('r')                                # cross
        # position: top right corner
        self.quitbutton.setGeometry(self.width() - PMusic.QUITBUTTON_SIZE, 0, PMusic.QUITBUTTON_SIZE, PMusic.QUITBUTTON_SIZE)
        self.quitbutton.clicked.connect(self.onclick_quit)

        self.show()

    def enterEvent(self, event):
        '''on mouse enter, show the buttons'''

        super().enterEvent(event)

        self.buttonbar.show()
        self.quitbutton.show()
    
    def leaveEvent(self, event):
        '''on mouse leave, hide the buttons'''

        super().leaveEvent(event)

        self.buttonbar.hide()
        self.quitbutton.hide()

    @pyqtSlot()
    def onclick_quit(self):
        '''quit button was clicked'''

        debug('quit')
        self.stop()
        self.parent().close()

    @pyqtSlot()
    def onclick_img_label(self):
        '''image label was clicked'''

        debug('onclick_img_label')
        self.pause()

    @pyqtSlot()
    def onclick_prev(self):
        '''back button was pressed'''

        debug('onclick_prev')
        self.playlist.previous()

        if self.player.state() != QMediaPlayer.PlayingState:
            self.play()

    @pyqtSlot()
    def onclick_next(self):
        '''next button was pressed'''

        debug('onclick_next')
        self.playlist.next()

        if self.player.state() != QMediaPlayer.PlayingState:
            self.play()

    @pyqtSlot()
    def onclick_main(self):
        '''main button was pressed'''

        debug('onclick_main')

        # bring up directory selection dialog
        # have a preference for $HOME/Music/
        try:
            homedir = os.environ['HOME']
            if not os.path.isdir(homedir):
                homedir = os.path.curdir
        except KeyError:
            homedir = os.path.curdir
        music_dir = os.path.join(homedir, 'Music')
        if not os.path.isdir(music_dir):
            music_dir = os.path.curdir

        path = QFileDialog.getExistingDirectory(self, 'Select directory', music_dir, QFileDialog.ShowDirsOnly)
        debug('path == [{}]'.format(path))
        if not path:
            # cancel
            return

        self.stop()
        self.load_playlist(path)
        self.load_albumart(path)
        self.play()

    def onmedia_status_changed(self):
        '''media changed; player switched to next song'''

        debug('onmedia_status_changed')
        media = self.player.currentMedia()
        if media.isNull():
            debug('media isNull')
            return
        
        filename = media.canonicalUrl().path()
        debug('current media == [{}]'.format(filename))
        folder = os.path.dirname(filename)
        self.load_albumart(folder)

    def load_playlist(self, path):
        '''load new playlist'''

        debug('load playlist')
        self.playlist.clear()

        # Note: not actually sure these formats are all supported ...
        files = QDirIterator(path, ['*.mp3', '*.ogg', '*.wav', '*.flac'], flags=QDirIterator.Subdirectories)
        while files.hasNext():
            filename = files.next()
            debug('+ {}'.format(filename))

            url = QUrl.fromLocalFile(filename)
            if not self.playlist.addMedia(QMediaContent(url)):
                debug('addMedia() => False')

        self.player.setPlaylist(self.playlist)

    def load_albumart(self, path):
        '''load album art'''

        debug('load album art')
        # load album art
        for name in ('cover.jpg', 'Folder.jpg', 'folder.jpg', 'cover.png', 'AlbumArt.jpg', 'AlbumArtSmall.jpg'):
            filename = os.path.join(path, name)
            if os.path.isfile(filename):
                if filename == self.current_albumart:
                    debug('same albumart, already loaded')
                    break

                pixmap = QPixmap(filename)
                self.img_label.setPixmap(pixmap)
                self.current_albumart = filename
                break

    def stop(self):
        '''stop playing'''

        debug('stop')
        self.player.stop()

    def play(self):
        '''start playing'''

        debug('play()')
        self.player.play()

    def pause(self):
        '''pause playing'''

        if self.player.state() == QMediaPlayer.PlayingState:
            debug('pause')
            self.player.pause()

        elif self.player.state() in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.player.play()



class PMusicWindow(QMainWindow):
    '''main window'''

    WINDOW_SIZE = (150, 150)

    def __init__(self):
        '''initialize instance'''

        super().__init__()

        self.setWindowTitle('pMusic')
        self.setWindowIcon(QIcon('appIcon.png'))

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.setFixedSize(PMusicWindow.WINDOW_SIZE[0], PMusicWindow.WINDOW_SIZE[1])
        self.setCentralWidget(PMusic(self))

        self.old_pos = self.pos()

        self.show()

    def mousePressEvent(self, event):
        '''mouse down'''

        super().mousePressEvent(event)

        self.old_pos = event.pos()

    def mouseMoveEvent(self, event):
        '''mouse drag; move window
        this event happens only when mouse button is down
        '''

        super().mouseMoveEvent(event)

        self.move(self.pos() + (event.pos() - self.old_pos))



if __name__ == '__main__':
    app_ = QApplication(sys.argv)
    main_window_ = PMusicWindow()
    sys.exit(app_.exec_())


# EOB
