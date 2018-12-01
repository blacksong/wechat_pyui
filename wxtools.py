from pathlib import Path
import wxpy 
import time
import sqlite3 as sql 
import hashlib
import sys
import yxspkg_encrypt as encrypt
import os
import asyncio
import base64
from threading import Thread
from collections import defaultdict
from os.path import getsize
import pickle
from wxpy import TEXT, PICTURE, MAP, VIDEO, NOTE, SHARING, RECORDING, ATTACHMENT, VIDEO, FRIENDS, SYSTEM
'''
TEXT = 'Text'
# 位置
MAP = 'Map'
# 名片
CARD = 'Card'
# 提示
NOTE = 'Note'
# 分享
SHARING = 'Sharing'
# 图片
PICTURE = 'Picture'
# 语音
RECORDING = 'Recording'
# 文件
ATTACHMENT = 'Attachment'
# 视频
VIDEO = 'Video'
# 好友请求
FRIENDS = 'Friends'
# 系统
SYSTEM = 'System'
'''
HEAD_SYSTEM = '__SYS__'
HEAD_ENCRYPT = '__ENC__'
ASK_FOR_PUBLIC_KEY = HEAD_SYSTEM + 'PUK'
RSA_PUBLIC_KEY_FILE_PASSWD = 'I just want encrypt this file!666'
SUFFIX_PUBLICKEY = '.yprkf' #系统用文件后缀名
PUBLIC_KEY_FILE = 'pupu.yprkf'
PRIVATE_KEY_FILE = 'prpr.yprkf'
class mydb:
    def __init__(self,conn):
        self.conn=conn
        self.cur=self.conn.cursor()
        self.has_table = defaultdict(lambda :None)

    def __del__(self):

        self.commit()
        self.cur.close()
        self.conn.close()
        print('sqlite3 has been closed')

    def dict_to_table(self,dic,table):
        a=[]
        for key,value in dic.items():
            if isinstance(value,int):
                stype = 'int'
            elif isinstance(value,float):
                stype = 'double'
            else:
                stype = 'varchar({0})'.format(len(str(value))+2)
            a.append('{0} {1},'.format(str(key),stype))
        content = ''.join(a)
        s='create table {table}({content})'.format(table = table,content=content[:-1])
        self.cur.execute(s)
    def table_exists(self,table):
        if self.has_table[table]:
            return True
        print('check table',table)
        result = self.cur.execute("select * from sqlite_master where name='{name}' ".format(name=table)).fetchall()
        if result:
            self.has_table[table] = True
            return True
        else:
            return False
    def commit(self):
        self.conn.commit()
    def to_sql(self,table,data,if_exists='append'):
        result = self.table_exists(table)

        if not result:
            print('without ',table)
            self.dict_to_table(data[0],table)
        else:
            if if_exists == 'replace':
                self.cur.execute('delete from {table} where 1=1'.format(table=table))
                
        res = self.cur.execute('select * from {}'.format(table))
        columns = set([i[0].lower() for i in res.description])
        def filter_key(key,keys):
            if key.lower() in keys:
                return True
            else:
                return False
        for d in data:
            g = set([i for i in d.keys() if not filter_key(i,columns)])
            if g:
                for i in g:
                    try:
                        self.cur.execute('alter table {table} add {column} varchar(3)'.format(table = table, column = i))
                    except Exception as e:
                        print(e)
                        continue
            t=','.join(['`'+i+'`' for i in d.keys()])
            v=['"'+str(i).replace('"','""')+'"' for i in d.values()]
            v=','.join(v)
            v='('+v+')'
            s='insert into '+table+'('+t+') values'+v
            self.cur.execute(s)
    def select(self,table=None,columns=('*',),where='1=1',return_dict = False):
        c=','.join(columns)
        s='select %s from %s where %s;' % (c,table,where)
        try:
            c=self.cur.execute(s)
        except Exception as err:
            print(s,err)
            return []
        c=self.cur.fetchall()
        if return_dict:
            c=[dict(zip(columns,i)) for i in c]
        return c

class myBot(wxpy.Bot):
    def __init__(self,*d,**kargs):
        super().__init__(*d,**kargs)
        self.cache_path = kargs.get('cache_path')
        self.TransPassword = None
        self.SavePassword = None
        #发生消息传送时更新对话页面的显示内容
        self.update_conversation = lambda :None
        self.senders = None
        self.me_info = None
        self.conversation_list_now=None #保存对话信息的的list
        self.message_dispatcher=dict()
        self.is_first=False
        self.contact_info_dict = None
        # self.puid_to_yxsid = dict()#{puid:yxsid}
        self.public_key_dict = dict()
        self.hash_write_auto = 1#记录自动写入硬盘的hash值
        self.img_saved_dict = dict()
    def enable_rsa(self):# 启用加密

        path_rsa_key = self.rsa_path
        self.publicfile = path_rsa_key / PUBLIC_KEY_FILE
        self.privatefile = path_rsa_key / PRIVATE_KEY_FILE
        if (not self.publicfile.is_file()) or (not self.privatefile.is_file()):
            self.public_key, self.private_key = encrypt.newkeys(2048)
            pu_der = self.public_key.save_pkcs1('DER')
            pr_der = self.private_key.save_pkcs1('DER')
            pu_der = encrypt.encode(pu_der,RSA_PUBLIC_KEY_FILE_PASSWD)
            pr_der = encrypt.encode(pr_der,RSA_PUBLIC_KEY_FILE_PASSWD)
            open(self.publicfile, 'wb').write(pu_der)
            open(self.privatefile, 'wb').write(pr_der)
        else:
            pu_der = open(self.publicfile, 'rb').read()
            pr_der = open(self.privatefile, 'rb').read()
            pu_der = encrypt.decode(pu_der,RSA_PUBLIC_KEY_FILE_PASSWD)
            pr_der = encrypt.decode(pr_der,RSA_PUBLIC_KEY_FILE_PASSWD)
            self.public_key = encrypt._rsa.PublicKey.load_pkcs1(pu_der,'DER')
            self.private_key = encrypt._rsa.PrivateKey.load_pkcs1(pr_der,'DER')
        self.public_key_id = '{:04d}'.format(self.public_key.n % 10000)

    def get_me_info(self):
        if self.me_info is None:
            yxsid = self.get_user_yxsid(self.self)
            self.me_info = {'yxsid': yxsid, 'name': self.self.raw['NickName'], 'img_path': self.get_img_path(yxsid)}
        return self.me_info
    def setTransPassword(self,password):
        self.TransPassword = password
    def set_init(self):#登录成功之后运行的第一个函数
        self.enable_sql()
        self.enable_yxsid()
        self.get_senders()
    def enable_yxsid(self):#这是一个待开发的函数，目的是返回一个不变的id  目前以puid作为yxsid
        
        puid_path = self.path / 'wxpy_puid.pkl'
        print('puid path', puid_path )
        self.enable_puid(str(puid_path))
        yxsid_path = self.path / 'wxpy_yxsid.pkl'
        self.yxsid_path = yxsid_path
        if yxsid_path.is_file():
            self.yxsid_puid,self.yxsid_md5,self.yxsid_yxsid = pickle.load(open(yxsid_path,'rb'))
        else:
            self.yxsid_puid,self.yxsid_md5,self.yxsid_yxsid =list(),list(),list()

        self.yxsid = self.get_user_yxsid(self.self) #

    def enable_sql(self):
        nickname = self.self.raw['NickName']
        m = hashlib.md5(nickname.encode('utf8')).hexdigest()
        self.setPath(Path(sys.path[0]) / 'user_data' / m)
    def get_user_md5(self,user):
        raw_data = user.raw
        m=hashlib.md5()
        for i in ('Signature','RemarkName','Province','Sex','NickName','City'):
            m.update(str(raw_data.get(i,i)).encode('utf8'))
        return m.hexdigest()[:15]
    
    def get_user_yxsid(self,user):#user_data is a dict, like {yxsid:(md5,puid,avamd5)}
        if user.user_name == 'filehelper':
            return 'filehelper'
        puid = user.puid
        ymd5 = self.get_user_md5(user)
        
        if puid in self.yxsid_puid:
            n = self.yxsid_puid.index(puid)
            self.yxsid_md5[n] = ymd5
            return self.yxsid_yxsid[n]
        elif ymd5 in self.yxsid_md5:
            n = self.yxsid_md5.index(ymd5)
            self.yxsid_puid[n] = puid
            return self.yxsid_yxsid[n]
        else:#新成员
            self.yxsid_puid.append(puid)
            self.yxsid_md5.append(ymd5)
            if ymd5 in self.yxsid_yxsid:
                print('warning ! yxsid is existed!')
                ymd5 += '1'
            self.yxsid_yxsid.append(ymd5)
            return ymd5 
    def contact_dict(self):
        if self.contact_info_dict:
            return self.contact_info_dict
        tags = ('yxsid', 'NickName', 'RemarkName','PYInitial','RemarkPYInitial','md5','imgmd5','user_type','puid')
        t = self.db.select('friend_info', tags, return_dict=True)+self.db.select('group_info', tags, return_dict=True) 
        for i in t:
            i['name']=i['RemarkName'] if i['RemarkName'] else i['NickName']
            i['img_path'] = self.get_img_path(i['yxsid'])
        info_dict = {i['yxsid']:i for i in t}
        self.contact_info_dict = info_dict
        return self.contact_info_dict

    def add_conversation(self,d):

        self.contact_dict()
        yxsid = d['yxsid']
        d['img_path'] =  self.get_img_path(yxsid)
        user = self.senders.get(yxsid)
        if user:
            name = user.name
        else:
            name = None 
        if not name:
            if d['user_type']==2:
                membercount = user.raw['MemberCount']
                name = '群聊{}'.format(membercount)
            
        d['name'] = str(name)
        con = self.conversation_dict_now.get(yxsid)
        if con:
            d['unread_num']+=con['unread_num']
            con.update(d)
        else:
            self.conversation_list_now.append(d)
            self.conversation_dict_now[yxsid] = d
    def conversation_list(self):#返回已经发生过的对话列表
        tags = ('yxsid', 'name', 'latest_time','unread_num', 'latest_user_name','text','user_type')
        if self.conversation_list_now:
            return self.conversation_list_now
        elif self.db.table_exists('conversation_list'):
            t = self.db.select('conversation_list', tags, return_dict=True)
            for i in t:
                i['img_path'] = self.get_img_path(i['yxsid'])
                i['unread_num'] = int(i['unread_num'])
            self.conversation_list_now = t
            self.conversation_dict_now = {i['yxsid']:i for i in t}

        else:
            d=dict.fromkeys(tags)
            self.db.dict_to_table(d,'conversation_list')
            self.conversation_list_now = list()
            self.conversation_dict_now = dict()
        return self.conversation_list_now
    def write_content(self,yxsid,data,passwd=None):
        #data保存的数据格式 字典形式，包括Value:str,Msg_type,Time,yxsid(两人对话时0代表自己，1代表对方，群聊时代表发送者的yxsid)
        self.db.to_sql('Record_'+yxsid,[data])
    def read_content(self,yxsid,time_before,nums):
        if not self.db.table_exists('Record_'+yxsid):
            return []
        return self.db.cur.execute('SELECT yxsid,Value,Msg_type,Time,name FROM {0} WHERE Time<{1} ORDER BY Time DESC LIMIT {2};'.format('Record_'+yxsid,time_before,nums))

    def setPath(self,path): #设置微信账号的信息存储路径

        self.path = Path(path)
        self.avatar_path = self.path / 'avatar'
        if not self.avatar_path.exists():
            self.avatar_path.mkdir(parents=True)
            self.is_first = True

        self.thumbnail_path = self.path / 'thumbnail'
        self.video_path = self.path / 'videos'
        self.image_path = self.path / 'images'
        self.rsa_path = self.path / 'rsa_key'
        self.attachment_path = self.path / 'attachments'
        for epath in [self.video_path,self.image_path,self.thumbnail_path,self.rsa_path,self.attachment_path]:
            if not epath.exists():
                epath.mkdir()

        self.db = mydb(sql.connect(
            str(self.path / 'wechat_data.db'), check_same_thread=False))
        self.enable_rsa()
        if not self.is_first:
            #不是第一次登录 则开始检测用户数据更新
            thread = Thread(target=self.async_check_and_update)
            thread.start()
    def first_run(self):
        #创建储存联系人信息的表
        self.get_avatar_all()
        self.db.commit()

    async def get_avatar_one(self,user):
        if user.user_name == 'filehelper':
            return
        print(user)
        loop = asyncio.get_event_loop()
        fu = loop.run_in_executor(None,user.get_avatar)
        im = await fu
        self.update_user_info_one(user,is_append=True,img = im)#更新用户数据信息
        self.save_avatar(user,im)
        
    def save_avatar(self,user,im):#保存用户头像
        name = self.avatar_path / (self.get_user_yxsid(user)+'.jpg')
        open(name,'wb').write(im)

    def get_avatar_all(self):#下载头像
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [self.get_avatar_one(user) for user in self.get_senders().values()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()
    def get_img_md5(self,img):
        return hashlib.md5(img).hexdigest()

    def check_and_update_user_info_one(self,user):
        if user.user_name == 'filehelper':
            return
        im = user.get_avatar()
        yxsid = self.get_user_yxsid(user)
        if yxsid in self.contact_info_dict:
            is_append = False
        else:
            is_append = True
        self.update_user_info_one(user,is_append,im)

    def check_and_update_user_info_all(self):
        for user in self.get_senders().values():
            self.check_and_update_user_info_one(user)
    def async_check_and_update(self):
        print('check and update user info')
        time.sleep(20)
        self.contact_dict()
        self.check_and_update_user_info_all()
    def update_user_info_one(self,user,is_append,img = None):
        d=user.raw
        d['md5']=self.get_user_md5(user)
        d['yxsid'] = self.get_user_yxsid(user)
        d['puid'] = user.puid 
        d['imgmd5'] = self.get_img_md5(img)
        ftype = self.get_user_type(user)
        d['user_type'] = ftype

        if is_append:

            if ftype == 2:
                self.db.to_sql('group_info',[d])
            elif ftype == 3:
                self.db.to_sql('mp_info',[d])
            else:
                self.db.to_sql('friend_info', [d])
        else:
            user_info_history = self.contact_info_dict[d['yxsid']]
            if user_info_history['imgmd5'] != d['imgmd5']:
                self.save_avatar(user,img)
            


    def get_senders(self):#微信机器人启动后自动后台运行的程序
        if self.senders:
            return self.senders
        print('get_senders')
        try:
            groups = self.groups()
        except:
            groups = []
        self.senders = {self.get_user_yxsid(s): s for s in self.friends()+groups}
        print('It is OK!')
        self.senders['filehelper']=self.file_helper
        return self.senders
    def get_public_key(self,yxsid):#返回用户publick key
        #检查是否读取过yxsid的public key
        if yxsid in self.public_key_dict:
            return self.public_key_dict[yxsid]
        else:
            #检查是否之前已经获取过yxsid的publickey 并存在硬盘中
            key_path = self.rsa_path
            public_key = list(key_path.glob(yxsid+'_'+PUBLIC_KEY_FILE))
            if public_key:
                #在文件夹中 读取public key
                pu_der = open(public_key[0], 'rb').read()
                pu_der = encrypt.decode(pu_der,RSA_PUBLIC_KEY_FILE_PASSWD)
                pu = encrypt._rsa.PublicKey.load_pkcs1(pu_der,'DER')
                public_key_id = '{:04d}'.format(pu.n % 10000)
                self.public_key_dict[yxsid] = pu , public_key_id
                return pu , public_key_id
            else:
                #通过网络获取对方的public key
                sender = self.senders[yxsid]
                sender.send(ASK_FOR_PUBLIC_KEY)
                return None,None
    def encrypt_data(self,data,msg_type,yxsid):#加密消息
        public_key, public_key_id = self.get_public_key(yxsid) 
        if public_key is None:
            print('no public key')
            return
        if msg_type == TEXT:
            data = encrypt.rsaencode(data.encode('utf8'),public_key)
            data = base64.b64encode(data).decode('utf8')
            return HEAD_ENCRYPT+ public_key_id + data
        else:
            return data
    def decrypt_data(self,data,msg_type):#解密消息
        if msg_type == TEXT:
            head_length = len(HEAD_ENCRYPT)
            public_key_id = data[head_length:head_length+4]
            if public_key_id != self.public_key_id:
                self.public_key_dict = {}
                return False #加密所使用的密钥错误
            data = data[head_length+4:] #4代表public_key_id 的长度
            data = base64.b64decode(data.encode('utf8'))
            data = encrypt.rsadecode(data,self.private_key)
            return data.decode('utf8')
        else:
            return data  

    def send_data(self,data,msg_type,target,is_encrypt=True,update_con = True):
        if target['yxsid'] not in self.senders:
            return False,"Group is not in the list"
        friend = self.senders[target['yxsid']]
        if msg_type == ATTACHMENT:
            friend.send_file(data)
            text_conversation = '[文件]'
            content = data
        elif msg_type == TEXT:
            if is_encrypt:
                data_send = self.encrypt_data(data,msg_type,target['yxsid'])
                if data_send is None:
                    return False,'Encryption failed, please try it again'
            else:
                data_send = data
            friend.send(data_send)
            text_conversation = data
            content = data
        elif msg_type == PICTURE:
            text_conversation = '[图片]'
            content = data
            friend.send_image(data)
        elif msg_type == VIDEO:
            text_conversation = '[视频]'
            content = data  
            friend.send_video(data)
        elif msg_type == RECORDING:
            text_conversation = '[语音]'
            content = data
            friend.send_video(data)
        time_index = str(time.time())
        data_record = {'yxsid':'0','Value':content,'Time':time_index,'Msg_type':msg_type,'name':''}
        
        cons = {'yxsid':target['yxsid'],'text':text_conversation,'latest_user_name':'','unread_num':0,'latest_time':time_index,'user_type':self.get_user_type(friend)}
        info = (target['yxsid'],data_record,cons)
        if update_con:
            self.async_update_conversation(info)
        return True,info

    def async_update_conversation(self,args):
        yxsid,data_record,cons = args
        self.write_content(yxsid,data_record)
        self.add_conversation(cons)#latest_user_name=''意味着最后说话的人是自己
        self.update_conversation()

    def save_publickey(self,msg,file_path):
        filename = msg.file_name
        yxsid = self.get_user_yxsid(msg.sender)
        filename = Path(yxsid+'_'+filename)
        filename = self.rsa_path /filename
        if filename.exists():
            os.remove(filename)
        print('saving public key',filename)
        if file_path and (not filename.exists()):
            os.rename(file_path,filename)
            return
        msg.get_file(str(filename))
    def system_message(self,content,yxsid):
        print('system-message',content)
        if content == ASK_FOR_PUBLIC_KEY:
            #发送public key
            sender = self.senders[yxsid]
            print('send file', str(self.publicfile))
            sender.send_file(str(self.publicfile))
    def RSAError(self,msg):
        '''RSA解密时出现错误调用此函数，发送一条明文消息给对方，告诉对方消息发送错误，请对方重发，并且发送我方公钥给对方'''
        msg.sender.send_file(str(self.publicfile))
        msg.sender.send('信息错误，请尝试重发上一条信息')
    def get_message(self,msg,file_path=None):#处理收到的消息
        #yxsid_send 发送msg的人
        type_ = self.get_user_type(msg.chat)
        yxsid_send = self.get_user_yxsid(msg.sender)#
        yxsid_chat = self.get_user_yxsid(msg.chat)#对话框的yxsid，个人对话框和对方用户的yxsid相同
        msg_type = msg.type#获取消息类型
        sender_name = '' #发消息人的名字，主要是用来在对话框预览界面显示群聊天中群成员的名字，其它对话中不 显示

        if type_ == 1:#好友消息，文件助手
            message_sender = msg.sender
            yxsid_send_user = yxsid_send #发送消息的人的yxsid
        elif type_ == 2:#群聊
            yxsid_member = self.get_user_yxsid(msg.member)
            print('yxsid_member',yxsid_member)
            message_sender = msg.member
            sender_name = message_sender.name+':'
            yxsid_send_user = yxsid_member
        else:#除去群聊，好友，文件助手的一切消息
            print('公众号消息')
            message_sender = msg.sender
            yxsid_send_user = yxsid_send

        if yxsid_chat not in self.senders:
            print('增加聊天',msg.chat,msg.chat.name)
            self.senders[yxsid_chat] = msg.chat
        receiver = self.message_dispatcher.get(yxsid_chat)
        
        #解析获取的消息
        if msg_type == TEXT:
            content = msg.text
            if content.startswith(HEAD_SYSTEM):#自定义消息 无需显示在界面中
                self.system_message(content,yxsid_send_user)
                return
            elif content.startswith(HEAD_ENCRYPT):#加密信息  需要解析后显示
                content = self.decrypt_data(content,TEXT)
                if content is False:
                    self.RSAError(msg)
                    return
            text_conversation = content
        elif msg_type == PICTURE:
            content = str(self.image_path /(yxsid_chat+msg.file_name))
            if not file_path:
                msg.get_file(content)
            else:
                if Path(content).exists():
                    os.remove(content)
                os.rename(file_path,content)
            is_existed = Path(content).is_file()
            if not is_existed or getsize(content) == 0:
                if is_existed:
                    os.remove(content)
                msg_type = TEXT 
                content = '[收到了一个表情，请在手机上查看]'
                text_conversation = content
            else:
                text_conversation = '[图片]'
        elif msg_type in [ATTACHMENT, VIDEO, RECORDING]:
            if msg.file_name.endswith(SUFFIX_PUBLICKEY):#如果文件后缀为SUFFIX_PUBLICKEY则不显示该文件 该文件是公钥文件，，进行保存
                self.save_publickey(msg,file_path)
                return

            if msg_type == VIDEO:
                epath = self.video_path
                text_conversation = '[视频]'
            elif msg_type == RECORDING:
                text_conversation = '[语音]'
                epath = self.attachment_path
            else:
                text_conversation = '[文件]'
                epath = self.attachment_path
            filename = str(epath/msg.file_name)
            if not file_path:
                msg.get_file(filename)
            else:
                try:
                    if Path(filename).exists():
                        os.remove(filename)
                    os.rename(file_path,filename)
                except Exception as e:
                    print('Error:文件已存在 无法删除',e)
            content = filename
                
        elif msg_type == NOTE:
            text_conversation = msg.text 
            content = text_conversation
        elif msg_type == SHARING:
            content = msg.url+' '+msg.text
            text_conversation = '[链接]'
        else:
            content = 'None'
            text_conversation = '[消息]'
            print(msg.text)

        if receiver is not None:
            receiver(content, msg_type,message_sender)#

        time_index = '{:.2f}'.format(time.time())
        data_record = {'yxsid':yxsid_send_user,'Value':content,'Time':time_index,'Msg_type':msg_type,'name':message_sender.name}
        print('You receive a new message!')
        print('sender',data_record)
        print('receiver',yxsid_chat,msg.chat,msg_type)
        self.write_content(yxsid_chat,data_record)
        if yxsid_send_user == self.yxsid:
            unread = 0
        else:
            unread = 1
        self.add_conversation({'yxsid': yxsid_chat,'text':sender_name+text_conversation, 'latest_user_name': '','unread_num': unread, 'latest_time': str(time.time()),'user_type':type_})        
        self.update_conversation()
    def get_img_path(self,yxsid,group_yxsid=None):
        if yxsid in self.img_saved_dict:
            return self.img_saved_dict[yxsid]
        if yxsid == 'filehelper':
            self.img_saved_dict[yxsid] = str(self.path.parent.with_name('wechat_data') /'icon'/'filehelper.jpg')
            return self.img_saved_dict[yxsid]
        p = self.avatar_path/(yxsid+'.jpg')
        default_img= str(self.path.parent.with_name('wechat_data') / 'icon' / 'system_icon.jpg')
        if not p.is_file():
            try:
                if group_yxsid:
                    friend = self.senders[group_yxsid]
                    for member in friend:
                        if self.get_user_yxsid(member) == yxsid:
                            print('get avatar',self.get_user_yxsid(member))
                            break
                    else:
                        member = None
                    friend = member
                else:
                    friend = self.senders.get(yxsid)

                if friend:
                    friend.get_avatar(str(p))
                else:
                    p = default_img
            except Exception as e:
                print('Error: get_img_path\n',e)
                p = default_img
        self.img_saved_dict[yxsid] = str(p)
        return str(p)
    def get_user_type(self,user):# 1-friend 2-group 3-mp(公众号)
        if user.user_name == 'filehelper':
            return 1
        membercount = user.raw.get('MemberCount',None)
        if membercount is None:return 3
        if membercount==0:
            if user.is_friend:
                return 1
            else:
                return 3
        else:
            return 2
    def write_auto(self):
        h = hash(str(self.conversation_list_now))
        if h == self.hash_write_auto:#无需写入
            return
        self.hash_write_auto = h
        self.db.to_sql('conversation_list',self.conversation_list_now,if_exists='replace')
        self.db.commit()
    def write_back(self):#程序退出时调用
        self.write_auto()
        datas = (self.yxsid_puid,self.yxsid_md5,self.yxsid_yxsid)
        pickle.dump(datas,open(self.yxsid_path,'wb'))
        del self.db
    def dump_login_status(self,cache_path=None):#保存登陆信息
        super().dump_login_status(self.cache_path)

        p = Path(self.cache_path)
        t = p.read_bytes()
        yxsid = self.yxsid
        open(p.with_name(yxsid+'_wx.pkl'),'wb').write(t)
        img_name = p.with_name(yxsid+'_'+self.self.name+'.jpg')
        if not img_name.is_file():
            img_data = (self.avatar_path / (yxsid+'.jpg')).read_bytes()
            img_name.write_bytes(img_data)
        print('Save login status')

