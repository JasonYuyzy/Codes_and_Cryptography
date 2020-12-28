import os
import sys
import time
import pickle

#File_name = sys.argv[1]
def file_compress(file):
    print("Starting encode...")
    f = open(file, "rb")

    count = os.path.getsize(file)
    print(count)
    prepare = bytes.decode(f.read()) #usding the read byte to make shure the encoding and decoding will be totally the same

    #compressing the LZ77
    if count != len(prepare):
        count = len(prepare)
    final = LZ_77(prepare, count)
    #print(final)
    LZ77 = open("md_77.lz", "wb")
    pointer, length, word = [], [], []
    for message in final:
        pointer.append(message[0])
        length.append(message[1])
        word.append(message[2])

    pointer_h = max(pointer)
    length_h = max(length)
    print("pointer head for LZ77:", pointer_h)
    print("length head for LZ77:", length_h)

    if pointer_h > 255:
        p_bit_width = 2
        if pointer_h > 65535:
            p_bit_width = 3
            if pointer_h > 16777215:
                p_bit_width = 4
    else:
        p_bit_width = 1

    if length_h > 255:
        l_bit_width = 2
        if length_h > 65535:
            l_bit_width = 3
            if length_h > 16777215:
                l_bit_width = 4
    else:
        l_bit_width = 1

    for num in range(len(pointer)):
        LZ77.write(word[num].encode(encoding="utf-8"))
        LZ77.write(int.to_bytes(length[num], l_bit_width, byteorder='big'))
        LZ77.write(int.to_bytes(pointer[num], p_bit_width, byteorder='big'))

    #compressing the LZ78
    pack = LZ_78(prepare)
    LZ78 = open("md_78.lz", "wb")
    pointer, word = [], []
    for d in pack:
        pointer.append(d[0])
        word.append(d[1])
    head = max(pointer)
    print("pointer head for LZ78:", head)  # change the bit width to optimized the size`
    if head > 255:
        bit_width = 2
        if head > 65535:
            bit_width = 3
            if head > 16777215:
                bit_width = 4
    else:
        bit_width = 1

    LZ78.write(int.to_bytes(bit_width, 1, byteorder='big'))
    for num in range(len(pointer)):
        LZ78.write(word[num].encode(encoding="utf-8"))
        LZ78.write(int.to_bytes(pointer[num], bit_width, byteorder='big'))


    LZ78.close()
    LZ77.close()
    print("LZ77 compressed size:", os.path.getsize("md_77.lz"))
    print("LZ78 compressed size:", os.path.getsize("md_78.lz"))
    f.close()
    return os.path.getsize(file)

def file_uncompress(file):
    print("Started decoding:")

    #LZ78
    unpick = LZ78_unpick(file)
    unpress_LZ78 = uncompress_LZ78(unpick)
    final_LZ78 = open("decode_78.tex", 'w')
    final_LZ78.write(unpress_LZ78)
    final_LZ78.close()
    return os.path.getsize("decode_78.tex")


def LZ_77(line, count):
    length = 0
    win = count
    pointer = 0
    message = line
    print("message length:", len(message))

    compressed_message = list()  #message temporal storage
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
    while i < m_len:
        # case I
        if line[i] not in tree_dict.keys():
            yield (0, line[i])
            tree_dict[line[i]] = len(tree_dict) + 1
            i += 1
        # case III
        elif i == m_len - 1:
            yield (tree_dict.get(line[i]), '')
            i += 1
        else:
            for j in range(i + 1, m_len):
                # case II
                if line[i:j + 1] not in tree_dict.keys():
                    yield (tree_dict.get(line[i:j]), line[j])
                    tree_dict[line[i:j + 1]] = len(tree_dict) + 1
                    i = j + 1
                    break
                # case III
                elif j == m_len - 1:
                    yield (tree_dict.get(line[i:j + 1]), '')
                    i = j + 1

def LZ78_unpick(file):
    f = open(file, "rb")
    i = 0
    b_width = int.from_bytes(f.read(1), byteorder='big')
    i += 1
    count = os.path.getsize(file)
    while i < count:
        word = f.read(1).decode(encoding="utf-8")
        pointer = int.from_bytes(f.read(b_width), byteorder='big')
        yield (pointer, word)
        i = i + b_width + 1


def uncompress_LZ78(packed):
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
    size = file_compress("test.tex")
    print ("encode size: ", size)
    size_78 = file_uncompress("md_78.lz")
    print("LZ78 decode size:", size_78, '\n', "original size:", os.path.getsize("test.tex"))

if __name__ == "__main__":
    main()

