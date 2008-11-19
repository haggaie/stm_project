#!/usr/bin/python

import os, csv, sys, time, subprocess
from avgtime import process_file

def system(cmd):
    print cmd
    ret = os.system(cmd)
    if ret != 0:
        print "Error: command returned %d." % ret
        sys.exit(ret)

class Experiment(object):
    def __init__(self, csvfilename):
        self.csvwriter = csv.DictWriter(file(csvfilename, 'wb'),\
            ("test", "num_cores", "host", "avg", "throughput", "duration"))
        self.csvwriter.writerow({ "test" : "Test", "num_cores" : "# Cores", \
            "host" : "Host", "avg" : "Average Response Time", \
            "throughput" : "Throughput", "duration" : "Duration"})

        self.flood_cmd = "../flood/flood"
        self.flood_dir = "~/stm_project_stuff/flood_config"
        self.flood_xml = "man-zipf.xml"
        self.main_dir = "~/stm_project_stuff/stm_project/"
        self.schedtool = "~/schedtool-1.3.0/schedtool"
        #self.flood_machines = ["u101", "u102", "u104", "localhost"]
        self.flood_machines = ["u101", "u102", "u104", "localhost"]
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
        for name in self.options.keys():
            for num_cores in range(1,9):
                self.test(name, num_cores)
    
    def test(self, test_name, num_cores):
        print "Test %s: %d cores." % (test_name, num_cores)
        system(self.apache(test_name, num_cores, "start"))
        time.sleep(3)
        results = self.flood(self.flood_xml)
        system(self.apache(test_name, num_cores, "stop"))
        time.sleep(3)
        for host, result in results.items():
            self.csvwriter.writerow({ "test" : test_name,   \
                "num_cores" : num_cores, "host" : host,     \
                "avg" : result['avg'], "throughput" : result['throughput'], \
                "duration" : result['duration']})

    def apache(self, test_name, num_cores, command):
        options = self.options[test_name]
        schedtool = self.schedtool + " -a 0x%x" % (2**num_cores-1)
        apache = os.path.join(options["apachedir"], "httpd") + \
            " -d %s -k %s " % (options["confdir"],command)
        return "%s -e %s" % (schedtool, apache)

    def flood(self, flood_xml):
        processes = []
        tempnames = []
        for host in self.flood_machines:
            tempname = os.tempnam()
            tempnames.append(tempname)
            if host == "localhost":
                cmd = "%s < %s > %s" % \
                    (self.flood_cmd, flood_xml, tempname)
            else:
                cmd = "ssh %s 'cd %s; %s' < %s > %s" % \
                    (host, self.flood_dir, self.flood_cmd, flood_xml, tempname)
            print cmd
            processes.append(subprocess.Popen(cmd, shell=True))
        print "Waiting for all processes."

        completed = 0
        while len(processes) > completed:
            if processes[-1].wait() != 0:
                print "Error with one of the processes."
                sys.exit(1)
            completed += 1
        print "All flood processes completed"
        results = {}
        for i in range(len(processes)):
            tempname = tempnames[i]
            host = self.flood_machines[i]
            print "Processing file '%s' of host %s" % (tempname, host)
            system("grep -v FAIL %s > /dev/null" % tempname)
            results[host]=process_file(tempname)
            os.remove(tempname)
        return results

if __name__ == "__main__":
    Experiment("result.csv").test_all()
