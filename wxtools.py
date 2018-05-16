
from pathlib import Path
import wxpy 
import time
import sqlite3 as sql 
import hashlib
import sys
import yxspkg_encrypt as encrypt
import asyncio
import base64
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
HEAD_SYSTEM = '__BLACKSONG__HDLJDYLZSX__'
HEAD_ENCRYPT = '__BLACKSONG__ENMESSAGE__'

SUFFIX_PUBLICKEY = '.BLCKS_KKK' #系统用文件后缀名
class mydb:
    def __init__(self,conn):
        self.conn=conn
        self.cur=self.conn.cursor()
        self.table_columns=dict()
    def __del__(self):
        self.cur.close()
        self.conn.close()
    def dict_to_table(self,dic,table):
        a=[]
        for key,value in dic.items():
            if isinstance(value,int):
                stype = 'int'
            elif isinstance(value,float):
                stype = 'double'
            else:
                print(value)
                stype = 'varchar({0})'.format(len(str(value))+2)
            a.append('{0} {1},'.format(str(key),stype))
        content = ''.join(a)
        print(content)
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
                print(g)
                columns.update(g)
                for i in g:
                    self.cur.execute('alter table {table} add {column} varchar(3)'.format(table = table, column = i))
            t=','.join(['`'+i+'`' for i in d.keys()])
            v=['"'+str(i).replace('"','""')+'"' for i in d.values()]
            v=','.join(v)
            v='('+v+')'
            s='insert into '+table+'('+t+') values'+v
            # print(s)
            self.cur.execute(s)
    def select(self,table=None,columns=('*',),where='1=1',return_dict = False):
        c=','.join(columns)
        s='select %s from %s where %s;' % (c,table,where)
        try:
            c=self.cur.execute(s)
        except Exception as err:
            print(s,err)
            return False
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
        self.is_encrypt = False
        self.encrypt_yxsid_dict = dict()
    
    def enable_rsa(self):# 启用加密
        if self.is_encrypt:
            return 
        else:
            path_rsa_key = self.path.with_name('rsa_key')
            if not path_rsa_key.is_dir():
                path_rsa_key.mkdir()
        self.publicfile = path_rsa_key / 'publicrsa.picklersa'
        self.privatefile = path_rsa_key / 'privatersa.picklersa'
        if (not self.publicfile.is_file()) or (not self.privatefile.is_file()):
            self.public_key, self.private_key = encrypt.newkeys(2048)
            pickle.dump(self.public_key, open(self.publicfile, 'wb'))
            pickle.dump(self.private_key, open(self.privatefile, 'wb'))
        else:
            self.public_key = pickle.load(open(self.publicfile,'rb'))
            self.private_key = pickle.load(open(self.privatefile, 'rb'))
        self.is_encrypt = True
    def deable_rsa(self):
        self.is_encrypt = False
    def get_me_info(self):
        if self.me_info is None:
            yxsid = self.get_user_yxsid(self.self)
            self.me_info = {'yxsid': yxsid, 'name': self.self.raw['NickName'], 'img_path': str(self.avatar_path/(yxsid+'.jpg'))}
        return self.me_info
    def setTransPassword(self,password):
        self.TransPassword = password
    def set_init(self):#登录成功之后运行的第一个函数
        self.enable_sql()
        self.enable_yxsid()
    def enable_yxsid(self):#这是一个待开发的函数，目的是返回一个不变的id  目前以puid作为yxsid

        puid_path = self.path / 'wxpy_puid.pkl'
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
        info_list = [{'yxsid': yxsid, 'name': (RemarkName if RemarkName else NickName), 'img_path': str(
            self.avatar_path / (yxsid+'.jpg'))} for yxsid, NickName, RemarkName in t]
        self.contact_info_list = info_list
        return info_list
    def add_conversation(self,d):
        if self.contact_info_list is None:
            self.contact_info_list = self.contact_list()
        yxsid = d['yxsid']
        d['img_path'] = str(self.avatar_path / (d['yxsid']+'.jpg'))
        if not d.get('name'):
            for i in self.contact_info_list:
                if i['yxsid'] == yxsid:
                    d['name']=i['name']
                    break
            else:
                d['name']='None'
        # print(d,'add'*9)
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
                i['img_path'] = str(self.avatar_path / (i['yxsid']+'.jpg'))
            self.conversation_list_now = t
            self.conversation_list_now.sort(key=lambda x: x['latest_time'])
            self.conversation_list_now.reverse()
        else:
            d=dict.fromkeys(tags)
            self.db.dict_to_table(d,'conversation_list')
            self.conversation_list_now = list()
        return self.conversation_list_now

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
        # self.first_run()
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
            print(ftype)
            if ftype == 'Group':
                self.db.to_sql('group_info',[d])
            elif ftype == 'MP':
                self.db.to_sql('mp_info',[d])
            else:
                self.db.to_sql('friend_info', [d])
    def auto_run(self):#微信机器人启动后自动后台运行的程序
        
        self.senders = {self.get_user_yxsid(s): s for s in self.friends()+self.groups()}
    def encrypt_data(self,data,msg_type,yxsid):#加密消息
        public_key = self.encrypt_yxsid_dict[yxsid] 
        if msg_type == TEXT:
            data = encrypt.rsaencode(data.encode('utf8'),public_key)
            data = base64.b64encode(data).decode('utf8')
            return data,TEXT 
        else:
            return data,msg_type
    def decrypt_data(self,data,msg_type):#解密消息
        if msg_type == TEXT:
            data = base64.b64decode(data.encode('utf8'))
            data = encrypt.rsadecode(data,self.private_key)
            return data.decode('utf8'),TEXT
        else:
            return data,msg_type    
    def send_data(self,data,msg_type,target):
        
        friend = self.senders[target['yxsid']]
        print(data,target)
        if msg_type == TEXT:
            friend.send(data)
        else:
            friend.send('不支持的消息类型')
        # tags = ('yxsid', 'name', 'latest_time','unread_num', 'latest_user_name')
        self.add_conversation({'yxsid':target['yxsid'],'name':target['name'],'latest_user_name':'','unread_num':0,'latest_time':str(time.time())})#latest_user_name=''意味着最后说话的人是自己
        self.update_conversation()

    def send_publickey(self,sender):
        sender.send_file(str(self.publicfile))
    def save_publickey(self,msg):
        filename = msg.file_name
        msg.get_file(filename)
    def get_message(self,msg):#处理收到的消息
        if not self.is_encrypt:
            self.enable_rsa()
        yxsid_send = self.get_user_yxsid(msg.sender)

        yxsid = self.get_user_yxsid(msg.chat)
        receiver = self.message_dispatcher.get(yxsid)

        msg_type = msg.type#获取消息类型
        if receiver is not None:
            if msg_type == TEXT:
                content = msg.text
                if content.startswith(HEAD_SYSTEM):#自定义消息 无需显示在界面中
                    self.send_publickey(msg.sender)
                    return
                elif content.startswith(HEAD_ENCRYPT):#加密信息  需要解析后显示
                    pass
            elif msg_type == PICTURE:
                content = str(self.path/msg.file_name)
                msg.get_file(content)
            elif msg_type == ATTACHMENT:
                if msg.file_name.endswith(SUFFIX_PUBLICKEY):#如果文件后缀为SUFFIX_PUBLICKEY则不显示该文件 该文件是公钥文件，，进行保存
                    self.save_publickey(msg)
                    return
                filename = str(self.path/msg.file_name)
                print(filename)
                msg.get_file(filename)
            else:
                content = 'None'
            receiver(content,msg_type, yxsid_send)
            unread = 0
        else:
            unread = 1
        if msg_type == TEXT:
            text_conversation = msg.text
        elif msg_type == PICTURE:
            text_conversation = '[图片]'
        elif msg_type == ATTACHMENT:
            text_conversation = '[文件]'
        else:
            text_conversation = '[消息]'
        self.add_conversation({'yxsid': yxsid,'text':text_conversation, 'latest_user_name': '','unread_num': unread, 'latest_time': str(time.time())})        
        self.update_conversation()
    def update_user_info(self):
        t = self.db.table_exists('friend_info')
        if not t:
            friends = self.friends()
    def write_back(self):
        self.db.to_sql('conversation_list',self.conversation_list_now,if_exists='replace')
        self.db.commit()

if __name__=='__main__':
    # bot = myBot(cache_path=True)
    # print(t)
    x = myBot(True)
    x.path = Path('./')
    x.enable_rsa()
