import os
import time
import random
import subprocess
import progressbar
p1 = progressbar.ProgressBar()

check_str = '903408ec4d951acfaeb47ca88390c475'

def load_words():
    with open('words_alpha.txt') as word_file1:
        valid_words = word_file1.read().split()
    return valid_words

def check_if_right(hex_code, encode_len):
    check = r'encrypt.exe "' + hex_code + '"'  # exe文件的绝对路径
    a = subprocess.getstatusoutput(check)
    return 1, a[1]

def main():
    f = open("bad_words_d1.txt", "w")
    g = open("final_test_code.txt", 'w')
    word_listd = list()
    word_liste = list()
    english_words = load_words()
    print("total words number:", len(english_words))
    #pop out the word which length bigger than 4
    for w in english_words:
        if len(w) > 3:
            if len(w) < 7:
                #if w[0] == 't':
                if w != 'fuck' and w != 'shit':
                    word_listd.append(w)
    word_list1 = word_listd
    list_lengthd = len(word_listd)
    print("words length:", list_lengthd)
    print("total words to search:", list_lengthd ** 3)
    p1.start(1000)
    count1 = 0
    size = 45
    num_list = []
    first = random.randint(0, list_lengthd - 1)
    second = random.randint(0, list_lengthd - 1)
    for i in range(list_lengthd):
        for j in range(list_lengthd):
            while [first, second] in num_list:
                first = random.randint(0, list_lengthd-1)
                second = random.randint(0, list_lengthd-1)
            num_list.append([first, second])
            #for k in range(list_lengthe):
            combine = word_list1[first] + '.' + word_list1[second] + '.' + word_list1[random.randint(0, list_lengthd-1)]
            if len(combine) == 16:
                hex_code = combine.encode().hex()
                encoded, code = check_if_right(hex_code, len(hex_code))
                if encoded == 1:
                    gap = size - len(combine)
                    f.write(combine + ":" + " "*gap + code + '\n')
                    g.write(code + '\n')
                    count1 += 1
                    if count1 == 1000:
                        p1.update(count1)
                        exit()

            p1.update(count1)
    f.close()
    g.close()
    exit()


if __name__ == '__main__':
    main()