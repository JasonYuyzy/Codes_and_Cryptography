import os
import sys
import six
from typing import Dict, List
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


def file_uncompress(file, decoder, out_file):
    print("Started decoding:")
    final_outfile = open(out_file, 'wb')

    if decoder == 0:
        final_outfile.write(b'')
        final_outfile.close()

    elif decoder == 77: #LZ77
        decode77 = LZ77_file_decode(file)
        unpress_LZ77 = uncompress_LZ77(decode77)
        final_outfile.write(unpress_LZ77.encode(encoding="ascii"))
        final_outfile.close()

    elif decoder == 79: #LZW
        decodeW_s = LZW_file_decode(file)
        unpress_LZW = uncompress_LZW(decodeW_s)
        final_outfile.write(unpress_LZW)
        final_outfile.close()

    elif decoder == 80: #HUF
        Huf_file = open(file, 'rb')
        Huf_file.read(1)
        Huf_filedata = Huf_file.read()
        Huf_filesize = Huf_file.tell() - 1
        Huf_decode = Huffman_decompress(Huf_filedata, Huf_filesize)
        final_outfile.write(Huf_decode)
        final_outfile.close()

    elif decoder == 81: #HY
        WH_file = open(file, 'rb')
        WH_file.read(1)
        WH_filedata = WH_file.read()
        WH_filesize = WH_file.tell() - 1
        WH_decompress_one = Huffman_decompress(WH_filedata, WH_filesize)
        symbol_lst, s_width = reading_string_WH(WH_decompress_one)
        WH_decompress_two = decode_HY(symbol_lst, s_width)
        WH_decode = uncompress_LZW(WH_decompress_two)
        final_outfile.write(WH_decode)
        final_outfile.close()

    else: #77H
        Hy77_file = open(file, 'rb')
        Hy77_file.read(1)
        Hy77_filedata = Hy77_file.read()
        Hy77_filesize = Hy77_file.tell() - 1
        Hy77_decompress_one = Huffman_decompress(Hy77_filedata, Hy77_filesize)
        word_lst, pointer_lst, length_lst, pointer_width, length_width = read_string_77H(Hy77_decompress_one)
        p_lst = decode_HY(pointer_lst, pointer_width)
        l_lst = decode_HY(length_lst, length_width)
        decode77H = H77_decode(word_lst, p_lst, l_lst)
        unpress_77H = uncompress_LZ77(decode77H)
        final_outfile.write(unpress_77H.encode(encoding="ascii"))
        final_outfile.close()

    #return os.path.getsize(file78.split('.')[0] + out_file), os.path.getsize(file77.split('.')[0] + out_file), os.path.getsize(fileW.split('.')[0] + out_file)


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
    # pop out the first bit
    f.read(1)
    i = 1
    symbol = []
    count = os.path.getsize(file)

    s_bit_width = int.from_bytes(f.read(1), byteorder='big')
    i += 1
    while i < count:
        symbol.append(int.from_bytes(f.read(s_bit_width), byteorder='big'))
        i += s_bit_width

    return symbol

def uncompress_LZW(decodeW_s):
    # reverse dictionary
    ORIGINAL_KDICT = [int2byte(x) for x in range(256)]
    kdict: List[bytes] = ORIGINAL_KDICT.copy()
    i = 0

    #decode the main text
    message = kdict[decodeW_s[i]]
    for i in range(1, len(decodeW_s)):
        if decodeW_s[i] < len(kdict):
            p_char = kdict[decodeW_s[i-1]]
            c_char = (kdict[decodeW_s[i]].decode())[0].encode()
            p_c = p_char + c_char
            kdict.append(p_c)
            message += kdict[decodeW_s[i]]
        else:
            p_char = kdict[decodeW_s[i-1]]
            c_char = (kdict[decodeW_s[i-1]].decode())[0].encode()
            p_c = p_char + c_char
            kdict.append(p_c)
            message += p_c

    return message


def reading_string_WH(WH_decompress_one):
    byte_width = WH_decompress_one[0]
    group_lst = list()
    for i in range(1, len(WH_decompress_one), byte_width):
        group = []
        for x in range(byte_width):
            group.append(WH_decompress_one[i + x])
        group_lst.append(group)
    return group_lst, byte_width

def decode_HY(symbol_lst, s_width):
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
    #pop out the first bit
    f.read(1)
    #get the length of the encoded file
    count = os.path.getsize(file) - 1
    #read the byte width of length and pointer
    l_b_width = int.from_bytes(f.read(1), byteorder='big')
    p_b_width = int.from_bytes(f.read(1), byteorder='big')
    message = []
    #start to decode message code of LZ77
    while i < count:
        ######################write out coder#######################
        word = f.read(1).decode(encoding="ascii")
        #word = f.read(1).decode(encoding="utf-8")
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
        word_lst.append(kdict[Hy77_decompress_one[x]].decode(encoding="ascii"))
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

def main():
    byte_width = 1
    out_name = sys.argv[1]
    out_file = open(out_name, 'rb')
    try:
        decoder = int.from_bytes(out_file.read(byte_width), byteorder='big')
    except:
        decoder = 0
    out_file.close()
    decode_file = out_name.split('.')[0]
    #dsize_78, dsize_77, dsize_W =
    print(decode_file + "-decoded.tex")
    file_uncompress(out_name, decoder, decode_file + "-decoded.tex")
    #print("LZ78 decode size:", dsize_78,'\n',"LZ77 decode size:", dsize_77, '\n', "LZ_W decode size:", dsize_W,'\n', "original size:", os.path.getsize("test.tex"))

if __name__ == "__main__":
    main()