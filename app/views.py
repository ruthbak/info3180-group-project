"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from app import app, db
from flask import request, jsonify, send_file, session, flash, send_from_directory, url_for, redirect
from werkzeug.utils import secure_filename
from app.forms import RegistrationForm, LoginForm, ProfileForm
from app.models import *
from functools import wraps
from flask_wtf.csrf import CSRFProtect, CSRFError
from werkzeug.security import generate_password_hash, check_password_hash
import os, datetime, jwt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import date
import math


###
# Routing for your application.
###

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Assuming Bearer token
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            _current_user = users.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(_current_user, *args, **kwargs)
    return decorated


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        errors = []

        if db.session.execute(db.select(users).filter_by(email=form.email.data)).scalar() is not None:
            errors.append("Email already registered")

        if db.session.execute(db.select(users).filter_by(username=form.username.data)).scalar() is not None:
            errors.append("Username already taken")

        if errors:
            return jsonify(errors=errors), 400

        hashed_password = generate_password_hash(form.password.data, method='sha256')

        new_user = users(
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
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            gender=form.gender.data,
            description="",
            photo=url_for('static', filename='default.png')
        )
        db.session.add(new_profile)

        new_looking_for = user_looking_for(
            user_id=new_user.id,
            looking_for=form.looking_for.data
        )
        db.session.add(new_looking_for)

        db.session.commit()
        return jsonify(message="Successfully created user account."), 201
    else:
        return jsonify(errors=form_errors(form)), 400


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(users).filter_by(email=form.email.data)).scalar()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            token = jwt.encode(
                {
                    'user_id': user.id,
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
def users():
    query = request.args.get('query')
    if not query:
        return jsonify(message="Query parameter is required"), 400
    
    calculate_age = lambda dob: date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day)) if dob else None

    results = (
        db.session.query(
            users.id,
            users.username,
            users.joined_at,
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
        .join(user_profile,user_profile.user_id==users.id)
        .join(user_location,user_location.user_id==users.id)
        .join(user_preferences,user_preferences.user_id==users.id)
        .filter(users.username.ilike(f'%{query}%'))
        .all()
    )

    if not results:
        return jsonify(message="No users found matching the query"), 404

    user_cards = []
    for row in results:
        looking_for_rows = db.session.execute(db.select(user_looking_for).filter_by(user_id=row.id)).scalars().all()
        looking_for_list = [lf.looking_for for lf in looking_for_rows]

        photo = db.session.execute(db.select(user_photo).filter_by(user_id=row.id)).scalars()

        user_cards.append({
            "username":row.username,
            "first_name":row.first_name,
            "last_name":row.last_name,
            "age":calculate_age(row.dob) if row.dob else None,
            "gender":row.gender,
            "location":row.location_name,
            "preferences":{
                "min_age":row.min_age,
                "max_age":row.max_age,
                "gender_preference":row.gender_preference,
                "max_distance":row.max_distance
            },
            "looking_for":looking_for_list,  
            "photo":photo,          
            "joined_at":row.joined_at.strftime('%Y-%m-%d')
        })

    return jsonify(users=user_cards), 200


@app.route('/api/v1/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.execute(db.select(users).filter_by(id=id)).scalar()
    if not user:
        return jsonify(message="User not found"), 404
    return jsonify(user={
        'username':   user.username,
        'email':      user.email,
        'visibility': user.visibility,
        'joined_at':  user.joined_at,
        'updated_at': user.updated_at,
        'last_seen':  user.last_seen
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

    calculate_age = lambda dob: date.today().year - dob.year - ((date.today().month, date.today().day) < (dob.month, dob.day)) if dob else None

    result = (
        db.session.query(
            users.id,
            users.username,
            users.joined_at,
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
        .join(user_profile,user_profile.user_id==users.id)
        .join(user_location,user_location.user_id==users.id)
        .join(user_preferences,user_preferences.user_id==users.id)
        .filter(users.username == username)   # exact match, case-sensitive
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

def haversine(lat1, lon1, lat2, lon2):
    """Returns distance in kilometres between two coordinates."""
    R = 6371  # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


@app.route('/api/v1/matches', methods=['GET'])
@token_required
def get_matches(current_user):

    #Fetch current user's data (all in 4 focused queries)

    cu_profile = db.session.execute(db.select(user_profile).filter_by(user_id=current_user.id)).scalar()

    cu_prefs = db.session.execute(db.select(user_preferences).filter_by(user_id=current_user.id)).scalar()

    cu_location = db.session.execute(db.select(user_location).filter_by(user_id=current_user.id)).scalar()

    cu_looking_for = {
        row.looking_for for row in db.session.execute(db.select(user_looking_for).filter_by(user_id=current_user.id)).scalars().all()
    }

    cu_hobbies = {
        row.hobby_id for row in db.session.execute(db.select(user_hobbies).filter_by(user_id=current_user.id)).scalars().all()
    }

    cu_age = calculate_age(cu_profile.dob) if cu_profile and cu_profile.dob else None

    # Guard condition; can't match without these
    if not cu_profile or not cu_prefs or not cu_location or not cu_age:
        return jsonify(message="Complete your profile, preferences, and location before matching"), 400

    #Fetch all other users with their profile + preferences + location in one join

    candidates = (
        db.session.query(
            users.id,
            users.username,
            user_profile.first_name,
            user_profile.last_name,
            user_profile.dob,
            user_profile.gender,
            user_preferences.min_age,
            user_preferences.max_age,
            user_preferences.gender_preference,
            user_preferences.max_distance,
            user_location.location_name,
            user_location.latitude,
            user_location.longitude,
        )
        .join(user_profile, user_profile.user_id==users.id)
        .join(user_preferences, user_preferences.user_id==users.id)
        .join(user_location, user_location.user_id==users.id)
        .filter(users.id!=current_user.id)
        .all()
    )

    if not candidates:
        return jsonify(matches=[]), 200

    # Collect all candidate user IDs for batch lookups
    candidate_ids = [c.id for c in candidates]

    # Batch fetch looking_for for all candidates — avoids N+1
    all_looking_for = db.session.execute(db.select(user_looking_for).filter(user_looking_for.user_id.in_(candidate_ids))).scalars().all()

    # Batch fetch hobbies for all candidates — avoids N+1
    all_hobbies = db.session.execute(db.select(user_hobbies).filter(user_hobbies.user_id.in_(candidate_ids))).scalars().all()

    # Batch fetch photos for all candidates — avoids N+1
    all_photos = db.session.execute(db.select(user_photo).filter(user_photo.user_id.in_(candidate_ids))).scalars().all()

    # Build lookup dicts keyed by user_id for O(1) access
    looking_for_map = {}   # { user_id: {"dating", "friendship", ...} }
    for lf in all_looking_for:
        looking_for_map.setdefault(lf.user_id, set()).add(lf.looking_for)

    hobbies_map = {} # { user_id: {hobby_id, ...} }
    for h in all_hobbies:
        hobbies_map.setdefault(h.user_id, set()).add(h.hobby_id)

    photos_map = {} # { user_id: photo_url }
    for p in all_photos:
        photos_map[p.user_id] = p.photo_url if p.photo_url else url_for('static', filename='default.png')

    # --- Run matching logic ---

    matches = []
    for c in candidates:
        c_age = calculate_age(c.dob) if c.dob else None
        if not c_age:
            continue

        # 1. Current user's age must fall within candidate's preferred age range
        if not (c.min_age <= cu_age <= c.max_age):
            continue

        # 2. Candidate's age must fall within current user's preferred age range
        if not (cu_prefs.min_age <= c_age <= cu_prefs.max_age):
            continue

        # 3. Gender preference — each must match the other's gender
        if c.gender_preference != cu_profile.gender:
            continue
        if cu_prefs.gender_preference != c.gender:
            continue

        # 4. Distance must be within BOTH users' max_distance
        distance = haversine(
            cu_location.latitude, cu_location.longitude,
            c.latitude, c.longitude
        )
        if distance > cu_prefs.max_distance or distance > c.max_distance:
            continue

        # 5. Looking_for in common
        c_looking_for = looking_for_map.get(c.id, set())
        if not cu_looking_for.intersection(c_looking_for):
            continue

        # 6. At least one hobby in common
        c_hobbies = hobbies_map.get(c.id, set())
        if not cu_hobbies.intersection(c_hobbies):
            continue

        # If all criteria passed — build the user card
        matches.append({
            "user_id": c.id,
            "username": c.username,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "age": c_age,
            "gender":c.gender,
            "location": c.location_name,
            "distance_km": round(distance, 1),
            "looking_for": list(c_looking_for),
            "photo": photos_map.get(c.id) or url_for('static', filename='default.png'),
            "common_looking_for": list(cu_looking_for.intersection(c_looking_for)),
            "common_hobbies": list(cu_hobbies.intersection(c_hobbies))
        })

    # Sort by closest distance first
    matches.sort(key=lambda x: x['distance_km'])

    return jsonify(matches=matches, total=len(matches)), 200

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