import os
import time
import subprocess

check_str = '903408ec4d951acfaeb47ca88390c475'

def load_words():
    with open('words_alpha.txt') as word_file1:
        valid_words = word_file1.read().split()
    return valid_words

def check_if_right(hex_code):
    check = r'encrypt.exe "' + hex_code + '"'  # exe文件的绝对路径
    a = subprocess.getstatusoutput(check)
    if a[1] == check_str:
        return True
    else:
        False