#!/usr/bin/python
#
#  Copyright 2009 Haggai Eran, Ohad Lutzky
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

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
