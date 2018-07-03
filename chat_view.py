# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLineEdit,QDialog,QCheckBox
from PyQt5 import QtCore, QtGui, QtWidgets,Qt
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from CoreWidget import *

import functions
import time
import sys 
from pathlib import Path
from os import path as path_

platform = sys.platform

class async_send(QThread):
    trigger = pyqtSignal(tuple)
    def __init__(self,target,args=tuple()):
        super().__init__()
        self.target = target
        self.args = args
    def run(self):
        try:
            succ,info = self.target(*self.args,update_con = False)
        except Exception as e:
            print(e)
            succ,info = False,'Failed to send'
        self.trigger.emit((succ,info,self.args))
class Ui_Chat(QWidget):
    def __init__(self):
        super().__init__()
        self.scrollWidget_message_size= 200,70
        self.scrollWidget_message_bottom = 0

        
    def set_chat_info(self,Bot,user_info):
        self.user_info = user_info
        self.me_info = Bot.get_me_info()
        self.bot = Bot
        self.is_encrypt = False
        self.isback=False
        self.time_before = '{:.2f}'.format(9529456999.83)
        self.time_latest = 0
        self.time_pre = 0
        self.members_info = dict() #群消息时存储群成员信息的字典
        if user_info['yxsid'] in Bot.senders:
            if Bot.get_user_type(Bot.senders[user_info['yxsid']])==2:
                self.is_group = True#该对话是否是群对话
            else:
                self.is_group = False
        else:
            print('No user')
            self.is_group = True
        print('群对话',self.is_group)
        self.icon_other=QtGui.QIcon(user_info['img_path'])
        self.icon_me = QtGui.QIcon(self.me_info['img_path'])
        self.icon_dict={ME:self.icon_me,OTHER:self.icon_other}
        self.setWindowTitle(user_info['name'])
        self.setWindowIcon(self.icon_other)
    def setupUi(self,Bot ,user_info:dict,father):
 
        self.father = father
        self.Form=self
        self.set_chat_info(Bot,user_info)
        self.resize(520,520)
        self.blabel = QLabel(self)
        self.blabel.setStyleSheet('QWidget{background-color:rgb(255,255,255)}')

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

        self.setLayout(layout)
        self.show()

        self.insert_some_message(100)
    def insert_some_message(self,nums):    
        an = list(self.bot.read_content(self.user_info['yxsid'],time_before= self.time_before,nums = nums))
        an.reverse()
        ans = []
        me_yxsid = self.me_info['yxsid']
        for yxsid, value, msg_type, time_ in an:
            if yxsid == '0' or yxsid == me_yxsid:
                idendity = ME
            else:
                idendity = OTHER
            ans.append((yxsid,value, idendity, msg_type, time_))
        self.insertMessage(ans)
    def resizeEvent(self,d):#根据窗口大小调整白色背景的大小以及发送键的位置
        size = self.size()
        self.blabel.resize(size)
        size_send = self.send_widget.size()
        size_send.setWidth(size.width())
        self.send_widget.resize(size_send)
        self.Button_send.move(size.width()-self.Button_send.width()-20,0)
        self.encrypt_box.move(size.width()-self.Button_send.width()-80,0)

    def click_name(self,d):#点击用户名响应函数
        print('press name button')
    def set_title(self):#设置对话框的标题
        size_title = 250,40
        title = QWidget()
        title.setMaximumHeight(40)
        title.setMinimumHeight(40)
        p=YTextButton(title)
        p.setTextIcon(self.user_info['name'],(255,255,255),(10,10,10),size_title,position='left')
        p.resize(*size_title)
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

        self.encrypt_box = QCheckBox('RSA',send_widget)
        self.encrypt_box.stateChanged.connect(self.encrypt_state)
        self.encrypt_box.resize(60, 30)
        return send_widget

    def encrypt_state(self, state):#加密状态改变
        if state == Qt.Checked:
            self.is_encrypt = True
            self.addMessage('Enable RSA',None,SYSTEM_YXS)
        else:
            self.is_encrypt = False
            self.addMessage('Disable RSA',None,SYSTEM_YXS)

    def generate_time_element(self,Time):
        if Time - self.time_latest > 300 and Time - self.time_pre > 60:
            time_button = YTalkWidget(self.scrollWidget_message,self.bot)
            Time_str = functions.get_latest_time(Time, True)
            time_button.setContent(Time_str, SYSTEM_YXS, None, None)
            time_button.show()
            self.time_latest = Time
        else:
            time_button = None
        self.time_pre = Time
        return time_button
    def addMessage(self,value:str,identity=OTHER,Format=TEXT,yxsid_send_user = None,is_slided=True): #value的值始终都为str类型
        Time = time.time()
        time_button = self.generate_time_element(Time)
        if time_button is not None: 
            self.scrollArea.append_element(time_button)
        button=YTalkWidget(self.scrollWidget_message,self.bot)
        if identity is not None:
            if self.is_group and identity == OTHER:
                icon = self.get_icon_group(yxsid_send_user)
            else:
                icon = self.icon_dict[identity]
        else:
            icon = None

        button.setContent(value,Format,icon,identity=identity,user_name_yxsid = yxsid_send_user)

        bar_value = self.bar.value()#计算bar的大小和位置，
        bar_height = self.scrollWidget_message.height()
        scroll_height = self.scrollArea.height()

        self.scrollArea.append_element(button)
        button.show()

        if is_slided or bar_height - bar_value - scroll_height < 0.2 * scroll_height:
            self.autoSlideBar()
    def get_icon_group(self,yxsid_send):
        if yxsid_send == '0':
            return self.icon_dict[ME]
        icon = self.members_info.get(yxsid_send)
        if icon is None:
            icon_path = self.bot.get_img_path(yxsid_send,self.user_info['yxsid'])
            icon = QtGui.QIcon(icon_path)
            self.members_info[yxsid_send]={'icon':icon}
        else:
            icon = icon['icon']
        return icon
    def insertMessage(self,msgs:list):#在对话前面插入历史对话信息
        
        def generate_element(msg):
            yxsid_send,value, identity, Format,_ = msg
            button = YTalkWidget(self.scrollWidget_message,self.bot)
            if self.is_group:
                icon = self.get_icon_group(yxsid_send)
            else:
                icon = self.icon_dict[identity]
            button.setContent(value, Format, icon, identity=identity,user_name_yxsid = yxsid_send)
            button.show()
            return button
        buttons = []
        time_latest, time_pre = self.time_latest,self.time_pre
        Time = 0
        for i in msgs:
            *_,Time = i
            Time = float(Time)
            time_button = self.generate_time_element(Time)
            if time_button is not None:
                buttons.append(time_button)
                
            buttons.append(generate_element(i))
        self.time_latest, self.time_pre = time_latest, time_pre

        self.scrollArea.insert_elements(buttons)
        self.autoSlideBar()
        self.time_latest =max(self.time_latest, Time)
    def autoSlideBar(self,pos='bottom'):
        if pos=='bottom':
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
    def accept_callback(self,content,msg_type,yxsid_send,yxsid_send_user):#yxsid_send本质是yxsid

        if yxsid_send == self.me_info['yxsid']:#判断消息是自己从手机发出的还是别人发过来的
            person = ME
        else:
            person = OTHER
        print('yxsid_send_user', yxsid_send_user)
        self.addMessage(content, person, msg_type,
                        yxsid_send_user=yxsid_send_user,is_slided=False)  # 显示消息
    

    def button_send_click(self,e):#发送消息
        def is_file(text):
            text = text.strip()
            if path_.exists(text):
                return text
                
            if platform.startswith('win'):
                if text.startswith('file:///'):
                    return text[8:]
                else:
                    return False 
            elif platform.startswith('linux'):
                if text.startswith('file://'):
                    return text[7:]
                else:
                    return False
        s=self.input_text.toPlainText()
        if not s.strip():
            return
        self.input_text.setPlainText('')
        fs = is_file(s)
        if fs and path_.exists(fs):
            data_path = fs
            suffix = data_path.split('.')[-1].lower()
            if suffix in ('jpg','png','jpeg','gif'):
                msg_type = PICTURE 
            elif suffix in ('mp4','mkv','flv','avi'):
                msg_type = VIDEO
            else:
                msg_type = ATTACHMENT
            s = data_path
        else:
            msg_type = TEXT
        self.asyncSend = async_send(self.bot.send_data,(s,msg_type,self.user_info,self.is_encrypt))
        self.asyncSend.trigger.connect(self.send_callback)
        self.asyncSend.start()
        
    def send_callback(self,args):
        print('send',args)
        succ,info,args_ = args
        s,msg_type,*_ = args_
        if not succ:
            self.addMessage(info,None,SYSTEM_YXS)
            self.input_text.setPlainText(s)
            return
        self.bot.async_update_conversation(info)
        self.addMessage(s,ME,msg_type)
        self.input_text.setFocus()
    def closeEvent(self,e):
        self.bot.message_dispatcher.pop(self.user_info['yxsid'])
        self.father.chat_view_dict.pop(self.user_info['yxsid'])
        self.destroy()

class Ui_Mobile(Ui_Chat):
    def setupUi(self, Form,w,h,view,user_info,Bot,ox=0,oy=0):
        #view:上一个view，value：该对话的信息，ox，oy是该界面显示的位置左上角的坐标，默认为0，0

        self.Form=Form
        self.set_chat_info(Bot,user_info)
        self.config_path = str(Bot.path.parent.with_name('wechat_data'))
        self.size=(w,h)
        self.isback=False
        self.view_last=view #用于返回上一个界面的变量
        self.max_text_height=2.5*CRITERION


        #底边栏的高度

        tw1,tw2=int(100/720*w+0.2),int((100+520)/720*w+0.2)
        ph=CRITERION
        ph_top=ph

        self.Button_back = QtWidgets.QPushButton(Form)
        self.setButton(self.Button_back,self.config_path+"/icon/back.jpg",tw1,ph,'Button_back',(ox, oy,tw1,ph),self.button_back_click)

        self.Button_title = YTextButton(Form)
        self.Button_title.setTextIcon(' {0}'.format(user_info['name']),(60,60,65),(255,255,255),(tw2-tw1,ph),'vcenter')
        self.setButton(self.Button_title,None,tw2-tw1,ph,'Button_title',(ox+tw1,oy,tw2-tw1,ph),self.button_title_click)

        self.Button_info = QtWidgets.QPushButton(Form)
        self.setButton(self.Button_info,self.config_path+"/icon/contact_info.jpg",w-tw2,ph,'Button_info',(ox+tw2,oy,w-tw2,ph),self.button_info_click)
        
        self.line_width=1
        ph=100/1280*h
        pw1,pw2,pw3=ph,w-2*ph,w-ph

        self.labelBackground=QtWidgets.QLabel(Form)
        
        self.labelBackground.setStyleSheet('QWidget{background-color:rgb(237,237,237)}')
        self.labelBackground.setGeometry(ox,oy+h-ph,w,ph)
        self.labelBackground_top=oy+h-ph

        self.Button_speak = YButton(Form)
        self.setButton(self.Button_speak,self.config_path+"/icon/speak.jpg",pw1,ph,'Button_speak',(ox,oy+h-ph,pw1,ph),self.button_info_click)

        self.Button_emotion = YButton(Form)
        self.setButton(self.Button_emotion,self.config_path+"/icon/emotion.jpg",pw3-pw2,ph,'Button_emotion',(ox+pw2,oy+h-ph,pw3-pw2,ph),self.button_info_click)

        self.Button_send = YButton(Form)
        self.setButton(self.Button_send,self.config_path+"/icon/send.jpg",w-pw3,ph,'Button_function',(ox+pw3,oy+h-ph,w-pw3,ph),self.button_send_click)
       
        self.Button_function = YButton(Form)
        self.setButton(self.Button_function,self.config_path+"/icon/function_plus.jpg",w-pw3,ph,'Button_function',(ox+pw3,oy+h-ph,w-pw3,ph),self.button_info_click)
        

        self.input_text=YInputText(Form)
        pp=ph*0.2
        self.input_text.setGeometry( ox+pw1+pp , oy+h-ph+pp , pw2-pw1-pp*2 , ph-pp*2 )
        self.input_text.setStatusConnect(self.textStatus)
        self.input_text_top=oy+h-ph+pp
        self.input_text_height=self.input_text.document().size().height()
        self.input_text.press_enter_connect(lambda :self.button_send_click(None))

        self.labelButton=QtWidgets.QLabel(Form)
        self.textStatus('NOFOCUS')
        self.labelButton.setGeometry( ox+pw1+pp , oy+h-pp+2 , pw2-pw1-pp*2 , self.line_width )
        
        self.labelLine=QtWidgets.QLabel(Form)
        self.labelLine.setStyleSheet('QWidget{background-color:rgb(200,200,200)}')
        self.labelLine.setGeometry(ox,oy+h-ph,w,self.line_width)

        self.labelLine_top=oy+h-ph  #输入部分的顶部不能比该值小


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
        self.insert_some_message(100)
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
        self.button_back_click()
        self.view_last.goto_view('chat',(self.user_info,True))
    def button_text_click(self):
        if self.input_text is not None:
            return
    def button_info_click(self):
        if self.is_encrypt:
            self.encrypt_state(False)
        else:
            self.encrypt_state(Qt.Checked)
    def textStatus(self,f):
        if self.isback:return
        if f=='FOCUS':
            self.labelButton.setStyleSheet('QWidget{background-color:rgb(100,200,90)}') 
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

