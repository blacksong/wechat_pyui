from pathlib import Path
import wxpy 
import time
import sqlite3 as sql 
import hashlib
import sys
import yxspkg_encrypt as encrypt
import asyncio
import base64
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
        self.table_columns=dict()
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
        result = self.cur.execute("select * from sqlite_master where name='{name}' ".format(name=table)).fetchall()
        if result:
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
        columns = set([i[0] for i in res.description])
        
        for d in data:
            c2 = set(d.keys())
            g = c2-columns
            if g:
                columns.update(g)
                for i in g:
                    self.cur.execute('alter table {table} add {column} varchar(3)'.format(table = table, column = i))
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
        self.TransPassword = None
        self.SavePassword = None
        #发生消息传送时更新对话页面的显示内容
        self.update_conversation = lambda x=None:x
        self.senders = None
        self.me_info = None
        self.conversation_list_now=None
        self.message_dispatcher=dict()
        self.is_first=False
        self.contact_info_list = None

        self.public_key_dict = dict()
        self.hash_write_auto = 1#记录自动写入硬盘的hash值
    def enable_rsa(self):# 启用加密

        path_rsa_key = self.path / ('rsa_key')
        if not path_rsa_key.is_dir():
            path_rsa_key.mkdir()
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
    def enable_yxsid(self):#这是一个待开发的函数，目的是返回一个不变的id  目前以puid作为yxsid
        
        puid_path = self.path / 'wxpy_puid.pkl'
        print('puid path', puid_path )
        self.enable_puid(str(puid_path))
        self.yxsid = self.get_user_yxsid(self.self) #

    def enable_sql(self):
        nickname = self.self.raw['NickName']
        m = hashlib.md5(nickname.encode('utf8')).hexdigest()
        self.setPath(Path(sys.path[0]) / 'user_data' / m)
    def get_user_md5(self,user):
        raw_data = user.raw
        m=hashlib.md5()
        for i in ('Signature','RemarkName','Province','Sex','NickName','City'):
            m.update(str(raw_data[i]).encode('utf8'))
        return m.hexdigest()

    def get_user_yxsid(self,user):#user_data is a dict, like {yxsid:(md5,puid,avamd5)}
        # md5 = self.get_user_md5(user)
        return user.puid
    def contact_list(self):
        tags = ('yxsid', 'NickName', 'RemarkName')
        t = self.db.select('friend_info', tags)+self.db.select('group_info', tags) 
        info_list = [{'yxsid': yxsid, 'name': (RemarkName if RemarkName else NickName), 'img_path': self.get_img_path(yxsid)} for yxsid, NickName, RemarkName in t]
        self.contact_info_list = info_list
        return info_list
    def add_conversation(self,d):
        if self.contact_info_list is None:
            self.contact_info_list = self.contact_list()
        yxsid = d['yxsid']
        d['img_path'] =  self.get_img_path(d['yxsid'])
        if not d.get('name'):
            for i in self.contact_info_list:
                if i['yxsid'] == yxsid:
                    d['name']=i['name']
                    break
            else:
                user = self.senders.get(yxsid)
                if user is None:
                    d['name']='None'
                else:
                    d['name'] = user.raw['NickName']
        for i in self.conversation_list_now:
            if i['yxsid'] == yxsid:
                i.update(d)
                break
        else:
            self.conversation_list_now.append(d)
    def conversation_list(self):#返回已经发生过的对话列表
        tags = ('yxsid', 'name', 'latest_time','unread_num', 'latest_user_name','text')
        if self.conversation_list_now:
            self.conversation_list_now.sort(key = lambda x: x['latest_time'])
            self.conversation_list_now.reverse()
            return self.conversation_list_now
        elif self.db.table_exists('conversation_list'):
            t = self.db.select('conversation_list', tags, return_dict=True)
            for i in t:
                i['img_path'] = self.get_img_path(i['yxsid'])
            self.conversation_list_now = t
            self.conversation_list_now.sort(key=lambda x: x['latest_time'])
            self.conversation_list_now.reverse()
        else:
            d=dict.fromkeys(tags)
            self.db.dict_to_table(d,'conversation_list')
            self.conversation_list_now = list()
        return self.conversation_list_now
    def write_content(self,yxsid,data,passwd=None):
        #data保存的数据格式 字典形式，包括Value:str,Msg_type,Time,yxsid(两人对话时0代表自己，1代表对方，群聊时代表发送者的yxsid)
        self.db.to_sql('Record_'+yxsid,[data])
    def read_content(self,yxsid,time_before,nums):
        if not self.db.table_exists('Record_'+yxsid):
            return []
        return self.db.cur.execute('SELECT yxsid,Value,Msg_type,Time FROM {0} WHERE Time<{1} ORDER BY Time DESC LIMIT {2};'.format('Record_'+yxsid,time_before,nums))

    def setPath(self,path): #设置微信账号的信息存储路径

        def makedirs(path_dirs):
            if not path_dirs.exists():
                makedirs(path_dirs.parent)
                path_dirs.mkdir()

        self.path = Path(path)
        self.avatar_path = self.path / 'avatar'
        if not self.avatar_path.exists():
            makedirs(self.avatar_path)
            self.is_first = True
        self.db = mydb(sql.connect(
            str(self.path / 'wechat_data.db'), check_same_thread=False))
        self.enable_rsa()
    def first_run(self):
        if not self.db.table_exists('friend_info'):
            friends = self.friends()
            groups = self.groups()
            mps = self.mps()
            for i in friends+groups+mps:
                self.update_user_info_one(i,is_append=True)
        self.db.commit()
        self.get_avatar_all()

    async def get_avatar_one(self,user,name):
        print(user)
        loop = asyncio.get_event_loop()
        fu = loop.run_in_executor(None,user.get_avatar)
        im = await fu
        open(name,'wb').write(im)

    def get_avatar_all(self):#下载头像
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [self.get_avatar_one(user,self.avatar_path / (self.get_user_yxsid(user)+'.jpg')) for user in self.friends()+self.groups()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def update_user_info_one(self,user,is_append):
        d=user.raw
        d['md5']=self.get_user_md5(user)
        d['yxsid'] = self.get_user_yxsid(user)
        d['puid'] = user.puid 
        d['imgmd5'] = self.get_user_md5(user)
        ftype = str(user)[1:].split(':')[0]
        if is_append:
            if ftype == 'Group':
                self.db.to_sql('group_info',[d])
            elif ftype == 'MP':
                self.db.to_sql('mp_info',[d])
            else:
                self.db.to_sql('friend_info', [d])

    def auto_run(self):#微信机器人启动后自动后台运行的程序
        print('auto_run')
        self.senders = {self.get_user_yxsid(s): s for s in self.friends()+self.groups()}
    def get_public_key(self,yxsid):#返回用户publick key
        #检查是否读取过yxsid的public key
        if yxsid in self.public_key_dict:
            return self.public_key_dict[yxsid]
        else:
            #检查是否之前已经获取过yxsid的publickey 并存在硬盘中
            key_path = self.path / "rsa_key"
            public_key = list(key_path.glob(yxsid+'_'+PUBLIC_KEY_FILE))
            if public_key:
                #在文件夹中 读取public key
                pu_der = open(public_key[0], 'rb').read()
                pu_der = encrypt.decode(pu_der,RSA_PUBLIC_KEY_FILE_PASSWD)
                pu = encrypt._rsa.PublicKey.load_pkcs1(pu_der,'DER')
                self.public_key_dict[yxsid] = pu 
                return pu 
            else:
                #通过网络获取对方的public key
                sender = self.senders[yxsid]
                sender.send(ASK_FOR_PUBLIC_KEY)
                return None
    def encrypt_data(self,data,msg_type,yxsid):#加密消息
        public_key = self.get_public_key(yxsid) 
        if public_key is None:
            print('no public key')
            return
        if msg_type == TEXT:
            data = encrypt.rsaencode(data.encode('utf8'),public_key)
            data = base64.b64encode(data).decode('utf8')
            return HEAD_ENCRYPT + data
        else:
            return data
    def decrypt_data(self,data,msg_type):#解密消息
        if msg_type == TEXT:
            data = data[len(HEAD_ENCRYPT):]
            data = base64.b64decode(data.encode('utf8'))
            data = encrypt.rsadecode(data,self.private_key)
            return data.decode('utf8')
        else:
            return data  

    def send_data(self,data,msg_type,target,is_encrypt=True):
        friend = self.senders[target['yxsid']]
        if msg_type == TEXT:
            if is_encrypt:
                data_send = self.encrypt_data(data,msg_type,target['yxsid'])
                if data_send is None:
                    return False,'Encryption failed, please try it again'
            else:
                data_send = data
            friend.send(data_send)
            print('send',data_send)
            text_conversation = data
            value_record = data
        else:
            text_conversation = '[Others]'
            friend.send('不支持的消息类型')
            value_record = text_conversation
        # tags = ('yxsid', 'name', 'latest_time','unread_num', 'latest_user_name')
        time_index = str(time.time())
        data_record = {'yxsid':'0','Value':value_record,'Time':time_index,'Msg_type':msg_type}
        self.write_content(target['yxsid'],data_record)
        self.add_conversation({'yxsid':target['yxsid'],'text':text_conversation,'name':target['name'],'latest_user_name':'','unread_num':0,'latest_time':time_index})#latest_user_name=''意味着最后说话的人是自己
        self.update_conversation()
        return True,None

        
    def save_publickey(self,msg):
        filename = msg.file_name
        yxsid = self.get_user_yxsid(msg.sender)
        filename = Path(yxsid+'_'+filename)
        filename = self.path / 'rsa_key' /filename
        print('saving public key',filename)
        msg.get_file(str(filename))
    def system_message(self,content,yxsid):
        print('system-message',content)
        if content == ASK_FOR_PUBLIC_KEY:
            #发送public key
            sender = self.senders[yxsid]
            print('send file', str(self.publicfile))
            sender.send_file(str(self.publicfile))
    def get_message(self,msg):#处理收到的消息
        #yxsid_send 发送msg的人
        print(msg.create_time)
        type_ = self.get_user_type(msg.chat)
        if type_ == 3:
            print('公众号消息')
            return
        elif type_ == 1:
            msg_chat = 'Friend'
        elif type_ == 2:
            msg_chat = 'Group'
            yxsid_member = self.get_user_yxsid(msg.member)
        else:
            print('Error:\n',self.get_message)
            return
        yxsid_send = self.get_user_yxsid(msg.sender)
        yxsid = self.get_user_yxsid(msg.chat)
        if yxsid not in self.senders:
            print('增加群聊天',msg.chat)
            self.senders[yxsid] = msg.chat
        receiver = self.message_dispatcher.get(yxsid)

        msg_type = msg.type#获取消息类型
        
        if msg_type == TEXT:
            content = msg.text
            if content.startswith(HEAD_SYSTEM):#自定义消息 无需显示在界面中
                self.system_message(content,yxsid_send)
                return
            elif content.startswith(HEAD_ENCRYPT):#加密信息  需要解析后显示
                content = self.decrypt_data(content,TEXT)
            text_conversation = content
            value_record = text_conversation
        elif msg_type == PICTURE:
            content = str(self.path/msg.file_name)
            msg.get_file(content)
            text_conversation = '[图片]'
            value_record = content
        elif msg_type == ATTACHMENT or msg_type == VIDEO:
            if msg.file_name.endswith(SUFFIX_PUBLICKEY):#如果文件后缀为SUFFIX_PUBLICKEY则不显示该文件 该文件是公钥文件，，进行保存
                self.save_publickey(msg)
                return
            filename = str(self.path/msg.file_name)
            print(filename)
            msg.get_file(filename)
            content = filename
            if msg_type == ATTACHMENT:
                text_conversation = '[文件]'
            else:
                text_conversation = '[视频]'
            value_record = filename
        elif msg_type == NOTE:
            text_conversation = msg.text 
            value_record = text_conversation
            content = text_conversation
        else:
            content = 'None'
            text_conversation = '[消息]'
            value_record = ''
            print(msg.text)
            print(dir(msg))

        if msg_chat == 'Group':
            yxsid_send_user = yxsid_member
        else:
            yxsid_send_user = yxsid_send
        if receiver is not None:
            receiver(content, msg_type, yxsid_send,yxsid_send_user)
        unread = 0
        if msg_chat == 'Group':
            yxsid_send = yxsid_member
        time_index = '{:.2f}'.format(time.time())
        data_record = {'yxsid':yxsid_send,'Value':value_record,'Time':time_index,'Msg_type':msg_type}
        print('\a','You receive a new message!',msg.chat,msg_type)
        print(data_record)
        self.write_content(yxsid,data_record)
        self.add_conversation({'yxsid': yxsid,'text':text_conversation, 'latest_user_name': '','unread_num': unread, 'latest_time': str(time.time())})        
        self.update_conversation()
    def get_img_path(self,yxsid,group_yxsid=None):
        p = self.avatar_path/(yxsid+'.jpg')
        if not p.is_file():
            try:
                if group_yxsid is not None:
                    friend = self.senders[group_yxsid]
                    for member in friend.members:
                        if self.get_user_yxsid(member) == yxsid:
                            print(self.get_user_yxsid(member),'sdadf')
                    friend = member
                else:
                    friend = self.senders[yxsid]
                friend.get_avatar(str(p))
            except Exception as e:
                print('Error: get_img_path\n',e)
                p = self.path.parent.with_name('wechat_data') / 'icon' / 'system_icon.jpg'
        return str(p)
    def get_user_type(self,user):# 1-friend 2-group 3-mp(公众号)
        if user.raw['MemberCount']==0:
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
        del self.db

if __name__=='__main__':
    # bot = myBot(cache_path=True)
    # print(t)
    x = myBot(True)
    x.path = Path('./')
    x.enable_rsa()
