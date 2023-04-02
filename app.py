from flask import Flask,render_template, Response, session, jsonify, request, redirect, g, url_for, flash
from datetime import datetime
from views import views
from auth import auth
from flask_mysqldb import MySQL
import mysql.connector
from camera import VideoCamera
import bcrypt
import re
import os
import cv2
import numpy as np
import joblib
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical

app = Flask(__name__)

video_camera = None
global_frame = None

@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera 
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")

def video_stream():
    global video_camera 
    global global_frame

    if video_camera == None:
        video_camera = VideoCamera()
            
    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')








# Establish a connection to the MySQL database
mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="perpspot_db"
)


# Check if the connection is successful
if mysql_connection.is_connected():
    print("Connected to MySQL database")

# #Creating a connection cursor
# cursor = mysql_connection.cursor()
 
# # #Executing SQL Statements
# # cursor.execute(''' INSERT INTO users VALUES(v1,v2...) ''')
# # #Saving the Actions performed on the DB
# # mysql.connection.commit()
 
# #Closing the cursor
# cursor.close()


# Specifying the secret key for the app

app.secret_key = "PerpSpot-Final-Year" 

# Creating flask instance
# registering blueprints
app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')


# **************** WEB PAGES ******************************

# ********* Home page route *************
@app.route('/')
def home():
    return render_template('home.html')

# ********* Submit Tip page **************
@app.route('/submit-tip', methods=['POST'])
def submit_tip():
    full_name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    category = request.form['category']
    message = request.form['message']

    # Validating Full Name
    if not re.match(r'^[A-Z][a-z]+\s[A-Z][a-z]+$', full_name):
        flash('Full Name should contain at least two separate words, and each word should start with a capital letter.')
        return redirect(url_for('submit_tip'))

    # # Validating Email
    # elif not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
    #     flash('Please enter a valid email address.')
    #     return redirect(url_for('submit_tip'))

    # Validating Phone
    elif not re.match(r'^\d{9}$', phone):
        flash('Please enter the last nine(9) digits of your phone number.')
        return redirect(url_for('submit_tip'))


    # create a cursor
    cursor = mysql_connection.cursor()

    # insert the data into the database
    sql = "INSERT INTO tips (full_name, email, phone, category, message) VALUES (%s, %s, %s, %s, %s)"
    val = (full_name, email, phone, category, message)
    cursor.execute(sql, val)

    # check if the query was successful
    if cursor.rowcount == 1:
        print('Submission success!')
        mysql_connection.commit()
        cursor.close()
        return redirect(url_for('submit_success'))
    else:
        print('Submission failed!')
        mysql_connection.rollback()
        cursor.close()

    return render_template('submit-tip.html')


@app.route('/submit-success')
def submit_success():
    return render_template('submit-success.html')



@app.route('/register-criminal', methods=['POST'])
def register():
    if not 'logged_in' in session and session['logged_in']:
        return redirect(url_for('login'))
    else:
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = request.form['birth_date']
        nationality = request.form['nationality']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        height = request.form['height']
        weight = request.form['weight']
        crime_category = request.form['crimeCategory']
        crime_type = request.form['crimeType']
        date_of_offense = request.form['date_of_offense']
        location_of_offense = request.form['location_of_offense']

        # Validate form data
        # ...

        # Insert data into database table
        cursor = mysql_connection.cursor()
        sql = "INSERT INTO criminals (first_name, last_name, birth_date, nationality, gender, phone_number, height, weight, crime_category, crime_type, date_of_offense, location_of_offense) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (first_name, last_name, birth_date, nationality, gender, phone_number, height, weight, crime_category, crime_type, date_of_offense, location_of_offense)
        cursor.execute(sql, val) 

        # check if the query was successful
        if cursor.rowcount == 1:
            flash('Registration success!')
            mysql_connection.commit()
            cursor.close()
            return redirect(url_for('register'))
        else:
            print('Registration failed!')
            mysql_connection.rollback()
            cursor.close()
        return render_template(url_for('register'))

@app.route('/photo-matching')
def matching():
    return render_template('photo-matching.html')

@app.route('/video-surveillance')
def surveillance():
    return render_template('video-surveillance.html')

# ***************   VIEWING SUBMITTED TIPS ******************
@app.route('/view-tips')
def view_tips():
    cursor = mysql_connection.cursor()
    cursor.execute("SELECT * FROM tips")
    data = cursor.fetchall()
    cursor.close()
    return render_template('view-tips.html', tips=data)


# ******************    VIEWING CRIMINAL INFO ***********************
@app.route('/view-info')
def view():
    return render_template('view-info.html')

def get_staffid(staffid):

    cursor = mysql_connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username=%s", (staffid))
    row = cursor.fetchone()
    mysql_connection.close()

    if row:
        return row[0]
    else:
        return None

#   ********************** LOGIN ROUTE ***********************
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        staffid = request.form['staffid']
        password = request.form['password']
        result = validate_login(staffid, password)
        check_staffid = validate_staffid(staffid)


        if result == "Login successful":
            # If the login is successful, create a session and redirect to the dashboard
            # session["loggedin"] = True
            # session["staffid"] = result["staffid"]

            session['loggedin'] = True
            session['staffid'] = staffid

            # Record login time in the database
            login_time = datetime.now()
            record_login_time(staffid, login_time)


            return redirect(url_for('register'))
        else:
            # If the login is unsuccessful, redirect back to the login page with an error message
            if check_staffid == False:
                # error_message = "Invalid Staff ID"
                flash("Invalid Staff ID")
            else:
                return redirect(url_for('register'))
            

            return redirect(url_for('login'))
        

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    # Get the staff ID from the session
    staffid = session.get('staffid')

    # Record logout time in the database
    logout_time = datetime.now()
    record_logout_time(staffid, logout_time)

    # Clear the session
    session.pop("staffid", None)

    # return render_template(url_for('login'))
    return render_template('home.html')



        

# **************************** VALIDATION FUNCTIONS ******************************
# **************** StaffID validation using Regular Expression ********************
def validate_staffid(staffid):
    # checking if it is exactly 10 characters long
    if len(staffid) != 10:
        return False
    # checking if it starts with "GPPSA"
    if not staffid.startswith("GPPSA"):
        return False
    # checking if the last 5 characters are all digits.
    if not staffid[5:].isdigit() or len(staffid[5:]) != 5:
        return False
    return True

# ******************  Login Validation *******************
def validate_login(staffid, password):
    # StaffID input validation        
    if not validate_staffid(staffid):
        return render_template("login.html")

    # Create a cursor object
    cursor = mysql_connection.cursor()

    # Execute a SELECT statement to retrieve the hashed password for the given staffid
    cursor.execute('''SELECT password FROM users WHERE staff_id = %s''', (staffid,))
    result = cursor.fetchone()
    print("Result: ", result)

    if result:
        # If a row was found for the given staffid, verify the password
        # hashed_password = result[0].encode('utf-8')
        # print("Hashed password: ", hashed_password)
        # if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        #     # If the password is correct, grant access to the system
        #     return "Login successful"
        user_password = result[0]
        print("Hashed password: ", user_password)
        if (password == user_password):
            # If the password is correct, grant access to the system
            return "Login successful"
        else:
            # If the password is incorrect, return an error message
            return "Incorrect password"
    else:
        # If no row was found for the given staffid, return an error message

        return render_template("login.html")


# ******** Recording Login Time ***********
def record_login_time(staffid, login_time):
    cursor = mysql_connection.cursor()
    # Insert a new row into the login_logout table
    sql = "INSERT INTO login_logout (staffid, login_time) VALUES (%s, %s)"
    val = (staffid, login_time)
    cursor.execute(sql, val)
    mysql_connection.commit()

# ******** Recording Logout Time **************
def record_logout_time(staffid, logout_time):
    cursor = mysql_connection.cursor()
    print("Record logout time function called with staffid: {}, logout_time: {}".format(staffid, logout_time))
    sql = "UPDATE login_logout SET logout_time = %s WHERE staffid = %s AND login_time = (SELECT MAX(login_time) FROM login_logout WHERE staffid = %s)"
    val = (logout_time, staffid, staffid)
    cursor.execute(sql, val)
    mysql_connection.commit()
    print("Logout time recorded successfully for staffid: {}".format(staffid))
    


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
