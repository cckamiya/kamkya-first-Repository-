import pymysql
import re

f=open("dict.txt")
db=pymysql.connect('localhost','root','123456','dict')
cursor=db.cursor()

for line in f:
    L=re.split(r'\s+',line)
    word=L[0]
    interpret=' '.join(L[1:])
    sql_insert='insert into words(word,interpret) values(%s,%s);'
    try:
        cursor.execute(sql_insert,[word,interpret])
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
cursor.close()
db.close()

f.close()