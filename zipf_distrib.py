#!/usr/bin/python

import sys

DENOM = {}

def nat_range(N): return xrange(1,N+1)

def denom(s, N):
    if (s,N) not in DENOM:
        DENOM[(s,N)] = sum(n**(-s) for n in nat_range(N))
    return DENOM[(s,N)]

def f(k, s, N):
    return k**(-s) / denom(s,N)

def zipfify_list(l, s, target_length):
    N = len(l)
    distrib = ((l[k-1],f(k,s,N)) for k in nat_range(N))

    target_list = []

    for element, probability in distrib:
        occurences = int(round(target_length * probability))
        for i in xrange(occurences):
            target_list.append(element)

    return target_list

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >>sys.stderr, 'Usage: %s [s] [target_length]' % sys.argv[0]
        sys.exit(1)

    s = int(sys.argv[1])
    target_length = int(sys.argv[2])

    lines = [ l.rstrip() for l in sys.stdin ]

    for l in zipfify_list(lines, s, target_length):
        print l
