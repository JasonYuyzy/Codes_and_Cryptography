#-×- coding:utf-8 -*-
import time
a=open('test.tex','r')
b=open('decode_78.tex', 'r')
row=0

print("first checking...")
for linea,lineb in zip(a,b):
    row+=1
    if not linea==lineb:
        col=0
        for chara,charb in zip(linea,lineb):
            col+=1
            if not chara==charb:
                print("difference in row:%d col:%d"%(row,col))
                break
print("text is right")
a.close()
b.close()


print("second checking...")
a=open('test.tex','rb')
b=open('decode_78.tex', 'rb')

row = 0

for linea,lineb in zip(a,b):
    row+=1
    la = bytes.decode(linea)
    lb = bytes.decode(lineb)
    if not la == lb:
        col=0
        for chara,charb in zip(la, lb):
            col+=1
            if not chara==charb:
                print("difference in row:%d col:%d"%(row,col))
                print("the difference: ", str.encode(chara), str.encode(charb))
                print("un_b_a:", linea)
                print("un_b_b:", lineb)
                exit()
                break

a.flush()
b.flush()

a_text = bytes.decode(a.read())
b_text = bytes.decode(b.read())
if len(a_text) != len(b_text):
    print("different length: byte error")
    print("a:", len(a_text))
    print("b:", len(b_text))
    a.close()
    b.close()
    exit()
print("checking finished, well done")
