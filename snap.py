import os, time, cv2, copy
import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

SRC_DIR = "/Users/Augustus/Dropbox/Wake Images"
HOST = "yankuanz@aludra.usc.edu"
DEST_PATH = "/home/scf-09/yankuanz/public_html/snap/latest.jpg"
SCRIPT_DIR = "/Users/Augustus/Documents/snap"
ENHENCED_IMG_NAME = "enhenced.jpg"
CROPPED_IMG_NAME = "cropped.jpg"
SENT_IMG_NAME = "LatestSnap.jpg"
SUBJECT = "This is my latest selfie!"
RUNNING_LIMIT = 6 * 60 * 24 * 7 # one week
TEST_TO = "yankuanz@usc.edu"

FROM = "yankuanz@usc.edu"
TO = ["summerdaxi@163.com", "geniusyankuan@163.com", "shangmengsm@163.com"]
SUBJECT = "This is my latest selfie!"

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
	print "Upload file:", os.path.join(SCRIPT_DIR, fileToCopy)
	os.system('scp "%s" "%s:%s"' % (os.path.join(SCRIPT_DIR, fileToCopy), HOST, DEST_PATH))
	time.sleep(1)
	# delete the file from local after uploading it
	# otherwise, it will mess up with getLatestImgName()
	# print fileToCopy
	# if fileToCopy == "upload":
	# os.system('rm "%s"' % (os.path.join(SCRIPT_DIR, fileToCopy)))

# enhence image before upload it and return new filename if any
def enhenceImage(imageFileName):
	# 1. read in as matrix and crop it to square (720x720)
	print "Process:", os.path.join(SRC_DIR, imageFileName)
	img = cv2.imread(os.path.join(SRC_DIR, imageFileName))
	img = img[:, 280:1000, :] #crop in the middle
	cv2.imwrite(os.path.join(SCRIPT_DIR, CROPPED_IMG_NAME), img) # for email

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
	print "Save to:", os.path.join(SCRIPT_DIR, ENHENCED_IMG_NAME)
	cv2.imwrite(os.path.join(SCRIPT_DIR, ENHENCED_IMG_NAME), img) # for webpage
	time.sleep(1)

def sendEmail(imageFileName):
	sendEmail_1(imageFileName)
	sendEmail_2(imageFileName)

# email original image
def sendEmail_1(imageFileName):
	# send email in school network without logging in personal email account
	os.system('(echo "%s"; uuencode %s "%s") | mail -s "%s" %s' % ("This snap is taken at " + time.strftime('%X %x') + '.\n', os.path.join(SCRIPT_DIR, imageFileName), imageFileName, SUBJECT, TEST_TO))  
	print "Email", os.path.join(SCRIPT_DIR, imageFileName), "to", TEST_TO

def sendEmail_2(imageFileName):
	# Create the message
	# Create the container (outer) email message.
	msg = MIMEMultipart()
	# msg['To'] = email.utils.formataddr(('', TO[0]))
	msg['From'] = email.utils.formataddr(('Yankuan', FROM))
	msg['Subject'] = SUBJECT

	# body text
	body = MIMEText("This snap is taken at " + time.strftime('%X %x') + '.\n')
	msg.attach(body)

	# attached image
	fp = open(os.path.join(SCRIPT_DIR, imageFileName), 'rb')
	img = MIMEImage(fp.read())
	fp.close()
	msg.attach(img)

	# body html
	html = '<html><head></head><body><br><br>Click <a href="http://www-scf.usc.edu/~yankuanz/snap/">here</a> to see it online!</p></body></html>' #<img src="' + "http://www-scf.usc.edu/~yankuanz/snap/latest.jpg" + '"/>

	# Record the MIME types of text/html and attach it
	htmlPart = MIMEText(html, 'html')
	msg.attach(htmlPart)

	try:
		server = smtplib.SMTP('localhost',25)
		server.set_debuglevel(True) # show communication with the server
		server.sendmail(FROM, TO, msg.as_string())
		# server.send_message(msg)
		server.quit()
		print "Email", os.path.join(SCRIPT_DIR, imageFileName), "to", " ".join(TO)
	except Exception:
		print "Email 1 failure."
	# finally:

def sendIfUpdated(originalFile):
	latest = getLatestImgName()
	if not latest or latest == originalFile: 
		print "[ Nothing new ]"
		return False
	print "[ Something new ]", latest
	enhenceImage(latest)
	sendEmail(CROPPED_IMG_NAME)
	copyToServer(ENHENCED_IMG_NAME)
	return latest

def standby(timeSpan):
	print "< Standby >",
	for i in range(timeSpan):
		print timeSpan - i,
		time.sleep(1)
	print 

lastFile = None
count = 0
while count < RUNNING_LIMIT:
	result = sendIfUpdated(lastFile)
	if result: 
		# print("Uploaded file: {}".format(result))
		lastFile = result
	# else:
	# 	print("Nothing new. Latest: {}".format(lastFile))
	count += 1
	print "[ Progress ] {0:.3f}%".format(count / (RUNNING_LIMIT + 0.1) * 100)
	standby(10)

