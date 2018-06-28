# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget

from PyQt5 import QtCore, QtGui, QtWidgets,Qt

from CoreWidget import *
import os
import gif,random

class Ui_Chat(object):

    def setupUi(self, Form,w,h,view,user_info,ox=0,oy=0):
        #view:上一个view，value：该对话的信息，ox，oy是该界面显示的位置左上角的坐标，默认为0，0

        self.Form=Form
        self.size=(w,h)
        self.isback=False
        self.view_last=view #用于返回上一个界面的变量
        self.max_text_height=2.5*CRITERION
        self.user_info=user_info #识别信息
        self.change_button=0 #用来判断是否要改变发送和功能按钮的逻辑变量
        #判断是要运行程序的计算器人  还是对话
        if user_info['name'] in myrobot:
            self.recognize='myrobot'

        else:
            self.recognize='customer'
        self.icon_other=self.get_icon(user_info['id_tag'])
        print(user_info['id_tag'])
        self.icon_me=self.get_icon(ME)
        self.icon_dict={ME:self.icon_me,OTHER:self.icon_other}
        #底边栏的高度

        tw1,tw2=int(100/720*w+0.2),int((100+520)/720*w+0.2)
        ph=CRITERION
        ph_top=ph

        self.Button_back = QtWidgets.QPushButton(Form)
        self.setButton(self.Button_back,"icon/back.jpg",tw1,ph,'Button_back',(ox, oy,tw1,ph),self.button_back_click)

        self.Button_title = YTextButton(Form)
        self.Button_title.setTextIcon(' {0}'.format(user_info['name']),(60,60,65),(255,255,255),(tw2-tw1,ph),'vcenter')
        self.setButton(self.Button_title,None,tw2-tw1,ph,'Button_title',(ox+tw1,oy,tw2-tw1,ph),self.button_title_click)

        self.Button_info = QtWidgets.QPushButton(Form)
        self.setButton(self.Button_info,"icon/contact_info.jpg",w-tw2,ph,'Button_info',(ox+tw2,oy,w-tw2,ph),self.button_info_click)
        
        self.line_width=1
        ph=100/1280*h
        pw1,pw2,pw3=ph,w-2*ph,w-ph

        self.labelBackground=QtWidgets.QLabel(Form)
        
        self.labelBackground.setStyleSheet('QWidget{background-color:rgb(237,237,237)}')
        self.labelBackground.setGeometry(ox,oy+h-ph,w,ph)
        self.labelBackground_top=oy+h-ph

        self.Button_speak = YButton(Form)
        self.setButton(self.Button_speak,"icon/speak.jpg",pw1,ph,'Button_speak',(ox,oy+h-ph,pw1,ph),self.button_info_click)

        self.Button_emotion = YButton(Form)
        self.setButton(self.Button_emotion,"icon/emotion.jpg",pw3-pw2,ph,'Button_emotion',(ox+pw2,oy+h-ph,pw3-pw2,ph),self.button_info_click)

        self.Button_send = YButton(Form)
        self.setButton(self.Button_send,"icon/send.jpg",w-pw3,ph,'Button_function',(ox+pw3,oy+h-ph,w-pw3,ph),self.button_send_click)
       
        self.Button_function = YButton(Form)
        self.setButton(self.Button_function,"icon/function_plus.jpg",w-pw3,ph,'Button_function',(ox+pw3,oy+h-ph,w-pw3,ph),self.button_info_click)
        

        self.input_text=YInputText(Form)
        pp=ph*0.2
        self.input_text.setGeometry( ox+pw1+pp , oy+h-ph+pp , pw2-pw1-pp*2 , ph-pp*2 )
        self.input_text.setStatusConnect(self.textStatus)
        self.input_text_top=oy+h-ph+pp
        self.input_text_height=self.input_text.document().size().height()

        self.labelButton=QtWidgets.QLabel(Form)
        self.textStatus('NOFOCUS')
        self.labelButton.setGeometry( ox+pw1+pp , oy+h-pp+2 , pw2-pw1-pp*2 , self.line_width )
        
        self.labelLine=QtWidgets.QLabel(Form)
        self.labelLine.setStyleSheet('QWidget{background-color:rgb(200,200,200)}')
        self.labelLine.setGeometry(ox,oy+h-ph,w,self.line_width)

        self.labelLine_top=oy+h-ph  #输入部分的顶部不能比该值小
        print(self.labelLine.geometry())


        self.scrollArea = YScrollArea(Form)
        self.bar=self.scrollArea.verticalScrollBar()
        self.scrollArea.setGeometry(QtCore.QRect(0, ph_top, w, h-ph_top-ph-1))
        self.scrollArea_bottom=ph_top+h-ph_top-ph-1

        self.scrollArea.setStyleSheet("border:none;")
        self.scrollArea.setObjectName("scrollArea")
        self.scrollWidget_message = YWidget()#显示对话的Widget
        self.scrollWidget_message.setGeometry(QtCore.QRect(0, 0, w, h-ph_top-ph))
        # self.scrollWidget_message.setMinimumSize(QtCore.QSize(w, h-ph_top-ph-5))
        self.scrollWidget_message_size=w, h-ph_top-ph
        self.scrollWidget_message_bottom=0  #显示信息最底部的位置

        self.scrollWidget_message.setObjectName("scrollWidget_message")
        # self.pushButton1 = QtWidgets.QPushButton(self.scrollWidget_message)
        # self.pushButton1.setGeometry(QtCore.QRect(40, 30, 92, 36))
        
        self.scrollArea.setWidget(self.scrollWidget_message)

        self.Buttons=[self.Button_send,self.Button_back,self.labelLine,self.labelBackground,self.Button_title,self.Button_info,self.scrollArea,self.Button_speak,
        self.Button_emotion,self.Button_function,self.labelButton,self.input_text]

        if self.recognize == 'myrobot':self.robot_run()
    def robot_run(self):
        if self.user_info['id_tag']=='GIFMAKER':
            gif.run(self)
    def get_icon(self,value):
        icon = QtGui.QIcon()
        if value is ME:
            icon.addPixmap(QtGui.QPixmap('icon_users/me.png'))
        else:
            icon.addPixmap(QtGui.QPixmap('icon_users/{0}.png'.format(value)))
        return icon
    def addMessage(self,value,identity=OTHER,Format=TEXT): 

        button=YTalkWidget(self.scrollWidget_message)
        button.setContent(value,Format,self.icon_dict[identity],self.scrollWidget_message_bottom,identity=identity)
        height=button.height()
        w,h=self.scrollWidget_message_size
        if self.scrollWidget_message_bottom+height>h:
            self.scrollWidget_message.resize(w,self.scrollWidget_message_bottom+height)
            self.scrollWidget_message.setMinimumSize(QtCore.QSize(w, self.scrollWidget_message_bottom+height))
            self.scrollWidget_message_size=w,self.scrollWidget_message_bottom+height
        self.scrollWidget_message_bottom+=height
        button.show()
        self.autoSlideBar()


    def autoSlideBar(self,pos='bottom'):
        if pos=='bottom':
            bottom=self.scrollWidget_message_bottom-self.scrollArea.height()+10
            self.bar.setValue(bottom)

    def setButton(self,B,I,pw,ph,objectname,position=None,connect=None):
        if I is not None:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(I) )
            B.setIcon(icon)
            B.setIconSize(QtCore.QSize(pw , ph))
        B.setObjectName(objectname)
        if position is not None:B.setGeometry(QtCore.QRect(*position))
        if connect is not None:B.clicked.connect(connect)

    def hide(self):
        for i in self.Buttons:
            i.hide()
    def show(self):
        for i in self.Buttons:
            i.show()

    def button_back_click(self):
        print('back')
        self.isback=True
        self.hide()
        self.view_last.show()
    def button_title_click(self):
        print('title')
        pass
    def button_text_click(self):
        if self.input_text is not None:
            return
        
    def button_info_click(self):
        print('info')
        pass
    def textStatus(self,f):
        if self.isback:return
        if f=='FOCUS':
            self.labelButton.setStyleSheet('QWidget{background-color:rgb(100,200,90)}') 
            print(self.input_text.d.isEmpty(),'FOCUS')
        elif f=='NOFOCUS':
            self.labelButton.setStyleSheet('QWidget{background-color:rgb(200,200,200)}')
        else:
            h_d,h_t,isEmpty=f 
            if h_d!=h_t and h_d<self.max_text_height:
                self.adjustInputTextSize(h_d)
            if isEmpty:
                self.Button_function.show()
                self.Button_send.hide()
            else:
                self.Button_send.show()
                self.Button_function.hide()
    def adjustInputTextSize(self,h_d):
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
        isEmpty=True
        s=self.input_text.toPlainText()
        self.input_text.setPlainText('')
        self.textStatus((self.input_text_height,self.input_text_height+1,isEmpty)) #使输入框恢复初始状态
        self.addMessage(s,ME,TEXT)
if __name__ == '__main__':
    '''
    主函数
    '''
    app = QApplication(sys.argv)
    # ui = Ui_Form()
    # ui.setupUi(mainWindow)
    # mainWindow.show()
    s=FunctionInputButton()
    sys.exit(app.exec_())