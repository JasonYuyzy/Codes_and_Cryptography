import os
import time
import subprocess

#goal: find the str: 903408ec4d951acfaeb47ca88390c475
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

def main():
    english_words = load_words()
    word_list1 = english_words
    word_list2 = english_words
    word_list3 = english_words

    list_length = len(english_words)
    starts = time.time()
    for i in range(list_length):
        for j in range(list_length):
            for k in range(list_length):
                combine = word_list1[i] + '.' + word_list2[j] + '.' + word_list3[k]
                #combine = 'tile' + '.' + 'bills' + '.' + 'print'
                location = check_if_right(combine.encode().hex())
                if location:
                    print("the final location is:", combine)
                    ends = time.time()
                    time_cost = ends - starts
                    print("searching time:", time_cost)
                    print("searching steps:", i + j + k)
                    exit()


if __name__ == '__main__':
    main()
