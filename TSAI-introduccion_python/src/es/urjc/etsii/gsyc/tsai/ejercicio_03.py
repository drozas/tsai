#!/usr/bin/python
import string


fich = open("/etc/passwd", 'r')
lines = fich.readlines()
fich.close

print ("There are " + str(len(lines)) + " users")
dictionary = {}
for line in lines:
    trozos =  string.split(line, ":")
    print trozos[0] + " is using the shell " + trozos[-1]
    print "storing it in dictionary"
    dictionary[trozos[0]] = trozos[-1]
    
print "Value for root in dictionary: " + dictionary["root"]
try:
    print "Value for imaginario in dictionary: " + dictionary["imaginario"] 
except KeyError:
    print "there is no value!"  