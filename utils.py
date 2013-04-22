import argparse
import ConfigParser
import codecs
import urllib
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import tarfile
import zipfile
import logging
import extract_files
import re
  
def mountparse(line_from_mount):
    '''
    give it a line from mount(not /etc/fstab!) as a string and it return a dict
    with the following keys:
        
    device(eg /dev/sdc), mountpoint /media/foo, os (linux or darwin),
    type (fstype), opts (mountoptions)
    
    from jojoo, gplv3
    '''
    ret={}

 
    device_point = r'''
    ^       # beginning of the line
    (.+)    #   some chars until there is a whitespace and a on - DEVICE
    \s      #   whitespace
    on      #   on - valid at linux and osx
    \s      #   whitespace
    (.+)\s  #   some chars until there is a whitespace and a "type" or ( - MPOINT            
    (\(.*\s| #( with a whitespace after some time (mac) OR              )
    type\s) #type with a whitespace short after(linux)
    (.*)\)           
    '''
    d_p = re.compile(device_point, re.VERBOSE)
    try:
        dm_listet = d_p.search(line_from_mount).groups()
    except AttributeError:
        #print "mountparse could not parse the line from mount"
        return None
    try:
        ret["device"], ret["mountpoint"] = dm_listet[0], dm_listet[1]
    except ValueError:
        print "could'nt decifer your mounts. is it a linux or a mac with /dev/foobar on /mountpoint ?"
    if (dm_listet[2].find("type")>=0):
        ret['os'] = 'linux'
        try:
            ret["type"], ret["opts"] = dm_listet[3].split(" (")
        except ValueError:
            print "not a linux? dont know what to do, splitting of", dm_listet[3], "failed"
    else:
        ret['os'] = 'darwin'
        temp = dm_listet[2].split(', ')
        ret['type'] = temp[0].replace('(', '')
        ret['opts'] = ", ".join(temp[1:]) + dm_listet[3]

    return ret
    
def detect_stick():
    '''
    detects if a stick is plugged in, returns a dict with infos about the stick. see 
    mountparse for a description of the dict
    '''    
    #read from mount for the first time
    output_first,error_first = subprocess.Popen("mount",stdout = subprocess.PIPE,
        stderr= subprocess.PIPE).communicate()


    print "Pleaze insert stick, and wait thill is it mountet, then press ENTER"
    raw_input()

    #read from mount for the second time
    output_second,error_second = subprocess.Popen("mount",stdout = subprocess.PIPE,
        stderr= subprocess.PIPE).communicate()

    #convert it to sets
    output_first_set = set(output_first.split("\n"))
    output_second_set = set(output_second.split("\n"))

    #iterate through the items, which are not in both sets (e.g. new lines)

    for i in output_first_set.symmetric_difference(output_second_set):
        mp = mountparse(i)
        if (mp):
            return mp
        else:
            return None




#from http://docs.python.org/2/howto/logging-cookbook.html explainations there

#tempdir = tempfile.mkdtemp()

tempdir = os.path.realpath(tempfile.mkdtemp())
tc_mountpoint = os.path.realpath(tempfile.mkdtemp())

logfile = os.path.realpath(tempdir+"parabirdy_log.txt")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=tempdir+"parabirdy_log.txt",
                    filemode='w')
                    
console = logging.StreamHandler()
console.setLevel(logging.INFO)
#formatter = logging.Formatter('%(name)-6s: %(levelname)-6s %(message)s')
formatter = logging.Formatter('[%(levelname)s::%(name)s]: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
mainLogger = logging.getLogger('main')



mainLogger.info('Logfile: ' + logfile)

def dependency_check(checked_app):
# This function tests dependencies. All stdout is send to devnull
    try:
        FNULL = open(os.devnull, 'w')
        subprocess.check_call(checked_app, stdout=FNULL)

    except OSError:
        mainLogger.error("[ERROR] Missing Depedencies:", checked_app,+"not installed, exiting...")
        from sys import exit
        exit()

def update_config(section, key, value_from_argparser):
# This function checks if there is any parameter given, 
# If there is a parameter given, it updates the config 
# if not it uses default values from config.ini
    if value_from_argparser:
        mainLogger.info('Parameter given, device or container is: ' + value_from_argparser)
        parser.set(section, key, value_from_argparser)

    if value_from_argparser == None:
        mainLogger.info("Taking %s %s from Config: %s" % (section, key, parser.get(section, key) ))

def download_application(progname, url, filename):
# This function tries to downloads all the programs we 
# want to install. 
    mainLogger.info('[INFO] Downloading: ' + progname)

    try:
        for r in range(3):
            returnobject, header = urllib.urlretrieve(url, filename=tempdir+"/"+filename)
            if header.get('status') == '200 OK':
                break
        else:
            mainLogger.error("[ERROR] Could not download %s. exiting " %(progname))
            exit()
    except:
        mainLogger.error("[ERROR] Could not download %s" %(progname))
        return None
    
#    try:
#        returnobject, header = urllib.urlretrieve(url, filename=tempdir+"/"+filename)
#        status = header.get('status')
#        if status == 404:
#            mainLogger.error("[ERROR] Could not download", progname)
#            exit()
#    except:
#        mainLogger.error("[ERROR] Could not download", progname)
#        return None



# Parsing Arguments given as Parameter from Shell
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--device", help="Device Flag to specify USB Stick")
parser.add_argument("-t", "--thunder", help="Specify Thunderbird version to download")
parser.add_argument("-b", "--torbirdy", help="Specify Torbirdy Version")
parser.add_argument("-e", "--enigmail", help="Specify Enigmail Version") 
parser.add_argument("-a", "--vidalia", help="Specify Vidalia Version")
parser.add_argument("-n", "--container_name", help="Specify Container Name")

args = parser.parse_args()

# Importing Config File: config.ini
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
with codecs.open('config.ini', 'r', encoding='utf-8') as f:
    parser.readfp(f)


