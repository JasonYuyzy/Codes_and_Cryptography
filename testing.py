#for the huffman part cite from https://www.omegaxyz.com/2018/05/12/huffman_python/
import os
import sys
import time
import math
from typing import Dict, List
import six
from six import int2byte


class HuffNode(object):
    def get_wieght(self):
        raise NotImplementedError(
            "The Abstract Node Class doesn't define 'get_wieght'")
    def isleaf(self):
        raise NotImplementedError(
            "The Abstract Node Class doesn't define 'isleaf'")

class LeafNode(HuffNode):
    def __init__(self, value=0, freq=0, ):
        super(LeafNode, self).__init__()
        self.value = value
        self.wieght = freq
    def isleaf(self):
        return True
    def get_wieght(self):
        return self.wieght
    def get_value(self):
        return self.value

class IntlNode(HuffNode):
    def __init__(self, left_child=None, right_child=None):
        super(IntlNode, self).__init__()
        self.wieght = left_child.get_wieght() + right_child.get_wieght()
        self.left_child = left_child
        self.right_child = right_child
    def isleaf(self):
        return False
    def get_wieght(self):
        return self.wieght
    def get_left(self):
        return self.left_child
    def get_right(self):
        return self.right_child

class HuffTree(object):
    def __init__(self, flag, value=0, freq=0, left_tree=None, right_tree=None):
        super(HuffTree, self).__init__()
        if flag == 0:
            self.root = LeafNode(value, freq)
        else:
            self.root = IntlNode(left_tree.get_root(), right_tree.get_root())
    def get_root(self):
        return self.root
    def get_wieght(self):
        return self.root.get_wieght()
    def traverse_huffman_tree(self, root, code, char_freq):
        if root.isleaf():
            char_freq[root.get_value()] = code
            return None
        else:
            self.traverse_huffman_tree(root.get_left(), code + '0', char_freq)
            self.traverse_huffman_tree(root.get_right(), code + '1', char_freq)


def buildHuffmanTree(list_hufftrees):
    while len(list_hufftrees) > 1:
        list_hufftrees.sort(key=lambda x: x.get_wieght())
        temp1 = list_hufftrees[0]
        temp2 = list_hufftrees[1]
        list_hufftrees = list_hufftrees[2:]
        newed_hufftree = HuffTree(1, 0, 0, temp1, temp2)
        list_hufftrees.append(newed_hufftree)
    return list_hufftrees[0]



#File_name = sys.argv[1]
def file_compress(file):
    ORIGINAL_KDICT = [int2byte(x) for x in range(256)]
    kdict: List[bytes] = ORIGINAL_KDICT.copy()
    #print("Starting encode...")
    f = open(file, "rb")
    count = os.path.getsize(file)
    print("Compress file size:", count)
    Huf_data = f.read()
    Huf_size = f.tell()
    prepare = bytes.decode(Huf_data)


#compressing with Huffman
    Huf_com = huffman_compress(Huf_data, Huf_size)
    HUF = open("test_compare/md_hu.lz", 'wb')
    HUF.write(Huf_com)
    HUF.close()

#compressing with LZW
    LZW = open("test_compare/md_W.lz", 'wb')
    have_dict = 0
    dict_num = list()
    key = list()
    final_LZW, d_dict = LZ_W(file, count)
    LZW_COM = b''
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
        #LZW.write(int.to_bytes(have_dict, 1, byteorder='big'))
        LZW_COM += int.to_bytes(have_dict, 1, byteorder='big')
    # changing the symbol bit width to optimized the size
    head_W = max(final_LZW)
    if head_W > 255:
        s_bit_width = 2
        if head_W > 65535:
            s_bit_width = 3
            if head_W > 16777215:
                s_bit_width = 4
    else:
        s_bit_width = 1

    #record the symbol bit width
    #LZW.write(int.to_bytes(s_bit_width, 1, byteorder='big'))
    LZW_COM += int.to_bytes(s_bit_width, 1, byteorder='big')
    #record the symbol into byte
    for final_num in final_LZW:
        #LZW.write(int.to_bytes(final_num, s_bit_width, byteorder='big'))
        LZW_COM += int.to_bytes(final_num, s_bit_width, byteorder='big')

    LZW.write(LZW_COM)
    LZW.close()


#compressing with the hybird Huffman-LZW
    if head_W > 255:
        s_bit_width = 2
        if head_W > 255**2:
            s_bit_width = 3
            if head_W > 255**3:
                s_bit_width = 4
    else:
        s_bit_width = 1

    waiting = encode_Hy(final_LZW, s_bit_width)
    second_b = b''
    second_b += kdict[s_bit_width]
    for w in waiting:
        for i in range(s_bit_width):
            second_b += kdict[w[i]]
    HY = huffman_compress(second_b, len(second_b))
    Hybrid_H_LZW = open("test_compare/md_Hy.lz", "wb")
    Hybrid_H_LZW.write(HY)
    Hybrid_H_LZW.close()



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

    # Hybrid LZ77-Huffman
    if pointer_h > 255:
        p_bit_width = 2
        if pointer_h > 255**2:
            p_bit_width = 3
            if pointer_h > 255**3:
                p_bit_width = 4
    else:
        p_bit_width = 1

    if length_h > 255:
        l_bit_width = 2
        if length_h > 255**2:
            l_bit_width = 3
            if length_h > 255**3:
                l_bit_width = 4
    else:
        l_bit_width = 1

    waiting_pointer = encode_Hy(pointer, p_bit_width)
    waiting_length = encode_Hy(length, l_bit_width)
    second_77b = b''
    second_77b += kdict[p_bit_width]
    second_77b += kdict[l_bit_width]
    for w in range(len(waiting_pointer)):
        second_77b += word[w].encode(encoding="utf-8")
        for i in range(p_bit_width):
            second_77b += kdict[waiting_pointer[w][i]]
        for j in range(l_bit_width):
            second_77b += kdict[waiting_length[w][j]]
    H77 = huffman_compress(second_77b, len(second_77b))
    Hybrid_77H = open("test_compare/md_77H.lz", "wb")
    Hybrid_77H.write(H77)
    Hybrid_77H.close()

    f.close()
    #print("SSSSS:", os.path.getsize("compare_file/md_77.lz"), os.path.getsize("compare_file/md_78.lz"), os.path.getsize("compare_file/md_W.lz"))
    return os.path.getsize("test_compare/md_77H.lz"), os.path.getsize("test_compare/md_77.lz"), os.path.getsize("test_compare/md_W.lz"), os.path.getsize("test_compare/md_hu.lz"),  os.path.getsize("test_compare/md_Hy.lz")

def huffman_compress(filedata, filesize):
    char_freq = {}
    for x in range(filesize):
        tem = filedata[x]
        if tem in char_freq.keys():
            char_freq[tem] = char_freq[tem] + 1
        else:
            char_freq[tem] = 1
    list_hufftrees = []
    for x in char_freq.keys():
        tem = HuffTree(0, x, char_freq[x], None, None)
        list_hufftrees.append(tem)
    length = len(char_freq.keys())
    output = b''

    a4 = length & 255
    length = length >> 8
    a3 = length & 255
    length = length >> 8
    a2 = length & 255
    length = length >> 8
    a1 = length & 255
    output += six.int2byte(a1)
    output += six.int2byte(a2)
    output += six.int2byte(a3)
    output += six.int2byte(a4)

    for x in char_freq.keys():
        output += six.int2byte(x)
        #output += x.encode()
        temp = char_freq[x]
        a4 = temp & 255
        temp = temp >> 8
        a3 = temp & 255
        temp = temp >> 8
        a2 = temp & 255
        temp = temp >> 8
        a1 = temp & 255
        output += six.int2byte(a1)
        output += six.int2byte(a2)
        output += six.int2byte(a3)
        output += six.int2byte(a4)

    tem = buildHuffmanTree(list_hufftrees)
    tem.traverse_huffman_tree(tem.get_root(), '', char_freq)

    code = ''
    for i in range(filesize):
        key = filedata[i]
        code = code + char_freq[key]
        out = 0
        while len(code) > 8:
            for x in range(8):
                out = out << 1
                if code[x] == '1':
                    out = out | 1
            code = code[8:]
            output += six.int2byte(out)
            out = 0

    output += six.int2byte(len(code))
    out = 0
    for i in range(len(code)):
        out = out << 1
        if code[i] == '1':
            out = out | 1
    for i in range(8 - len(code)):
        out = out << 1
    output += six.int2byte(out)

    return output

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

def encode_Hy(final_LST, bitwidth):
    final_hy = []
    for final_num in final_LST:
        ret_lst = []
        for i in range(bitwidth):
            check = int(final_num/(255**i))%255
            ret_lst.append(check)
        final_hy.append(ret_lst)
    return final_hy


def LZ_77(line, count):
    length = 0
    win = count
    pointer = 0
    message = line
    compressed_message = list()  #message temporal storage
    #encoding the main text
    while True:

        if pointer - win < 0:
            match = message[0:pointer]
        else:
            match = message[pointer - win:pointer]
        while match.find(message[pointer:pointer + length + 1]) != -1:
            if pointer + length == count - 1:
                break
            length += 1


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
        if pointer == len(message):
            break
    return compressed_message


def file_uncompress(file77, fileW, fileHu, fileHy, file77H, out_file):
    print("Started decoding:")
    #Huffman
    Huf_file = open(fileHu, 'rb')
    Huf_filedata = Huf_file.read()
    Huf_filesize = Huf_file.tell()
    Huf_decode = Huffman_decompress(Huf_filedata, Huf_filesize)
    final_HUF = open(fileHu.split('.')[0] + out_file, 'wb')
    final_HUF.write(Huf_decode)
    final_HUF.close()

    #LZW
    decodeW_d, decodeW_s = LZW_file_decode(fileW)
    unpress_LZW = uncompress_LZW(decodeW_d, decodeW_s)
    final_LZW = open(fileW.split('.')[0] + out_file, 'wb')
    final_LZW.write(unpress_LZW)
    final_LZW.close()

    #Hy
    Hy_file = open(fileHy, 'rb')
    Hy_filedata = Hy_file.read()
    Hy_filesize = Hy_file.tell()
    Hy_decompress_one = Huffman_decompress(Hy_filedata, Hy_filesize)
    symbol_lst, s_width= uncompress_hy(Hy_decompress_one)
    Hy_decompress_two = decode_LZW(symbol_lst, s_width)
    Hy_decode = uncompress_LZW({}, Hy_decompress_two)
    final_HUF = open(fileHy.split('.')[0] + out_file, 'wb')
    final_HUF.write(Hy_decode)
    final_HUF.close()

    #LZ77
    decode77 = LZ77_file_decode(file77)
    unpress_LZ77 = uncompress_LZ77(decode77)
    final_LZ77 = open(file77.split('.')[0] + out_file, 'wb')
    final_LZ77.write(unpress_LZ77.encode(encoding="utf-8"))
    final_LZ77.close()

    #Hybrid LZ77-Huffman
    Hy77_file = open(file77H, 'rb')
    Hy77_filedata = Hy77_file.read()
    Hy77_filesize = Hy77_file.tell()
    Hy77_decompress_one = Huffman_decompress(Hy77_filedata, Hy77_filesize)
    word_lst, pointer_lst, length_lst, pointer_width, length_width = read_string_77H(Hy77_decompress_one)
    p_lst = decode_LZW(pointer_lst, pointer_width)
    l_lst = decode_LZW(length_lst, length_width)
    decode77H = H77_decode(word_lst, p_lst, l_lst)
    unpress_77H = uncompress_LZ77(decode77H)
    final_77H = open(file77H.split('.')[0] + out_file, 'wb')
    final_77H.write(unpress_77H.encode(encoding="utf-8"))
    final_77H.close()


    return os.path.getsize(file77H.split('.')[0] + out_file), os.path.getsize(file77.split('.')[0] + out_file), os.path.getsize(fileW.split('.')[0] + out_file), os.path.getsize(fileHu.split('.')[0] + out_file), os.path.getsize(fileHy.split('.')[0] + out_file)


def Huffman_decompress(filedata, filesize):
    a1 = filedata[0]
    a2 = filedata[1]
    a3 = filedata[2]
    a4 = filedata[3]
    j = 0
    j = j | a1
    j = j << 8
    j = j | a2
    j = j << 8
    j = j | a3
    j = j << 8
    j = j | a4

    leaf_node_size = j
    char_freq = {}
    for i in range(leaf_node_size):
        c = filedata[4 + i * 5 + 0]
        a1 = filedata[4 + i * 5 + 1]
        a2 = filedata[4 + i * 5 + 2]
        a3 = filedata[4 + i * 5 + 3]
        a4 = filedata[4 + i * 5 + 4]
        j = 0
        j = j | a1
        j = j << 8
        j = j | a2
        j = j << 8
        j = j | a3
        j = j << 8
        j = j | a4
        char_freq[c] = j

    list_hufftrees = []
    for x in char_freq.keys():
        tem = HuffTree(0, x, char_freq[x], None, None)
        list_hufftrees.append(tem)
    tem = buildHuffmanTree(list_hufftrees)
    tem.traverse_huffman_tree(tem.get_root(), '', char_freq)
    output = b''
    code = ''
    currnode = tem.get_root()
    for x in range(leaf_node_size * 5 + 4, filesize):
        c = filedata[x]
        for i in range(8):
            if c & 128:
                code = code + '1'
            else:
                code = code + '0'
            c = c << 1
        while len(code) > 24:
            if currnode.isleaf():
                tem_byte = six.int2byte(currnode.get_value())
                output += tem_byte
                currnode = tem.get_root()

            if code[0] == '1':
                currnode = currnode.get_right()
            else:
                currnode = currnode.get_left()
            code = code[1:]

    sub_code = code[-16:-8]
    last_length = 0
    for i in range(8):
        last_length = last_length << 1
        if sub_code[i] == '1':
            last_length = last_length | 1
    code = code[:-16] + code[-8:-8 + last_length]

    while len(code) > 0:
        if currnode.isleaf():
            tem_byte = six.int2byte(currnode.get_value())
            output += tem_byte
            currnode = tem.get_root()
        if code[0] == '1':
            currnode = currnode.get_right()
        else:
            currnode = currnode.get_left()
        code = code[1:]
    if currnode.isleaf():
        tem_byte = six.int2byte(currnode.get_value())
        output += tem_byte
        currnode = tem.get_root()

    return output


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


def uncompress_hy(Hy_decompress):
    s_bit_width = Hy_decompress[0]
    symbol_lst = list()
    for i in range(1, len(Hy_decompress), s_bit_width):
        group = []
        for x in range(s_bit_width):
            group.append(Hy_decompress[i+x])
        symbol_lst.append(group)
    return symbol_lst, s_bit_width

def decode_LZW(symbol_lst, s_width):
    lst = list()
    for symbol_group in symbol_lst:
        symbol = 0
        for i in range(s_width):
            symbol += symbol_group[i]*(255**i)
        lst.append(symbol)
    return lst


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
    while i < count-2:
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

def read_string_77H(Hy77_decompress_one):
    ORIGINAL_KDICT = [int2byte(x) for x in range(256)]
    kdict: List[bytes] = ORIGINAL_KDICT.copy()
    word_lst = list()
    pointer_lst = list()
    length_lst = list()

    pointer_width = Hy77_decompress_one[0]
    length_width = Hy77_decompress_one[1]

    for x in range(2, len(Hy77_decompress_one), 1+pointer_width+length_width):
        word_lst.append(kdict[Hy77_decompress_one[x]].decode(encoding="utf-8"))
        pointer_group = []
        length_group = []
        for i in range(pointer_width):
            pointer_group.append(Hy77_decompress_one[1+x+i])
        for j in range(length_width):
            length_group.append(Hy77_decompress_one[1+x+pointer_width+j])
        pointer_lst.append(pointer_group)
        length_lst.append(length_group)
    return word_lst, pointer_lst, length_lst, pointer_width, length_width

def H77_decode(word_lst, p_lst, l_lst):
    message77H = list()
    for i in range(len(word_lst)):
        message77H.append((p_lst[i], l_lst[i], word_lst[i]))

    return message77H

if __name__ == "__main__":
    node_dict = {}
    count_dict = {}
    ec_dict = {}
    nodes = []
    inverse_dict = {}
    file_name = sys.argv[1]
    input_file = file_name.split('.')
    output_name = '.' + input_file[1]
    esize_WH, esize_77, esize_W, esize_Hu, esize_Hy = file_compress(file_name)
    print("Hybrid 77H encode size:", esize_WH, '\n', "LZ77 encode size:", esize_77, '\n', "LZ_W encode size:", esize_W, '\n', "Huffman encode size:", esize_Hu,  '\n', "Hybrid WH encode size:", esize_Hy)

    dsize_77H, dsize_77, dsize_W, dsize_H, dsize_Hy = file_uncompress("test_compare/md_77.lz",
                                                  "test_compare/md_W.lz", "test_compare/md_hu.lz", "test_compare/md_Hy.lz", "test_compare/md_77H.lz",output_name)
    print("Hybrid 77H decode size:",dsize_77H,'\n',"LZ77 decode size:",dsize_77,'\n',"LZ_W decode size:",dsize_W,'\n',"LZ_H decode size:",dsize_H,'\n',"LZ_Hy decode size:",dsize_Hy,'\n')
