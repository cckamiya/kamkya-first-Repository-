import os,sys
import signal
from socket import *
import time
import traceback
from multiprocessing import *
import pymysql

class edict_server(object):
    def __init__(self,c,db):
        self.c=c
        self.db=db
        
    

    def do_exit(self):
        self.c.close()
        
        #self.db.close()

    def do_history(self,name):
        cursor=self.db.cursor()
        sql_select='select * from hist where name=%s;'
        try:
            cursor.execute(sql_select,[name])
            data=cursor.fetchall()
            print(data)
        except Exception:
            traceback.print_exc()
        if not data:
            self.c.send('H 无历史记录!'.encode())
            return
        else:
            for sid,name,word,t in data:
                print(str(sid)+','+name+','+word+','+t)
                data=str(sid)+','+name+','+word+','+t+'\n'
                self.c.send(data.encode())
            time.sleep(0.2)
            self.c.send('##'.encode())





    def do_register(self,name,passwd):
        sql_select='select name from user where name=%s;'
        cursor=self.db.cursor()
        try:
            cursor.execute(sql_select,[name])
            data=cursor.fetchone()
        except Exception:
            traceback.print_exc()
        #没找到该姓名,则可以注册
        if data is None:
            sql_insert='insert into user(name,passwd) values(%s,%s);'
            try:
                cursor.execute(sql_insert,[name,passwd])
                self.db.commit()
                self.c.send('ok'.encode())
                
            except Exception:
                traceback.print_exc()
                self.db.rollback()
                self.c.send("注册失败!".encode())
        else:
            self.c.send("改名已被注册，请重新输入名称!".encode())
    




    def do_login(self,name,passwd):
        sql_select='select name,passwd from user where name=%s;'
        cursor=self.db.cursor()
        try:
            cursor.execute(sql_select,[name])
            data=cursor.fetchone()
            print(data)
        except Exception:
            traceback.print_exc()
        if data is None:
            self.c.send('该用户不存在!'.encode())
            return
        if name==data[0] and passwd==data[1]:
            self.c.send('ok'.encode())
            self.name=name
        elif name==data[0] and passwd!=data[1]:
            self.c.send('输入密码错误,请重新输入!'.encode())

    def do_select(self,word):
        sql_select='select interpret from words where word=%s;'
        cursor=self.db.cursor()
        try:
            cursor.execute(sql_select,[word])
            interpret=cursor.fetchone()
            print(interpret)
        except Exception:
            traceback.print_exc()
        if interpret is None:
            self.c.send('查无此单词!'.encode())
            return
        else:
            data='S '+interpret[0]
            self.c.send(data.encode())
            t=time.asctime(time.localtime())
            sql_insert='insert into hist(name,word,time) values(%s,%s,%s);'
            try:
                cursor.execute(sql_insert,[self.name,word,t])
                self.db.commit()
            except Exception as e:
                traceback.print_exc()
                self.db.rollback()



def handler(c,db,addr):
    edict=edict_server(c,db)
    while True:
        data=c.recv(1024).decode()
        if not data:#每一个子进程对应着一个客户端，当客户端异常退出，这个子进程也退出
            edict.do_exit()
            sys.exit("客户端: "+addr[0]+','+str(addr[1])+" 已退出!")
        
        #print(data[0])
        if data[0]=='R':
            L=data.split(' ')
            print(L)
            name=L[1]
            passwd=L[2]
            print(name,passwd)
            edict.do_register(name,passwd)
        elif data[0]=='L':
            L=data.split(' ')
            name=L[1]
            passwd=L[2]
            print(name,passwd)
            edict.do_login(name,passwd)
        elif data[0]=='S':
            word=data[2:]
            edict.do_select(word)
        elif data[0]=='H':
            name=data[2:]
            edict.do_history(name)
        elif data[0]=='Q':
            name=data[2:]
            print(name+"已退出!")
        elif data=='exit':
            edict.do_exit()
            sys.exit("客户端: "+addr[0]+','+str(addr[1])+" 已退出!")





def main():
    s=socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(('0.0.0.0',8888))
    s.listen(5)
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    db=pymysql.connect('localhost','root','123456','dict')
    
    while True:
        try:
            c,addr=s.accept()
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务端退出")
        except Exception:
            traceback.print_exc()
            continue
        print(addr,'已连接!')
        p=Process(target=handler,args=(c,db,addr))
        p.daemon=True
        p.start()
    print("服务端结束!")

        









if __name__ == '__main__':
    main()


