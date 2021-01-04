import os
import time
import random
import subprocess
import progressbar
from rich.progress import track
p = progressbar.ProgressBar()

check_str = '903408ec4d951acfaeb47ca88390c475'

def load_words():
    with open('words_alpha.txt') as word_file1:
        valid_words = word_file1.read().split()
    return valid_words

def check_if_right(hex_code, encode_len):
    check = r'encrypt.exe "' + hex_code + '"'
    a = subprocess.getstatusoutput(check)
    return 1, a[1]

def main():
    f = open("bad_words_d1.txt", "a+")
    word_list1 = list()
    word_list2 = list()
    word_list3 = list()
    total = 1200
    head = 'til bill prin'
    head_list = head.split(' ')
    w1, w2, w3 = head_list[0], head_list[1], head_list[2]
    english_words = load_words()
    print("total words number:", len(english_words))
    #pop out the word which length bigger than 4
    for w in track(english_words):
        if len(w) > 3:
            if len(w) < 7:
                if w != 'fuck' and w != 'shit':
                    if w[0:3] == w1:
                        word_list1.append(w)
                    if w[0:4] == w2:
                        word_list2.append(w)
                    if w[0:4] == w3:
                        word_list3.append(w)

    list_length1 = len(word_list1)
    list_length2 = len(word_list2)
    list_length3 = len(word_list3)
    print("words start with {0} : {1}".format(w1, list_length1))
    print("words start with {0} : {1}".format(w2, list_length2))
    print("words start with {0} : {1}".format(w3, list_length3))
    write_in = 0
    '''
    for i in range(list_length1):
        for j in range(list_length2):
            for k in track(range(total)):
                first = random.randint(0, list_length1 - 1)
                second = random.randint(0, list_length2 - 1)
                third = random.randint(0, list_length3 - 1)
                if k < total/6:
                    combine = word_list1[first] + '.' + word_list2[second] + '.' + word_list3[third]
                elif k >= total/6 and k < (total*2)/6:
                    combine = word_list3[third] + '.' + word_list1[first] + '.' + word_list2[second]
                elif k >= (total*2)/6 and k < (total*3)/6:
                    combine = word_list3[third] + '.' + word_list2[second] + '.' + word_list1[first]
                elif k >= (total*3)/6 and k < (total*4)/6:
                    combine = word_list2[second] + '.' + word_list1[first] + '.' + word_list3[third]
                elif k >= (total*4)/6 and k < (total*5)/6:
                    combine = word_list1[first] + '.' + word_list3[third] + '.' + word_list2[second]
                else:
                    combine = word_list2[second] + '.' + word_list3[third] + '.' + word_list1[first]
                if len(combine) == 16:
                    hex_code = combine.encode().hex()
                    encoded, code = check_if_right(hex_code, len(hex_code))
                    if encoded == 1:
                        out = combine + ":"
                        f.write(out.ljust(20, ' ') + code + '\n')
                        write_in += 1
                if k == total - 1:
                    print("There are totally {0} recorded".format(write_in))
                    exit()'''
    p.start(list_length3 * list_length1 * list_length2)
    count = 0
    for i in range(list_length1):
        for j in range(list_length2):
            for k in range(list_length3):
                combine = word_list1[i] + '.' + word_list2[j] + '.' + word_list3[k]
                if len(combine) == 16:
                    hex_code = combine.encode().hex()
                    encoded, code = check_if_right(hex_code, len(hex_code))
                    if encoded == 1:
                        out = combine + ":"
                        f.write(out.ljust(20, ' ') + code + '\n')
                        write_in += 1
                count += 1
                p.update(count)
    print("There are totally {0} recorded".format(write_in))
    f.close()
    exit()


if __name__ == '__main__':
    main()