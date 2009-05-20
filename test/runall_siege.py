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

import os, csv, sys, time
from copy import copy

# Client host name
CLIENT_HOST = "trinity"

# Directory where the project is.
MAIN_DIR = "~/stm_project_stuff/stm_project"

# Schedtool binary
SCHED_TOOL = "schedtool"

# URL lists (on the client host)
URL_LISTS = ["man2html-zipf-%d" % i for i in range(1,2)]
URL_LISTS = [os.path.join(MAIN_DIR, "test/url-lists", file) for file in URL_LISTS]

# Minimum and maxmimum number of cores
MIN_CORES, MAX_CORES = 1,32

def system(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print "Error: command returned %d." % ret
        sys.exit(ret)

def wait_while_running(cmd):
    def is_running(cmd):
        return os.system("ps ax|egrep -v '(ps|grep)' | grep %s > /dev/null" % cmd) == 0
    print "Waiting for %s" % cmd
    while is_running(cmd):
        sys.stdout.write('.')
        time.sleep(0.5)
        sys.stdout.flush()

class Experiment(object):
    def __init__(self):
        self.siege_options = { 
            "host" : CLIENT_HOST,
            "cmd" : "~/local/bin/siege", "concurrent" : 350, \
            "time" : "30s",
            "options" : "-b -i",
            "output_file" : "~/siege_output.txt"
             } 
        self.main_dir = MAIN_DIR
        self.schedtool = SCHED_TOOL
        self.url_lists = URL_LISTS
        self.options = {
            "no-cache" : { 
                "apachedir" : os.path.join(self.main_dir, "httpd-2.2.x.no-transactions/"),
                "confdir"   : os.path.join(self.main_dir, "no-cache-conf")
            },
            "no-transactions" : { 
                "apachedir" : os.path.join(self.main_dir, "httpd-2.2.x.no-transactions/"),
                "confdir"   : os.path.join(self.main_dir, "cache-conf")
            },
            "transactified" : { 
                "apachedir" : os.path.join(self.main_dir, "httpd-2.2.x"),
                "confdir"   : os.path.join(self.main_dir, "cache-conf")
            }
        }

    def test_all(self):
        for url_list in self.url_lists:
            for name in self.options.keys():
                for num_cores in range(MIN_CORES,MAX_CORES+1):
                    self.test(name, num_cores, url_list)
    
    def test(self, test_name, num_cores, url_list):
        print "Test %s: %d cores." % (test_name, num_cores)
        system(self.apache(test_name, num_cores, "start"))
        time.sleep(5)
        self.siege(test_name, num_cores, url_list)
        system(self.apache(test_name, num_cores, "stop"))
        wait_while_running("httpd")
        self.remove_logs(self.options[test_name]["confdir"])

    def apache(self, test_name, num_cores, command):
        options = self.options[test_name]
        schedtool = self.schedtool + " -a 0x%x" % (2**num_cores-1)
        apache = os.path.join(options["apachedir"], "httpd") + \
            " -d %s -k %s " % (options["confdir"],command)
        return "%s -e %s" % (schedtool, apache)

    def siege(self, test_name, num_cores, url_list):
        options = copy(self.siege_options)
        options['file'] = url_list 
        cmd = "%(cmd)s -f %(file)s -t %(time)s -c %(concurrent)d %(options)s" % options
        if num_cores == 1:
            cmd += ' -m "%s, url-list=%s"' % (test_name,url_list)
        cmd += " > %(output_file)s" % options
        cmd = "ssh %s '%s'" % (options['host'], cmd)
        system(cmd)

    def remove_logs(self, confdir):
        log = os.path.join(confdir, "logs/access_log")
        log = os.path.expanduser(log)
        try:
            os.remove(log)
        except OSError: pass

if __name__ == "__main__":
    Experiment().test_all()
