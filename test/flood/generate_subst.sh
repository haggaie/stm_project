#!/bin/bash

if [[ -z $1 ]]; then
	echo "Usage: $0 [dirname]";
	exit 1;
fi

cd $1
find -type f | 
	python -c "
import sys
import urllib
for line in sys.stdin: print urllib.quote(line.rstrip())" |
	sed 's/^\.\///'
