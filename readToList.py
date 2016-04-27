from scanner import *
import sys

def main(argv):
    inputFile = argv[1]
    readToList(inputFile,"output.txt");

def readToList(inputFile,outputFile):
    inn = open(inputFile,"r")
    out = open(outputFile,"w")
    line = inn.readline()
    out.write("[")
    while (line != ""):
        out.write('"' + line + '",')
        line = inn.readline()
    inn.close()
    out.close()

if __name__ == "__main__":
    main(sys.argv)
                    
