#!/usr/bin/python

import sys,random

DENOM = {}

def nat_range(N): return xrange(1,N+1)

def denom(s, N):
    if (s,N) not in DENOM:
        DENOM[(s,N)] = sum(n**(-s) for n in nat_range(N))
    return DENOM[(s,N)]

def f(k, s, N):
    return k**(-s) / denom(s,N)

def random_with_probability(list):
    x = random.random()
    cdf = 0
    for item,probability in list:
        cdf += probability
        if cdf > x:
            return item
    return item

def zipfify_list(l, s, target_length = None):
    N = len(l)

    if not target_length:
        target_length = 1.0 / f(N, s, N)

    distrib = [(l[k-1],f(k,s,N)) for k in nat_range(N)]

    target_list = []

    for i in xrange(target_length):
        target_list.append(random_with_probability(distrib))

    return target_list

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print >>sys.stderr, 'Usage: %s [<s>] [<target_length>]' % sys.argv[0]
        sys.exit(1)

    s = 1
    target_length = None

    try: s = float(sys.argv[1])
    except IndexError: pass

    try: target_length = int(sys.argv[2])
    except IndexError: pass

    lines = [ l.rstrip() for l in sys.stdin ]

    for l in zipfify_list(lines, s, target_length):
        print l
