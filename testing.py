import os
import sys
import time
import math
from typing import Dict, List

from six import int2byte

# original data for Huffman coding
node_dict = {}
count_dict = {}
ec_dict = {}
nodes = []
inverse_dict = {}
# decode data
O_node_dict = {}
O_ec_dict = {}
O_nodes = []
O_inverse_dict = {}

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

#File_name = sys.argv[1]
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
    LZW = open("test_compare/md_W.lz", 'wb')
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

#compressing with the hybird double LZW

#compressing with the LZ77
    if count != len(prepare):
        count = len(prepare)
    final = LZ_77(prepare, count)
    LZ77 = open("test_compare/md_77.lz", "wb")
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
    LZ78 = open("test_compare/md_78.lz", "wb")
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
    return os.path.getsize("test_compare/md_77.lz"), os.path.getsize("test_compare/md_78.lz"), os.path.getsize("test_compare/md_W.lz"), os.path.getsize("test_compare/md_hu.lz")


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
    #print("Read OK")
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



def file_uncompress(file78, file77, fileW, fileHu, out_file):
    print("Started decoding:")
    #Huffman
    unpress_Hu = Huf_file_decode(fileHu)
    final_HU = open(fileHu.split('.')[0] + out_file, 'wb')
    final_HU.write(unpress_Hu.encode(encoding="utf-8"))
    final_HU.close()

    #LZW
    decodeW_d, decodeW_s = LZW_file_decode(fileW)
    unpress_LZW = uncompress_LZW(decodeW_d, decodeW_s)
    final_LZW = open(fileW.split('.')[0] + out_file, 'wb')
    final_LZW.write(unpress_LZW)
    final_LZW.close()

    #LZ77
    decode77 = LZ77_file_decode(file77)
    unpress_LZ77 = uncompress_LZ77(decode77)
    final_LZ77 = open(file77.split('.')[0] + out_file, 'wb')
    final_LZ77.write(unpress_LZ77.encode(encoding="utf-8"))
    final_LZ77.close()

    #LZ78
    decode78 = LZ78_file_decode(file78)
    unpress_LZ78 = uncompress_LZ78(decode78)
    final_LZ78 = open(file78.split('.')[0] + out_file, 'wb')
    final_LZ78.write(unpress_LZ78.encode(encoding="utf-8"))
    final_LZ78.close()

    return os.path.getsize(file78.split('.')[0] + out_file), os.path.getsize(file77.split('.')[0] + out_file), os.path.getsize(fileW.split('.')[0] + out_file), os.path.getsize(fileHu.split('.')[0] + out_file)

def O_encode(echo):
    for x in O_node_dict.keys():
        O_ec_dict[x] = hu_node.encode(O_node_dict[x])
        #output the form for testing
        if echo == True:
            print(x)
            print(O_ec_dict[x])

def Huf_file_decode(file):
    f = open(file, 'rb')
    d_of = os.path.getsize(file)
    # get the branch number
    count = int.from_bytes(f.read(2), byteorder='big')
    # get the byte width
    bit_width = int.from_bytes(f.read(1), byteorder='big')
    i = 0
    de_dict = {}
    # analyze the head
    while i < count:
        key = f.read(1)
        value = int.from_bytes(f.read(bit_width), byteorder='big')
        de_dict[key] = value
        i = i + 1
    for x in de_dict.keys():
        O_node_dict[x] = hu_node(de_dict[x])
        O_nodes.append(O_node_dict[x])
    # rebuild the tree
    tree = build_tree(O_nodes)
    # rebuild the form
    O_encode(False)
    # build the reverse dictionary
    for x in O_ec_dict.keys():
        O_inverse_dict[O_ec_dict[x]] = x
    i = f.tell()
    data = b''
    out_text = ''
    # start decoding
    while i < d_of:
        raw = int.from_bytes(f.read(1), byteorder='big')
        # print("raw:",raw)
        i = i + 1
        j = 8
        while j > 0:
            if (raw >> (j - 1)) & 1 == 1:
                data = data + b'1'
                raw = raw & (~(1 << (j - 1)))
            else:
                data = data + b'0'
                raw = raw & (~(1 << (j - 1)))
            if O_inverse_dict.get(data, 0) != 0:
                out_text += O_inverse_dict[data].decode()
                data = b''
            j = j - 1
    f.close()
    return out_text


def LZW_file_decode(file):
    f = open(file, 'rb')
    i = 0
    symbol = []
    extra_dict = {}
    count = os.path.getsize(file)
    have_dict = int.from_bytes(f.read(1), byteorder='big')
    i += 1
    if have_dict == 1:
        #get the key number width
        DN_bit_width = int.from_bytes(f.read(1), byteorder='big')
        #get the dictionary length width
        DL_bit_width = int.from_bytes(f.read(1), byteorder='big')
        #get the dictionary length
        dict_length = int.from_bytes(f.read(DL_bit_width), byteorder='big')
        while i < dict_length:
            #key = f.read(1).decode(encoding="utf-8")
            #d_num = int.from_bytes(f.read(DN_bit_width), byteorder='big')
            #update the extra dictionary
            extra_dict.update(({f.read(1).decode(encoding="utf-8"): int.from_bytes(f.read(DN_bit_width), byteorder='big')}))
            i += 1
    else:
        s_bit_width = int.from_bytes(f.read(1), byteorder='big')
        i += 1
    while i < count:
        symbol.append(int.from_bytes(f.read(s_bit_width), byteorder='big'))
        i += s_bit_width
    return extra_dict, symbol

def uncompress_LZW(decodeW_d, decodeW_s):
    # original dictionary
    ORIGINAL_CDICT = dict(zip((int2byte(x) for x in range(256)), range(256)))
    # reverse dictionary
    ORIGINAL_KDICT = [int2byte(x) for x in range(256)]
    odict: Dict[bytes, int] = ORIGINAL_CDICT.copy()  # 字符串编码表
    kdict: List[bytes] = ORIGINAL_KDICT.copy()  # 编码映射字符串
    i = 0
    #update the dictionary
    if decodeW_d != {}:
        for key in decodeW_d:
            odict.update({key: decodeW_d[key]})
    #decode the main text
    message = kdict[decodeW_s[i]]
    for i in range(1, len(decodeW_s)):
        if decodeW_s[i] < len(kdict):
            p_char = kdict[decodeW_s[i-1]]
            c_char = (kdict[decodeW_s[i]].decode())[0].encode()
            p_c = p_char + c_char
            kdict.append(p_c)
            #odict.update({p_c: kdict.index(p_c)})
            message += kdict[decodeW_s[i]]
        else:
            p_char = kdict[decodeW_s[i-1]]
            c_char = (kdict[decodeW_s[i-1]].decode())[0].encode()
            p_c = p_char + c_char
            kdict.append(p_c)
            #odict.update({p_c: len(kdict)})
            message += p_c

    return message


def LZ77_file_decode(file):
    f = open(file, "rb")
    i = 0
    #get the length of the encoded file
    count = os.path.getsize(file)
    #read the byte width of length and pointer
    l_b_width = int.from_bytes(f.read(1), byteorder='big')
    p_b_width = int.from_bytes(f.read(1), byteorder='big')
    message = []
    #start to decode message code of LZ77
    while i < count:
        word = f.read(1).decode(encoding="utf-8")
        length = int.from_bytes(f.read(l_b_width), byteorder='big')
        pointer = int.from_bytes(f.read(p_b_width), byteorder='big')
        message.append((pointer, length, word))
        i = i + p_b_width + l_b_width + 1
    return message

def uncompress_LZ77(message):
    #decoding the main text
    de_msg = ''
    for s in message:
        if s[0] != 0:
            de_msg += de_msg[(len(de_msg) - s[0]): (len(de_msg) - s[0] + s[1])]
        de_msg += s[2]
    return de_msg


def LZ78_file_decode(file):
    f = open(file, "rb")
    i = 0
    #get the length of the encoded file
    count = os.path.getsize(file)
    # read the byte width of length and pointer
    b_width = int.from_bytes(f.read(1), byteorder='big')
    i += 1
    # start to decode message code of LZ78
    while i < count:
        #last group of encoded
        if i > count - b_width - 2:
            #print("DECIDE:", count - i)
            if count - i > 2:
                #drop one more bytes
                last_w = f.read(1).decode(encoding="utf-8")
                last_p = int.from_bytes(f.read(b_width), byteorder='big')
                yield (last_p, last_w)
                i = i + b_width + 1
            else:
                i = i + b_width
                last_p = int.from_bytes(f.read(b_width), byteorder='big')
                yield (last_p, '')
        else:
            word = f.read(1).decode(encoding="utf-8")
            pointer = int.from_bytes(f.read(b_width), byteorder='big')
            yield (pointer, word)
            i = i + b_width + 1


def uncompress_LZ78(packed):
    #decoding the main text
    unpacked, tree_dict = '', {}
    for index, ch in packed:
        if index == 0:
            unpacked += ch
            tree_dict[len(tree_dict) + 1] = ch
        else:
            term = tree_dict.get(index) + ch
            unpacked += term
            tree_dict[len(tree_dict) + 1] = term

    return unpacked




if __name__ == "__main__":
    node_dict = {}
    count_dict = {}
    ec_dict = {}
    nodes = []
    inverse_dict = {}
    file_name = sys.argv[1]
    input_file = file_name.split('.')
    output_name = '.' + input_file[1]
    esize_77, esize_78, esize_W, esize_hu = file_compress(file_name)
    print("LZ78 encode size:", esize_78, '\n', "LZ77 encode size:", esize_77, '\n', "LZ_W encode size:", esize_W, '\n',
          "Huffman encode size:", esize_hu, '\n')

    node_dict = {}
    count_dict = {}
    ec_dict = {}
    nodes = []
    inverse_dict = {}
    dsize_78, dsize_77, dsize_W, dsize_hu = file_uncompress("test_compare/md_78.lz", "test_compare/md_77.lz",
                                                  "test_compare/md_W.lz", "test_compare/md_hu.lz", output_name)
    print("LZ78 decode size:", dsize_78,'\n',"LZ77 decode size:",dsize_77,'\n',"LZ_W decode size:",dsize_W,'\n',"LZ_HU decode size:",dsize_hu,'\n')
