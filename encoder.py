import os
import sys
import time

File_name = sys.argv[1]
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
    print(prepare)
    LZ_77(prepare, count)

    f.close()
    return os.path.getsize(file)

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
            a = (pointer - first, length, message[pointer + length])
            compressed_message.append(a)
            pointer += length + 1
        else:
            b = (0, 0, message[pointer])
            compressed_message.append(b)
            pointer += 1

        length = 0
        #if pointer > 1179:
            #print(match.find(message[pointer:pointer + length + 1]) != -1)
        if pointer == len(message):
            break
    print(compressed_message)
    print(len(compressed_message))

def main():
    size = file_compress_LZ77(File_name)
    print ("encode size: ", size)

if __name__ == "__main__":
    main()

