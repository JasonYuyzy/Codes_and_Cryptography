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
    if count == 0:
        Nothing = b''
        return Nothing, 0
# compressing with Huffman
    try:
        Huf_com = huffman_compress(Huf_data, Huf_size)
    except:
        Huf_com = b''
#compressing with LZW
    try:
        final_LZW = LZ_W(file, count)
        LZW_com = b''
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
        LZW_com += int.to_bytes(s_bit_width, 1, byteorder='big')
        #record the symbol into byte
        for final_num in final_LZW:
            LZW_com += int.to_bytes(final_num, s_bit_width, byteorder='big')


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
        second_WH = b''
        second_WH += kdict[s_bit_width]
        for w in waiting:
            for i in range(s_bit_width):
                second_WH += kdict[w[i]]
        WH = huffman_compress(second_WH, len(second_WH))
    except:
        LZW_com = b''
        WH = b''



#compressing with the LZ77
    try:
        if count != len(prepare):
            count = len(prepare)
        final = LZ_77(prepare, count)
        pointer, length, word = [], [], []
        LZ77_com = b''
        for message in final:
            pointer.append(message[0])
            length.append(message[1])
            word.append(message[2])

        pointer_h = max(pointer)
        length_h = max(length)
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

        LZ77_com += int.to_bytes(l_bit_width, 1, byteorder='big')
        LZ77_com += int.to_bytes(p_bit_width, 1, byteorder='big')

        for num in range(len(pointer)):
            ######################write in coder#######################
            LZ77_com += word[num].encode(encoding="ascii")
            LZ77_com += int.to_bytes(length[num], l_bit_width, byteorder='big')
            LZ77_com += int.to_bytes(pointer[num], p_bit_width, byteorder='big')
    except:
        LZ77_com = b''
#compressing with the LZ77-Huffman
    try:
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
        second_77H = b''
        second_77H += kdict[p_bit_width]
        second_77H += kdict[l_bit_width]
        for w in range(len(waiting_pointer)):
            second_77H += word[w].encode(encoding="utf-8")
            for i in range(p_bit_width):
                second_77H += kdict[waiting_pointer[w][i]]
            for j in range(l_bit_width):
                second_77H += kdict[waiting_length[w][j]]
        H77 = huffman_compress(second_77H, len(second_77H))
    except:
        H77 = b''

    f.close()

    Huf_len, LZW_len, LZ77_len, WH_len, H77_len = len(Huf_com), len(LZW_com), len(LZ77_com), len(WH), len(H77)
    len_lst = min([Huf_len, LZW_len, LZ77_len, WH_len, H77_len])
    if len_lst == LZ77_len:
        return LZ77_com, 77
    elif len_lst == LZW_len:
        return LZW_com, 79
    elif len_lst == Huf_len:
        return Huf_com, 80
    elif len_lst == WH_len:
        return WH, 81
    else:
        return H77, 82


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
    f = open(file, "rb")
    p_char = b''
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
    return message

def encode_Hy(number_sequence, bytewidth):
    final_sequence_group = []
    for num in number_sequence:
        group = []
        for i in range(bytewidth):
            check = int(num/(255**i))%255
            group.append(check)
        final_sequence_group.append(group)
    return final_sequence_group

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
    return compressed_message


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
    if num == 0:
        smallest_file.write(b'')
    else:
        smallest_file.write(int.to_bytes(num, byte_width, byteorder='big'))
    smallest_file.write(final_com)
    smallest_file.close()


if __name__ == "__main__":
    main()

