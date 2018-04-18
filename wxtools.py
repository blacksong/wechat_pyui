
from pathlib import Path
import wxpy 
import time
import sqlite3 as sql 
import hashlib
import sys
import asyncio
import yxspkg_encrypt as encrypt
semaphore = asyncio.Semaphore(8)
class mydb:
    def __init__(self,conn):
        self.conn=conn
        self.cur=self.conn.cursor()
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
                stype = 'varchar({0})'.format(len(str(value).encode('utf8'))+2)
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
    def to_sql(self,table,data,if_exists='append'):
        result = self.table_exists(table)
        
        if not result:
            print('without ',table)
            self.dict_to_table(data[0],table)
        else:
            if if_exists == 'replace':
                self.cur.execute('delete from {table} where 1=1'.format(table=table))
                self.conn.commit()
        # print(table,'exists')
        for d in data:
            t=','.join(['`'+i+'`' for i in d.keys()])
            v=['"'+str(i).replace('"','""')+'"' for i in d.values()]
            v=','.join(v)
            v='('+v+')'
            s='insert into '+table+'('+t+') values'+v
            print(s)
            self.cur.execute(s)
        self.conn.commit()
    def select(self,table=None,columns=('*',),where='1=1'):
        c=','.join(columns)
        s='select %s from %s where %s;' % (c,table,where)
        try:
            c=self.cur.execute(s)
        except Exception as err:
            print(s,err)
            return False
        c=self.cur.fetchall()
        return c

class myBot(wxpy.Bot):
    def __init__(self,*d,**kargs):
        super().__init__(*d,**kargs)
        self.TransPassword = None
        self.SavePassword = None
        self.senders = None
        self.me_info = None
        self.message_dispatcher=dict()
    def get_me_info(self):
        if self.me_info is None:
            yxsid = self.get_user_yxsid(self.self)
            self.me_info = {'yxsid': yxsid, 'name': self.self.raw['NickName'], 'img_path': str(self.avatar_path/(yxsid+'.jpg'))}
        return self.me_info
    def setTransPassword(self,password):
        self.TransPassword = password
    def enable_yxsid(self):#这是一个待开发的函数，目的是返回一个不变的id  目前以puid作为yxsid
        self.enable_puid()

    def enable_sql(self):
        nickname = self.self.raw['NickName']
        m = hashlib.md5(nickname.encode('utf8')).hexdigest()
        self.setPath(Path(sys.path[0]) / 'wechat_data' / m)
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
        t = self.db.select('friend_info', tags)
        print(t)
        info_list = [{'yxsid': yxsid, 'name': (RemarkName if RemarkName else NickName), 'img_path': str(
            self.avatar_path / (yxsid+'.jpg'))} for yxsid, NickName, RemarkName in t]
        print(info_list)
        return info_list
    def conversation_list(self):
        tags = ('yxsid', 'NickName', 'RemarkName')
        t = self.db.select('friend_info',tags)
        print(t)
        info_list = [{'yxsid':yxsid,'name': (RemarkName if RemarkName else NickName),'img_path':str(self.avatar_path / (yxsid+'.jpg'))} for yxsid,NickName,RemarkName in t]
        print(info_list)
        return info_list

    def setPath(self,path): #设置微信账号的信息存储路径
        print(path)
        self.path = Path(path)
        self.avatar_path = self.path / 'avatar'
        if not self.path.exists():
            self.path.mkdir()
        if not self.avatar_path.exists():
            self.avatar_path.mkdir()
        self.db = mydb(sql.connect(str(self.path / 'wechat_data.db')))
        self.first_run()
    def first_run(self):
        if not self.db.table_exists('friend_info'):
            friends = self.friends()
            groups = self.groups()
            mps = self.mps()
            for i in friends+groups+mps:
                self.update_user_info_one(i,is_append=True)

    async def get_avatar_one(self,user,name):
        async with semaphore:
            loop = asyncio.get_event_loop()
            fu = loop.run_in_executor(None,user.get_avatar)
            im = await fu
            open(name,'wb').write(im)
            print(name)

    def get_avatar_all(self):
        loop = asyncio.get_event_loop()
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
        
        self.senders = {self.get_user_yxsid(s): s for s in self.friends()+self.groups()}

    def send_data(self,data,target):
        if self.senders is None:
            return

        friend = self.senders[target['yxsid']]
        print(data,target)
        friend.send(data.decode('utf8'))
    def get_message(self,msg):
        yxsid = self.get_user_yxsid(msg.chat)
        receiver = self.message_dispatcher.get(yxsid)
        if receiver is not None and msg.type == wxpy.TEXT:
            receiver((msg.text.encode('utf8'),yxsid))
        print(msg)
    def update_user_info(self):
        t = self.db.table_exists('friend_info')
        if not t:
            friends = self.friends()

if __name__=='__main__':
    bot = myBot(cache_path=True)
    # @bot.register()
    # def get_message(msg):
    #     bot.get_message(msg)
    # bot.enable_yxsid()
    # bot.conversation_list()
    # input()
    s=bot.chats()
    for i in s:
        print(i)
