#!/usr/bin/python

from subprocess import PIPE, Popen
import time, re

def ifline():
    return Popen("/sbin/ifconfig eth0 | grep bytes", shell=True, stdout=PIPE).communicate()[0].strip().strip().strip().strip().strip()

regexp = re.compile(r"RX bytes:(\d+).*TX bytes:(\d+)")

def bw():
    line = ifline()
    m = regexp.search(line)
    return map(int,m.groups())

diff=[0,0]
cur = bw()
while True:
    time.sleep(1)
    next = bw()
    diff[0] = (next[0] - cur[0]) / 1024
    diff[1] = (next[1] - cur[1]) / 1024
    print diff
    cur = next
