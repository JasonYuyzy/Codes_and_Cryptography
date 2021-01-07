import os
import sys
import time
import math
from typing import Dict, List
from six import int2byte

# buile the data collection
node_dict = {}
count_dict = {}
ec_dict = {}
nodes = []
inverse_dict = {}

# design the node of Huffman coding
class hu_node(object):
    def __init__(self, value=None, left=None, right=None, father=None):
        self.value = value
        self.left = left
        self.right = right
        self.father = father

    def build_father(left, right):
        n = hu_node(value=left.value + right.value, left=left, right=right)
        left.father = right.father = n
        return n

    def encode(n):
        if n.father == None:
            return b''
        if n.father.left == n:
            # left branch '0'
            return hu_node.encode(n.father) + b'0'
        else:
            # right branch '1'
            return hu_node.encode(n.father) + b'1'

def file_compress(file):
    #print("Starting encode...")
    f = open(file, "rb")
    count = os.path.getsize(file)
    print("Compress file size:", count)
    prepare = bytes.decode(f.read())

# compressing with Huffman
    i = 0
    raw = 0b1
    buff = Huffman(file, count)
    # sort all the branch number
    head = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    # change the bit width to optimized the size
    if head[0][1] > 255:
        bit_width = 2
        if head[0][1] > 65535:
            bit_width = 3
            if head[0][1] > 16777215:
                bit_width = 4
    else:
        bit_width = 1

    Huf = open("test_compare/md_hu.lz", 'wb')
    # write the branch humber
    Huf.write(int.to_bytes(len(ec_dict), 2, byteorder='big'))
    # write the byte width
    Huf.write(int.to_bytes(bit_width, 1, byteorder='big'))
    # encode the head
    for x in ec_dict.keys():
        Huf.write(x)
        Huf.write(int.to_bytes(count_dict[x], bit_width, byteorder='big'))
    # compressing
    while i < count:
        for x in ec_dict[buff[i]]:
            raw = raw << 1
            if x == 49:
                raw = raw | 1
            if raw.bit_length() == 9:
                raw = raw & (~(1 << 8))
                Huf.write(int.to_bytes(raw, 1, byteorder='big'))
                Huf.flush()
                raw = 0b1
                tem = int(i / len(buff) * 100)

        i = i + 1
    # handle the last bit
    if raw.bit_length() > 1:
        raw = raw << (8 - (raw.bit_length() - 1))
        raw = raw & (~(1 << raw.bit_length() - 1))
        Huf.write(int.to_bytes(raw, 1, byteorder='big'))
    Huf.close()

#compressing with LZW
    LZW = open("compare_file/md_W.lz", 'wb')
    have_dict = 0
    dict_num = list()
    key = list()
    final_LZW, d_dict = LZ_W(file, count)
    #waiting list for changing the extra dict(if the char is not appear in the dict)
    if d_dict != {}:
        have_dict = 1
        for d_key in d_dict:
            key.append(d_key)
            dict_num.append(d_dict[d_key])

        #changing the dictionary bit width to optimize the size
        head_DN = max(dict_num)
        #print("head_DN:", head_DN)
        if head_DN > 255:
            DN_bit_width = 2
            if head_DN > 65535:
                DN_bit_width = 3
                if head_DN > 16777215:
                    DN_bit_width = 4
        else:
            DN_bit_width = 1

        dict_char_len = sum(len(d_c_l) for d_c_l in key)
        dict_length = len(dict_num) * DN_bit_width + dict_char_len
        #changing the bit width of the total length of the extra dictionary
        if dict_length > 255:
            DL_bit_width = 2
            if dict_length > 65535:
                DL_bit_width = 3
                if dict_length > 16777215:
                    DL_bit_width = 4
        else:
            DL_bit_width = 1
        #record whether have the extra dictionary (have)
        LZW.write(int.to_bytes(have_dict, 1, byteorder='big'))
        #record the coding ditionary number bit width
        LZW.write(int.to_bytes(DN_bit_width, 1, byteorder='big'))
        # record the coding ditionary length bit width
        LZW.wrtie(int.to_bytes(DL_bit_width, 1, byteorder='big'))
        #record the totally bit length
        LZW.wrtie(int.to_bytes(dict_length, DL_bit_width, byteorder='big'))
        #recording the extra dictionary
        for num in range(len(key)):
            LZW.write(key[num].encode(encoding="utf-8"))
            LZW.write(int.to_bytes(dict_num[num], DN_bit_width, byteorder='big'))
    else:
        # record whether have the extra dictionary (have)
        LZW.write(int.to_bytes(have_dict, 1, byteorder='big'))

    # changing the symbol bit width to optimized the size
    head_W = max(final_LZW)
    #print("head_W:", head_W)
    if head_W > 255:
        s_bit_width = 2
        if head_W > 65535:
            s_bit_width = 3
            if head_W > 16777215:
                s_bit_width = 4
    else:
        s_bit_width = 1
    #record the symbol bit width
    #print("S_BIT:", s_bit_width)
    LZW.write(int.to_bytes(s_bit_width, 1, byteorder='big'))
    #record the symbol into byte
    for final_num in final_LZW:
        LZW.write(int.to_bytes(final_num, s_bit_width, byteorder='big'))

    LZW.close()

    #LZW_decode = open("md_W.lz", 'rb')

    #print("extra:", int.from_bytes(LZW_decode.read(1), byteorder='big'))
    #os_bit_width = int.from_bytes(LZW_decode.read(1), byteorder='big')
    #while True:
    #    print(int.from_bytes(LZW_decode.read(os_bit_width), byteorder='big'))
    #    if LZW_decode.read(os_bit_width) == b'':
    #        break
    #exit()


#compressing with the LZ77
    if count != len(prepare):
        count = len(prepare)
    final = LZ_77(prepare, count)
    LZ77 = open("compare_file/md_77.lz", "wb")
    pointer, length, word = [], [], []
    for message in final:
        pointer.append(message[0])
        length.append(message[1])
        word.append(message[2])

    pointer_h = max(pointer)
    length_h = max(length)
    #print("pointer head for LZ77:", pointer_h)
    #print("length head for LZ77:", length_h)
    # change the bit width to optimized the size
    if pointer_h > 255:
        p_bit_width = 2
        if pointer_h > 65535:
            p_bit_width = 3
            if pointer_h > 16777215:
                p_bit_width = 4
    else:
        p_bit_width = 1
    # change the bit width to optimized the size
    if length_h > 255:
        l_bit_width = 2
        if length_h > 65535:
            l_bit_width = 3
            if length_h > 16777215:
                l_bit_width = 4
    else:
        l_bit_width = 1

    LZ77.write(int.to_bytes(l_bit_width, 1, byteorder='big'))
    LZ77.write(int.to_bytes(p_bit_width, 1, byteorder='big'))

    for num in range(len(pointer)):
        LZ77.write(word[num].encode(encoding="utf-8"))
        LZ77.write(int.to_bytes(length[num], l_bit_width, byteorder='big'))
        LZ77.write(int.to_bytes(pointer[num], p_bit_width, byteorder='big'))

    LZ77.close()

#compressing with the LZ78
    pack = LZ_78(prepare)
    LZ78 = open("compare_file/md_78.lz", "wb")
    pointer, word = [], []
    for d in pack:
        pointer.append(d[0])
        word.append(d[1])
    head_78 = max(pointer)
    #print("pointer head for LZ78:", head_78)
    # change the bit width to optimized the size
    if head_78 > 255:
        bit_width_78 = 2
        if head_78 > 65535:
            bit_width_78 = 3
            if head_78 > 16777215:
                bit_width_78 = 4
    else:
        bit_width_78 = 1

    LZ78.write(int.to_bytes(bit_width_78, 1, byteorder='big'))
    for num in range(len(pointer)):
        if word[num] == '':
            LZ78.write(b'')
            #print(pointer[num], word[num].encode())
        else:
            #print(word[num].encode(encoding="utf-8"))
            LZ78.write(word[num].encode(encoding="utf-8"))
        LZ78.write(int.to_bytes(pointer[num], bit_width_78, byteorder='big'))
        ##############test the difference of the encoding
        #print(int.to_bytes(pointer[num], bit_width_78, byteorder='big'))
        #print(pointer[num].to_bytes(length=bit_width_78, byteorder='big'))
    #exit()

    LZ78.close()

    f.close()
    #print("SSSSS:", os.path.getsize("compare_file/md_77.lz"), os.path.getsize("compare_file/md_78.lz"), os.path.getsize("compare_file/md_W.lz"))
    return os.path.getsize("compare_file/md_77.lz"), os.path.getsize("compare_file/md_78.lz"), os.path.getsize("compare_file/md_W.lz"), os.path.getsize("compare_file/md_hu.lz")


def Huffman(file, count):
    f = open(file, "rb")
    i = 0
    nodes = []
    buff = [b''] * int(count)
    # count the frequency
    while i < count:
        buff[i] = f.read(1)
        if count_dict.get(buff[i], -1) == -1:
            count_dict[buff[i]] = 0
        count_dict[buff[i]] = count_dict[buff[i]] + 1
        i = i + 1

    for x in count_dict.keys():
        node_dict[x] = hu_node(count_dict[x])
        nodes.append(node_dict[x])
    f.close()
    # building the huffman tree
    tree = build_tree(nodes)
    # building the code form
    encode(False)
    return buff

#building the huffman tree
def build_tree(l):
    if len(l) == 1:
        return l
    sorts = sorted(l, key=lambda x: x.value, reverse=False)
    n = hu_node.build_father(sorts[0], sorts[1])
    sorts.pop(0)
    sorts.pop(0)
    sorts.append(n)
    return build_tree(sorts)

def encode(echo):
    for x in node_dict.keys():
        ec_dict[x] = hu_node.encode(node_dict[x])
        #output the form for testing
        if echo == True:
            print(x)
            print(ec_dict[x])

def LZ_W(file, count):
    # original dictionary
    ORIGINAL_CDICT = dict(zip((int2byte(x) for x in range(256)), range(256)))
    odict: Dict[bytes, int] = ORIGINAL_CDICT.copy()  # 字符串编码表
    cdict = odict.copy()
    f = open(file, "rb")
    p_char = b''
    different_dict = {}
    buff = [b''] * int(count)
    message = []
    dict_num = len(odict)
    symbol = 0
    i = 0
    bytes_width = 1
    while i < count:
        buff[i] = f.read(bytes_width)
        if odict.get(buff[i], -1) == -1:
            odict[buff[i]] = symbol
            symbol += 1
        i += 1
    for diff in odict:
        if diff not in cdict:
            different_dict.update({diff: odict[diff]})

    #encoding the main text
    for c_char in buff:
        p_c = p_char + c_char
        if p_c in odict:
            p_char = p_c
        else:
            message.append(odict[p_char])
            odict.update({p_c: dict_num})
            dict_num += 1
            p_char = c_char

    message.append(odict[p_char])
    f.close()
    return message, different_dict


def LZ_77(line, count):
    length = 0
    win = count
    pointer = 0
    message = line
    print("message length:", len(message))

    compressed_message = list()  #message temporal storage
    #encoding the main text
    while True:

        #if pointer > 1179:
            #time.sleep(3)
            #print("length update:", length, "pointer update:", pointer)
            #print(message[pointer:pointer+length])
            #print(match.find(message[pointer:pointer + length + 1]) != -1)
            #print(first)

        if pointer - win < 0:
            match = message[0:pointer]
        else:
            match = message[pointer - win:pointer]
        while match.find(message[pointer:pointer + length + 1]) != -1:
            if pointer + length == count - 1:
                break
            length += 1

            #if pointer > 1179:
                #print(message[pointer:pointer + length])
                #print(match.find(message[pointer:pointer + length + 1]) != -1)
                #time.sleep(3)

        first = match.find(message[pointer:pointer + length])
        if pointer - win > 0:
            first += pointer - win
        if length != 0:
            a = (pointer - first,length,message[pointer + length])
            compressed_message.append(a)
            pointer += length + 1
        else:
            b = (0,0,message[pointer])
            compressed_message.append(b)
            pointer += 1

        length = 0
        #if pointer > 1179:
            #print(match.find(message[pointer:pointer + length + 1]) != -1)
        if pointer == len(message):
            break
    #print(compressed_message)
    return compressed_message

def LZ_78(line):
    tree_dict, m_len, i = {}, len(line), 0
    #encoding the main text
    while i < m_len:
        #print(len(tree_dict))
        # case I
        if line[i] not in tree_dict.keys():
            #print("I:", tree_dict.get(line[i]))
            #print("I:", line[i])
            yield (0, line[i])
            tree_dict[line[i]] = len(tree_dict) + 1
            i += 1
        # case III
        elif i == m_len - 1:
            yield (tree_dict.get(line[i]), '')
            #print("III:", tree_dict.get(line[i]))
            #print("III:", line[i])
            i += 1
        else:
            for j in range(i + 1, m_len):
                # case II
                if line[i:j + 1] not in tree_dict.keys():
                    yield (tree_dict.get(line[i:j]), line[j])
                    #print("II:", tree_dict.get(line[i:j]))
                    #print("II:", line[i:j])
                    #print("II:", line[j])
                    tree_dict[line[i:j + 1]] = len(tree_dict) + 1
                    i = j + 1
                    break
                # case III
                elif j == m_len - 1:
                    yield (tree_dict.get(line[i:j + 1]), '')
                    #print("III2:", tree_dict.get(line[i:j+1]))
                    #print("III2:", line[i:j+1])
                    #print("III2:", line[j])
                    i = j + 1

def main():
    byte_width = 1
    #take the file name
    file_name = sys.argv[1]
    input_file = file_name.split('.')
    output_name = input_file[0]
    smallest_file = open(output_name + '.lz', 'wb')
    esize_77, esize_78, esize_W, esize_Hu = file_compress(file_name)
    smallest = min([esize_77, esize_78, esize_W])
    if smallest == esize_77:
        s_77 = open("compare_file/md_77.lz", 'rb')
        smallest_file.write(int.to_bytes(77, byte_width, byteorder='big'))
        smallest_file.write(s_77.read())
        s_77.close()
        smallest_file.close()
    elif smallest == esize_78:
        s_78 = open("compare_file/md_78.lz", 'rb')
        smallest_file.write(int.to_bytes(78, byte_width, byteorder='big'))
        smallest_file.write(s_78.read())
        s_78.close()
        smallest_file.close()
    elif smallest == esize_W:
        s_W = open("compare_file/md_W.lz", 'rb')
        smallest_file.write(int.to_bytes(79, byte_width, byteorder='big'))
        smallest_file.write(s_W.read())
        s_W.close()
        smallest_file.close()
    else:
        s_Hu = open("compare_file/md_hu.lz", 'rb')
        smallest_file.write(int.to_bytes(80, byte_width, byteorder='big'))
        smallest_file.write(s_Hu.read())
        s_Hu.close()
        smallest_file.close()

    #print ("LZ78 encode size:", esize_78,'\n',"LZ77 encode size:", esize_77,'\n',"LZ_W encode size:", esize_W,'\n')
    #dsize_78, dsize_77, dsize_W = file_uncompress("md_78.lz", "md_77.lz", "md_W.lz", output_name)
    #print("LZ78 decode size:",dsize_78,'\n',"LZ77 decode size:",dsize_77, '\n',"LZ_W decode size:", dsize_W)

if __name__ == "__main__":
    main()

