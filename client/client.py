#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
tank battle field, client, using PyQt4
'''


import sys
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import QMessageBox
from socket import *




class NotImplementedException(Exception):
    pass


class LogRegDlg(object):
    def __init__(self, parent=None):
        self.ui = uic.loadUi("ai_client_ui/login_regist.ui")
        self.ui.show()
        self.ui.loginBtn.clicked.connect(self.onLoginClicked)
        self.user_token = None

    def exec_(self):
        self.ui.exec_()

    def onLoginClicked(self, event):
        print event
        self.user_token = 'XXOO'
        ret = QMessageBox.question(self.ui, 'haha', 'how are you?',
                                   QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            print 'yes'
        elif ret == QMessageBox.No:
            print 'no'
        sys.exit()
        self.ui.accept()

    @classmethod
    def getLoginToken(cls):
        dlg = cls()
        dlg.exec_()
        return dls.user_token


class TimerMixin(object):
    '''inherite this, and override periodic_call() '''
    def __init__(self):

        self._timer_interval = 500  # msec
        self._qtimer = QtCore.QTimer()
        self._qtimer.timerEvent = self.periodic_call

    def periodic_call(self, event):
        raise NotImplementedException("periodic_call() should be override")

    def start_pcall(self, interval = None):
        self._timer_interval = interval or self._timer_interval
        self._qtimer.start(self._timer_interval)

    def stop_pcall(self):
        self._qtimer.stop()


class BattleWindow(QtGui.QMainWindow, TimerMixin):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        TimerMixin.__init__(self)
        self.ui = uic.loadUi('ai_client_ui/mainwindow.ui')
        self.ui.show()
        self.start_pcall(1000)

    def periodic_call(self, event):
        print 'fuck'


def main():
    app = QtGui.QApplication(sys.argv)
    if LogRegDlg.getLoginToken():
        win = BattleWindow()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
