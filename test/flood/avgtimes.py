#!/usr/bin/python

from avgtime import process_file
import os,sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: avgtimes <directory>"
        sys.exit(1)

    dir = sys.argv[1]
    for root, dirs, files in os.walk(dir):
        for file in files:
            r = process_file(os.path.join(dir, file))
            print file, r['avg']
