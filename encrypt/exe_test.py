#import os
import time
import random
import subprocess
from multiprocessing import Pool

check_str = '903408ec4d951acfaeb47ca88390c475'

def load_words():
    with open('10k_words.txt') as word_file1:
        valid_words = word_file1.read().split()
    return valid_words


def check_if_right(hex_code, num):
    check = r'encrypt' + str(num) + '.exe "' + hex_code + '"'
    a = subprocess.getstatusoutput(check)
    if a[1][0:16] == check_str[0:16]:
        return 1, a[1]
    else:
        return 0, ''


def task(num):
    print("processing from:", num, "~", num + 1000)
    final = open("final.txt", "a+")
    range_chose = num + 1000
    word_list1 = list()
    word_list2 = list()
    word_list4 = list()
    word_list5 = list()
    word_list6 = list()
    english_words = load_words()
    print("Processing: start from", num, "total words number:", len(english_words))

    # pop out the word which length bigger than 3 smaller than 7
    for w in english_words:
        if len(w) > 3:
            if len(w) < 7:
                if w != 'fuck' and w != 'shit':
                    word_list1.append(w)
                    word_list2.append(w)
                if len(w) == 4:
                    word_list4.append(w)
                if len(w) == 5:
                    word_list5.append(w)
                if len(w) == 6:
                    word_list6.append(w)

    list_length1 = len(word_list1)
    list_length2 = len(word_list2)
    list_length4 = len(word_list4)
    list_length5 = len(word_list5)
    list_length6 = len(word_list6)
    if range_chose > list_length1:
        range_chose = list_length1
    write_in = 0
    # search the target
    count = 0
    for i in range(num, range_chose):
        for j in range(list_length2):
            combine = word_list1[i] + '.' + word_list2[j] + '.'
            if len(combine) == 10:
                combine += word_list6[random.randint(0,list_length6-1)]
            elif len(combine) == 11:
                combine += word_list5[random.randint(0,list_length5-1)]
            elif len(combine) == 12:
                combine += word_list4[random.randint(0,list_length4-1)]
            if len(combine) == 16:
                hex_code = combine.encode().hex()
                encoded, code = check_if_right(hex_code, num)
                if encoded == 1:
                    out = combine + ":"
                    final.write(out.ljust(20, ' ') + code + '\n')
                    write_in += 1
            count += 1
        if i%10 == 0:
            print("Processing: start from ", num, "There are totally {0} recorded".format(count))

    print("Processing: start from ", num, "There are totally {0} recorded".format(write_in))
    final.close()


if __name__ == '__main__':
    print("processing start:", time.ctime())
    start = time.time()
    p = Pool(2)
    pending_list = [0, 1000, 2000, 3000, 4000]
    for i in pending_list:
        p.apply_async(task, args=(i,))
    p.close()
    p.join()
    end = time.time()
    print("The total searching time is:", end - start)

