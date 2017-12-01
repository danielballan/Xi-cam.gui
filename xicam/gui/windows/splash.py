from typing import Callable

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from xicam.gui import static


class XicamSplashScreen(QSplashScreen):
    minsplashtime = 3000

    def __init__(self, mainwindow: Callable[[], QMainWindow] = None,
                 f: int = Qt.WindowStaysOnTopHint | Qt.SplashScreen):
        """
        A QSplashScreen customized to display an animated gif. The splash triggers launch when clicked.

        After minsplashtime, this splash waits until the animation finishes before triggering the launch.

        Parameters
        ----------
        mainwindow  :   class
            Subclass of QMainWindow to display after splashing
        f           :   int
            Extra flags (see base class)
        """

        # Get logo movie from relative path
        self.movie = QMovie(str(static.path('images/animated_logo.gif')))

        # Setup drawing
        self.movie.frameChanged.connect(self.paintFrame)
        self.movie.jumpToFrame(1)
        self.pixmap = QPixmap(self.movie.frameRect().size())
        super(XicamSplashScreen, self).__init__(self.pixmap, f)
        self.setMask(self.pixmap.mask())
        self.movie.finished.connect(self.restartmovie)

        # Setup timed triggers for launching the QMainWindow
        self.timer = QTimer(self)
        self.timer.singleShot(self.minsplashtime, self.launchwindow)
        self._launching = False
        self._launchready = False
        self.mainwindow = mainwindow

        # Start splashing
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.show()
        self.raise_()
        self.activateWindow()
        QApplication.instance().setActiveWindow(self)

    def showMessage(self, message: str, color=Qt.white):
        # TODO: Make this work.
        super(XicamSplashScreen, self).showMessage(message, color)

    def mousePressEvent(self, *args, **kwargs):
        # TODO: Apparently this doesn't work?
        self.timer.stop()
        self.execlaunch()

    def showEvent(self, event):
        """
        Start the animation when shown
        """
        self.movie.start()

    def paintFrame(self):
        """
        Paint the current frame
        """
        self.pixmap = self.movie.currentPixmap()
        self.setMask(self.pixmap.mask())
        self.setPixmap(self.pixmap)
        self.movie.setSpeed(self.movie.speed() + 20)

    def sizeHint(self):
        return self.movie.scaledSize()

    def restartmovie(self):
        """
        Once the animation reaches the end, check if its time to launch, otherwise restart animation
        """
        if self._launchready:
            self.execlaunch()
            return
        self.timer.singleShot(0.000001, self.movie.start)

    def launchwindow(self):
        """
        Save state, defer launch until animation finishes
        """
        self._launchready = True

    def execlaunch(self):
        """
        Launch the mainwindow
        """
        if not self._launching:
            self._launching = True

            app = QApplication.instance()

            from xicam.gui.windows.mainwindow import XicamMainWindow
            self.mainwindow = XicamMainWindow()
            self.timer.stop()

            # Show the QMainWindow
            self.mainwindow.show()
            self.mainwindow.raise_()
            self.mainwindow.activateWindow()
            app.setActiveWindow(self.mainwindow)

            # Stop splashing
            self.hide()
            self.movie.stop()
            self.finish(self.mainwindow)