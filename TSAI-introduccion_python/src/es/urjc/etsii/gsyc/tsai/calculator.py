#!/usr/bin/python
import sys

if len(sys.argv[1:])==3:

    #checking arguments
    func = sys.argv[1]
    try:
        op1 = int(sys.argv[2])
        op2 = int(sys.argv[3])
        if(func == "+" or func == "-" or func == "*" or func == "/" ):
            if (func == "+"):
                print(op1 + op2)
            elif (func == "-"):
                print(op1 - op2)
            elif (func == "*"):
                print(op1 * op2)
            elif (func =="/"):
                print(op1 / op2)
        else:
            print "function should be +, -, * o /"
    except ValueError:
        print "op1 y op2 should be integers"
else:
    print "Use: calculator function op1 op2"