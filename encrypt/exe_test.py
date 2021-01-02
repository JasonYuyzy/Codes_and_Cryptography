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
    f = open("bad_words_a.txt", "w")
    word_list = list()
    english_words = load_words()
    for w in english_words:
        if w[0] == 'a':
            word_list.append(w)
    word_list1 = word_list
    list_length = len(word_list)
    print("words length:", list_length)
    print("total words:", list_length ** 3)
    for i in range(list_length):
        for j in range(list_length):
            for k in range(list_length):
                combine = word_list1[i] + '.' + word_list1[j] + '.' + word_list1[k]
                hex_code = combine.encode().hex()
                #combine = 'tile' + '.' + 'bills' + '.' + 'print'
                useless = check_if_right(hex_code, len(hex_code))
                if useless:
                    #three equal
                    if word_list1[i] == word_list1[j] and word_list1[j] == word_list1[k]:
                        f.write(word_list1[i] + '\n')

                    else:
                        #two equal
                        if word_list1[i] == word_list1[j]:
                            f.write(word_list1[i] + '\n')
                            f.write(word_list1[k] + '\n')
                        elif word_list1[j] == word_list1[k]:
                            f.write(word_list1[j] + '\n')
                            f.write(word_list1[i] + '\n')
                        elif word_list1[i] == word_list1[k]:
                            f.write(word_list1[i] + '\n')
                            f.write(word_list1[j] + '\n')
                        else:
                            #no equal
                            f.write(word_list1[i] + '\n')
                            f.write(word_list1[j] + '\n')
                            f.write(word_list1[k] + '\n')

            print("About {:.2%} search done so far...".format((i + j + k) / (list_length ** 3)))
        #print("2  About {:.2%} search done so far...".format((i + j + k) / (list_length ** 3)))


if __name__ == '__main__':
    main()