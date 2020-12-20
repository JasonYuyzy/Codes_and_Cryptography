import os
import sys

File_name = sys.argv[1]
def file_compress_LZ77(file):
    waiting = open(file, r)
    zfile = open("test.lz", "wb")
    a = "safasdfagas"
    zfile.write(a)
    zfile.close()

def main():
    size = file_compress_LZ77(File_name)
    print ("encode size: " + size)

if __name__ == "__main__":
    main()