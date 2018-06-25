# -*- coding: utf-8 -*-

#
# Created by: PyQt5 UI code generator 5.9
#

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget,QPushButton

from PyQt5 import QtCore, QtGui, QtWidgets

from CoreWidget import *
import wxtools
import os
from pathlib import Path



class LogInThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(tuple)

    def setValue(self,father):
        self.father = father

    def run(self):
        bot = wxtools.myBot(cache_path=self.father.cache,qr_callback = self.father.qr_callback,login_callback=self.father.login_callback)
        bot.set_init()
        @bot.register(except_self=False)
        def get_message(msg):
            self.trigger.emit((msg,'MSG'))

        if bot.is_first:
            bot.first_run()
        
        self.trigger.emit((bot, 'BOT'))
        # bot.auto_run()

class WelcomeFrame:
    def __init__(self,cache=False):
        self.cache = cache#存储登录信息路径的pkl文件
    def setupUi(self, Form,ox,oy,w,h,father=None):
        self.father_view=father
        self.Form=Form
        self.size=(w,h)

        self.LogIn_button = YTextButton(Form)
        self.LogIn_button.setTextIcon("登录",(12,234,12),(0,0,0),(int(w/2),int(w/6)))
        self.LogIn_button.clicked.connect(self.get_QRcode)
        self.LogIn_button.setGeometry(int(w/4), int(h/2*1.3), int(w/2), int(w/6))
        self.QR_label = QLabel(Form)
        self.QR_label.setScaledContents(True)
        self.QR_label.setGeometry(int(w/6), int(w/3), int(w/6*4), int(w/6*4))
        self.QR_label.hide()
        # self.get_QRcode()

    def qr_callback(self, uuid, status, qrcode):
        open('qrcode.png','wb').write(qrcode)
        s=QtGui.QImage('qrcode.png')
        self.QR_label.setPixmap(QtGui.QPixmap.fromImage(s))
        self.QR_label.show()
        os.remove('qrcode.png')

    def login_callback(self,*t):
        print('login callback')

    def bot_callback(self,callback_data):
        data, TYPE = callback_data
        if TYPE == 'BOT':
            self.bot=data
            self.father_view.bot = self.bot
            self.father_view.Form.setBot(self.bot)
            self.hide()
            self.father_view.setupUi()
            self.father_view.show()
        elif TYPE == 'MSG':
            self.bot.get_message(data)
            return
        elif TYPE == 'FIRST':
            pass
        p = Path(self.cache)
        print(p.is_file(), '是否产生登录文件?')
        t = p.read_bytes()
        yxsid = self.bot.get_user_yxsid(self.bot.self)
        open(p.with_name(yxsid+'_wx.pkl'),'wb').write(t)
    def get_QRcode(self):
        print('jump to user frame')
        self.loginthread=LogInThread()
        self.loginthread.setValue(self)
        self.loginthread.trigger.connect(self.bot_callback)
        self.loginthread.start()

    def goto_view(self,name):
        #跳转到conversation的内容界面
        self.father_view.goto_view('chat',name)

    def hide(self):
        self.LogIn_button.hide()
        self.QR_label.hide()

    
