# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLineEdit,QDialog

from PyQt5 import QtCore, QtGui, QtWidgets,Qt
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from CoreWidget import *


class Ui_Chat(QWidget):

    def setupUi(self,Bot ,user_info:dict ,me_info:dict ):
        Form = self
        self.Form=self
        self.resize(520,520)
        self.isback=False
        self.blabel = QLabel(self)
        self.blabel.setStyleSheet('QWidget{background-color:rgb(255,255,255)}')
        self.max_text_height=2.5*CRITERION
        self.change_button=0 #用来判断是否要改变发送和功能按钮的逻辑变量

        self.user_info = user_info
        self.me_info = me_info
        self.icon_other=QtGui.QIcon(user_info['img_path'])
        self.icon_me = QtGui.QIcon(me_info['img_path'])
        self.icon_dict={ME:self.icon_me,OTHER:self.icon_other}
        layout = QVBoxLayout()

        self.title_widget = self.set_title()
        layout.addWidget(self.title_widget)
        layout.addWidget(self.set_line())
        self.content_widget = self.set_content()
        layout.addWidget(self.content_widget)
        self.line_widget = self.set_line()
        layout.addWidget(self.line_widget)
        self.input_widget = self.set_input()
        layout.addWidget(self.input_widget)
        self.send_widget = self.set_send()
        layout.addWidget(self.send_widget)

        self.scrollWidget_message_size= 200,70
        self.scrollWidget_message_bottom = 0

        
        self.setLayout(layout)
        self.show()


        self.bot = Bot
    
    def get_me_info(self,info):
        pass
    def get_other_info(self,info):
        pass
    def resizeEvent(self,d):#根据窗口大小调整白色背景的大小以及发送键的位置
        size = self.size()
        self.blabel.resize(size)
        size_send = self.send_widget.size()
        print(size_send)
        size_send.setWidth(size.width())
        self.send_widget.resize(size_send)
        self.Button_send.move(size.width()-self.Button_send.width()-20,0)

    def click_name(self,*d):
        print('press name button')
    def set_title(self):
        title = QWidget()
        title.setMaximumHeight(40)
        title.setMinimumHeight(40)
        p=YTextButton(title)
        p.setTextIcon(self.user_info['name'],(255,255,255),(10,10,10),(150,40),position='left')
        p.resize(150,40)
        p.clicked.connect(self.click_name)
        p.move(20,10)
        return title
    def set_content(self):
        self.scrollArea = YScrollArea(self)
        
        
        self.bar=self.scrollArea.verticalScrollBar()

        self.scrollArea.setStyleSheet("border:none;")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget_message = YWidget()#显示对话的Widget
        self.scrollWidget_message.setMinimumSize(500,100)


        self.scrollWidget_message.setObjectName("scrollWidget_message")
        self.scrollArea.setWidget(self.scrollWidget_message)
        return self.scrollArea
    def set_line(self):
        function = QWidget()
        function.setStyleSheet('QWidget{background-color:rgb(100,100,100)}')
        function.setMaximumHeight(1)
        function.setMinimumHeight(1)
        return function
    def set_input(self):

        self.input_text=YInputText(self)
        self.input_text.setMaximumHeight(70)
        self.input_text.setMinimumHeight(70)
        self.input_text.move( 10,10 )

        self.input_text.press_enter_connect(lambda :self.button_send_click(None))

        self.input_text_height=self.input_text.document().size().height()

        return self.input_text
    def set_send(self):
        send_widget = QWidget(self)
        send_widget.setMaximumHeight(30)
        send_widget.setMinimumHeight(30)
        send_widget.setStyleSheet('QWidget{background-color:rgb(255,255,255)}')
        self.Button_send = YTextButton(send_widget)
        self.Button_send.setTextIcon('Send',(24,240,12),(244,244,244),(80,30))
        self.Button_send.resize(80,30)
        self.Button_send.clicked.connect(self.button_send_click)

        return send_widget

    def addMessage(self,value,identity=OTHER,Format=TEXT): 

        button=YTalkWidget(self.scrollWidget_message)
        button.setContent(value,Format,self.icon_dict[identity],identity=identity)
        self.scrollArea.append_element(button)
        button.show()
        self.autoSlideBar()

    def autoSlideBar(self,pos='bottom'):
        if pos=='bottom':
            bottom=self.scrollArea.bottom-self.scrollArea.height()+10
            self.bar.setValue(self.scrollArea.bottom)
        
    def setButton(self,B,I,pw,ph,objectname,position=None,connect=None):
        if I is not None:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(I) )
            B.setIcon(icon)
            B.setIconSize(QtCore.QSize(pw , ph))
        B.setObjectName(objectname)
        if position is not None:B.setGeometry(QtCore.QRect(*position))
        if connect is not None:B.clicked.connect(connect)
    def accept_callback(self,data):
        print(data)
        data = data[0]
        self.addMessage(data.decode('utf8'),OTHER,TEXT)
    def adjustInputTextSize(self,h_d):
        return 
        if h_d<=self.input_text_height:
            init_value=True 
        else:
            init_value=False
        g=self.input_text.geometry()
        p=g.bottom()-h_d
        if init_value:p=self.input_text_top
        g.setTop(p)
        self.input_text.setGeometry(g)
        
        gs=self.scrollArea.geometry()
        if init_value:p=self.scrollArea_bottom+4
        gs.setBottom(p-4)
        self.scrollArea.setGeometry(gs)
        self.autoSlideBar()

        gg=self.labelBackground.geometry()
        if init_value:p=self.labelBackground_top+2 
        gg.setTop(p-2)
        self.labelBackground.setGeometry(gg)

        gt=self.labelLine.geometry()
        if init_value:p=self.labelLine_top+3
        gt.moveTo(QtCore.QPoint(gt.x(),p-3))
        self.labelLine.setGeometry(gt)

    def button_send_click(self,e):
        s=self.input_text.toPlainText()
        self.bot.send_data(s.encode('utf8'),self.user_info)
        self.input_text.setPlainText('')
        self.addMessage(s,ME,TEXT)
    def closeEvent(self,e):
        self.bot.message_dispatcher.pop(self.user_info['yxsid'])
