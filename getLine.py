#! /usr/bin/python3.6

import sys

with open(sys.argv[1]) as f:
    count = 0
    index = int(sys.argv[2])
    for line in f:
        if count+1 == index:
            print(count, line)
        if count == index:
            print(index, line)
        count += 1
f.close()
