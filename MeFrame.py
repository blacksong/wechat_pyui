# -*- coding: utf-8 -*-

#
# Created by: PyQt5 UI code generator 5.9
#
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget

from PyQt5 import QtCore, QtGui, QtWidgets

from CoreWidget import *

import os

class MeFrame:

    def setupUi(self, Form,ox,oy,w,h,father=None):
        self.father_view=father
        self.Form=Form
        self.size=(w,h)

        self.scrollArea = YScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(ox, oy, w, h))
        self.scrollArea.setObjectName("DiscoverFrame")
        self.scrollWidget_discover = YWidget()
        self.scrollArea.setWidget(self.scrollWidget_discover)
        self.circle=FunctionButton(self.scrollWidget_discover)
        self.circle.setContent('discover/1.jpg','退出登录',pos=(0,0.3*CRITERION))       
        self.circle.setName('退出登录',self)
        # self.circle.clicked.connect(self.log_out)

    def goto_view(self,name):
        #跳转到conversation的内容界面
        self.hide()
        self.father_view.goto_view('LogOut',name)
    def getDiscover(self):
        dirname='discover/'
        self.conversation_list=[dirname+i for i in os.listdir(dirname)]
        if len(self.conversation_list)>30:
            self.conversation_list=self.conversation_list[:30]
        self.conversation_height=int(CRITERION*(128/90))
        self.conversation_width=self.size[0]

    def setButton(self,B,I,pw,ph,objectname,position=None):
        if I is not None:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(I) )
            B.setIcon(icon)
            B.setIconSize(QtCore.QSize(pw , ph))
        B.setName(objectname,self)
        if position is not None:B.setGeometry(QtCore.QRect(*position))

    def hide(self):
        self.scrollArea.hide()
    def show(self):
        self.scrollArea.show()


if __name__ == '__main__':
    '''
    主函数
    '''
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = MeFrame()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
    