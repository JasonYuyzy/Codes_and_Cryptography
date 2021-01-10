import time
import random
import progressbar
import subprocess
from des import DesKey
from multiprocessing import Pool

check_str = '903408ec4d951acfaeb47ca88390c475'
p = progressbar.ProgressBar()

def load_words():
    with open('words_alpha.txt') as word_file1:
        valid_words = word_file1.read().split()
    word_file1.close()
    return valid_words


def check_if_right(hex_code):
    check = r'encrypt.exe "' + hex_code + '"'
    a = subprocess.getstatusoutput(check)
    #check = key.encrypt(words)
    if a[1] == check_str:
        return 1, a[1]
    else:
        return 0, ''


def task():
    print("processing from:", time.ctime())
    final = open("final.txt", "r")
    word_list2 = list()
    word_list3 = list()
    for line in final.readlines():
        words = line.split(':')[0]
        f_word = words.split('.')[0]
        word_list2.append(words.split('.')[1])
    final.close()
    english_words = load_words()
    # pop out the word which length bigger than 3 smaller than 7
    for w in english_words:
        if len(w) > 3:
            if len(w) < 7:
                if w != 'fuck' and w != 'shit':
                    word_list3.append(w)

    list_length2 = len(word_list2)
    list_length3 = len(word_list3)
    # search the target
    count = 0
    p.start(list_length2*list_length3)
    for i in range(list_length2):
        for j in range(list_length3):
            combine = f_word + '.' + word_list2[i] + '.' +word_list3[j]
            if len(combine) == 16:
                words = combine.encode().hex()
                encoded, code = check_if_right(words)
                if encoded == 1:
                    out = combine + ":"
                    print(out.ljust(20, ' ') + code + '\n')
                    print("processing till:", time.ctime())
                    return
            count += 1
            p.update(count)


if __name__ == '__main__':
    start = time.time()
    task()
    end = time.time()
    print("The searching time is:", end-start)
