import os, time

SRC_DIR="/Users/Augustus/Dropbox/Wake Images"
HOST="yankuanz@aludra.usc.edu"
DEST_PATH="/home/scf-09/yankuanz/public_html/snap/latest.jpg"

def getLatestImgName():
	mtime = lambda f: os.stat(os.path.join(SRC_DIR, f)).st_mtime
	files = list(sorted(os.listdir(SRC_DIR), key=mtime))
	if not files: 
		return False
	return files[-1]

def copyToServer(fileToCopy):
	os.system('scp "%s" "%s:%s"' % (os.path.join(SRC_DIR, fileToCopy), HOST, DEST_PATH))

def sendIfUpdated(originalFile):
	latest = getLatestImgName()
	if not latest or latest == originalFile: 
		return False
	copyToServer(latest)
	return latest

lastFile = None
while True:
	result = sendIfUpdated(lastFile)
	if result: 
		print("Uploaded file: {}".format(result))
		lastFile = result
	else:
		print("Nothing new. Latest: {}".format(lastFile))
	time.sleep(10)
