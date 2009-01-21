#!/usr/bin/env python
import sys
import re

heading_line = re.compile(r'\*{4}(.*), url-list=.*-(.*)\*{4}')

def parse(file):
    line = file.readline().strip()
    print "Version, S, Cores, ", line
    for line in file:
        m = heading_line.match(line)
        if m:
            version = m.groups()[0].strip()
            s = float(m.groups()[1])
            cores = 1
        else:
            print version, ", ", s, ", ", cores, ", ", line.strip()
            cores += 1

if __name__ == '__main__':
    parse(sys.stdin)
