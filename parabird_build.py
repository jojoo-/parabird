import urllib # url handling, downloads
import getopt # optionen/argumente parsen
import sys    # dinge die den interpreter betreffen
import subprocess  # make system calls

print sys.argv[1:]

truecrypt_version = "7.0a" # hier koennen wir spaeter nen argument uebergeben
version = '1.0'
# alle argumente werden von getopt bearbeitet, das resultat in options und remainder gesichert

options, remainder = getopt.getopt(sys.argv[1:], 'o:v', ['output=', 
						'verbose',
						'truecrypt=',
						'device=',
						])

print type(options)
for opt, arg in options:
	if opt in ('-o', '--output'):
		output_filename = arg
	elif opt in ('-v', '--verbose'):
		verbose = True
	elif opt == '--truecrypt':
		truecrypt_version = arg
	elif opt == '--device':
		usb_device = arg

truecrypt_url = "http://www.truecrypt.org/download/truecrypt-"+ truecrypt_version +  "-linux-console-x86.tar.gz"
urllib.urlretrieve(truecrypt_url, "/tmp/tc.tgz")

TRUECRYPT = "truecrypt --filesystem=none"+ usb_device +
MAKE_FS = "mkfs.ntfs --quick /dev/mapper/truecrypt0" # hier muss noch ein Check eingebaut werden, damit er auch das richtige device bekommt.
UNMOUNT_USB = "truecrypt -d"+ usb_device + 
MOUNTPOINT_CREATE = "mkdir /tmp/mount/" #ueberlegung: das mit dem mounten mit nem eigenen py modul machen
MOUNTPOINT = "/tmp/mount/"
TRUEMOUNT = "truecrypt"+ usb_device +""+ MOUNTPOINT + "" # man kann direkt vergetten, siehe shell->

cmds_create [TRUECRYPT, MAKE_FS, UNMOUNT_USB]
cmds_mount [MOUNTPOINT_CREATE, TRUEMOUNT]
for cmd in cmds_create:
	print "Creating encrypted USB-Stick"
	subprocess.call(cmd_create, shell=True) # bin mir nicht sicher ob das klappt. 1) leerzeichen, 2) kann sein, dass man jedes arg einzeln übergeben muss
	print "Encrypted USB-Stick created and mounted to:", MOUNTPOINT # siehe shell -> 

for cmd in cmds_mount:
	print "Creating Mountpoint and Mounting USB Stick"
	try:
		subprocess.check_call(cmd_mount, shell=True)
	except 
	print "USB-Stick mounted..."

# Truecrypt tut, jetzt kommt Thunderbird

TB_DOWNFILE "/tmp/thunderbird.tar.bz2"
print "Downloading Thunderbird"
thunderbird_url = "http://releases.mozilla.org/pub/mozilla.org/thunderbird/releases/17.0.5/linux-x86_64/de/thunderbird-17.0.5.tar.bz2"
urllib.urlretrieve(thunderbird_url, TB_DOWNFILE) # erstes rgument: url. zweites argument: ziel. + kettet stings aneinander
ß
print "Download complete, unpacking"
subprocess.call(tar xfj + TB_DOWNFILE +, shell=True)

