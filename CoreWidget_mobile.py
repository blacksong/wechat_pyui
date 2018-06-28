# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,QMainWindow,
                             QHBoxLayout, QVBoxLayout,QLabel)
from PyQt5.QtCore import Qt,QPoint,QRect
from PyQt5.QtGui import QTextDocument,QPalette,QBrush,QColor,QFontMetrics,QPainter,QPen,QImage,QPixmap
import sys,time,random
#滚动区域
global_font=QtGui.QFont()
global_font.setFamily('SimHei')

myrobot=['GIFMAKER']

#宏定义值
TEXT=2
AUTO_PUSH=1
PICTURE = 3
GIF = 4
CRITERION = 90/1280*640

ME=5
OTHER=6

class YButton(QtWidgets.QPushButton):
    def __init__(self,d=None):
        super().__init__(d)
    def tt(self):
        pass



class YScrollArea(QtWidgets.QScrollArea):
    def __init__(self,*d,**k):
        super().__init__(*d,**k)
        self.setAcceptDrops(False)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
    def mouseMoveEvent(self,e):
        print(e.x(),e.y(),'Ms')
    def mousePressEvent(self,e):
        print(e.x(),e.y(),'Ps')
    def mouseReleaseEvent(self,e):
        print(e.x(),e.y(),'Rs')
#滚动区域的Widget
class YWidget(QtWidgets.QWidget):
    def __init__(self,*d,**k):
        super().__init__(*d,**k)
    def mouseMoveEvent(self,e):
        print(e.x(),e.y(),'M')
    def mousePressEvent(self,e):
        print(e.x(),e.y(),'P')
    def mouseReleaseEvent(self,e):
        print(e.x(),e.y(),'R')

class YTextButton(QtWidgets.QPushButton):
    position_dict={'center':Qt.AlignCenter,'left':Qt.AlignLeft,'hcenter':Qt.AlignHCenter,'vcenter':Qt.AlignVCenter,'justify':Qt.AlignJustify}
    def setTextIcon(self,text,color_background,color_text,icon_size,position='center',font=None,font_percent_size=0.4):
        position_qt=self.position_dict[position.lower()]
        qp = QtGui.QPainter()
        icon=QtGui.QIcon()
        if font is None:
            font=global_font
            font.setPixelSize(icon_size[1]*font_percent_size)
        img=QtGui.QImage(icon_size[0],icon_size[1],QtGui.QImage.Format_RGB32)
        img.fill(QtGui.QColor(*color_background))
        qp.begin(img)
        qp.setPen(QtGui.QColor(*color_text))
        qp.setFont(font)
        qp.drawText(img.rect(), position_qt,text)
        qp.end()
        qimg=QtGui.QPixmap.fromImage(img)
        icon.addPixmap(qimg)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(*icon_size))

#显示图片
class YPictureBubble(QtWidgets.QLabel):
    
    def __init__(self,d=None):
        super().__init__(d)
        self.Yw=d.width()
    def YSetPicture(self,p,identity):
        pic=QImage(p)
        self.setPixmap

    def YSetGif(self,p,identity):
        pass
#聊天时显示对话文字内容的bubble
class YSentenceBubble(QtWidgets.QWidget):
    me_color=100,200,90
    other_color=255,255,255
    other_triangle=(QPoint(100,100),QPoint(120,80),QPoint(120,120))
    me_triangle=(QPoint(140,140),QPoint(120,80),QPoint(120,120))
    other_rect_pos=(120/90*CRITERION,24/90*CRITERION)
    radius=10/90*CRITERION

    border_text=8/90*CRITERION #bubble和文字边框之间的距离

    font_size=int(30/90*CRITERION) #字体大小css  单文px
    max_width=450/90*CRITERION
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.Yw
        
        self.min_height=d.min_height
    def paintEvent(self,e):
        qp = QPainter()
        QPoint
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()
 
    def drawWidget(self, qp):

        Width,Height=self.Ysize
        self.rect=QRect(self.rect_pos[0]-self.border_text,self.rect_pos[1]-self.border_text,Width+self.border_text*2,Height+self.border_text*2)
        self.textEdit.setGeometry(self.rect_pos[0],self.rect_pos[1],Width,Height)
        qp.setBrush(QBrush(self.color))
        qp.setPen(QPen(self.color))
        qp.drawRoundedRect(self.rect,self.radius,self.radius)
    
    def setBubble(self,identity=ME):
        if identity is ME:
            self.color=QColor(*self.me_color)
            self.triangle = self.me_triangle
            Width=self.Ysize[0]+self.border_text 
            self.rect_pos=self.Yw-(self.other_rect_pos[0]+Width),self.other_rect_pos[1]
        else:
            self.color=QColor(*self.other_color)
            self.triangle = self.me_triangle
            self.rect_pos=self.other_rect_pos
        self.window_height = max(self.Ysize[1]+self.border_text+self.rect_pos[1],self.min_height)
    def setMessage(self,text,identity=ME):
        self.textEdit = QtWidgets.QTextEdit(self)
        # self.textEdit.setGeometry(0,0,self.max_width,90)
        self.textEdit.setObjectName("textEdit")
        pl=QPalette()
        pl.setBrush(pl.Base,QBrush(QColor(255,0,0,0)))
        self.textEdit.setPalette(pl)
        self.textEdit.setStyleSheet("border:none;")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        global_font.setPixelSize(self.font_size)
        self.f=QFontMetrics(global_font,self.textEdit)
        self.d=self.textEdit.document()
        self.textEdit.setPlainText(text)
        self.d.setTextWidth(self.max_width)
        print(self.f.width(text))
        self.Ysize=min(self.f.width(text)+self.font_size/2,self.d.size().width()),self.d.size().height()
        print(self.Ysize)

        self.setBubble(identity)

class YTalkWidget(QtWidgets.QWidget):
    obj_name={ME:'me',OTHER:'other'}
    other_rect_topleft=(120/90*CRITERION,12/90*CRITERION)
    max_size=250/90*CRITERION
    min_size=104/90*CRITERION
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.width()
        self.pos_me=(self.Yw-110/90*CRITERION,12/90*CRITERION)
        self.pos_other=(30/90*CRITERION,12/90*CRITERION)
        self.pic_qsize=QtCore.QSize(80/90*CRITERION,80/90*CRITERION)
        self.min_height=104/90*CRITERION
    def setContent(self,value,Format,icon_name,pos_h,identity):
        self.identity=identity
        # value='232.jpg'
        # Format=PICTURE
        self.pos_h=pos_h
        self.setPic(icon_name,self.obj_name[identity])
        if Format is TEXT:
            h=self.setMessage(value)
            self.message_bubble.resize(self.Yw,h)
        elif Format is PICTURE:
            h=self.setMessage_Picture(value)
        self.setGeometry(0,pos_h,self.Yw,h)
    def setMessage(self,e): # 绘制用户文字信息
        self.message_bubble = YSentenceBubble(self)
        self.message_bubble.setMessage(e,self.identity)
        return self.message_bubble.window_height
    def setPic(self,icon_name,oname): #绘制用户头像
        self.figure_button=YButton(self)
        self.figure_button.setIcon(icon_name)
        self.figure_button.setIconSize(self.pic_qsize)
        self.figure_button.setObjectName(oname)
        if self.identity is ME:
            pos=self.pos_me
        else:
            pos=self.pos_other
        self.figure_button.setGeometry(*pos,80/90*CRITERION,80/90*CRITERION)
    def setMessage_Picture(self,value):
        if isinstance(value,str):
            qimg=QImage(value)
        else:
            qimg=value
        max_wh =max(qimg.size().width(),qimg.size().height())
        if max_wh>self.max_size:factor=self.max_size/max_wh
        elif max_wh < self.min_size:factor=self.min_size/max_wh
        else:factor=1
        qimg=qimg.scaled(factor * qimg.size())
        self.label_picture=QLabel(self)
        self.label_picture.setPixmap(QPixmap.fromImage(qimg))
        w,h=qimg.size().width(),qimg.size().height()
        if self.identity is ME:
            pos=self.Yw-(self.other_rect_topleft[0]+w),self.other_rect_topleft[1]
        else:
            pos=self.other_rect_topleft
        self.label_picture.move(*pos)
        print(pos)
        return h+pos[1]


class YDesignButton(QtWidgets.QPushButton):
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.width()
        self.Yh=100/90
        self.color_background=(255,255,255)
        self.color_film=(220,220,220)
    def setDesigning(self,*d,color_background=(255,255,255),pos=(0,0),size=(2*CRITERION,CRITERION),sep=False):
        self.d=d
        self.p=pos
        self.s=size
        qp = QtGui.QPainter()
        img=QtGui.QImage(*size,QtGui.QImage.Format_RGB32)
        img.fill(QtGui.QColor(*color_background))
        qp.begin(img)
        for i,v in d:
            if i is TEXT:
                self.YdrawText(*v,qp)
            elif i is PICTURE:
                self.YdrawImage(*v,qp)
            else:
                pass
        if sep is True:
            qp.setPen(QColor(200,200,200))
            print(pos,'pos')
            qp.drawLine(0.05*self.Yw,0,self.Yw*0.95,0)
        qp.end()
        qimg=QtGui.QPixmap.fromImage(img)
        icon=QtGui.QIcon()
        icon.addPixmap(qimg)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(*size))
        self.setGeometry(QtCore.QRect(*pos,*size))

    def YdrawText(self,text,pos,size,color,qp):
        qp.setPen(QtGui.QColor(*color))
        global_font.setPixelSize(size)
        qp.setFont(global_font)
        qp.drawText(pos[0],pos[1],1000,1000,QtCore.Qt.AlignLeft,text)
    def YdrawImage(self,filename,pic_rect,qp):
        image=QtGui.QImage(filename)
        qp.drawImage(QtCore.QRectF(*pic_rect),image)
    def mousePressEvent(self,e):
        self.setDesigning(*self.d,color_background=self.color_film,pos=self.p ,size=self.s)
    def mouseReleaseEvent(self,e):
        self.setDesigning(*self.d,color_background=self.color_background,pos=self.p ,size=self.s)
        self.father_surface.goto_view(self.Yname)
    def setName(self,name,father):
        self.Yname=name
        self.father_surface=father

class FunctionButton(YDesignButton):
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.width()
        self.Yh=100/90
        
    def setContent(self,picture,name,pos=(0,0),sep=False):
        #picture:功能按钮的图片
        #name:功能按钮显示出来的名字

        w=self.Yw
        h=self.Yh*CRITERION
        color_background=self.color_background

        color_text_name=(63,63,63)
        picture_rect=(41/90*CRITERION,26/90*CRITERION,47/90*CRITERION,47/90*CRITERION)
        name_size=30/90*CRITERION
        pos_name=(124/90*CRITERION,34/90*CRITERION)
        arg1=PICTURE,(picture,picture_rect)
        arg2=TEXT,(name,pos_name,name_size,color_text_name)
        self.setDesigning(arg1,arg2,pos=pos,size=(w,h),sep=sep)
#微信信息输入框
class YInputText(QtWidgets.QTextEdit):
    def __init__(self,d):
        super().__init__(d)
        self.max_length=2*CRITERION
        pl=QPalette()
        pl.setBrush(pl.Base,QBrush(QColor(255,0,0,0)))
        self.setPalette(pl)
        self.setStyleSheet("border:none;")
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.d=self.document()
    def focusInEvent(self,e):
        super().focusInEvent(e)
        self.statusConnect('FOCUS')
        self.statusConnect((self.d.size().height(),self.height(),self.d.isEmpty()))
    def focusOutEvent(self,e):
        super().focusInEvent(e)
        self.statusConnect('NOFOCUS')
    def setStatusConnect(self,p):
        self.statusConnect=p
    def keyReleaseEvent(self,e):
        self.statusConnect((self.d.size().height(),self.height(),self.d.isEmpty()))
    def paintEvent(self,d):
        super().paintEvent(d)
        self.statusConnect((self.d.size().height(),self.height(),self.d.isEmpty()))
if __name__=='__main__':
    for i in dir(QtWidgets.QTextEdit):
        if i.lower().find('event')!=-1:
            print(i)