import os
import subprocess
from subprocess import Popen, PIPE

location = "./encrypt.exe"

os.system(location + ' "0123456789abcdef"')

main = r'./encrypt.exe "0123456789abcdef"'  # exe文件的绝对路径
a = subprocess.getstatusoutput(main)
print(a)

'''
p= Popen([location],stdin=PIPE,stdout=PIPE,stderr=PIPE, encoding="UTF8")
command='START'
p.stdin.write(command)
response=p.stdout.readine()
'''