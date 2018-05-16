# -*- coding: utf-8 -*-

#
# Created by: PyQt5 UI code generator 5.9
#
import sys

from PyQt5.QtWidgets import QApplication , QMainWindow,QWidget

from PyQt5 import QtCore, QtGui, QtWidgets

from CoreWidget import *

import os
class ConversationButton(YDesignButton):
    def setContent(self,picture,name,content,time,w,h,color_background=None):
        picture = str(picture)
        if color_background is None:
            color_background=self.color_background
        self.Ypicture=picture
        self.Yname=name
        self.Ycontent=content 
        self.Ytime=time
        self.Yw=w 
        self.Yh=h 

        font=global_font
        image=QtGui.QImage(picture)
        color_text_name=(63,63,63)
        color_text_content=(161,161,161)
        color_text_time=(190,190,190)

        picture_rect=(28/90*CRITERION,16/90*CRITERION,97/90*CRITERION,97/90*CRITERION)

        name_size=32/90*CRITERION
        content_size=24/90*CRITERION
        time_size=20/90*CRITERION

        pos_name=(148/90*CRITERION,28/90*CRITERION)
        pos_content=(148/90*CRITERION,74/90*CRITERION)
        pos_time=(w-86/90*CRITERION,28/90*CRITERION)

        qp = QtGui.QPainter()
        icon=QtGui.QIcon()

        img=QtGui.QImage(w,h,QtGui.QImage.Format_RGB32)
        img.fill(QtGui.QColor(*color_background))
        qp.begin(img)
        self.YdrawText(name,pos_name,name_size,color_text_name,qp)
        self.YdrawText(content,pos_content,content_size,color_text_content,qp)
        self.YdrawText(time,pos_time,time_size,color_text_time,qp)
        qp.drawImage(QtCore.QRectF(*picture_rect),image)
        qp.setPen(QtGui.QColor(225,225,225))
        qp.drawRect(QtCore.QRectF(-10,0,w+10,h))
        qp.end()
        qimg=QtGui.QPixmap.fromImage(img)
        icon.addPixmap(qimg)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(w,h))
        self.resize(self.Yw,self.Yh)
    def YdrawText(self,text,pos,size,color,qp):
        qp.setPen(QtGui.QColor(*color))
        global_font.setPixelSize(size)
        qp.setFont(global_font)
        qp.drawText(pos[0],pos[1],200,40,QtCore.Qt.AlignLeft,text)
    def mousePressEvent(self,e):
        self.setContent(self.Ypicture,self.Yname,self.Ycontent,self.Ytime,self.Yw,self.Yh,self.color_film)
        
    def mouseReleaseEvent(self,e):
        self.setContent(self.Ypicture,self.Yname,self.Ycontent,self.Ytime,self.Yw,self.Yh,self.color_background)
        self.father_surface.goto_view(self.user_info)
    def setName(self,user_info,father):
        self.user_info=user_info
        self.father_surface=father
    def adjust_position(self,*d):
        pass


class ConversationFrame(object):

    def setupUi(self, Form,ox,oy,w,h,father=None):
        self.father_view=father
        self.Form=Form
        self.size=(w,h)
        self.bot = self.father_view.bot
        self.bot.update_conversation = self.update_conversation
        self.conversation_height = int(CRITERION*(128/90))
        self.conversation_width = self.size[0]

        self.scrollArea = YScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(ox, oy, w, h))
        self.scrollArea.setObjectName("conversation_surface")
        self.scrollWidget_conversation = YWidget()
        self.scrollArea.setWidget(self.scrollWidget_conversation)
        self.drawConversations()
        

    def drawConversations(self):
        print('draw'*8)
        conversation_list = self.getConversations()
        print(conversation_list)
        for info in conversation_list:
            p1 = ConversationButton(self.scrollWidget_conversation)
            p1.setName(info,self)
            p1.setContent(info['img_path'],info['name'],info['text'],'前天',self.conversation_width,self.conversation_height)
            self.scrollArea.append_element(p1)
            p1.show()

    def update_conversation(self):
        self.scrollArea.reset()
        self.drawConversations()
    def goto_view(self,user_info):
        #跳转到conversation的内容界面
        self.father_view.goto_view('chat',user_info)
    def getConversations(self): #获取对话列表
        return self.bot.conversation_list()
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
    
