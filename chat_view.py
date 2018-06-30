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
import wxpy
import functions
import time
import sys 
from pathlib import Path

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

    def setupUi(self,Bot ,user_info:dict ,me_info:dict):
        Form = self
        self.Form=self
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

        self.is_encrypt = False

        
        self.setLayout(layout)
        self.show()


        self.bot = Bot

        self.time_before = '{:.2f}'.format(9529456999.83)
        self.time_latest = 0
        self.time_pre = 0
        self.at_bottom = True
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

    def click_name(self,*d):#点击用户名响应函数
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

    def button_send_click(self,e):#发送消息
        def is_file(text):
            if Path(text.strip()).is_file():
                return text.strip()
                
            if platform.startswith('win'):
                if text.strip().startswith('file:///'):
                    return text.strip()[8:]
                else:
                    return False 
            elif platform.startswith('linux'):
                if text.strip().startswith('file://'):
                    return text.strip()[7:]
                else:
                    return False
        s=self.input_text.toPlainText()
        if not s.strip():
            return
        self.input_text.setPlainText('')
        fs = is_file(s)
        if fs:
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
