import sys,os
from PyQt5.QtWidgets import QApplication ,QWidget,QSystemTrayIcon
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets,Qt
from CoreWidget import *
import CoreWidget
import chat_view
import ConversationFrame,MeFrame,ContactFrame,DiscoverFrame
import WelcomeFrame
import ctypes
if sys.platform.startswith('win'):#为了使任务栏图标和标题栏图标一样，需要ctypes的设置
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
    del ctypes
global_app = [None]
class Ui_Form:
    def __init__(self, Form, h=1280/90, w=720/90):
        super().__init__()
        self.Form=Form 
        h, w = h*CRITERION, w*CRITERION
        Form.setObjectName("Form")
        Form.resize(w, h)
        Form.setMinimumSize(QtCore.QSize(w, h))
        Form.setMaximumSize(QtCore.QSize(w, h))
        self.size = (w, h)
        self.bot=None #设置机器人变量 初始为None，登录后会有值，在welcomeFrame中进行赋值
        self.start_login(True)
        self.chat_view_dict=dict()
        Form.chat_view_dict = self.chat_view_dict

        #在系统托盘显示图标
        self.pannelIcon = QSystemTrayIcon(Form)
        self.system_icon = QtGui.QIcon(WECHAT_DATA_PATH+'icon/WeChat.ico')
        self.pannelIcon.setIcon(self.system_icon)
        self.pannelIcon.show()
        self.pannelIcon.setToolTip("微信")
        Form.del_funs.append(self.close_chat)#关闭对话框 当关闭主程序的时候

    def start_login(self,state=None):#进入登录界面 
        w,h = self.size
        # cache相当于设置了整个用户数据文件的存储位置
        cache = Path(sys.path[0]) / Path('user_data/log_in_cache') / 'wx.pkl'  
        if not cache.parent.exists():
            os.makedirs(cache.parent)
        self.welcome = WelcomeFrame.WelcomeFrame(cache)
        t = self.welcome.setupUi(self.Form, 0, 0, w, h, father=self)
    def setupUi(self):
        Form = self.Form
        w,h=self.size

        #底边栏的高度
        ph=int(0.15*w)

        pw=int(w/4)
        pw+=1
        self.horizontalLayoutWidget = QtWidgets.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, h-ph, w, ph))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.Button_1 = YButton(self.horizontalLayoutWidget)
        self.Button_1.setObjectName("Button_1")
        self.horizontalLayout.addWidget(self.Button_1)

        self.Button_2 = YButton(self.horizontalLayoutWidget)
        self.Button_2.setObjectName("Button_2")
        self.horizontalLayout.addWidget(self.Button_2)

        self.Button_3 = YButton(self.horizontalLayoutWidget)
        self.Button_3.setObjectName("Button_3")
        self.horizontalLayout.addWidget(self.Button_3)

        self.Button_4 = YButton(self.horizontalLayoutWidget)
        self.Button_4.setObjectName("Button_4")
        self.horizontalLayout.addWidget(self.Button_4)

        self.setButton(self.Button_1,WECHAT_DATA_PATH+"icon/button1_ok.jpg",pw,ph,'Button_1',self.button1_click)

        self.setButton(self.Button_2,WECHAT_DATA_PATH+"icon/button2_no.jpg",pw,ph,'Button_2',self.button2_click)

        self.setButton(self.Button_3,WECHAT_DATA_PATH+"icon/button3_no.jpg",pw,ph,'Button_3',self.button3_click)

        self.setButton(self.Button_4,WECHAT_DATA_PATH+"icon/button4_no.jpg",pw,ph,'Button_4',self.button4_click)
        #顶部设计
        tw1,tw2=int(490/720*w+0.2),int((490+94)/720*w+0.2)
        ph_top=CRITERION

        self.Button_name = YTextButton(Form)
        self.Button_name.setTextIcon(' 微信',(60,60,65),(255,255,255),(tw1,ph_top),'vcenter')
        self.setButton(self.Button_name,None,tw1,ph_top,'Button_title',self.button_name_click)
        self.Button_name.setGeometry(QtCore.QRect(0, 0,tw1,ph_top))


        self.Button_search = YButton(Form)
        self.setButton(self.Button_search,WECHAT_DATA_PATH+"icon/search.jpg",tw2-tw1,ph_top,'Button_search',self.button_search_click)
        self.Button_search.setGeometry(QtCore.QRect( tw1,0,tw2-tw1,ph_top))

        self.Button_plus = YButton(Form)
        self.setButton(self.Button_plus,WECHAT_DATA_PATH+"icon/plus.jpg",w-tw2,ph_top,'Button_plus',self.button_plus_click)
        self.Button_plus.setGeometry(QtCore.QRect( tw2,0,w-tw2,ph_top))

        #主界面显示
        self.surface_list=[None]*4
        self.surface_rect=0,ph_top,w,h-ph_top-ph
        self.surface=ConversationFrame.ConversationFrame()
        self.surface.setupUi(self.Form,0,ph_top,w,h-ph_top-ph,self)
        self.surface_list[0]=self.surface
        self.surface.show()

        self.active=1
        self.redirect()

        self.timer = QtCore.QTimer(self.Form)
        self.timer.timeout.connect(self.auto_run)
        self.timer.start(120000)

        
    def auto_run(self):#间隔一段时间自动运行
        self.bot.write_auto()
    def redirect(self):
    	# self.button1_click(None)
        pass

    def setButton(self,B,I,pw,ph,objectname,connect=None):
        if I is not None:
            icon = QtGui.QIcon(I)
            B.setIcon(icon)

            B.setIconSize(QtCore.QSize(pw , ph))
        B.setObjectName(objectname)
        if connect is not None:B.clicked.connect(connect)

    def release_button(self):
        if self.active==1:
            self.button1_click(AUTO_PUSH)
        elif self.active==2:
            self.button2_click(AUTO_PUSH)
        elif self.active==3:
            self.button3_click(AUTO_PUSH)
        else:
            self.button4_click(AUTO_PUSH)
    def hide(self):
        self.horizontalLayoutWidget.hide()
        self.Button_name.hide()
        self.Button_plus.hide()
        self.Button_search.hide()
    def show(self):
        self.horizontalLayoutWidget.show()
        self.Button_name.show()
        self.Button_plus.show()
        self.Button_search.show()

    def goto_view(self,kind,value):#功能跳转，调度
        if kind == 'chat':
            value,is_window = value
            if value['yxsid'] in self.chat_view_dict:
                frame = self.chat_view_dict[value['yxsid']]
                frame.showNormal()
                frame.activateWindow()
                return  # 保证一个窗口只被打开一次
                
            if is_window:
                view_active=chat_view.Ui_Chat()
                view_active.setupUi(Bot = self.bot,user_info = value, father = self)
                self.bot.message_dispatcher[value['yxsid']] = view_active.accept_callback
                view_active.show()
                self.chat_view_dict[value['yxsid']] = view_active
            else:
                self.view_active_in=chat_view.Ui_Mobile()
                self.view_active_in.setupUi(self.Form,self.size[0],self.size[1],self,value,self.bot)
                self.bot.message_dispatcher[value['yxsid']
                                            ] = self.view_active_in.accept_callback
                self.view_active_in.show()
        elif kind == 'LogOut':
            self.log_out()
        else:
            pass
    def log_out(self):#退出当前登录
        self.bot.write_back()
        self.welcome.loginthread.quit()
        self.bot.logout()
        self.start_login(False)
        self.hide()
    def button_name_click(self):
        print('name')
    def button_search_click(self):
        print('search')
    def button_plus_click(self):
        print('plus')
    def button1_click(self,k):
        # k is False: 鼠标点击 吗
        img = None
        if self.active!=1:
            img=WECHAT_DATA_PATH+"icon/button1_ok.jpg"
            self.release_button()
            self.active=1
            if self.surface_list[0] is None:
                surface=ConversationFrame.ConversationFrame()
                surface.setupUi(self.Form,*self.surface_rect,self)
                surface.show()
                self.surface_list[0]=surface 
            else:
                self.surface_list[0].show()
            self.surface.hide()
            self.surface=self.surface_list[0]
        elif k is AUTO_PUSH:
            img=WECHAT_DATA_PATH+"icon/button1_no.jpg"
        if img:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(img)  )
            self.Button_1.setIcon(icon)
    def button2_click(self,k):
        img = None
        if k is False and self.active!=2:
            img=WECHAT_DATA_PATH+"icon/button2_ok.jpg"
            self.release_button()
            self.active=2
            if self.surface_list[1] is None:
                surface=ContactFrame.ContactFrame()
                surface.setupUi(self.Form,*self.surface_rect,self)
                surface.show()
                self.surface_list[1]=surface
            else:
                self.surface_list[1].show()
            self.surface.hide()
            self.surface=self.surface_list[1]
        elif k is AUTO_PUSH:
            img=WECHAT_DATA_PATH+"icon/button2_no.jpg"
        if img:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(img)  )
            self.Button_2.setIcon(icon)
        
    def button3_click(self,k):
        img = None
        if self.active!=3:
            img=WECHAT_DATA_PATH+"icon/button3_ok.jpg"
            self.release_button()
            self.active=3
            if self.surface_list[2] is None:
                surface=DiscoverFrame.DiscoverFrame()
                surface.setupUi(self.Form,*self.surface_rect,self)
                surface.show()
                self.surface_list[2]=surface
            else:
                self.surface_list[2].show()
            self.surface.hide()
            self.surface=self.surface_list[2]

        elif k is AUTO_PUSH:
            img=WECHAT_DATA_PATH+"icon/button3_no.jpg"
        if img:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(img)  )
            self.Button_3.setIcon(icon)
    def button4_click(self,k):
        img = None
        if k is False and self.active!=4:
            img=WECHAT_DATA_PATH+"icon/button4_ok.jpg"
            self.release_button()
            self.active=4
            if self.surface_list[3] is None:
                surface=MeFrame.MeFrame()
                surface.setupUi(self.Form,*self.surface_rect,self)
                surface.show()
                self.surface_list[3]=surface
            else:
                self.surface_list[3].show()
            self.surface.hide()
            self.surface=self.surface_list[3]
        elif k is AUTO_PUSH:
            img=WECHAT_DATA_PATH+"icon/button4_no.jpg"
        if img:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(img)  )
            self.Button_4.setIcon(icon)
    def close_chat(self):
        for i in self.chat_view_dict.values():
            i.close()
class myMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('WeChat')
        self.chat_yxsid_present = None#记录当前对话框yxsid的一个变量，相当于一个全局变量，因为Form会出现在很多widget中
        self.chat_view_dict = None#记录单独剥离出来的对话框
        self.del_funs = []
        self.system_icon = QtGui.QIcon(WECHAT_DATA_PATH+'icon/WeChat.ico')
        self.setWindowIcon(self.system_icon)#设置标题栏和系统任务栏图标
        self.is_warning = False
    def start_warning(self):
        if not self.is_warning:
            GLOBAL_DICT['alert_msg']()
            self.is_warning=True
    def stop_warning(self):
        if self.is_warning:
            self.is_warning=False
    def setBot(self,bot):
        self.bot=bot
    def setUi(self,ui):
        self.ui = ui
    def enterEvent(self,e):
        # self.stop_warning()
        pass
    def closeEvent(self,e):
        try:
            self.ui.timer.stop()
            print('timer stop')
            for fun in self.del_funs:
                print(fun.__name__)
                # fun()
            self.bot.write_back()
        except Exception as e:
            print('Error 0:',e)
        sys.exit()
def alert_msg():
    app,widget = global_app[0]
    app.alert(widget)
GLOBAL_DICT['alert_msg'] = alert_msg
def main():
    app = QApplication(sys.argv)
    
    mainWindow = myMainWindow()
    global_app[0] = app,mainWindow
    ui = Ui_Form(mainWindow)
    mainWindow.setUi(ui)
    mainWindow.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    '''
    主函数
    '''
    main()
    
