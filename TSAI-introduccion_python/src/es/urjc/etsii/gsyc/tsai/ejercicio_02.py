#!/usr/bin/python
import string

if __name__ == '__main__':
    fich = open("/etc/passwd", 'r')
    lines = fich.readlines()
    fich.close
    
    print ("There are " + str(len(lines)) + " users")
    for line in lines:
        trozos =  string.split(line, ":")
        print trozos[0] + " is using the shell " + trozos[-1]