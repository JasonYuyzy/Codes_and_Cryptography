import os
import sys
import time
import pickle

#File_name = sys.argv[1]
def file_compress_LZ77(file):
    print("Starting encode...")
    f = open(file, "r")

    bytes_width = 1  # 每次读取的字节宽度
    i = 0
    count = os.path.getsize(file)
    buff = [b''] * int(count)
    prepare = ''
    for line in f:
        prepare += line
        #print(line)
    #print(prepare)
    final = LZ_77(prepare, count)
    pack = LZ_78(prepare)
    j = open("md_78.lz", "wb")
    p, w = [], []
    for d in pack:
        p.append(d[0])
        w.append(d[1])
    head = max(p)
    print("head:", head)  # change the bit width to optimized the size`
    if head > 255:
        bit_width = 2
        if head > 65535:
            bit_width = 3
            if head > 16777215:
                bit_width = 4
    for num in range(len(p)):
        j.write(w[num].encode(encoding="utf-8"))
        j.write(int.to_bytes(p[num], bit_width, byteorder='big'))

    #print(last)
    #pickle.dump(w,j)
    j.close()
    f.close()
    return os.path.getsize(file)

def LZ_77(line, count):
    length = 0
    win = count
    pointer = 0
    message = line
    print("message length:", len(message))

    o = open("compressd.lz", "w")

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
            o.write(str(a))
            pointer += length + 1
        else:
            b = (0,0,message[pointer])
            compressed_message.append(b)
            o.write(str(b))
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

def main():
    size = file_compress_LZ77("test.tex")
    print ("encode size: ", size)

if __name__ == "__main__":
    main()

