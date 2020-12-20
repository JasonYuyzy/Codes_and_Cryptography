import os
import sys

File_name = sys.argv[1]
def file_unzip (file):
    unzfile = open("test-decoded.tex", "wb")
    a = "safasdfagas"
    unzfile.write(a)
    unzfile.close()

def main():
    size = file_unzip(File_name)
    print ("Decode size: " + size)

if __name__ == "__main__":
    main()