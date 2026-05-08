"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""
from email import message
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
        )
        db.session.add(new_profile)

        new_user_photo = user_photo(
            user_id=new_user.id,
            photo_url = url_for('static', filename='default.jpg')
        )
        db.session.add(new_user_photo)

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
            user.id, user.username, user.joined_at,
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender, user_profile.description
        )
        .join(user_profile, user_profile.user_id == user.id)
        .all()
    )
    if not results:
        return jsonify(users=[], total=0), 200

    user_ids = [r.id for r in results]

    # Batch fetch to avoid N+1
    lf_map = {}
    for lf in db.session.execute(
        db.select(user_looking_for).filter(user_looking_for.user_id.in_(user_ids))
    ).scalars().all():
        lf_map.setdefault(lf.user_id, []).append(lf.looking_for)

    photo_map = {
        p.user_id: p.photo_url for p in db.session.execute(
            db.select(user_photo).filter(user_photo.user_id.in_(user_ids))
        ).scalars().all()
    }

    return jsonify(
        users=[
            {
                "user_id":     row.id,
                "username":    row.username,
                "first_name":  row.first_name,
                "last_name":   row.last_name,
                "age":         calculate_age(row.dob) if row.dob else None,
                "gender":      row.gender,
                "description": row.description,
                "looking_for": lf_map.get(row.id, []),
                "photo":       photo_map.get(row.id) or url_for('static', filename='default.jpg'),
                "joined_at":   row.joined_at.strftime('%Y-%m-%d') if row.joined_at else None
            }
            for row in results
        ],
        total=len(results)
    ), 200


@app.route('/api/v1/user/', methods=['GET'])
@token_required
def get_user():
    userr = g.current_user

    result = (
        db.session.query(
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender, user_profile.description,
            user_location.location_name,
            user_photo.photo_url
        )
        .outerjoin(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_location, user_location.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(user.id == userr.id)
        .first()
    )

    looking_for = db.session.execute(db.select(user_looking_for.looking_for).filter_by(user_id=userr.id)).scalar()

    hobbies = db.session.execute(db.select(hobby.hobby_name).join(user_hobbies, user_hobbies.hobby_id == hobby.id).filter(user_hobbies.user_id == userr.id)).scalars().all()

    return jsonify(user={
        'user_id':     userr.id,
        'username':    userr.username,
        'email':       userr.email,
        'first_name':  result.first_name    if result else None,
        'last_name':   result.last_name     if result else None,
        'age':         calculate_age(result.dob) if result and result.dob else None,
        'gender':      result.gender        if result else None,
        'bio':         result.description   if result else None,
        'location':    result.location_name if result else None,
        'photo':       result.photo_url     if result else url_for('static', filename='default.jpg'),
        'looking_for': looking_for,
        'hobbies':     list(hobbies),
        'visibility':  userr.visibility,
        'joined_at':   userr.joined_at.strftime('%Y-%m-%d') if userr.joined_at else None
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
            if form.firstname.data:
                existing_profile.first_name = form.firstname.data
            if form.lastname.data:
                existing_profile.last_name = form.lastname.data
            if form.bio.data:
                existing_profile.description = form.bio.data
        else:
            # Create a new profile if one doesn't exist yet
            existing_profile = user_profile(
                user_id=current_user.id,
                first_name=form.firstname.data or "",
                last_name=form.lastname.data or "",
                dob=form.dob.data,
                gender=form.gender.data or "",
                description=form.bio.data or ""
            )
            db.session.add(existing_profile)

        if form.interests.data:
            # first add the interest/hobby to the hobby table if it doesn't exist, then add to user_hobbies attached to the user id. the hobbies submitted will be a comma-separated string, so we need to split it and process each one separately
            hobby_names = [name.strip().lower() for name in form.interests.data.split(',')]
            for hobby_name in hobby_names:
                hobby_entry = db.session.execute(db.select(hobby).filter_by(hobby_name=hobby_name)).scalar()
                if not hobby_entry:
                    hobby_entry = hobby(hobby_name=hobby_name)
                    db.session.add(hobby_entry)
                db.session.flush()  # to get the id of the new hobby
            # Now add to user_hobbies if not already added
                user_hobby_entry = db.session.execute(db.select(user_hobbies).filter_by(user_id=current_user.id, hobby_id=hobby_entry.id)).scalar()
                if not user_hobby_entry:
                    user_hobby_entry = user_hobbies(user_id=current_user.id, hobby_id=hobby_entry.id)
                    db.session.add(user_hobby_entry)
                    db.session.flush()  # to get the id of the new user_hobby entry

        existing_preference = db.session.execute(db.select(user_preferences).filter_by(user_id=current_user.id)).scalar()
        if existing_preference:
            if form.interested_in.data:
                existing_preference.gender_preference = form.interested_in.data
            if form.min_age.data: 
                existing_preference.min_age = form.min_age.data
            if form.max_age.data:
                existing_preference.max_age = form.max_age.data
            if form.max_distance.data:
                existing_preference.max_distance = form.max_distance.data
        else:
            existing_preference = user_preferences(
                user_id=current_user.id,
                gender_preference=form.interested_in.data or "",
                min_age=form.min_age.data or 18,
                max_age=form.max_age.data or 18,
                max_distance=form.max_distance.data or 1
            )

        db.session.add(existing_preference)
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

    if target_user.visibility == False and target_user.id != db.session.execute(db.select(match).filter_by(id=g.current_user.id)).scalar().id:
        return jsonify(profile={'username': target_user.username,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'age': calculate_age(profile.dob) if profile.dob else None,
        'gender': profile.gender,
        'description': profile.description,
        'photo': photo.photo_url if photo else None}, message="User profile is private"), 403
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
@token_required
def search():
    current_user = g.current_user
    username = request.args.get('username')
    location = request.args.get('location')
    min_age = request.args.get('min_age',  type=int)
    max_age = request.args.get('max_age',  type=int)
    interest = request.args.get('interest')

    query = (
        db.session.query(
            user.id, user.username, user.visibility, user.joined_at,
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender, user_profile.description,
            user_location.location_name
        )
        .join(user_profile,       user_profile.user_id  == user.id)
        .outerjoin(user_location, user_location.user_id == user.id)
        .filter(user.id != current_user.id)
    )
    if username:
        query = query.filter(user.username.ilike(f'%{username}%'))
    if location:
        query = query.filter(user_location.location_name.ilike(f'%{location}%'))

    results = query.all()
    if not results:
        return jsonify(users=[], total=0), 200

    result_ids = [r.id for r in results]

    # Batch fetch photos and looking_for
    photo_map = {
        p.user_id: p.photo_url for p in db.session.execute(
            db.select(user_photo).filter(user_photo.user_id.in_(result_ids))
        ).scalars().all()
    }
    lf_map = {}
    for lf in db.session.execute(
        db.select(user_looking_for).filter(user_looking_for.user_id.in_(result_ids))
    ).scalars().all():
        lf_map.setdefault(lf.user_id, []).append(lf.looking_for)

    # Batch fetch current user's active matches for visibility checks
    current_match_ids = {
        row.user2_id if row.user1_id == current_user.id else row.user1_id
        for row in db.session.execute(
            db.select(match).filter(
                db.or_(match.user1_id == current_user.id, match.user2_id == current_user.id),
                match.status == 'active'
            )
        ).scalars().all()
    }

    # Batch fetch hobby matches if interest filter applied
    hobby_user_ids = None
    if interest:
        matching_hobbies = db.session.execute(
            db.select(hobby).filter(hobby.hobby_name.ilike(f'%{interest}%'))
        ).scalars().all()
        hobby_ids = [h.id for h in matching_hobbies]
        hobby_user_ids = {
            uh.user_id for uh in db.session.execute(
                db.select(user_hobbies).filter(
                    user_hobbies.hobby_id.in_(hobby_ids),
                    user_hobbies.user_id.in_(result_ids)
                )
            ).scalars().all()
        }

    user_cards = []
    for row in results:
        age = calculate_age(row.dob) if row.dob else None

        if min_age and age and age < min_age: 
            continue
        if max_age and age and age > max_age:                
            continue
        if hobby_user_ids is not None and row.id not in hobby_user_ids: 
            continue

        # Visibility — private profiles only visible to matches
        if not row.visibility and row.id not in current_match_ids:
            continue

        user_cards.append({
            "user_id": row.id,
            "username": row.username,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "age": age,
            "gender": row.gender,
            "description": row.description,
            "location": row.location_name,
            "looking_for": lf_map.get(row.id, []),
            "photo": photo_map.get(row.id) or url_for('static', filename='default.jpg'),
            "joined_at": row.joined_at.strftime('%Y-%m-%d') if row.joined_at else None
        })

    return jsonify(users=user_cards, total=len(user_cards)), 200


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
            likes.created_at.label('liked_at')
        )
        .join(likes, likes.liked_user_id == user.id)
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(likes.user_id == current_user.id)
        .order_by(likes.created_at.desc())
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
            match.id.label('match_id'),
            match.matched_at
        )
        .join(match, db.or_(
            db.and_(match.user1_id == current_user.id, match.user2_id == user.id),
            db.and_(match.user2_id == current_user.id, match.user1_id == user.id)
        ))
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(
            user.id != current_user.id,
            match.status == 'active'
        )
        .all()
    )
 
    if not matched_users:
        return jsonify(message="No matches yet", matches=[], total=0), 200
 
    matched_user_ids = [m.id for m in matched_users]
 
    # Batch fetch all existing conversations for these users
    existing_convos = db.session.execute(db.select(conversation).filter(
            db.or_(
                db.and_(
                    conversation.user1_id == current_user.id,
                    conversation.user2_id.in_(matched_user_ids)
                ),
                db.and_(
                    conversation.user2_id == current_user.id,
                    conversation.user1_id.in_(matched_user_ids)
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

    cu_profile  = db.session.execute(db.select(user_profile).filter_by(user_id=current_user.id)).scalar()
    cu_prefs    = db.session.execute(db.select(user_preferences).filter_by(user_id=current_user.id)).scalar()
    cu_location = db.session.execute(db.select(user_location).filter_by(user_id=current_user.id)).scalar()

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

    if not cu_profile or not cu_prefs or not cu_location or not cu_age:
        return jsonify(message="Complete your profile, preferences, and location before matching"), 400

    # Exclude already-liked, passed, and already-matched users
    already_actioned = {
        row.liked_user_id for row in db.session.execute(
            db.select(likes).filter_by(user_id=current_user.id)
        ).scalars().all()
    }
    already_matched = {
        row.user2_id if row.user1_id == current_user.id else row.user1_id
        for row in db.session.execute(
            db.select(match).filter(
                db.or_(match.user1_id == current_user.id, match.user2_id == current_user.id)
            )
        ).scalars().all()
    }
    excluded_ids = already_actioned | already_matched | {current_user.id}

    candidates = (
        db.session.query(
            user.id, user.username,
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender, user_profile.description,
            user_preferences.min_age, user_preferences.max_age,
            user_preferences.gender_preference, user_preferences.max_distance,
            user_location.location_name, user_location.latitude, user_location.longitude,
        )
        .join(user_profile, user_profile.user_id == user.id)
        .join(user_preferences, user_preferences.user_id == user.id)
        .join(user_location, user_location.user_id == user.id)
        .filter(user.id.notin_(excluded_ids), user.visibility == True)
        .all()
    )

    if not candidates:
        return jsonify(match_list=[], total=0), 200

    candidate_ids = [c.id for c in candidates]

    looking_for_map = {}
    for lf in db.session.execute(
        db.select(user_looking_for).filter(user_looking_for.user_id.in_(candidate_ids))
    ).scalars().all():
        looking_for_map.setdefault(lf.user_id, set()).add(lf.looking_for)

    hobbies_map = {}
    for h in db.session.execute(
        db.select(user_hobbies).filter(user_hobbies.user_id.in_(candidate_ids))
    ).scalars().all():
        hobbies_map.setdefault(h.user_id, set()).add(h.hobby_id)

    photos_map = {
        p.user_id: p.photo_url for p in db.session.execute(
            db.select(user_photo).filter(user_photo.user_id.in_(candidate_ids))
        ).scalars().all()
    }

    match_list = []
    for c in candidates:
        c_age = calculate_age(c.dob) if c.dob else None
        if not c_age:                                                    
            continue
        if not (c.min_age <= cu_age <= c.max_age):                       
            continue
        if not (cu_prefs.min_age <= c_age <= cu_prefs.max_age):          
            continue
        if c.gender_preference != cu_profile.gender:                     
            continue
        if cu_prefs.gender_preference != c.gender:                       
            continue

        distance = haversine(cu_location.latitude, cu_location.longitude, c.latitude, c.longitude)
        if distance > cu_prefs.max_distance or distance > c.max_distance: 
            continue

        c_looking_for = looking_for_map.get(c.id, set())
        common_lf = cu_looking_for.intersection(c_looking_for)
        if not common_lf:                                                
            continue

        c_hobbies = hobbies_map.get(c.id, set())
        common_hobbies = cu_hobbies.intersection(c_hobbies)
        if not common_hobbies:                                           
            continue

        # Simple match score based on shared interests and hobbies
        lf_score      = len(common_lf)      / max(len(cu_looking_for), 1)
        hobby_score   = len(common_hobbies) / max(len(cu_hobbies), 1)
        match_score   = round(((lf_score + hobby_score) / 2) * 100, 1)

        match_list.append({
            "user_id": c.id,
            "username": c.username,
            "first_name":  c.first_name,
            "last_name": c.last_name,
            "age": c_age,
            "gender": c.gender,
            "description": c.description,
            "location": c.location_name,
            "distance_km": round(distance, 1),
            "looking_for": list(c_looking_for),
            "photo": photos_map.get(c.id) or url_for('static', filename='default.jpg'),
            "common_looking_for": list(common_lf),
            "common_hobbies": list(common_hobbies),
            "match_score": match_score
        })

    match_list.sort(key=lambda x: x['distance_km'])
    return jsonify(match_list=match_list, total=len(match_list)), 200
 
 
@app.route('/api/v1/likes/<string:username>', methods=['POST'])
@token_required
def like_user(username):
    current_user = g.current_user

    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
    if target_user.id == current_user.id:
        return jsonify(message="You cannot like yourself"), 400

    existing = db.session.execute(
        db.select(likes).filter_by(user_id=current_user.id, liked_user_id=target_user.id)
    ).scalar()
    if existing:
        return jsonify(message="You have already liked this user"), 409

    db.session.add(likes(
        user_id=current_user.id,
        liked_user_id=target_user.id,
        created_at=datetime.datetime.utcnow(),
        action='like'
    ))
    db.session.flush()

    # Mutual like check — create an active match if both users liked each other
    return_like = db.session.execute(
        db.select(likes).filter_by(
            user_id=target_user.id, liked_user_id=current_user.id, action='like'
        )
    ).scalar()

    if return_like:
        already_matched = db.session.execute(
            db.select(match).filter(
                db.or_(
                    db.and_(match.user1_id == current_user.id, match.user2_id == target_user.id),
                    db.and_(match.user1_id == target_user.id,  match.user2_id == current_user.id)
                )
            )
        ).scalar()
        if not already_matched:
            db.session.add(match(
                user1_id=current_user.id,
                user2_id=target_user.id,
                status='active',
                matched_at=datetime.datetime.utcnow()
            ))
        db.session.commit()
        return jsonify(message=f"It's a match with {username}!", matched=True), 201

    db.session.commit()
    return jsonify(message=f"You liked {username}.", matched=False), 201


@app.route('/api/v1/pass/<string:username>', methods=['POST'])
@token_required
def pass_user(username):
    """Records a pass — prevents the user from appearing in discovery again."""
    current_user = g.current_user

    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
    if target_user.id == current_user.id:
        return jsonify(message="You cannot pass yourself"), 400

    existing = db.session.execute(
        db.select(likes).filter_by(user_id=current_user.id, liked_user_id=target_user.id)
    ).scalar()
    if existing:
        return jsonify(message="Already actioned this user"), 409

    # Store as action='pass' so they are excluded from future discovery
    db.session.add(likes(
        user_id=current_user.id,
        liked_user_id=target_user.id,
        created_at=datetime.datetime.utcnow(),
        action='pass'
    ))
    db.session.commit()
    return jsonify(message=f"Passed on {username}."), 201


@app.route('/api/v1/likes/<string:username>', methods=['DELETE'])
@token_required
def unlike_user(username):
    current_user = g.current_user

    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404

    existing_like = db.session.execute(
        db.select(likes).filter_by(
            user_id=current_user.id, liked_user_id=target_user.id, action='like'
        )
    ).scalar()
    if not existing_like:
        return jsonify(message="You have not liked this user"), 404

    # Deactivate any match that resulted from this like
    existing_match = db.session.execute(
        db.select(match).filter(
            db.or_(
                db.and_(match.user1_id == current_user.id, match.user2_id == target_user.id),
                db.and_(match.user1_id == target_user.id,  match.user2_id == current_user.id)
            ),
            match.status == 'active'
        )
    ).scalar()
    if existing_match:
        existing_match.status = 'unmatched'

    db.session.delete(existing_like)
    db.session.commit()
    return jsonify(message=f"You unliked {username}."), 200

@app.route('/api/v1/matches', methods=['GET'])
@token_required
def get_matches():
    current_user = g.current_user

    matched_users = (
        db.session.query(
            user.id, user.username,
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender, user_profile.description,
            user_photo.photo_url,
            match.id.label('match_id'),
            match.matched_at
        )
        .join(match, db.or_(
            db.and_(match.user1_id == current_user.id, match.user2_id == user.id),
            db.and_(match.user2_id == current_user.id, match.user1_id == user.id)
        ))
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(user.id != current_user.id, match.status == 'active')
        .all()
    )

    if not matched_users:
        return jsonify(matches=[], total=0), 200

    matched_user_ids = [m.id for m in matched_users]
    convo_map = {
        (c.user2_id if c.user1_id == current_user.id else c.user1_id): c.id
        for c in db.session.execute(
            db.select(conversation).filter(
                db.or_(
                    db.and_(conversation.user1_id == current_user.id,
                            conversation.user2_id.in_(matched_user_ids)),
                    db.and_(conversation.user2_id == current_user.id,
                            conversation.user1_id.in_(matched_user_ids))
                )
            )
        ).scalars().all()
    }

    return jsonify(
        matches=[
            {
                "user_id": m.id,
                "username": m.username,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "age": calculate_age(m.dob) if m.dob else None,
                "gender": m.gender,
                "description": m.description,
                "photo": m.photo_url or url_for('static', filename='default.jpg'),
                "match_id": m.match_id,
                "matched_at": m.matched_at.strftime('%Y-%m-%d'),
                "conversation_id": convo_map.get(m.id)
            }
            for m in matched_users
        ],
        total=len(matched_users)
    ), 200

 
@app.route('/api/v1/messageable', methods=['GET'])
@token_required
def get_messageable():
    # Matches and messageable users are the same list
    return get_matches()

@app.route('/api/v1/messages/<string:username>', methods=['POST'])
@token_required
def send_message(username):
    current_user = g.current_user

    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
    if target_user.id == current_user.id:
        return jsonify(message="You cannot message yourself"), 400

    data         = request.get_json()
    message_text = data.get('message_text', '').strip() if data else ''
    if not message_text:
        return jsonify(message="Message cannot be empty"), 400
    if len(message_text) > 1000:
        return jsonify(message="Message cannot exceed 1000 characters"), 400

    existing_match = db.session.execute(
        db.select(match).filter(
            db.or_(
                db.and_(match.user1_id == current_user.id, match.user2_id == target_user.id),
                db.and_(match.user1_id == target_user.id,  match.user2_id == current_user.id)
            ),
            match.status == 'active'
        )
    ).scalar()
    if not existing_match:
        return jsonify(message="You can only message your matches"), 403

    # FIX: renamed variable to convo_obj to avoid shadowing the conversation model class
    convo_obj = db.session.execute(
        db.select(conversation).filter(
            db.or_(
                db.and_(conversation.user1_id == current_user.id,
                        conversation.user2_id == target_user.id),
                db.and_(conversation.user1_id == target_user.id,
                        conversation.user2_id == current_user.id)
            )
        )
    ).scalar()

    if not convo_obj:
        convo_obj = conversation(
            user1_id=current_user.id,
            user2_id=target_user.id,
            started_at=datetime.datetime.utcnow()
        )
        db.session.add(convo_obj)
        db.session.flush()

    new_msg = message(
        conversation_id=convo_obj.id,
        sender_id=current_user.id,
        message_text=message_text,
        sent_at=datetime.datetime.utcnow(),
        is_read=False
    )
    db.session.add(new_msg)
    db.session.commit()

    return jsonify(
        message="Message sent successfully",
        data={
            "message_id": new_msg.id,
            "conversation_id": convo_obj.id,
            "message_text": new_msg.message_text,
            "sent_at": new_msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": new_msg.is_read
        }
    ), 201


@app.route('/api/v1/messages/<int:conversation_id>', methods=['GET'])
@token_required
def get_messages(conversation_id):
    current_user = g.current_user

    # FIX: renamed to convo_obj throughout — avoids shadowing the conversation model
    convo_obj = db.session.execute(
        db.select(conversation).filter(
            conversation.id == conversation_id,
            db.or_(
                conversation.user1_id == current_user.id,
                conversation.user2_id == current_user.id
            )
        )
    ).scalar()
    if not convo_obj:
        return jsonify(message="Conversation not found"), 404

    all_messages = db.session.execute(
        db.select(message)
        .filter_by(conversation_id=conversation_id)
        .order_by(message.sent_at.asc())
    ).scalars().all()

    if not all_messages:
        return jsonify(messages=[], total=0), 200

    # Resolve both users once — O(1) lookup per message
    user1 = db.session.execute(db.select(user).filter_by(id=convo_obj.user1_id)).scalar()
    user2 = db.session.execute(db.select(user).filter_by(id=convo_obj.user2_id)).scalar()
    username_map = {user1.id: user1.username, user2.id: user2.username}

    unread = [m for m in all_messages if m.sender_id != current_user.id and not m.is_read]
    for msg in unread:
        msg.is_read = True
    if unread:
        db.session.commit()

    return jsonify(
        messages=[
            {
                "message_id": msg.id,
                "sender":username_map.get(msg.sender_id),
                "recipient": username_map.get(
                    convo_obj.user2_id if msg.sender_id == convo_obj.user1_id
                    else convo_obj.user1_id
                ),
                "message_text": msg.message_text,
                "sent_at":      msg.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                "is_read":      msg.is_read
            }
            for msg in all_messages
        ],
        total=len(all_messages)
    ), 200

 
 
@app.route('/api/v1/favourites', methods=['GET'])
@token_required
def get_favourites():
    current_user = g.current_user
    rows = (
        db.session.query(
            user.id, user.username,
            user_profile.first_name, user_profile.last_name,
            user_profile.dob, user_profile.gender,
            user_photo.photo_url,
            favorites.favorited_at
        )
        .join(favorites,    favorites.favorite_user_id == user.id)
        .join(user_profile, user_profile.user_id       == user.id)
        .outerjoin(user_photo, user_photo.user_id      == user.id)
        .filter(favorites.user_id == current_user.id)
        .order_by(favorites.favorited_at.desc())
        .all()
    )
    return jsonify(
        favourites=[
            {
                "user_id": row.id,
                "username": row.username,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "age": calculate_age(row.dob) if row.dob else None,
                "gender": row.gender,
                "photo": row.photo_url or url_for('static', filename='default.jpg'),
                "favourited_at": row.favorited_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for row in rows
        ],
        total=len(rows)
    ), 200



@app.route('/api/v1/favourites/<string:username>', methods=['POST'])
@token_required
def add_favourite(username):
    current_user = g.current_user
    target_user  = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
    if target_user.id == current_user.id:
        return jsonify(message="You cannot favourite yourself"), 400

    existing = db.session.execute(
        db.select(favorites).filter_by(user_id=current_user.id, favorite_user_id=target_user.id)
    ).scalar()
    if existing:
        return jsonify(message="Already in your favourites"), 409

    db.session.add(favorites(
        user_id=current_user.id,
        favorite_user_id=target_user.id,
        favorited_at=datetime.datetime.utcnow()
    ))
    db.session.commit()
    return jsonify(message=f"{username} added to favourites"), 201


@app.route('/api/v1/favourites/<string:username>', methods=['DELETE'])
@token_required
def remove_favourite(username):
    current_user = g.current_user
    target_user  = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404

    existing = db.session.execute(
        db.select(favorites).filter_by(user_id=current_user.id, favorite_user_id=target_user.id)
    ).scalar()
    if not existing:
        return jsonify(message="Not in your favourites"), 404

    db.session.delete(existing)
    db.session.commit()
    return jsonify(message=f"{username} removed from favourites"), 200


 
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
