from flask import Flask, render_template, request
import time
from pyfingerprint.pyfingerprint import PyFingerprint

import MySQLdb
 
db = MySQLdb.connect(host="localhost",  # your host 
                     user="root",       # username
                     passwd="***********",     # password
                     db="dooraccesslog")   # name of the database
 
# Create a Cursor object to execute queries.
cur = db.cursor()
 
# # Select data from table using SQL query.
# cur.execute("SELECT * FROM userList")
# # print the first and second columns      
# for row in cur.fetchall() :
#     print row[0], " ", row[1]

def enrollFinger(username):
	## Tries to initialize the sensor
	try:
	    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

	    if ( f.verifyPassword() == False ):
	        raise ValueError('The given fingerprint sensor password is wrong!')

	except Exception as e:
	    print('The fingerprint sensor could not be initialized!')
	    print('Exception message: ' + str(e))
	    exit(1)

	## Gets some sensor information
	print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

	## Tries to enroll new finger
	try:
	    print('Waiting for finger...')

	    ## Wait that finger is read
	    while ( f.readImage() == False ):
	        pass

	    ## Converts read image to characteristics and stores it in charbuffer 1
	    f.convertImage(0x01)

	    ## Checks if finger is already enrolled
	    result = f.searchTemplate()
	    positionNumber = result[0]

	    if ( positionNumber >= 0 ):
	        print('Template already exists at position #' + str(positionNumber))
	        exit(0)

	    print('Remove finger...')
	    time.sleep(2)

	    print('Waiting for same finger again...')

	    ## Wait that finger is read again
	    while ( f.readImage() == False ):
	        pass

	    ## Converts read image to characteristics and stores it in charbuffer 2
	    f.convertImage(0x02)

	    ## Compares the charbuffers
	    if ( f.compareCharacteristics() == 0 ):
	        raise Exception('Fingers do not match')

	    ## Creates a template
	    f.createTemplate()

	    ## Saves template at new position number
	    positionNumber = f.storeTemplate()
	    print('Finger enrolled successfully!')
	    print('New template position #' + str(positionNumber))

	except Exception as e:
	    print('Operation failed!')
	    print('Exception message: ' + str(e))
	    exit(1)

	    ##insert into database username and positionNumber
	    cur.execute("INSERT INTO userList (id, name) VALUES (int(positionNumber), username);")


app = Flask(__name__)


@app.route("/")
def homePage():
    return render_template('log.html', result='14:09')

@app.route("/administration", methods = ['POST', 'GET'])
def adminPage():
	templateList = []
	if request.method == 'POST':
	    username = request.form.getlist('name')
	    enrollFinger(username)
	cur.execute("SELECT * FROM userList")
	for row in cur.fetchall() :
		templateList.append([row[0], row[1]])
	return render_template('administration.html', result='14:09', templateList = templateList)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
