# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,QMainWindow,
                             QHBoxLayout, QVBoxLayout,QLabel,QFrame)
from PyQt5.QtCore import Qt,QPoint,QRect
from PyQt5.QtGui import QTextDocument,QPalette,QBrush,QColor,QFontMetrics,QPainter,QPen,QImage,QPixmap,QMovie
import sys
from pathlib import Path
import re
import os
from PIL import Image
from os.path import getsize
import yxspkg_songzviewer as ysv
from wxpy import TEXT, PICTURE, MAP, VIDEO, CARD, NOTE, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, SYSTEM
import video_player
import imageio
import webbrowser
import subprocess
from multiprocessing import Process
SYSTEM_YXS = 'SYSTEM_YXS'
global_font=QtGui.QFont()
global_font.setFamily('SimHei')


#宏定义值
AUTO_PUSH=1
CRITERION = 90/1280*640

ME=5 
OTHER=6
emoji = dict()
def read_emoji(path_emoji='./wechat_data/emoji'):
    p=Path(path_emoji)
    emo = {i.name[:-4]:str(i) for i in p.glob('*.png')}
    emoji.update(emo)
read_emoji()
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
        self.bottom = 0
        self.widgets = list()
        self.bar=self.verticalScrollBar()
    def wheelEvent(self,e):
        super().wheelEvent(e)
        # print(self.bar.value())
        
    def mousePressEvent(self,e):
        print(e.x(),e.y(),'Ps')
    def mouseReleaseEvent(self,e):
        print(e.x(),e.y(),'Rs')
    def resizeEvent(self,d):
        width_w = self.width()
        height_w = self.main_widget.height()
        self.main_widget.resize(width_w,height_w)
        for i in self.widgets:
            i.adjust_position(width_w)

    def append_element(self,element):
        
        h=element.height()
        mw,mh = self.main_widget.width(),self.main_widget.height()
        if h+self.bottom > mh:
            self.main_widget.resize(mw,self.bottom+h)
            self.main_widget.setMinimumSize(mw,self.bottom+h)
        element.move(0,self.bottom)
        self.bottom += h
        self.widgets.append(element)
    def insert_elements(self,elements):
        mw, mh = self.main_widget.width(), self.main_widget.height()
        heights = [e.height() for e in elements]
        delta_h = sum(heights)
        if delta_h + self.bottom > mh:
            self.main_widget.resize(mw,self.bottom+delta_h)
            self.main_widget.setMinimumSize(mw, self.bottom+delta_h)
        self.bottom += delta_h
        [i.move(0, i.pos().y()+delta_h) for i in reversed(self.widgets)]
            
        for i in reversed(elements):
            height = i.height()
            i.move(0,delta_h-height)
            delta_h -= height
            self.widgets.insert(0,i)

    def setWidget(self,w): #设置并记录该滚动区域的widget
        super().setWidget(w)
        self.main_widget = w
    def reset(self):
        self.bottom = 0
        self.main_widget.resize(self.main_widget.width(), 1)
        [i.hide() for i in self.widgets]
        self.widgets = list()
#滚动区域的Widget
class YWidget(QtWidgets.QWidget):
    def __init__(self,*d,**k):
        super().__init__(*d,**k)
    def mouseMoveEvent(self,e):
        # print(e.x(),e.y(),'M')
        pass
    def mousePressEvent(self,e):
        # print(e.x(),e.y(),'P')
        pass
    def mouseReleaseEvent(self,e):
        # print(e.x(),e.y(),'R')
        pass

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


#聊天时显示对话文字内容的bubble
class YSentenceBubble(QtWidgets.QWidget):
    me_color=100,200,90
    other_color=255,255,255
    other_rect_pos=(120/90*CRITERION,24/90*CRITERION)
    radius=10/90*CRITERION

    border_text=8/90*CRITERION #bubble和文字边框之间的距离

    font_size=int(30/90*CRITERION) #字体大小css  单文px

    max_width=450/90*CRITERION
    
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.Yw
        s='|'.join(emoji.keys())
        s=s.replace('[',r'\[')
        s=s.replace(']',r'\]')
        self.emoji_re = re.compile('({})'.format(s))
        self.min_height=d.min_height
    def paintEvent(self,e):
        qp = QPainter()
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
            Width=self.Ysize[0]+self.border_text 
            self.rect_pos=self.Yw-(self.other_rect_pos[0]+Width),self.other_rect_pos[1]
        else:
            self.color=QColor(*self.other_color)
            self.rect_pos=self.other_rect_pos
        self.window_height = max(self.Ysize[1]+self.border_text+self.rect_pos[1],self.min_height)
    def setMessage(self,text,identity=ME):
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setObjectName("textEdit")
        pl=QPalette()
        pl.setBrush(pl.Base,QBrush(QColor(255,0,0,0)))
        self.textEdit.setPalette(pl)
        self.textEdit.setStyleSheet("border:none;")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)
        
        self.d = self.textEdit.document() 
        self.d.setTextWidth(self.max_width) 
        def sub_func(t): 
            ft = ' < img src="{src}" height="{height}" /> ' 
            b = t.group() 
            return ft.format(src= emoji[b], height = int(self.font_size*1.3)) 
        tt = self.emoji_re.sub(sub_func, text) 
        text = '<p style="font-size:{height}px;font-family:\'Times New Roman\', Times, serif">{text}</p >'.format(text = tt.replace('\n', '<br />'), height=self.font_size) 
        self.textEdit.setHtml(text)



        width = self.d.idealWidth()   #获取对话框的宽度
        if sys.platform.startswith('linux'):
            width += int(self.font_size/4)
        self.Ysize=width,self.d.size().height()

        self.setBubble(identity)


class YSystemBubble(QtWidgets.QWidget):#显示系统提示消息
    radius = 5/90*CRITERION

    font_size = int(30/90*CRITERION)  # 字体大小css  单文px

    def __init__(self, d):
        super().__init__(d)
        self.Yw = d.Yw
        s = '|'.join(emoji.keys())
        s = s.replace('[', r'\[')
        s = s.replace(']', r'\]')
        self.emoji_re = re.compile('({})'.format(s))
        self.color = QColor(200,200,200)
        self.max_width = 7*CRITERION

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):

        Width, Height = self.Ysize
        self.rect = QRect(0, 0, Width, Height)
        self.textEdit.setGeometry(0, 0, Width, Height)
        qp.setBrush(QBrush(self.color))
        qp.setPen(QPen(self.color))
        qp.drawRoundedRect(self.rect, self.radius, self.radius)

    def setMessage(self, text, identity=ME):
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setObjectName("textEdit")
        pl = QPalette()
        pl.setBrush(pl.Base, QBrush(QColor(255, 0, 0, 0)))
        self.textEdit.setPalette(pl)
        self.textEdit.setStyleSheet("border:none;")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setReadOnly(True)

        self.d = self.textEdit.document()
        self.d.setTextWidth(self.max_width)

        def sub_func(t):
            ft = '< img src="{src}" height="{height}" />' #替换emoji
            b = t.group()
            return ft.format(src=emoji[b], height=self.font_size)
        tt = self.emoji_re.sub(sub_func, text)
        text = '<p style="font-size:{height}px;font-family:\'Times New Roman\', Times, serif">{text}</p >'.format(
            text=tt.replace('\n', '<br />'), height=self.font_size)
        self.textEdit.setHtml(text)

        width = self.d.idealWidth()  # 获取对话框的宽度
        if sys.platform.startswith('linux'):
            width += int(self.font_size/4)
        self.Ysize = width, self.d.size().height()
        self.resize(*self.Ysize)

#设置图片和动图的显示框
class YPictureBubble(QLabel):
    def __init__(self,widget):
        super().__init__(widget)
        self.parent_widget = widget
        self.setScaledContents(True)
    def setPicture(self,image_name):
        self.filename = image_name
        max_width = 300
        is_gif = False
        if image_name[-3:].lower() == 'gif':
            self.gif = QMovie(image_name)
            if self.gif.isValid():
                is_gif = True
                self.setMovie(self.gif)
                self.gif.start()
                g = self.gif.currentImage()
                w,h = (g.width(),g.height())
        if not is_gif:
            im = Image.open(image_name)
            w,h = im.size

            self.setPixmap(im.toqpixmap())
        
        if w>=h and w>max_width:
            ratio = max_width/w
        elif h>w and h>max_width:
            ratio = max_width/h
        else:
            ratio = 1
        w,h = int(w*ratio),int(h*ratio)
        self.resize(w,h)

class YTalkWidget(QtWidgets.QWidget):
    obj_name={ME:'me',OTHER:'other'}
    other_rect_topleft=(120/90*CRITERION,12/90*CRITERION)
    max_size=250/90*CRITERION
    min_size=104/90*CRITERION
    def __init__(self,d=None,Bot = None):
        super().__init__(d)
        self.Yw=d.width()
        self.bot = Bot
        self.pos_me=(self.Yw-110/90*CRITERION,12/90*CRITERION)
        self.pos_other=(30/90*CRITERION,12/90*CRITERION)
        self.pic_qsize=QtCore.QSize(80/90*CRITERION,80/90*CRITERION)
        self.min_height=104/90*CRITERION
        self.lable_geometry = None #显示消息widget的geometry
        self.message_label = None
    def setContent(self,value,Format,icon_name,identity,user_name=None):
        self.Format = Format 
        self.value = value
        if Format == NOTE:
            Format = SYSTEM_YXS
            identity = None
        self.identity=identity
        self.Format = Format
        if identity in (ME,OTHER):
            self.setPic(icon_name,self.obj_name[identity])
        if Format == TEXT:
            h=self.setMessage(value)
        elif Format == PICTURE:#显示表情或者图片
            h=self.setMessage_Picture(value)
        elif Format == SYSTEM_YXS:
            h=self.setMessage_System(value)
        elif Format == VIDEO:
            video_path = Path(value)
            path_video_cache = self.bot.thumbnail_path / ('thumbnail_'+video_path.name)
            path_video_cache = path_video_cache.with_suffix('.jpg')

            if not path_video_cache.is_file():
                reader = imageio.get_reader(value)
                img = reader.get_next_data()
                reader.close()
                img = Image.fromarray(img)
                w,h = img.size 
                if w>h:
                    rate = w/150
                else:
                    rate = h/150
                img.thumbnail((w//rate,h//rate))
                img.save(path_video_cache)
            h = self.setMessage_Picture(str(path_video_cache),is_video=True)
        elif Format == ATTACHMENT:
            h = self.setMessage_Attachment(value)
        elif Format == SHARING:
            h = self.setMessage_Attachment(value,is_sharing = True)
        else:
            h = self.setMessage('不支持的消息类型，请在手机中查看：{}\n{}'.format(Format,value))
        if user_name and identity is OTHER:
            dh = 15
            h += dh
            pos = self.message_label.pos()
            x,y = pos.x(), pos.y()
            if Format == TEXT:
                pic_width = self.pic_qsize.width()
                name_x = self.pos_other[0]+5+pic_width
                name_y = y+5
            else:
                name_x = x
                name_y = y
            self.name_label = QLabel(user_name,self)
            self.message_label.move(x,y+dh)
            self.name_label.move(name_x,name_y)
        self.resize(self.Yw,h)
    def mouseDoubleClickEvent(self,e): 
        if e.buttons() == Qt.LeftButton and self.lable_geometry:
            g = self.lable_geometry
            x,y,w,h = g.x(),g.y(),g.width(),g.height()
            m_x, m_y = e.x(),e.y()
            if not (x < m_x <x+w and y<m_y<y+h):
                return #点击不在区域内
            print('open a file')
            if self.Format in (PICTURE,VIDEO):
                if not Path(self.value).exists():
                    value = str(self.bot.path.parent.with_name('wechat_data') / 'icon' / 'error.jpg')
                else:
                    value = self.value
            if self.Format == PICTURE:
                self._display = ysv.GifPreview(name=value)
            elif self.Format == VIDEO:
                if sys.platform.startswith('linux'):
                    p = Process(target = subprocess.call,args=(['vlc',value],))
                    p.start()
                else:
                    self._play = video_player.Player([value])
                    self._play.show()
                    self._play.resize(700,600)
                    self._play.player.play()
            elif self.Format == SHARING:
                url = self.value.split()[0]
                webbrowser.open(url)
        else:
            pass
    def setMessage_System(self,value):
        self.system_bubble = YSystemBubble(self)
        self.message_label = self.system_bubble
        self.system_bubble.setMessage(value,None)
        w = (self.Yw - self.system_bubble.width()) // 2
        self.system_bubble.move(w,2)
        return self.system_bubble.Ysize[1]+4
    def adjust_position(self,width_w):#当窗口大小变化时调整对话内容的位置
        y=self.pos().y()
        sel_width = self.width()
        if self.identity is ME:
            pos_width=width_w-sel_width
        elif self.identity is None:
            pos_width = (width_w - sel_width)//2
        else:
            pos_width = 0
        self.move(pos_width, y)
    def setMessage(self,e): # 绘制用户文字信息
        self.message_bubble = YSentenceBubble(self)
        self.message_label = self.message_bubble
        self.message_bubble.setMessage(e,self.identity)
        h = self.message_bubble.window_height
        self.message_bubble.resize(self.Yw,h)
        return h+2

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
    def setMessage_Sharing(self,value):
        return self.setMessage_Attachment(value,True)
    def setMessage_Attachment(self,value,is_sharing = False):#定义显示附件的组件
        self.attachment_bubble = QLabel(self)
        self.message_label = self.attachment_bubble
        
        self.attachment_bubble.setFrameShape(QFrame.Box)
        self.attachment_bubble.setStyleSheet('QLabel{border-width:1px;border-style:solid;border-color:rgb(150,180,140);background-color:rgb(250,250,250)}')

        self.attachment_bubble.resize(int(5.5*CRITERION),int(1.5*CRITERION))
        if self.identity is ME:
            pos = self.pos_me[0]-self.attachment_bubble.width()-5,self.pos_me[1]
        else:
            pic_width = self.pic_qsize.width()
            pos = self.pos_other[0]+5+pic_width,self.pos_other[1]
        self.attachment_bubble.move(*pos)
        if is_sharing:
            icon_path = self.bot.path.parent.with_name('wechat_data') / 'icon' / 'icon_sharing.jpg'
        else:
            icon_path = self.bot.path.parent.with_name('wechat_data') / 'icon' / 'icon_file_red.jpg'
        self.file_icon = QLabel(self)
        self.file_icon.setScaledContents(True)
        pixmap = Image.open(icon_path).toqpixmap()
        self.file_icon.setPixmap(pixmap)
        w0,h0 = pos
        width = self.attachment_bubble.width()
        size = 50
        self.file_icon.setGeometry(w0+width-size*1.3,h0+0.2*CRITERION,size,size)

        bias = int(0.2*CRITERION)

        if not is_sharing:
            if Path(value).is_file():
                file_size = getsize(value)
            else:
                file_size = 0
            if file_size < 1024:
                fsize = '\n{}B'.format(file_size)
            elif file_size < 1024*1024:
                fsize = '\n{:.2f}KB'.format(file_size/1024)
            else:
                fsize = '\n{:.2f}KB'.format(file_size/1024/1024)
            text = Path(self.value).name+fsize
        else:
            n = value.find(' ')
            text = value[n+1:]
        self.text_label = QLabel(text ,self)
        self.text_label.setGeometry(w0+bias,h0+bias,width - size * 2.3 - bias, CRITERION)
        self.lable_geometry = self.attachment_bubble.geometry()
        return self.attachment_bubble.height()+10
    def setMessage_Picture(self,value,is_video=False):
        def get_thumbnail(value):
            p = Path(value)
            name_thum = 'thum_'+p.name
            path_thum = self.bot.thumbnail_path / name_thum

            if path_thum.exists():
                return str(path_thum)
            else:
                if not p.exists():
                    return str(self.bot.path.parent.with_name('wechat_data') / 'icon' / 'error.jpg')
                if getsize(value)<1024*100 or value.split('.')[-1].lower() == 'gif':
                    return value
                img = Image.open(p)
                w,h = img.size
                if w>h:
                    rate = w/150
                else:
                    rate = h/150
                img.thumbnail((w//rate,h//rate))
                img.save(path_thum)
                return str(path_thum)
        value = get_thumbnail(value)
        self.picture_bubble = YPictureBubble(self)#定义显示图片的组件
        self.message_label = self.picture_bubble
        self.picture_bubble.setPicture(value)
        if self.identity is ME:
            pos = self.pos_me[0]-self.picture_bubble.width()-5,self.pos_me[1]
        else:
            pic_width = self.pic_qsize.width()
            pos = self.pos_other[0]+5+pic_width,self.pos_other[1]
        self.picture_bubble.move(*pos)
        w,h = self.picture_bubble.width(),self.picture_bubble.height()
        if is_video:
            self.display_label = QLabel(self)
            self.display_label.setStyleSheet('QWidget{background-color:rgba(0,0,0,0)}')
            self.display_label.setScaledContents(True)
            display_path = self.bot.path.parent.with_name('wechat_data') / 'icon' /'video.png'
            pixmap = Image.open(display_path).toqpixmap()
            # pixmap.fill(Qt.transparent)
            self.display_label.setPixmap(pixmap)
            w0,h0 = pos
            size = 50
            self.display_label.setGeometry(w0+(w-size)//2,h0+(h-size)//2,size,size)
        self.lable_geometry = self.picture_bubble.geometry()
        return h



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
        self.sep = sep
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
            # print(pos,'pos')
            qp.drawLine(0.05*self.Yw,0,self.Yw*0.95,0)
        qp.end()
        qimg=QtGui.QPixmap.fromImage(img)
        icon=QtGui.QIcon()
        icon.addPixmap(qimg)
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(*size))
        # self.setGeometry(QtCore.QRect(*pos,*size))
        self.resize(*size)

    def YdrawText(self,text,pos,size,color,qp):
        qp.setPen(QtGui.QColor(*color))
        global_font.setPixelSize(size)
        qp.setFont(global_font)
        qp.drawText(pos[0],pos[1],1000,1000,QtCore.Qt.AlignLeft,text)
    def YdrawImage(self,filename,pic_rect,qp):
        image=QtGui.QImage(str(filename))
        qp.drawImage(QtCore.QRectF(*pic_rect),image)
    def mousePressEvent(self,e):
        self.setDesigning(*self.d,color_background=self.color_film,pos=self.p ,size=self.s,sep = self.sep)
    def mouseReleaseEvent(self,e):
        self.setDesigning(*self.d,color_background=self.color_background,pos=self.p ,size=self.s,sep = self.sep)
        self.father_surface.goto_view(self.Yname)
    def setName(self,name,father):
        self.Yname=name
        self.father_surface=father

class FunctionButton(YDesignButton):
    def __init__(self,d):
        super().__init__(d)
        self.Yw=d.width()
        self.Yh=100/90
    def adjust_position(self,*d):
        pass
    def setContent(self,picture,name,pos=(0,0),sep=False,size_rate = 0.8):
        #picture:功能按钮的图片
        #name:功能按钮显示出来的名字

        w=self.Yw
        h=self.Yh*CRITERION
        color_background=self.color_background

        color_text_name=(63,63,63)
        picture_rect=(33/90*CRITERION,18/90*CRITERION,63/90*CRITERION,63/90*CRITERION)
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
        self.statusConnect = lambda x:None
        self.d=self.document()

    def press_enter_connect(self,func):
        self.press_enter = func
        
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
    def keyPressEvent(self,e): #输入框按键事件
        value = e.key()
        if value == Qt.Key_Return:
            self.press_enter()
            return
        super().keyPressEvent(e)
    def paintEvent(self,d):
        super().paintEvent(d)
        self.statusConnect((self.d.size().height(),self.height(),self.d.isEmpty()))


if __name__=='__main__':
    '''__debug__'''
    pass