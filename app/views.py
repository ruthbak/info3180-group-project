"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from app import app, db
from flask import render_template, request, jsonify, send_file, session, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from app.forms import RegistrationForm, LoginForm, ProfileForm
from app.models import User
from functools import wraps
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime, jwt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


###
# Routing for your application.
###

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/register', methods=['POST'])
def register():
    form= RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        email = form.email.data

        errors = []
        if db.session.execute(db.select(User).filter_by(email=email)).scalar() is not None:
            errors.append("Email already registered")
            flash("Email already registered. Please use a different email.")

        username = form.username.data
        if db.session.execute(db.select(User).filter_by(username=username)).scalar() is not None:
            errors.append("Username already taken")
            flash("Username already taken. Please choose a different username.")

        if errors:
            return jsonify(errors=errors), 400
        
        new_user = User(email=form.email.data, username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, dob=form.dob.data, gender=form.gender.data, lookingfor=form.lookingfor.data, password=hashed_password, joined_at=datetime.datetime.utcnow(), last_seen=datetime.datetime.utcnow())
        db.session.add(new_user)
        db.session.commit()

        return jsonify(message="Successfully created user account."), 201
    else:
        return jsonify(errors=form_errors(form)), redirect(url_for('register')), 400
    
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar()
        if user and check_password_hash(user.password, form.password.data):
            token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")
            return jsonify(token=token), 200
        else:
            return jsonify(message="Invalid email or password"), 401
    return render_template('login.html', form=form)
    
@app.route('/api/v1/auth/logout', methods=['POST'])
@login_required
@token_required
def logout(current_user):
    logout_user()
    return jsonify(message="Successfully logged out"), 200

@app.route('/api/v1/profile', methods=['POST'])
@login_required
@token_required
def profile(current_user):
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.lastname = form.lastname.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.age = form.age.data
        current_user.interests = form.interests.data

        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(filepath)
            current_user.photo = filename

        db.session.commit()
        return jsonify(message="Profile updated successfully"), 200
    else:
        return jsonify(errors=form_errors(form)), 400
    
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'dob': user.dob.isoformat(),
            'gender': user.gender,
            'lookingfor': user.lookingfor,
            'bio': user.bio,
            'location': user.location,
            'age': user.age,
            'photo': user.photo
        }
        output.append(user_data)
    return jsonify(users=output), 200


###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return jsonify(message="Page not found"), 404