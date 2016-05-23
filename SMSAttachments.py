import FileLister
import io
import hashlib
import os
import xml.etree.ElementTree as ET
import sys
from shutil import copyfile
from subprocess import call
from timeit import default_timer

#created by Luis Sanchez
def main():
	backupPath = None
	userPath = os.environ['HOME']
	if '/' == userPath[0]:
		backupPath = userPath + "/Library/Application Support/MobileSync/Backup/"
	else:
		#same for windows
		print("windows")
	dictioList = getDevicesName(backupPath).items()
	print("Please select the device that you would like to extract the attachments from:")
	num = 1
	for name in dictioList:
		print(str(num) +":" + name[0])
		num +=1
	device = None
	while True:
		try: #end program with control c, its int he try and except errr
			selection = int(input(''))
			if 1<= selection <= len(dictioList):
				device = dictioList[selection-1]
				print("Thank you. The program will do the rest. Just sit back and relax :)\n")
				break
			else:
				print("Please try again. Select one of the option above.")
		except:
			print("Please enter a number from the list above.")
	start = default_timer()
	location, amountFiles = SMSAttachments(device)
	duration = str(default_timer() - start)
	print("\nThe program finished copying " + str(amountFiles) + " files to " + location + " in " + duration + " seconds.")

def SMSAttachments(device):
	path = device[1]
	newDirPath = makedir()
	backUpFiles = FileLister.process_mbdb_file(path + "/Manifest.mbdb")
	#copy files
	amountFiles = 0
	for hashed in backUpFiles:
		file = path+"/"+hashed[0]
		if os.path.isfile(file): #check if the file exists inside backup folder
			fileName = hashed[1]['filename'][67:]
			count = 1
			copy = ""
			newDes = newDirPath+"/"+fileName
			while True:
				if not os.path.isfile(newDes):
					#print(newDes)
					print("Copying "+ copy+fileName)
					copyfile(file, newDes)
					addProperties(hashed[1],newDes)
					amountFiles +=1
					break
				else:
					newDes = newDirPath+"/"+str(count)+fileName
					copy = str(count)
					count +=1
	return (newDirPath, amountFiles)

def addProperties(fileInfo, filePath):
	cTime = fileInfo['ctime']
	mTime = fileInfo['mtime']
	aTime = fileInfo['atime']
	#apply ctime, and mtime. not sure if ctime is the correct one...
	os.utime(filePath,(aTime, mTime))

def makedir():
	#make directory for the SMSAttachemnts
	original = "SMSAttachments"
	path = os.environ['HOME'] + "/Desktop/" #change for windows
	count = 1
	while True:
		if not os.path.exists(path + original):
			os.makedirs(path + original)
			break
		else:
			original = "SMSAttachments" + str(count)
			count +=1
	return path + original

def getDevicesName(path):
	#gets the path of the backup folders
	directory = os.listdir(path)
	deviceNames = {}
	for folder in directory:
		manifest = path+folder
		if folder != ".DS_Store" and os.path.exists(manifest +"/Manifest.mbdb"): #checks if there is a manifest.mbdb file, change for windows
			infoPlist = path + folder + "/Info.plist"
			#extracts the Device name from the info.plist file
			if os.path.exists(infoPlist):
				deviceNames[ET.parse(infoPlist).getroot()[0][5].text] = manifest
			else:
				print("There is not a Info.plist file, please back up your device correctly.")
	if not deviceNames:
		sys.exit("Please backup a device and run this program again.")
	return deviceNames

if __name__ == "__main__":
   main()