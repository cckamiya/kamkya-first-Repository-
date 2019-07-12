import os,sys
import signal
from socket import *
import time
import traceback

class edict_client(object):
    def __init__(self,s):
        self.s=s

    def do_exit(self):
        data="exit"
        self.s.send(data.encode())
        self.s.close()
        

    def do_quit(self):
        data="Q "+self.name
        self.s.send(data.encode())
        print(self.name+'退出登录!')

    def do_history(self):
        data='H　'+self.name
        self.s.send(data.encode())
        while True:
            data=self.s.recv(2048)
            if data.decode()[0]=='H':
                print(data.decode()[2:])
                return
            elif data.decode()=='##':
                return
            else:
                hist=data.decode()
                print(hist)



    def do_select(self):
        while True:
            word=input("请输入单词:")
            if not word:
                return
            data='S '+word
            self.s.send(data.encode())
            data=self.s.recv(2048)
            if data.decode()[0]=='S':
                interpret=data.decode()[2:]
                data=word+' : '+interpret
                print(data)
            else:
                print(data.decode())
                continue


    def do_login(self):
        name=input("请输入用户名:")
        passwd=input("请输入密码:")
        if not name or not passwd:
            print("输入有误!")
            return
        if ' ' in name or ' ' in passwd:
            print("用户名和密码不允许有空格!")
            return
        data='L {} {}'.format(name,passwd)
        self.s.send(data.encode())
        data=self.s.recv(1024)
        if data.decode()=='ok':
            #self.s.send(passwd.encode())
            print("登陆成功!")
            self.name=name
            self.passwd=passwd
            while True:
                print("+--------------------------------+")
                print("| 1) 查询单词  　　　　　　　　　|")
                print("| 2) 历史记录 　　　　　　　　　 |")
                print("| 3) 退出          　            |")
                print("+--------------------------------+")
                n=input('请输入选择:')
                if n=="1":
                    self.do_select()
                elif n=="2":
                    self.do_history()
                elif n=="3":
                    self.do_quit()
                    return
        else:
            print(data.decode())
            return

    def do_register(self):
        name=input("请输入用户名:")
        passwd=input("请输入密码:")
        passwd1=input("请再次输入密码:")
        if not name or not passwd:
            print("输入有误!")
            return
        if (' ' in name) or (' ' in passwd):
            print("用户名和密码不允许有空格!")
            return
        if passwd1 != passwd:
            print("两次密码输入不一致!")
            return    
        data='R {} {}'.format(name,passwd)
        self.s.send(data.encode())
        data=self.s.recv(1024)
        if data.decode()=='ok':
            #s.send(passwd.encode())
            print("注册成功,请登录!")
        else:
            print(data.decode())
            return



def main():
    s=socket()
    addr=()
    try:
        s.connect(('127.0.0.1',8888))
    except Exception as e:
        print("连接服务器失败:",e)
        return 
    edict=edict_client(s)
    while True:
        print("+--------------------------------+")
        print("| 1) 登录  　　　　　　　　　    |")
        print("| 2) 注册 　　　　　　　　　     |")
        print("| 3) 退出          　            |")
        print("+--------------------------------+")
        try:
            n=input('请输入选择:')
            if n=="1":
                edict.do_login()
            elif n=="2":
                edict.do_register()
            elif n=="3":
                edict.do_exit()
                sys.exit("客户端退出")
            else:
                print('输入有误，请重新输入!')
                sys.stdin.flush()#清除标准输入，让每次输入单独能识别，避免那种快速输入导致上次输入和下次输入粘连
                continue
        except KeyboardInterrupt:
            edict.do_exit()
            sys.exit("客户端退出")
    

    s.close()
    sys.exit("客户端退出")




if __name__ == '__main__':
    main()