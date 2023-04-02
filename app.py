from flask import Flask,render_template, Response, session, jsonify, request, redirect, g, url_for, flash
from datetime import datetime
from views import views
from auth import auth
from flask_mysqldb import MySQL
import mysql.connector
from camera import VideoCamera
import random
import requests
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
from keras.models import load_model






app = Flask(__name__)

# video_camera = None
# global_frame = None

# @app.route('/record_status', methods=['POST'])
# def record_status():
#     global video_camera 
#     if video_camera == None:
#         video_camera = VideoCamera()

#     json = request.get_json()

#     status = json['status']

#     if status == "true":
#         video_camera.start_record()
#         return jsonify(result="started")
#     else:
#         video_camera.stop_record()
#         return jsonify(result="stopped")

# def video_stream():
#     global video_camera 
#     global global_frame

#     if video_camera == None:
#         video_camera = VideoCamera()
            
#     while True:
#         frame = video_camera.get_frame()

#         if frame != None:
#             global_frame = frame
#             yield (b'--frame\r\n'
#                         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         else:
#             yield (b'--frame\r\n'
#                             b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

# @app.route('/video_viewer')
# def video_viewer():
#     return Response(video_stream(), 
#                     mimetype='multipart/x-mixed-replace; boundary=frame')





# def gen_frames():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             # Encode the frame in JPEG format
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             # Yield the frame to be displayed on the webpage
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# def gen_frames():
#     while True:
#         data = yield
#         # Convert the incoming data to an OpenCV frame
#         nparr = np.frombuffer(data, np.uint8)
#         frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         captured_log = []

#         # Process the frame to perform face recognition and attendance
#         if extract_faces(frame)!=():
#             (x,y,w,h) = extract_faces(frame)[0]
#             cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
#             face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
#             identified_person = identify_face(face.reshape(1,-1))[0]
#             captured_log.append(capture_log(identified_person))
#             cv2.putText(frame,f'{identified_person}',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)

#         # Encode the processed frame in JPEG format
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         # Yield the frame to be displayed on the webpage
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#### Initializing VideoCapture object to access WebCam
camera = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0)


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success or frame is None:
            continue  # skip to the next iteration if the frame is empty or invalid
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()
            # Pass the frame to the extract_faces() function
            faces = extract_faces(frame)
            # Draw bounding boxes around the detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # Convert the frame to RGB format and yield it to be displayed on the webpage
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')


@app.route('/video_feed')
def video_feed():
    # Return the response generated by the gen_frames() function
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame') 



#### If these directories don't exist, create them
if not os.path.isdir('Perps'):
    os.makedirs('Perps')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')

# **************** MACHINE LEARNING ASPECT FOR FACIAL RECOGNITION ***************


face_detector = cv2.CascadeClassifier(os.path.join('static', 'haarcascade_frontalface_default.xml'))

#### Extract the face from an image using the CNN model
def extract_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_points = face_detector.detectMultiScale(gray, 1.3, 5)
    return face_points

#### A function which trains the CNN model on all the faces available in faces folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (200, 200))
            faces.append(resized_face)
            labels.append(user)
    faces = np.array(faces)
    labels = np.array(labels)

    # One-hot encode the labels
    label_encoder = LabelEncoder()
    labels = to_categorical(label_encoder.fit_transform(labels))

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(faces, labels, test_size=0.2)

    # Normalize the pixel values of the images
    X_train = X_train.astype('float32') / 255.0
    X_test = X_test.astype('float32') / 255.0

    # Define the CNN architecture
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(200, 200, 3)))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(len(label_encoder.classes_), activation='softmax'))

    # Compile the model
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

    # Save the model
    model.save('static/face_recognition_model.h5')





def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.h5')
    return model.predict(facearray)



# def face_recognition():
#     url = 'http://localhost:5000/video_feed'  # Replace with the URL of your video feed

#     for frame in requests.get(url, stream=True).iter_content(chunk_size=1024):
#         if not frame:
#             break

#         frame = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), cv2.IMREAD_COLOR)

#         if extract_faces(frame)!=():
#             (x,y,w,h) = extract_faces(frame)[0]
#             cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
#             face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
#             identified_person = identify_face(face.reshape(1,-1))[0]
#             capture_log(identified_person)

#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def face_recognition():
    # Load the trained face recognition model
    model = load_model("face_recognition_model.h5")

    # Load the Haar Cascade classifier for face detection
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Start the video capture
    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame using the Haar Cascade classifier
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        # Loop over each detected face and predict the label using the trained model
        for (x, y, w, h) in faces:
            # Extract the face ROI from the grayscale frame
            face_roi = gray[y:y+h, x:x+w]

            # Resize the face ROI to match the input shape of the model
            face_roi = cv2.resize(face_roi, (224, 224))

            # Normalize the pixel values to be between 0 and 1
            face_roi = face_roi / 255.0

            # Add a batch dimension to the face ROI and make a prediction using the model
            face_roi = np.expand_dims(face_roi, axis=0)
            predictions = model.predict(face_roi)

            # Get the predicted label and confidence score
            label = np.argmax(predictions)
            confidence = predictions[0][label]

            # Draw a rectangle around the detected face and label it with the predicted label and confidence score
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        # Exit the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close all windows
    video_capture.release()
    cv2.destroyAllWindows()

def capture_log(name):
    def random_location(cities):
        cities = ["Tema", "Madina", "Ashongman", "Obuasi", "Dzorwulu", "Kasoa", "Ho", "Koforidua", "Mampong", "Teshie"]
        return random.choice(cities)
    firstName = name.split('_')[0]
    lastName = name.split('_')[1]
    current_time = datetime.now()
    location = random_location()

    sql = "INSERT INTO identified (date, first_name, last_name, location) VALUES (%s, %s, %s, %s)"
    val = (current_time, firstName, lastName, location)
    cursor.execute(sql, val)
    cursor.close()



# Establish a connection to the MySQL database
mysql_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="perpspot_db"
)

# create a cursor
cursor = mysql_connection.cursor()

# Check if the connection is successful
if mysql_connection.is_connected():
    print("Connected to MySQL database")

# Specifying the secret key for the app

app.secret_key = "PerpSpot-Final-Year" 

# Creating flask instance
# registering blueprints
app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')



# **************************** ROUTING FUNCTIONS ******************************

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


    # Validating Phone
    elif not re.match(r'^\d{9}$', phone):
        flash('Please enter the last nine(9) digits of your phone number.')
        return redirect(url_for('submit_tip'))


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


        perpimagefolder = 'static/faces/'+first_name+'_'+last_name
        if not os.path.isdir(perpimagefolder):
            os.makedirs(perpimagefolder)
        cap = cv2.VideoCapture(0)
        i = 0
        while 1:
            _,frame = cap.read()
            faces = extract_faces(frame)
            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
                cv2.putText(frame,f'Images Captured: {i}/50',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
                if i == 0:
                    # Get the path of the first image captured
                    perpimagepath = perpimagefolder+'/'+first_name+'_'+last_name+'_0.jpg'

                    # Insert data into database table with the image path
                    cursor = mysql_connection.cursor()
                    sql = "INSERT INTO criminals (first_name, last_name, birth_date, nationality, gender, phone_number, height, weight, crime_category, crime_type, date_of_offense, location_of_offense, perp_image_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val = (first_name, last_name, birth_date, nationality, gender, phone_number, height, weight, crime_category, crime_type, date_of_offense, location_of_offense, perpimagepath)
                    cursor.execute(sql, val)
                elif i < 50:
                    name = first_name +'_'+last_name+'_'+str(i)+'.jpg'
                    cv2.imwrite(perpimagepath,frame[y:y+h,x:x+w])
                i += 1
            if i >= 50:
                break
            cv2.imshow('Adding new Perp',frame)
            if cv2.waitKey(1)==27:
                break
        cap.release()
        cv2.destroyAllWindows()
        print('Training Model')
        train_model()




        # check if the query was successful
        if cursor.rowcount == 1:
            flash('Perp Registered Successfully')
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


# ***************** VIDEO SURVEILLANCE *******************
@app.route('/video-surveillance')
def surveillance():

    # ret = True
    # while ret:
    #     ret,frame = camera.read()
    # if extract_faces(frame)!=():
    #     (x,y,w,h) = extract_faces(frame)[0]
    #     cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
    #     face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
    #     identified_person = identify_face(face.reshape(1,-1))[0]

    #     captured_log = capture_log(identified_person)

    # vid_surveillance()

    # Start the generator function and pass the first frame of the video stream
    # gen = gen_frames()
    # next(gen)
    # gen.send(camera.read()[1])


    return render_template('video-surveillance.html')

# ***************   VIEWING SUBMITTED TIPS ******************
@app.route('/view-tips')
def view_tips():
    cursor.execute("SELECT * FROM tips")
    data = cursor.fetchall()
    cursor.close()
    return render_template('view-tips.html', tips=data)


# ******************    VIEWING CRIMINAL INFO ***********************
@app.route('/view-info')
def view():
    return render_template('view-info.html')

def get_staffid(staffid):

    cursor.execute("SELECT id FROM users WHERE username=%s", (staffid))
    row = cursor.fetchone()
    mysql_connection.close()

    if row:
        return row[0]
    else:
        return None
    

@app.route('/manage-users')
def manage_users():
    return render_template()


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
            # record_login_time(staffid, login_time)


            return redirect(url_for('register'))
        else:
            # If the login is unsuccessful, redirect back to the login page with an error message
            if check_staffid == False:
                # error_message = "Invalid Staff ID"
                flash("Invalid Staff ID")
            else:
                return redirect(url_for('register'))
            

            return redirect(url_for('login'))
        
# **************** Logout Route *****************************
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

# *************** Loading Data From the database *****************
# @app.route('/loadData', methods = ['GET', 'POST'])
# def loadData():
 
#     cursor.execute("select a.accs_id, a.accs_prsn, b.prs_name, b.prs_skill, date_format(a.accs_added, '%H:%i:%s') "
#                      "  from accs_hist a "
#                      "  left join prs_mstr b on a.accs_prsn = b.prs_nbr "
#                      " where a.accs_date = curdate() "
#                      " order by 1 desc")
#     data = cursor.fetchall()
 
#     return jsonify(response = data)



# ***************************** END OF ROUTING FUNCTIONS *********************************** 


        

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
            cursor.close()
            return "Login successful"
        
        else:
            # If the password is incorrect, return an error message
            return "Incorrect password"
    else:
        # If no row was found for the given staffid, return an error message

        return render_template("login.html")



    # cursor.execute("SELECT * FROM criminals WHERE first_name=%s AND last_name=%s", (firstName, lastName))

    # # fetch the row data if it exists
    # row = cursor.fetchone()

    # if row:
    #     # save the row data in a variable
    #     (id, first_name, last_name, email, phone) = row

# ******** Recording Login Time ***********
def record_login_time(staffid, login_time):
    # Insert a new row into the login_logout table
    sql = "INSERT INTO login_logout (staffid, login_time) VALUES (%s, %s)"
    val = (staffid, login_time)
    cursor.execute(sql, val)
    mysql_connection.commit()

# ******** Recording Logout Time **************
def record_logout_time(staffid, logout_time):
    print("Record logout time function called with staffid: {}, logout_time: {}".format(staffid, logout_time))
    sql = "UPDATE login_logout SET logout_time = %s WHERE staffid = %s AND login_time = (SELECT MAX(login_time) FROM login_logout WHERE staffid = %s)"
    val = (logout_time, staffid, staffid)
    cursor.execute(sql, val)
    mysql_connection.commit()
    cursor.close()
    print("Logout time recorded successfully for staffid: {}".format(staffid))
    


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
