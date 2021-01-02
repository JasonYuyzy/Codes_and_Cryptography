import os
import time
import subprocess

check_str = '903408ec4d951acfaeb47ca88390c475'

def load_words():
    with open('words_alpha.txt') as word_file1:
        valid_words = word_file1.read().split()
    return valid_words

def check_if_right(hex_code, encode_len):
    check = r'encrypt.exe "' + hex_code + '"'  # exe文件的绝对路径
    a = subprocess.getstatusoutput(check)
    if len(a[1]) != encode_len:
        return True
    else:
        False

def main():
    word_list = list()
    code_list = list()
    english_words = load_words()
    for w in english_words:
        if w[0] == 'a':
            word_list.append(w)
    word_list1 = word_list
    list_length = len(word_list)
    print("words length:", list_length)
    print("total words:", list_length ** 3)
    compare_list = list()
    for i in range(list_length):
        for j in range(list_length):
            for k in range(list_length):
                combine = word_list1[i] + '.' + word_list1[j] + '.' + word_list1[k]
                hex_code = combine.encode().hex()
                code_list.append(hex_code)
        print("{:.2%} combined...".format(list_length ** 2 / (list_length ** 3)))

    count = 0
    f = open("bad_words_a.txt", "a+")
    for code in code_list:
        useless = check_if_right(code, len(hex_code))
        if useless:
            if word_list1[i] not in compare_list:
                compare_list.append(word_list1[i])
                f.write(word_list1[i] + '\n')
            if word_list1[j] not in compare_list:
                compare_list.append(word_list1[j])
                f.write(word_list1[i] + '\n')
            if word_list1[k] not in compare_list:
                compare_list.append(word_list1[k])
                f.write(word_list1[k] + '\n')
        if len(compare_list) == len(code_list):
            print("finished early")
            exit()
        count += 1
        if count % 15 == 0:
            print("About {:.2%} search done so far...".format(count / len(code_list)))
    f.close()
    exit()


if __name__ == '__main__':
    main()