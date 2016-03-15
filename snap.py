import os, time, cv2, copy

SRC_DIR = "/Users/Augustus/Dropbox/Wake Images"
HOST = "yankuanz@aludra.usc.edu"
DEST_PATH = "/home/scf-09/yankuanz/public_html/snap/latest.jpg"
SCRIPT_DIR = "/Users/Augustus/Documents/snap"
ENHENCED_IMG_NAME = "enhenced.jpg"
# get the most recent file name from SRC_DIR
def getLatestImgName():
	mtime = lambda f: os.stat(os.path.join(SRC_DIR, f)).st_mtime
	files = list(sorted(os.listdir(SRC_DIR), key=mtime))
	if not files: 
		return False
	if not files[-1].split(".")[-1] == "jpg":
		# doing this because there might be .DS_Store showing up
		return False
	return files[-1]

# upload to file to server and then delete it locally
def copyToServer(fileToCopy):
	os.system('scp "%s" "%s:%s"' % (os.path.join(SRC_DIR, fileToCopy), HOST, DEST_PATH))
	# delete the file from local after uploading it
	# otherwise, it will mess up with getLatestImgName()
	# print fileToCopy
	# if fileToCopy == "upload":
	time.sleep(3)
	os.system('rm "%s"' % (os.path.join(SRC_DIR, fileToCopy)))

# enhence image before upload it and return new filename if any
def enhenceImage(imageFileName):
	# 1. read in as matrix and crop it to square (720x720)
	img = cv2.imread(os.path.join(SRC_DIR, imageFileName))
	img = img[:, 280:1000, :] #crop in the middle

	# 2. enhence it by equalizing the histogram of three bands
	equ = copy.deepcopy(img)
	for b in range(3): 
		equ[:,:,b] = cv2.equalizeHist(img[:,:,b])

	# 3. detect and mark face(s)
	face_cascade = cv2.CascadeClassifier(os.path.join(SCRIPT_DIR, 'haarcascade_frontalface_default.xml'))
	gray = cv2.cvtColor(equ, cv2.COLOR_BGR2GRAY)
	faces = face_cascade.detectMultiScale(gray, 1.025 , 3, minSize=(180, 180))
	if len(faces) > 0:
		for i,(x,y,w,h) in enumerate(faces):
			cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
		# 4. save it
	cv2.imwrite(os.path.join(SRC_DIR, ENHENCED_IMG_NAME), img)

def sendIfUpdated(originalFile):
	latest = getLatestImgName()
	if not latest or latest == originalFile: 
		return False
	enhenceImage(latest)
	copyToServer(ENHENCED_IMG_NAME)
	return latest

lastFile = None
while True:
	result = sendIfUpdated(lastFile)
	if result: 
		# print("Uploaded file: {}".format(result))
		lastFile = result
	# else:
	# 	print("Nothing new. Latest: {}".format(lastFile))
	time.sleep(5)
