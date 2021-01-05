import os
import sys
from typing import Dict, List
from six import int2byte


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
    else:
        decodeW_d, decodeW_s = LZW_file_decode(file)
        unpress_LZW = uncompress_LZW(decodeW_d, decodeW_s)
        final_outfile.write(unpress_LZW)
        final_outfile.close()

    #return os.path.getsize(file78.split('.')[0] + out_file), os.path.getsize(file77.split('.')[0] + out_file), os.path.getsize(fileW.split('.')[0] + out_file)

def LZW_file_decode(file):
    f = open(file, 'rb')
    # pop out the first bit
    f.read(1)
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
            i += s_bit_width
            symbol.append(int.from_bytes(f.read(s_bit_width), byteorder='big'))
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
    #pop out the first bit
    f.read(1)
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
    # pop out the first bit
    f.read(1)
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
                #print("W:", last_w)
                i = i + b_width + 1
            else:
                i = i + b_width
                last_p = int.from_bytes(f.read(b_width), byteorder='big')
                yield (last_p, '')
            #print("P:", last_p)
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