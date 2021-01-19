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


    if decoder == 77: #LZ77
        decode77 = LZ77_file_decode(file)
        unpress_LZ77 = uncompress_LZ77(decode77)
        final_outfile.write(unpress_LZ77.encode(encoding="utf-8"))
        final_outfile.close()

    elif decoder == 78: #LZ78
        decode78 = LZ78_file_decode(file)
        unpress_LZ78 = uncompress_LZ78(decode78)
        final_outfile.write(unpress_LZ78.encode(encoding="utf-8"))
        final_outfile.close()

    elif decoder == 79: #LZW
        decodeW_d, decodeW_s = LZW_file_decode(file)
        unpress_LZW = uncompress_LZW(decodeW_d, decodeW_s)
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

    else: #HY
        Hy_file = open(file, 'rb')
        Hy_file.read(1)
        Hy_filedata = Hy_file.read()
        Hy_filesize = Hy_file.tell() - 1
        Hy_decompress_one = Huffman_decompress(Hy_filedata, Hy_filesize)
        symbol_lst, s_width = uncompress_hy(Hy_decompress_one)
        Hy_decompress_two = decode_HY(symbol_lst, s_width)
        Huf_decode = uncompress_LZW({}, Hy_decompress_two)
        final_outfile.write(Huf_decode)
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
            ######################write out coder#######################
            extra_dict.update(({f.read(1).decode(encoding="ascii"): int.from_bytes(f.read(DN_bit_width), byteorder='big')}))
            #extra_dict.update(({f.read(1).decode(encoding="utf-8"): int.from_bytes(f.read(DN_bit_width), byteorder='big')}))
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
    ORIGINAL_CDICT = dict(zip((int2byte(x) for x in range(256)), range(256)))
    odict: Dict[bytes, int] = ORIGINAL_CDICT.copy()
    s_bit_width = Hy_decompress[0]
    symbol_lst = list()
    for i in range(1, len(Hy_decompress), s_bit_width):
        symbol_lst.append([Hy_decompress[i], Hy_decompress[i+1]])
    return symbol_lst, s_bit_width

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


def LZ78_file_decode(file):
    f = open(file, "rb")
    i = 0
    # pop out the first bit
    f.read(1)
    #get the length of the encoded file
    count = os.path.getsize(file) - 1
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
                ######################write out coder#######################
                last_w = f.read(1).decode(encoding="ascii")
                #last_w = f.read(1).decode(encoding="utf-8")
                last_p = int.from_bytes(f.read(b_width), byteorder='big')
                yield (last_p, last_w)
                #print("W:", last_w)
                i = i + b_width + 1
            else:
                i = i + b_width
                last_p = int.from_bytes(f.read(b_width), byteorder='big')
                yield (last_p, '')
            #print("P:", last_p)
        else:
            ######################write out coder#######################
            word = f.read(1).decode(encoding="ascii")
            #word = f.read(1).decode(encoding="utf-8")
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

def main():
    byte_width = 1
    out_name = sys.argv[1]
    out_file = open(out_name, 'rb')
    decoder = int.from_bytes(out_file.read(byte_width), byteorder='big')
    out_file.close()
    decode_file = out_name.split('.')[0]
    #dsize_78, dsize_77, dsize_W =
    print(decode_file + "-decoded.tex")
    file_uncompress(out_name, decoder, decode_file + "-decoded.tex")
    #print("LZ78 decode size:", dsize_78,'\n',"LZ77 decode size:", dsize_77, '\n', "LZ_W decode size:", dsize_W,'\n', "original size:", os.path.getsize("test.tex"))

if __name__ == "__main__":
    main()