"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
import math
from app import app, db
from flask import request, jsonify, send_file, session, flash, send_from_directory, g, url_for
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
        auth_header = request.headers.get('Authorization')

        #  Missing or malformed header
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Token is missing!'}), 401

        token = auth_header.split(' ')[1].strip()

        try:
            # Decode token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])

            # Get user from DB
            current_user = user.query.filter_by(id=data['user_id']).first()

            if not current_user:
                return jsonify({'message': 'User not found'}), 401

            #  Store user in request context
            g.current_user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401

        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

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
            description="",
            photo = url_for('static', filename='default.jpg')
        )
        db.session.add(new_profile)

        new_looking_for = user_looking_for(
            user_id=new_user.id,
            looking_for=form.lookingfor.data
        )
        db.session.add(new_looking_for)

        new_location = user_location(
            user_id=new_user.id,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            location_name=form.location_name.data
        )
        db.session.add(new_location)

        db.session.commit()
        return jsonify(message="Successfully created user account."), 201
    else:

        return jsonify(errors=form_errors(form)), 400

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
            userr.last_seen = datetime.datetime.utcnow()
            db.session.commit()
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
def logout():
    logout_user()  # This will clear the session cookie, but since we're using JWTs, the client should just discard the token
    return jsonify(message="Successfully logged out"), 200


def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

@app.route('/api/v1/users', methods=['GET'])
def get_users():

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
        looking_for_rows = (db.session.execute(db.select(user_looking_for).filter_by(user_id=row.id)).scalars().all())
        looking_for_list = [lf.looking_for for lf in looking_for_rows][0]

        #  Get photos and convert to list of filenames (or URLs)
        photo_rows = ( db.session.execute(db.select(user_photo).filter_by(user_id=row.id)).scalars().all())
        photo_list = [p.photo_url for p in photo_rows]  # adjust field if needed

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


@app.route('/api/v1/user/', methods=['GET'])
@token_required
def get_user():
    userr = g.current_user

    if not userr:
        return jsonify(message="User not found"), 404
    first_name = db.session.execute(db.select(user_profile.first_name).filter_by(user_id=userr.id)).scalar()
    last_name = db.session.execute(db.select(user_profile.last_name).filter_by(user_id=userr.id)).scalar()
    dob = db.session.execute(db.select(user_profile.dob).filter_by(user_id=userr.id)).scalar()
    age = None
    if dob:
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    location = db.session.execute(db.select(user_location.location_name).filter_by(user_id=userr.id)).scalar()
    bio = db.session.execute(db.select(user_profile.description).filter_by(user_id=userr.id)).scalar()
    looking_for = db.session.execute(db.select(user_looking_for.looking_for).filter_by(user_id=userr.id)).scalar()
    return jsonify(user={
        'username': userr.username,
        'first_name': first_name,
        'last_name':  last_name,
        'age': age,
        'location': location,
        'bio': bio,
        'looking_for': looking_for
    }), 200


@app.route('/api/v1/profile', methods=['POST'])
@token_required
def profile():
    current_user = g.current_user  

    form = ProfileForm()
    if form.validate_on_submit():

        existing_profile = db.session.execute(
            db.select(user_profile).filter_by(user_id=current_user.id)
        ).scalar()

        if existing_profile:
            # Update only fields that were submitted
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
            filename  = secure_filename(form.photo.data.filename)
            filepath  = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(filepath)

            existing_photo = db.session.execute(
                db.select(user_photo).filter_by(user_id=current_user.id)
            ).scalar()

            if existing_photo:
                # Delete old file from disk then overwrite the record
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], existing_photo.photo_url)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
                existing_photo.photo_url   = filename
                existing_photo.uploaded_at = datetime.datetime.utcnow()
            else:
                new_photo = user_photo(
                    user_id=current_user.id,
                    photo_url=filename,
                    uploaded_at=datetime.datetime.utcnow()
                )
                db.session.add(new_photo)

        db.session.commit()
        return jsonify(message="Profile updated successfully"), 200

    return jsonify(errors=form_errors(form)), 400


@app.route('/api/v1/profile/<string:username>', methods=['GET'])
@token_required
def get_profile(username):
    # Resolve the target user by username
    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    profile = db.session.execute(db.select(user_profile).filter_by(user_id=target_user.id)).scalar()
    if not profile:
        return jsonify(message="Profile not found"), 404
 
    photo = db.session.execute(db.select(user_photo).filter_by(user_id=target_user.id)).scalar()
 
    looking_for_rows = db.session.execute(db.select(user_looking_for).filter_by(user_id=target_user.id)).scalars().all()
 
    location = db.session.execute(db.select(user_location).filter_by(user_id=target_user.id)).scalar()

    if target_user.visibility == False and target_user.id != db.session.execute(db.select(matches).filter_by(id=g.current_user.id)).scalar().id:
        profile=profile(
        'username': target_user.username,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'age': calculate_age(profile.dob) if profile.dob else None,
        'gender': profile.gender,
        'description': profile.description,
        'photo': photo.photo_url if photo else None
        )
        return jsonify(profile=profile, message="User profile is private"), 403
    else:
        return jsonify(profile={
            'username': target_user.username,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'age': calculate_age(profile.dob) if profile.dob else None,
            'gender': profile.gender,
            'description': profile.description,
            'location': location.location_name if location else None,
            'looking_for': [lf.looking_for for lf in looking_for_rows][0] if looking_for_rows else None,
            'hobbies': [h.hobby_id for h in db.session.execute(db.select(user_hobbies).filter_by(user_id=target_user.id)).scalars().all()],
            'photo': photo.photo_url if photo else None
        }), 200


@app.route('/api/v1/location', methods=['GET'])
@token_required  
def get_location():
    locations = db.session.execute(db.select(user_location).filter_by(user_id=g.current_user.id)).scalars().all()

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


@app.route('/api/v1/search', methods=['GET'])
def search():
    username = request.args.get('username')
    if not username:
        return jsonify(message="Username parameter is required"), 400
    
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

@app.route('/api/v1/likes', methods=['GET'])
@token_required
def get_likes():
    current_user = g.current_user
 
    # Return every profile the current user has liked that has not yet become a match
    rows = (
        db.session.query(
            user.id,
            user.username,
            user_profile.first_name,
            user_profile.last_name,
            user_profile.dob,
            user_profile.gender,
            user_photo.photo_url,
            like.created_at.label('liked_at')
        )
        .join(like, like.liked_user_id == user.id)
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(like.user_id == current_user.id)
        .order_by(like.created_at.desc())
        .all()
    )
 
    likes_list = [
        {
            "username": row.username,
            "first_name":row.first_name,
            "last_name": row.last_name,
            "age": calculate_age(row.dob) if row.dob else None,
            "gender": row.gender,
            "photo": row.photo_url or None,
            "liked_at": row.liked_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        for row in rows
    ]
 
    return jsonify(likes=likes_list, total=len(likes_list)), 200
 

@app.route('/api/v1/messageable', methods=['GET'])
@token_required
def get_messageable():
    current_user = g.current_user
 
    # Single join — get matched users with their profile and photo
    matched_users = (
        db.session.query(
            user.id,
            user.username,
            user_profile.first_name,
            user_profile.last_name,
            user_photo.photo_url,
            matches.id.label('match_id'),
            matches.matched_at
        )
        .join(matches, db.or_(
            db.and_(matches.user1_id == current_user.id, matches.user2_id == user.id),
            db.and_(matches.user2_id == current_user.id, matches.user1_id == user.id)
        ))
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(
            user.id != current_user.id,
            matches.status == 'active'
        )
        .all()
    )
 
    if not matched_users:
        return jsonify(message="No matches yet", matches=[], total=0), 200
 
    matched_user_ids = [m.id for m in matched_users]
 
    # Batch fetch all existing conversations for these users
    existing_convos = db.session.execute(db.select(conversations).filter(
            db.or_(
                db.and_(
                    conversations.user1_id == current_user.id,
                    conversations.user2_id.in_(matched_user_ids)
                ),
                db.and_(
                    conversations.user2_id == current_user.id,
                    conversations.user1_id.in_(matched_user_ids)
                )
            )
        )
    ).scalars().all()
 
    # Map other_user_id -> conversation_id for O(1) lookup
    convo_map = {
        (c.user2_id if c.user1_id == current_user.id else c.user1_id): c.id
        for c in existing_convos
    }
 
    result = [
        {
            "user_id": m.id,
            "username": m.username,
            "first_name": m.first_name,
            "last_name": m.last_name,
            "photo": m.photo_url or None,
            "match_id": m.match_id,
            "matched_at": m.matched_at.strftime('%Y-%m-%d'),
            "conversation_id": convo_map.get(m.id)
        }
        for m in matched_users
    ]
 
    return jsonify(matches=result, total=len(result)), 200

@app.route('/api/v1/possible-matches', methods=['GET'])
@token_required
def get_possible_matches():
    current_user = g.current_user
 
    # Fetch current user's data
    cu_profile = db.session.execute(
        db.select(user_profile).filter_by(user_id=current_user.id)
    ).scalar()
 
    cu_prefs = db.session.execute(
        db.select(user_preferences).filter_by(user_id=current_user.id)
    ).scalar()
 
    cu_location = db.session.execute(
        db.select(user_location).filter_by(user_id=current_user.id)
    ).scalar()
 
    cu_looking_for = {
        row.looking_for for row in db.session.execute(
            db.select(user_looking_for).filter_by(user_id=current_user.id)
        ).scalars().all()
    }
 
    cu_hobbies = {
        row.hobby_id for row in db.session.execute(
            db.select(user_hobbies).filter_by(user_id=current_user.id)
        ).scalars().all()
    }
 
    cu_age = calculate_age(cu_profile.dob) if cu_profile and cu_profile.dob else None
 
    # Guard — can't match without a complete profile
    if not cu_profile or not cu_prefs or not cu_location or not cu_age:
        return jsonify(message="Complete your profile, preferences, and location before matching"), 400
 
    # Fetch all other users with their profile + preferences + location in one join
    candidates = (
        db.session.query(
            user.id,
            user.username,
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
        .join(user_profile, user_profile.user_id == user.id)
        .join(user_preferences, user_preferences.user_id == user.id)
        .join(user_location, user_location.user_id == user.id)
        .filter(user.id != current_user.id)
        .all()
    )
 
    if not candidates:
        return jsonify(matches=[]), 200
 
    # Collect all candidate IDs for batch lookups
    candidate_ids = [c.id for c in candidates]
 
    # Batch fetch looking_for, hobbies, and photos — avoids N+1
    all_looking_for = db.session.execute(
        db.select(user_looking_for).filter(user_looking_for.user_id.in_(candidate_ids))
    ).scalars().all()
 
    all_hobbies = db.session.execute(
        db.select(user_hobbies).filter(user_hobbies.user_id.in_(candidate_ids))
    ).scalars().all()
 
    all_photos = db.session.execute(
        db.select(user_photo).filter(user_photo.user_id.in_(candidate_ids))
    ).scalars().all()
 
    # Build lookup dicts keyed by user_id for O(1) access
    looking_for_map = {}
    for lf in all_looking_for:
        looking_for_map.setdefault(lf.user_id, set()).add(lf.looking_for)
 
    hobbies_map = {}
    for h in all_hobbies:
        hobbies_map.setdefault(h.user_id, set()).add(h.hobby_id)
 
    photos_map = {}
    for p in all_photos:
        photos_map[p.user_id] = p.photo_url if p.photo_url else url_for('static', filename='default.png')
 
    # Run matching logic
    match_list = []
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
 
        # 5. At least one looking_for value in common
        c_looking_for = looking_for_map.get(c.id, set())
        if not cu_looking_for.intersection(c_looking_for):
            continue
 
        # 6. At least one hobby in common
        c_hobbies = hobbies_map.get(c.id, set())
        if not cu_hobbies.intersection(c_hobbies):
            continue
 
        match_list.append({
            "user_id":c.id,
            "username": c.username,
            "first_name":c.first_name,
            "last_name": c.last_name,
            "age": c_age,
            "gender": c.gender,
            "location": c.location_name,
            "distance_km": round(distance, 1),
            "looking_for": list(c_looking_for),
            "photo": photos_map.get(c.id) or url_for('static', filename='default.png'),
            "common_looking_for":list(cu_looking_for.intersection(c_looking_for)),
            "common_hobbies": list(cu_hobbies.intersection(c_hobbies))
        })
 
    # Sort by closest distance first
    match_list.sort(key=lambda x: x['distance_km'])
 
    return jsonify(match_list=match_list, total=len(match_list)), 200
 
 
@app.route('/api/v1/likes/<string:username>', methods=['POST'])
@token_required
def like_user(username, match_list):
    current_user = g.current_user
 
    # Resolve target user
    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    if target_user.id == current_user.id:
        return jsonify(message="You cannot like yourself"), 400
 
    # Guard against duplicate likes
    existing_like = db.session.execute(db.select(likes).filter_by(swiper_id=current_user.id, swipee_id=target_user.id)).scalar()
    if existing_like:
        return jsonify(message="You have already liked this user"), 409
 
    # Record the like
    if match in match_list:
        new_like = likes(
            swiper_id=current_user.id,
            swipee_id=target_user.id,
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(new_like)
        db.session.flush()
 
    # Check whether the other user has already liked the current user back
    return_like = db.session.execute(
        db.select(likes).filter_by(
            swiper_id=target_user.id,
            swipee_id=current_user.id
        )
    ).scalar()
 
    if return_like:
        # Mutual like — create an active match
        new_match = matches(
            user1_id=current_user.id,
            user2_id=target_user.id,
            status='active',
            matched_at=datetime.datetime.utcnow()
        )
        db.session.add(new_match)
        db.session.commit()
        return jsonify(message=f"It's a match with {username}!", matched=True), 201
 
    db.session.commit()
    return jsonify(message=f"You liked {username}.", matched=False), 201
 
 
@app.route('/api/v1/likes/<string:username>', methods=['DELETE'])
@token_required
def unlike_user(username):
    current_user = g.current_user
 
    # Resolve target user
    target_user = db.session.execute(
        db.select(user).filter_by(username=username)
    ).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    existing_like = db.session.execute(
        db.select(likes).filter_by(
            swiper_id=current_user.id,
            swipee_id=target_user.id
        )
    ).scalar()
    if not existing_like:
        return jsonify(message="You have not liked this user"), 404
 
    # If a match exists from a prior mutual like, deactivate it
    existing_match = db.session.execute(
        db.select(matches).filter(
            db.or_(
                db.and_(matches.user1_id == current_user.id, matches.user2_id == target_user.id),
                db.and_(matches.user1_id == target_user.id,  matches.user2_id == current_user.id)
            ),
            matches.status == 'active'
        )
    ).scalar()
    if existing_match:
        existing_match.status = 'inactive'
 
    db.session.delete(existing_like)
    db.session.commit()
 
    return jsonify(message=f"You unliked {username}."), 200

 
@app.route('/api/v1/messages/<string:username>', methods=['POST'])
@token_required
def send_message(username):
    current_user = g.current_user
 
    # Resolve target user
    target_user = db.session.execute(
        db.select(user).filter_by(username=username)
    ).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    if target_user.id == current_user.id:
        return jsonify(message="You cannot message yourself"), 400
 
    # Validate body — cheapest check before any DB hits
    data         = request.get_json()
    message_text = data.get('message_text', '').strip() if data else ''
 
    if not message_text:
        return jsonify(message="Message cannot be empty"), 400
    if len(message_text) > 1000:
        return jsonify(message="Message cannot exceed 1000 characters"), 400
 
    # Verify an active match exists
    existing_match = db.session.execute(
        db.select(matches).filter(
            db.or_(
                db.and_(matches.user1_id == current_user.id, matches.user2_id == target_user.id),
                db.and_(matches.user1_id == target_user.id, matches.user2_id == current_user.id)
            ),
            matches.status == 'active'
        )
    ).scalar()
    if not existing_match:
        return jsonify(message="You can only message your matches"), 403
 
    # Find or create conversation
    conversation = db.session.execute(db.select(conversations).filter(
            db.or_(
                db.and_(conversations.user1_id == current_user.id, conversations.user2_id == target_user.id),
                db.and_(conversations.user1_id == target_user.id, conversations.user2_id == current_user.id)
            )
        )).scalar()
 
    if not conversation:
        conversation = conversations(
            user1_id=current_user.id,
            user2_id=target_user.id,
            started_at=datetime.datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.flush()
 
    new_message = messages(
        conversation_id=conversation.id,
        sender_id=current_user.id,
        message_text=message_text,
        sent_at=datetime.datetime.utcnow(),
        is_read=False
    )
    db.session.add(new_message)
    db.session.commit()
 
    return jsonify(
        message="Message sent successfully",
        data={
            "message_id": new_message.id,
            "conversation_id": conversation.id,
            "message_text": new_message.message_text,
            "sent_at": new_message.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": new_message.is_read
        }
    ), 201
 
 
@app.route('/api/v1/messages/<int:conversation_id>', methods=['GET'])
@token_required
def get_messages(conversation_id):
    current_user = g.current_user
 
    # Verify ownership in the same query — no separate permission check needed
    conversation = db.session.execute(
        db.select(conversations).filter(conversations.id == conversation_id,
            db.or_(
                conversations.user1_id == current_user.id,
                conversations.user2_id == current_user.id
            )
    )).scalar()
    if not conversation:
        return jsonify(message="Conversation not found"), 404
 
    all_messages = db.session.execute(
        db.select(messages)
        .filter_by(conversation_id=conversation_id)
        .order_by(messages.sent_at.asc())
    ).scalars().all()
 
    if not all_messages:
        return jsonify(messages=[], total=0), 200
 
    # Resolve both users once — only ever 2 in a conversation
    user1 = db.session.execute(db.select(user).filter_by(id=conversation.user1_id)).scalar()
    user2 = db.session.execute(db.select(user).filter_by(id=conversation.user2_id)).scalar()
    username_map = {user1.id: user1.username, user2.id: user2.username}
 
    # Mark unread messages in one pass — only commit if there's something to update
    unread = [m for m in all_messages if m.sender_id != current_user.id and not m.is_read]
    for msg in unread:
        msg.is_read = True
    if unread:
        db.session.commit()
 
    messages_list = [
        {
            "message_id": msg.id,
            "sender": username_map.get(msg.sender_id),
            "recipient": username_map.get(conversation.user2_id if msg.sender_id == conversation.user1_id else conversation.user1_id),
            "message_text":msg.message_text,
            "sent_at": msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": msg.is_read
        }
        for msg in all_messages
    ]
 
    return jsonify(messages=messages_list, total=len(messages_list)), 200
 
 
@app.route('/api/v1/match/<string:username>', methods=['POST'])
@token_required
def add_match(username):
    current_user = g.current_user
 
    # Resolve the target user
    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    if target_user.id == current_user.id:
        return jsonify(message="You cannot match yourself"), 400
 
    # Guard against duplicates
    existing = db.session.execute(db.select(matches).filter_by(user_id=current_user.id,matched_user_id=target_user.id)).scalar()
    if existing:
        return jsonify(message="User is already bookmarked"), 409
 
    new_match = matches(
        user_id=current_user.id,
        matched_user_id=target_user.id,
        created_at=datetime.datetime.utcnow()
    )
    db.session.add(new_match)
    db.session.commit()
 
    return jsonify(message=f"{username} has been bookmarked"), 201
 
 
@app.route('/api/v1/matches/<string:username>', methods=['DELETE'])
@token_required
def remove_match(username):
    current_user = g.current_user
 
    # Resolve the target user
    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
 
    existing = db.session.execute(db.select(matches).filter_by(user_id=current_user.id,matched_user_id=target_user.id)).scalar()
    if not existing:
        return jsonify(message="Match not found"), 404
 
    db.session.delete(existing)
    db.session.commit()
 
    return jsonify(message=f"{username} has been removed from bookmarks"), 200
 
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
    return jsonify(message="The requested resource was not found"), 404