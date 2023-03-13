from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mysqldb import MySQL


# Creating flask instance
def create_app():
    app = Flask(__name__)

    # Adding Database
    # db = mysql.connector.connect(
    #     host = 'localhost',
    #     user = 'root',
    #     password = 'asdf1234'
    #     )
    
    # mycursor = db.cursor()
    app.config['SECRET_KEY'] = "PERPSPOT"
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DATABASE'] = 'perpspot_db'

    # mysql = MySQL(app)

    # cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM users")
    # data = cur.fetchall()
    # cur.close()

    # print("Data from db id: " + data)



    # importing blueprints
    from .views import views
    from .auth import auth

    # registering blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app