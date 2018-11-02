# -*- coding: utf-8 -*-

#
# Created by: PyQt5 UI code generator 5.9
#
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget

from PyQt5 import QtCore, QtGui, QtWidgets

from CoreWidget import *
import functions
import os

class ContactFrame(object):

    def setupUi(self, Form,ox,oy,w,h,father=None):
        self.father_view=father
        self.Form=Form
        self.size=(w,h)
        self.bot = self.father_view.bot
        self.scrollArea = YScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(ox, oy, w, h))
        self.scrollArea.setObjectName("DiscoverFrame")
        self.scrollWidget_contact = YWidget()
        self.scrollArea.setWidget(self.scrollWidget_contact)
        
        contacts=self.get_contacts()
        self.drawContacts(contacts)
        
        # self.scrollWidget_contact.setMinimumSize(QtCore.QSize(Form.width(), Form.height()))
        
    def get_contacts(self):
        return self.bot.contact_dict()
    def drawContacts(self,contacts=None,label=None):#创建联系人列表
        # self.con=[]
        contacts = list(contacts.values())
        w = self.scrollWidget_contact.width()
        keys = lambda user:user['RemarkPYInitial'] if user['RemarkPYInitial'] else user['PYInitial']
        contacts.sort(key = keys)
        def generate_label(args):
            name,img,widget,contact,father = args
            clabel = FunctionButton(widget)
            clabel.setContent(img,name,pos = (0,0),sep=True)
            clabel.setName(contact,father)
            clabel.show()
            return clabel
        def accept_label(args):
            if args[0] is None:
                return
            clabel = generate_label(args)
            self.scrollArea.append_element(clabel)

        args_list = [(i['name'],i['img_path'],self.scrollWidget_contact,i,self) for i in contacts]
        self.contact_thread = functions.async_generate()
        self.contact_thread.setThread(args_list)
        self.contact_thread.trigger.connect(accept_label)
        self.contact_thread.start()

    def goto_view(self,name):
        #跳转到conversation的内容界面
        self.father_view.goto_view('chat',(name,False))

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
    
