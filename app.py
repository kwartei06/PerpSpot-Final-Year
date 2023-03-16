from flask import Flask,render_template, Response, session, jsonify, request, redirect, url_for, flash
from datetime import datetime
from views import views
from auth import auth
from flask_mysqldb import MySQL
import mysql.connector
from camera import VideoCamera
import bcrypt

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






# # Database Configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'perpspot_db'
 
# mysql = MySQL(app)


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

#Home page route
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/submit-tip')
def submit_tip():
    return render_template('submit-tip.html')


@app.route('/submit-success')
def submit_success():
    return render_template('submit-success.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register-criminal')
def register():
    return render_template('register-criminal.html')

@app.route('/photo-matching')
def matching():
    return render_template('photo-matching.html')

@app.route('/video-surveillance')
def surveillance():
    return render_template('video-surveillance.html')

@app.route('/view-info')
def view():
    return render_template('view-info.html')

#Login Route
@app.route('/login', methods = ['POST', 'GET'])
def login():
    # error_message = ""
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        staffid = request.form['staffid']
        password = request.form['password']
        result = validate_login(staffid, password)
        check_staffid = validate_staffid(staffid)

        if result == "Login successful":
            # If the login is successful, redirect to the main dashboard
            return redirect(url_for('dashboard'))
        else:
            # If the login is unsuccessful, redirect back to the login page with an error message
            if check_staffid == False:
                # error_message = "Invalid Staff ID"
                flash("Invalid Staff ID")
            else:
                return redirect(url_for('dashboard'))
            

            return redirect(url_for('login'))
        

# Validation Functions
# StaffID validation using Regular Expression
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

# Login Validation
def validate_login(staffid, password):

    mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="perpspot_db"
    )

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


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
