from flask import Blueprint, render_template, redirect, session, url_for

views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html')


@views.route('/submit-tip')
def submit_tip():
    return render_template('submit-tip.html')


@views.route('/submit-success')
def submit_success():
    return render_template('submit-success.html')


@views.route('/dashboard')
def dashboard():
    if session['logged'] is False:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@views.route('/register-criminal')
def register():
    return render_template('register-criminal.html')


@views.route('/photo-matching')
def matching():
    return render_template('photo-matching.html')


@views.route('/video-surveillance')
def surveillance():
    return render_template('video-surveillance.html')


@views.route('/view-info')
def view():
    return render_template('view-info.html')
