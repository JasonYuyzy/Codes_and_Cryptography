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


def file_compress(file):
    #print("Starting encode...")
    f = open(file, "rb")
    count = os.path.getsize(file)
    print("Compress file size:", count)
    Huf_data = f.read()
    Huf_size = f.tell()
    prepare = bytes.decode(Huf_data)

# compressing with Huffman
    Huf_com = huffman_compress(Huf_data, Huf_size)
    HUF = open("test_compare/md_hu.lz", 'wb')
    HUF.write(Huf_com)
    HUF.close()

#compressing with LZW
    LZW = open("compare_file/md_W.lz", 'wb')
    have_dict = 0
    dict_num = list()
    key = list()
    final_LZW, d_dict = LZ_W(file, count)
    LZW_com = b''
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
            ######################write in coder#######################
            LZW.write(key[num].encode(encoding="ascii"))
            #LZW.write(key[num].encode(encoding="utf-8"))
            LZW.write(int.to_bytes(dict_num[num], DN_bit_width, byteorder='big'))
    else:
        # record whether have the extra dictionary (have)
        #LZW.write(int.to_bytes(have_dict, 1, byteorder='big'))
        LZW_com += int.to_bytes(have_dict, 1, byteorder='big')

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
    #LZW.write(int.to_bytes(s_bit_width, 1, byteorder='big'))
    LZW_com += int.to_bytes(s_bit_width, 1, byteorder='big')
    #record the symbol into byte
    for final_num in final_LZW:
        #LZW.write(int.to_bytes(final_num, s_bit_width, byteorder='big'))
        LZW_com += int.to_bytes(final_num, s_bit_width, byteorder='big')

    LZW.write(LZW_com)
    LZW.close()

# compressing with the hybrid Huffman-LZW
    if head_W > 255:
        s_bit_width = 2
        if head_W > 255 ** 2:
            s_bit_width = 3
            if head_W > 255 ** 3:
                s_bit_width = 4
    else:
        s_bit_width = 1
    ORIGINAL_KDICT = [int2byte(x) for x in range(256)]
    kdict: List[bytes] = ORIGINAL_KDICT.copy()
    waiting = encode_Hy(final_LZW, s_bit_width)
    second_b = b''
    second_b += kdict[s_bit_width]
    for w in waiting:
        for i in range(s_bit_width):
            second_b += kdict[w[i]]
    HY = huffman_compress(second_b, len(second_b))



#compressing with the LZ77
    if count != len(prepare):
        count = len(prepare)
    final = LZ_77(prepare, count)
    LZ77 = open("compare_file/md_77.lz", "wb")
    pointer, length, word = [], [], []
    LZ77_com = b''
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

    #LZ77.write(int.to_bytes(l_bit_width, 1, byteorder='big'))
    #LZ77.write(int.to_bytes(p_bit_width, 1, byteorder='big'))
    LZ77_com += int.to_bytes(l_bit_width, 1, byteorder='big')
    LZ77_com += int.to_bytes(p_bit_width, 1, byteorder='big')

    for num in range(len(pointer)):
        ######################write in coder#######################
        #LZ77.write(word[num].encode(encoding="ascii"))
        LZ77_com += word[num].encode(encoding="ascii")
        #LZ77.write(word[num].encode(encoding="utf-8"))
        #LZ77.write(int.to_bytes(length[num], l_bit_width, byteorder='big'))
        #LZ77.write(int.to_bytes(pointer[num], p_bit_width, byteorder='big'))
        LZ77_com += int.to_bytes(length[num], l_bit_width, byteorder='big')
        LZ77_com += int.to_bytes(pointer[num], p_bit_width, byteorder='big')

    LZ77.write(LZ77_com)
    LZ77.close()

#compressing with the LZ78
    pack = LZ_78(prepare)
    LZ78 = open("compare_file/md_78.lz", "wb")
    pointer, word = [], []
    LZ78_com = b''
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

    #LZ78.write(int.to_bytes(bit_width_78, 1, byteorder='big'))
    LZ78_com += int.to_bytes(bit_width_78, 1, byteorder='big')
    for num in range(len(pointer)):
        if word[num] == '':
            #LZ78.write(b'')
            LZ78_com += b''
            #print(pointer[num], word[num].encode())
        else:
            ######################write in coder#######################
            #LZ78.write(word[num].encode(encoding="ascii"))
            LZ78_com += word[num].encode(encoding="ascii")
            #LZ78.write(word[num].encode(encoding="utf-8"))
        #LZ78.write(int.to_bytes(pointer[num], bit_width_78, byteorder='big'))
        LZ78_com += int.to_bytes(pointer[num], bit_width_78, byteorder='big')
        ##############test the difference of the encoding
        #print(int.to_bytes(pointer[num], bit_width_78, byteorder='big'))
        #print(pointer[num].to_bytes(length=bit_width_78, byteorder='big'))
    #exit()

    LZ78.write(LZ78_com)
    LZ78.close()

    f.close()

    Huf_len, LZW_len, LZ78_len, LZ77_len, HY_len = len(Huf_com), len(LZW_com), len(LZ78_com), len(LZ77_com), len(HY)
    len_lst = min([Huf_len, LZW_len, LZ78_len, LZ77_len, HY_len])
    #print([Huf_len, LZW_len, LZ78_len, LZ77_len, HY_len])
    if len_lst == LZ77_len:
        return LZ77_com, 77
    elif len_lst == LZ78_len:
        return LZ78_com, 78
    elif len_lst == LZW_len:
        return LZW_com, 79
    elif len_lst == Huf_len:
        return Huf_com, 80
    else:
        return HY, 81
    #print("SSSSS:", os.path.getsize("compare_file/md_77.lz"), os.path.getsize("compare_file/md_78.lz"), os.path.getsize("compare_file/md_W.lz"))
    #return os.path.getsize("compare_file/md_77.lz"), os.path.getsize("compare_file/md_78.lz"), os.path.getsize("compare_file/md_W.lz"), os.path.getsize("compare_file/md_hu.lz")

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
    odict: Dict[bytes, int] = ORIGINAL_CDICT.copy()
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
    print("message length:", len(message))
    # message temporal storage
    compressed_message = list()
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
    #write in byte width
    byte_width = 1
    #take the file name
    file_name = sys.argv[1]
    input_file = file_name.split('.')
    output_name = input_file[0]
    smallest_file = open(output_name + '.lz', 'wb')
    # compressing and get the final compress file
    final_com, num = file_compress(file_name)
    smallest_file.write(int.to_bytes(num, byte_width, byteorder='big'))
    smallest_file.write(final_com)
    smallest_file.close()


    #print ("LZ78 encode size:", esize_78,'\n',"LZ77 encode size:", esize_77,'\n',"LZ_W encode size:", esize_W,'\n')
    #dsize_78, dsize_77, dsize_W = file_uncompress("md_78.lz", "md_77.lz", "md_W.lz", output_name)
    #print("LZ78 decode size:",dsize_78,'\n',"LZ77 decode size:",dsize_77, '\n',"LZ_W decode size:", dsize_W)

if __name__ == "__main__":
    main()

