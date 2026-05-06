"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import math
from app import app, db
from flask import request, jsonify, send_file, session, flash, send_from_directory
from werkzeug.utils import secure_filename
from app.forms import RegistrationForm, LoginForm, ProfileForm
from app.models import *
from functools import wraps
from flask_wtf.csrf import CSRFProtect, CSRFError, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime, jwt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import date


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
            _current_user = user.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(_current_user, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/register', methods=['POST'])
def register():
    form = RegistrationForm() 
    if form.validate_on_submit():
        errors = []
        if db.session.execute(db.select(user).filter_by(email=form.email.data)).scalar() is not None:
            errors.append("Email already registered")

        if db.session.execute(db.select(user).filter_by(username=form.username.data)).scalar() is not None:
            errors.append("Username already taken")

        if errors:
            return jsonify(errors=errors), 400

        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        new_user = user(
            email=form.email.data,
            username=form.username.data,
            password_hash=hashed_password,         
            visibility=True,
            joined_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            last_seen=datetime.datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.flush()  

        new_profile = user_profile(
            user_id=new_user.id,
            first_name=form.firstname.data,
            last_name=form.lastname.data,
            dob=form.dob.data,
            gender=form.gender.data,
            description=""
        )
        db.session.add(new_profile)

        new_looking_for = user_looking_for(
            user_id=new_user.id,
            looking_for=form.lookingfor.data
        )
        db.session.add(new_looking_for)

        db.session.commit()
        return jsonify(message="Successfully created user account."), 201
    else:
        e1 = "FORM DATA:", request.form
        e2 = "FORM ERRORS:", form.errors
        return jsonify(errors=form_errors(form), form_data=e1, form_errors=e2), 400

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2

    c = 2 * math.asin(math.sqrt(a))

    return R * c  # distance in km

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        userr = db.session.execute(db.select(user).filter_by(email=form.email.data)).scalar()
        
        if userr and check_password_hash(userr.password_hash, form.password.data):
            token = jwt.encode(
                {
                    'user_id': userr.id,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )
            return jsonify(token=token), 200
        else:
            return jsonify(message="Invalid email or password"), 401
    else:
        return jsonify(errors=form_errors(form)), 400

@app.route('/api/v1/csrf-token', methods=['GET']) 
def get_csrf(): 
    return jsonify({'csrf_token': generate_csrf()}) 

@app.route('/api/v1/auth/logout', methods=['POST'])
@token_required  
def logout(current_user):
    logout_user()  # This will clear the session cookie, but since we're using JWTs, the client should just discard the token
    return jsonify(message="Successfully logged out"), 200


@app.route('/api/v1/profile', methods=['POST'])
@token_required  
def profile(current_user):
    form = ProfileForm()
    if form.validate_on_submit():
    
        existing_profile = db.session.execute(db.select(user_profile).filter_by(user_id=current_user.id)).scalar()

        if existing_profile:
            if form.first_name.data:
                existing_profile.first_name = form.first_name.data
            if form.last_name.data:
                existing_profile.last_name = form.last_name.data
            if form.description.data:
                existing_profile.description = form.description.data
        else:
            # Create a new profile if one doesn't exist yet
            existing_profile = user_profile(
                user_id=current_user.id,
                first_name=form.first_name.data or "",
                last_name=form.last_name.data or "",
                dob=form.dob.data,
                gender=form.gender.data or "",
                description=form.description.data or ""
            )
            db.session.add(existing_profile)

        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(filepath)

            # Check if the user already has a photo
            existing_photo = db.session.execute(db.select(user_photo).filter_by(user_id=current_user.id)).scalar()

            if existing_photo:
                # Delete the old file from disk before overwriting
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], existing_photo.photo_url)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

                # Update the existing record instead of inserting a new one
                existing_photo.photo_url = filename
                existing_photo.uploaded_at = datetime.datetime.utcnow()
            else:
                # No photo yet — create the first one
                new_photo = user_photo(
                    user_id=current_user.id,
                    photo_url=filename,
                    uploaded_at=datetime.datetime.utcnow()
                )
            db.session.add(new_photo)
            db.session.commit()
            return jsonify(message="Profile updated successfully"), 200
        else:
            return jsonify(errors=form_errors(form)), 400


@app.route('/api/v1/users', methods=['GET'])
def get_users():

    def calculate_age(dob):
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    results = (
        db.session.query(
            user.id,
            user.username,
            user.joined_at,
            user_profile.first_name,
            user_profile.last_name,
            user_profile.dob,
            user_profile.gender
        )
        .join(user_profile, user_profile.user_id == user.id)
        .all()
    )

    if not results:
        return jsonify(message="No users found matching the query"), 404

    user_cards = []

    for row in results:
        #  Get "looking_for" values
        looking_for_rows = (
            db.session.execute(
                db.select(user_looking_for).filter_by(user_id=row.id)
            )
            .scalars()
            .all()
        )
        looking_for_list = [lf.looking_for for lf in looking_for_rows][0]

        #  Get photos and convert to list of filenames (or URLs)
        photo_rows = (
            db.session.execute(
                db.select(user_photo).filter_by(user_id=row.id)
            )
            .scalars()
            .all()
        )
        photo_list = [p.filename for p in photo_rows]  # adjust field if needed

        user_cards.append({
            "username": row.username,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "age": calculate_age(row.dob) if row.dob else None,
            "gender": row.gender,
            "looking_for": looking_for_list,
            "photo": photo_list,
            "joined_at": row.joined_at.strftime('%Y-%m-%d') if row.joined_at else None
        })

    return jsonify(users=user_cards), 200


@app.route('/api/v1/users/<int:id>', methods=['GET'])
def get_user(id):
    userr = db.session.execute(db.select(user).filter_by(id=id)).scalar()
    if not userr:
        return jsonify(message="User not found"), 404
    return jsonify(user={
        'username':   userr.username,
        'email':      userr.email,
        'visibility': userr.visibility,
        'joined_at':  userr.joined_at,
        'updated_at': userr.updated_at,
        'last_seen':  userr.last_seen
    }), 200


@app.route('/api/v1/profile/<int:id>', methods=['GET'])
def get_profile(id):
    profile = db.session.execute(db.select(user_profile).filter_by(user_id=id)).scalar()
    if not profile:
        return jsonify(message="Profile not found"), 404
    return jsonify(profile={
        'first_name': profile.first_name, 
        'last_name': profile.last_name,
        'dob': profile.dob.strftime('%Y-%m-%d') if profile.dob else None,
        'gender': profile.gender,
        'description': profile.description   
    }), 200


@app.route('/api/v1/location', methods=['GET'])
@token_required  
def get_location(current_user):
    locations = db.session.execute(db.select(user_location).filter_by(user_id=current_user.id)).scalars().all()

    if not locations:
        return jsonify(message="No location found"), 404

    location_list = []
    for loc in locations:
        location_list.append({
            'location_name':loc.location_name,
            'latitude':loc.latitude,
            'longitude':loc.longitude
        })
    return jsonify(locations=location_list), 200

@app.route('/api/v1/location', methods=['POST'])
@token_required  
def update_location(current_user):
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    location_name = data.get('location_name', '')

    if latitude is None or longitude is None:
        return jsonify(message="Latitude and longitude are required"), 400

    new_location = user_location(
        user_id=current_user.id,
        location_name=location_name,
        latitude=latitude,
        longitude=longitude
    )
    db.session.add(new_location)
    db.session.commit()
    return jsonify(message="Location updated successfully"), 200


@app.route('/api/v1/search', methods=['GET'])
def search():
    username = request.args.get('username')
    if not username:
        return jsonify(message="Username parameter is required"), 400

    def calculate_age(dob):
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    result = (
        db.session.query(
            user.id,
            user.username,
            user.joined_at,
            user_profile.first_name,
            user_profile.last_name,
            user_profile.dob,
            user_profile.gender,
            user_location.location_name,
            user_preferences.min_age,
            user_preferences.max_age,
            user_preferences.gender_preference,
            user_preferences.max_distance,
        )
        .join(user_profile,user_profile.user_id==user.id)
        .join(user_location,user_location.user_id==user.id)
        .join(user_preferences,user_preferences.user_id==user.id)
        .filter(user.username == username)   # exact match, case-sensitive
        .first()
    )

    if not result:
        return jsonify(message="User not found"), 404

    # Fetch looking_for list for this user
    looking_for_rows = db.session.execute(db.select(user_looking_for).filter_by(user_id=result.id)).scalars().all()
    looking_for_list = [lf.looking_for for lf in looking_for_rows]

    # Fetch photo for this user
    photo = db.session.execute(db.select(user_photo).filter_by(user_id=result.id)).scalars()

    user_card = {
        "username":result.username,
        "first_name":result.first_name,
        "last_name":result.last_name,
        "age":calculate_age(result.dob) if result.dob else None,
        "gender":result.gender,
        "location":result.location_name,
        "preferences":{
            "min_age":result.min_age,
            "max_age":result.max_age,
            "gender_preference":result.gender_preference,
            "max_distance":result.max_distance
        },
        "looking_for":looking_for_list,
        "photos":photo,
        "joined_at":result.joined_at.strftime('%Y-%m-%d')
    }

    return jsonify(user=user_card), 200

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