# encoding: utf-8

import os.path
import tarfile
import zipfile
import subprocess
import sys
import os
import tempfile
import shlex
import shutil
import tarfile
import zipfile
import requests
import plistlib
import glob
from xml.dom import minidom
#from utils import *
from utils import ParaLogger


extractLogger=ParaLogger('extract')


def extract_tarfile(progname, filename, path):
    extractLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        tar = tarfile.open(filename)
        tar.extractall(path)
        tar.close()
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        sys.exit()


def extract_7z(progname, filename, path):
    extractLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        subprocess.check_call(['7z', '-y', 'x', filename, '-o'+path])
    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting" .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting" .format(progname))
        sys.exit()


def extract_zipfile(progname, filename, path):
    extractLogger.info("[INFO] Extracting {}" .format(progname))
    try:
        zip = zipfile.ZipFile(filename)
        zip.extractall(path)
        zip.close()
    except:
        extractLogger.error("Could not extract {}. exiting " .format(progname))
        extractLogger.exception("extract_zipfile did not work:")
        raise
        sys.exit()


def extract_dmg_mac(progname, filename, path):
    '''
    extracts files from a dmg on mac:
    mounts the image via hdiutil, copies the stuff to the specified path

    parameters:
    progname is the name of the program, only used for messages
    filename is the name of the dmg to "extract"
    path is the path, where all files are copied

    returns the path
    '''
    extractLogger.info("Extracting {} with extract_dmg_mac".format(progname))
    try:
        outplist = subprocess.Popen(['hdiutil', 'attach', '-plist', filename], stdout=subprocess.PIPE).communicate()[0]
        pldict = plistlib.readPlistFromString(outplist)
        for se in pldict['system-entities']:
            if se.get('mount-point'):
                dmg_mountpoint = se.get('mount-point')+"/"
                extractLogger.info("Mac Extract: DMG Mountpoint is {}".format(dmg_mountpoint))
                break
        else:
            dmg_mountpoint = None
            extractLogger.error('Mac Extract: Mac mountpoint could not be figured out.')
            return False

        for i in glob.glob(dmg_mountpoint+"/*.app"):
            shutil.copytree(i, os.path.join(path, os.path.basename(i)))
            extractLogger.info('Mac Extract: Copying from {} to {}'
                               .format(i, os.path.join(path, os.path.basename(i))))
        try:
            extractLogger.info('Mac Extract: Copying for {} done'.format(progname))
            return i
        except NameError:
            #aka no i
            return False

    except OSError:
        extractLogger.error("Mac Extract: hdiutil not installed. quitting")
        extractLogger.exception("Mac Extract: hdiutil not installed. quitting")
        raise
        sys.exit()


def extract_dmg(progname, dmgfile, path):
    extractLogger.info("[INFO] Extracting {}" .format(progname))
    tempdir = os.path.dirname(dmgfile)
    os.makedirs(tempdir+"/dmg")
    try:
        extractLogger.debug("Linux DMG Extract: img2dmg: {} {} {}".format("dmg2img", dmgfile, dmgfile+".img"))
        subprocess.check_call(["dmg2img", dmgfile, dmgfile+".img"])
        extractLogger.debug(
            "Linux DMG Extract: mounting: {} {} {} {} {} {} {}".format(
            'mount', '-t', 'hfsplus', '-o', 'loop', 'quiet', dmgfile+".img",
            "/dmg/"))

    # The following Code need testing: subprocess call worked in shell.
    # Copying based on Mac Code, hope this works here too.

        subprocess.check_call(['mount', '-t', 'hfsplus', '-o', 'loop', os.path.join(dmgfile+".img"), os.path.join(tempdir+"/dmg/")])

        #for i in glob.glob(tempdir+"/dmg/*.app"):
        #    shutil.copytree(i, os.path.join(path, os.path.basename(i)))
        #    extractLogger.info('Mac Extract: Copying from {} to {}'.format
        #        (i, os.path.join(path, os.path.basename(i))))
        # wont work for wildcard bash reasons:
        #subprocess.check_call(['cp', '-r', os.path.join(tempdir+"/dmg/*.app/*"), path])
        for i in glob.glob(tempdir+"/dmg/*.app"):
            subprocess.check_call(['cp', '-r', i, path])

    except:
        extractLogger.error("[ERROR] Could not extract {}. exiting " .format(progname))
        extractLogger.exception("[ERROR] Could not extract {}. exiting " .format(progname))
        sys.exit()


def mount_dmg(path_to_dmg):
    '''
    mounts the specified .dmg, returns a path for the mounted dmg.

    this will deprecate extract_dmg and extract_dmg_mac
    '''
