# -*- coding: utf-8 -*-

#
# Created by: PyQt5 UI code generator 5.9
#
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget

from PyQt5 import QtCore, QtGui, QtWidgets

from CoreWidget import *

import os

class DiscoverFrame(object):

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
        self.circle.setContent('icon_users/GIFMAKER.png','GIF MAKER',pos=(0,0.3*CRITERION))       
        self.circle.setName({'name':'GIFMAKER','id_tag':'GIFMAKER'},self)

    def drawDiscover(self):
        self.getDiscover()
        height=max(self.size[1]-20,self.conversation_height*len(self.conversation_list))
        self.scrollWidget_discover.setGeometry(QtCore.QRect(0, 0, self.conversation_width,height ))
        self.scrollWidget_discover.setMinimumSize(QtCore.QSize(self.conversation_width, height))
        self.scrollWidget_discover.setObjectName("scrollWidget_discover")
        self.con=[]
        for n,i in enumerate(self.conversation_list):
            p1 = ConversationButton(self.scrollWidget_discover)
            p1.setContent(i,i[-10:-4],i[9:],'前天',self.conversation_width,self.conversation_height)
            self.setButton(p1,None,self.conversation_width,self.conversation_height,i,(0,n*self.conversation_height,self.conversation_width,self.conversation_height))
            self.con.append(p1)
    def goto_view(self,name):
        return
        self.father_view.goto_view('chat',name)
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
    ui = Ui_Form()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
    