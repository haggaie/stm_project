#!/usr/bin/python

import sys
from math import sqrt

def process_file(filename):
    f = open(filename, 'r')
    time_lines = [ map(int,(line.strip().split(" ")[0:5])) for line in f ]
    times = [ line[4] for line in time_lines]
    start_time = time_lines[0][0]
    finish_time = time_lines[-1][0] + time_lines[-1][4]
    f.close()
    r={}
    n = float(len(times))
    r['avg'] = sum(times)/n
    r['max'] = max(times)
    r['min'] = min(times)
    r['std'] = sqrt((sum(t**2 for t in times) / n) - (r['avg'] ** 2))
    r['duration'] = (finish_time-start_time)
    r['throughput'] = 1e6 * n / r['duration']
    f.close()
    return r
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage:", sys.argv[0], "[filename]"
        sys.exit(1)
    filename = sys.argv[1]
    print process_file(filename)
