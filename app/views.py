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
import os, datetime, jwt, uuid
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

def uploaded_photo_url(filename):
    return url_for('uploaded_file', filename=filename, _external=True)

def display_photo_url(photo_url):
    if not photo_url:
        return None
    if photo_url.startswith('/static/uploads/'):
        filename = photo_url.replace('/static/uploads/', '', 1)
        return uploaded_photo_url(filename)
    if '/static/uploads/' in photo_url:
        filename = photo_url.rsplit('/static/uploads/', 1)[1]
        return uploaded_photo_url(filename)
    if photo_url.startswith(('http://', 'https://')):
        return photo_url
    if photo_url.startswith('/uploads/'):
        filename = photo_url.replace('/uploads/', '', 1)
        return uploaded_photo_url(filename)
    if photo_url.startswith('/'):
        return photo_url

    return uploaded_photo_url(photo_url)

def uploaded_photo_path(photo_url):
    upload_prefix = url_for('static', filename='uploads/')
    external_upload_prefix = url_for('static', filename='uploads/', _external=True)
    uploads_prefix = url_for('uploaded_file', filename='')
    external_uploads_prefix = url_for('uploaded_file', filename='', _external=True)
    if not photo_url or not photo_url.startswith(upload_prefix):
        if photo_url and photo_url.startswith(external_upload_prefix):
            filename = photo_url.replace(external_upload_prefix, '', 1)
        elif photo_url and photo_url.startswith(uploads_prefix):
            filename = photo_url.replace(uploads_prefix, '', 1)
        elif photo_url and photo_url.startswith(external_uploads_prefix):
            filename = photo_url.replace(external_uploads_prefix, '', 1)
        else:
            return None
    else:
        filename = photo_url.replace(upload_prefix, '', 1)

    if not filename or filename != secure_filename(filename):
        return None

    return os.path.join(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
        return jsonify(users=[], matches=[], total=0), 200

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
                "photo":       display_photo_url(photo_map.get(row.id)),
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
    profile_photo = db.session.execute(db.select(user_photo.photo_url).filter_by(user_id=userr.id)).scalar()
    return jsonify(user={
        'username': userr.username,
        'first_name': first_name,
        'last_name':  last_name,
        'age': age,
        'location': location,
        'bio': bio,
        'looking_for': looking_for,
        'profile_photo': display_photo_url(profile_photo)
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
                first_name=form.firstname.data,
                last_name=form.lastname.data,
                description=form.bio.data
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
                gender_preference=form.interested_in.data,
                min_age=form.min_age.data,
                max_age=form.max_age.data,
                max_distance=form.max_distance.data
            )

        db.session.add(existing_preference)
        if form.photo.data:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            original_filename = secure_filename(form.photo.data.filename)
            extension = os.path.splitext(original_filename)[1].lower()
            filename = f"user_{current_user.id}_{uuid.uuid4().hex}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(filepath)
            photo_url = uploaded_photo_url(filename)

            existing_photo = db.session.execute(
                db.select(user_photo).filter_by(user_id=current_user.id)
            ).scalar()

            if existing_photo:
                # Delete old file from disk then overwrite the record
                old_filepath = uploaded_photo_path(existing_photo.photo_url)
                if old_filepath and os.path.exists(old_filepath):
                    os.remove(old_filepath)
                existing_photo.photo_url   = photo_url
                existing_photo.uploaded_at = datetime.datetime.utcnow()
            else:
                new_photo = user_photo(
                    user_id=current_user.id,
                    photo_url=photo_url,
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
    active_match = db.session.execute(
        db.select(match).filter(
            db.or_(
                db.and_(match.user1_id == g.current_user.id, match.user2_id == target_user.id),
                db.and_(match.user1_id == target_user.id, match.user2_id == g.current_user.id)
            ),
            match.status == 'active'
        )
    ).scalar()

    if target_user.visibility == False and target_user.id != g.current_user.id and not active_match:
        return jsonify(message="User profile is private"), 403

    hobby_rows = (
        db.session.query(hobby.hobby_name)
        .join(user_hobbies, user_hobbies.hobby_id == hobby.id)
        .filter(user_hobbies.user_id == target_user.id)
        .all()
    )
    hobbies = [row.hobby_name for row in hobby_rows]
    looking_for = [lf.looking_for for lf in looking_for_rows]
    display_name = f"{profile.first_name or ''} {profile.last_name or ''}".strip() or target_user.username

    return jsonify(profile={
        'user_id': target_user.id,
        'username': target_user.username,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'firstName': profile.first_name,
        'lastName': profile.last_name,
        'name': display_name,
        'age': calculate_age(profile.dob) if profile.dob else None,
        'gender': profile.gender,
        'description': profile.description,
        'bio': profile.description,
        'about': profile.description,
        'location': location.location_name if location else None,
        'looking_for': looking_for,
        'lookingFor': ", ".join(looking_for),
        'hobbies': hobbies,
        'interests': hobbies,
        'photo': display_photo_url(photo.photo_url if photo else None),
        'photoUrl': display_photo_url(photo.photo_url if photo else None),
        'matchScore': active_match.match_score if active_match and active_match.match_score else 0,
        'matched': bool(active_match)
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
    name = request.args.get('name') or username
    location = request.args.get('location')
    min_age = request.args.get('min_age',  type=int)
    max_age = request.args.get('max_age',  type=int)
    interest = request.args.get('interest')
    sort_by = request.args.get('sort', 'most_similar')

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
    if name:
        query = query.filter(db.or_(
            user.username.ilike(f'%{name}%'),
            user_profile.first_name.ilike(f'%{name}%'),
            user_profile.last_name.ilike(f'%{name}%')
        ))
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

    hobbies_map = {}
    all_hobby_ids = set()
    for row in db.session.execute(
        db.select(user_hobbies).filter(user_hobbies.user_id.in_(result_ids))
    ).scalars().all():
        hobbies_map.setdefault(row.user_id, set()).add(row.hobby_id)
        all_hobby_ids.add(row.hobby_id)

    hobby_name_map = {}
    if all_hobby_ids:
        hobby_name_map = {
            h.id: h.hobby_name for h in db.session.execute(
                db.select(hobby).filter(hobby.id.in_(all_hobby_ids))
            ).scalars().all()
        }

    current_hobbies = {
        row.hobby_id for row in db.session.execute(
            db.select(user_hobbies).filter_by(user_id=current_user.id)
        ).scalars().all()
    }
    current_looking_for = {
        row.looking_for for row in db.session.execute(
            db.select(user_looking_for).filter_by(user_id=current_user.id)
        ).scalars().all()
    }

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
    favorite_ids = {
        row.favorite_user_id for row in db.session.execute(
            db.select(favorite).filter_by(user_id=current_user.id)
        ).scalars().all()
    }
    actioned_ids = {
        row.swipee_id for row in db.session.execute(
            db.select(likes).filter_by(swiper_id=current_user.id)
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
        if row.id in current_match_ids or row.id in actioned_ids:
            continue

        user_hobby_ids = hobbies_map.get(row.id, set())
        hobby_names = [
            hobby_name_map[hobby_id] for hobby_id in user_hobby_ids
            if hobby_id in hobby_name_map
        ]
        candidate_lf = set(lf_map.get(row.id, []))
        common_lf = current_looking_for.intersection(candidate_lf)
        common_hobbies = current_hobbies.intersection(user_hobby_ids)
        lf_score = len(common_lf) / max(len(current_looking_for), 1)
        hobby_score = len(common_hobbies) / max(len(current_hobbies), 1)
        match_score = round(((lf_score + hobby_score) / 2) * 100, 1)
        display_name = f"{row.first_name or ''} {row.last_name or ''}".strip() or row.username

        user_cards.append({
            "id": row.id,
            "user_id": row.id,
            "username": row.username,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "name": display_name,
            "age": age,
            "gender": row.gender,
            "description": row.description,
            "bio": row.description,
            "location": row.location_name,
            "looking_for": lf_map.get(row.id, []),
            "lookingFor": ", ".join(lf_map.get(row.id, [])),
            "photo": display_photo_url(photo_map.get(row.id)),
            "joined_at": row.joined_at.strftime('%Y-%m-%d') if row.joined_at else None,
            "interests": hobby_names,
            "common_hobbies": [
                hobby_name_map[hobby_id] for hobby_id in common_hobbies
                if hobby_id in hobby_name_map
            ],
            "match_score": match_score,
            "matchScore": match_score,
            "status": "pending",
            "isFavorite": row.id in favorite_ids,
            "avatarBg": "linear-gradient(135deg, #C0395A, #E8563A)"
        })

    if sort_by == 'newest':
        user_cards.sort(key=lambda x: x.get('joined_at') or '', reverse=True)
    elif sort_by == 'name':
        user_cards.sort(key=lambda x: x.get('name') or '')
    elif sort_by == 'age_low':
        user_cards.sort(key=lambda x: x.get('age') or 999)
    elif sort_by == 'age_high':
        user_cards.sort(key=lambda x: x.get('age') or 0, reverse=True)
    else:
        user_cards.sort(key=lambda x: x.get('matchScore') or 0, reverse=True)

    return jsonify(users=user_cards, matches=user_cards, total=len(user_cards)), 200


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
        .join(likes, likes.swipee_id == user.id)
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(likes.swiper_id == current_user.id)
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
        row.swipee_id for row in db.session.execute(
            db.select(likes).filter_by(swiper_id=current_user.id)
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
        .outerjoin(user_preferences, user_preferences.user_id == user.id)
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

    all_hobby_ids = set(cu_hobbies)
    for candidate_hobbies in hobbies_map.values():
        all_hobby_ids.update(candidate_hobbies)

    hobby_name_map = {}
    if all_hobby_ids:
        hobby_name_map = {
            h.id: h.hobby_name for h in db.session.execute(
                db.select(hobby).filter(hobby.id.in_(all_hobby_ids))
            ).scalars().all()
        }

    photos_map = {
        p.user_id: p.photo_url for p in db.session.execute(
            db.select(user_photo).filter(user_photo.user_id.in_(candidate_ids))
        ).scalars().all()
    }
    favorite_ids = {
        row.favorite_user_id for row in db.session.execute(
            db.select(favorite).filter_by(user_id=current_user.id)
        ).scalars().all()
    }

    def preference_allows(preference, gender):
        if not preference:
            return True
        return preference.lower() in ("any", "all", "everyone") or preference.lower() == (gender or "").lower()

    match_list = []
    for c in candidates:
        c_age = calculate_age(c.dob) if c.dob else None
        if not c_age:                                                    
            continue
        if c.min_age and cu_age < c.min_age:
            continue
        if c.max_age and cu_age > c.max_age:
            continue
        if cu_prefs.min_age and c_age < cu_prefs.min_age:
            continue
        if cu_prefs.max_age and c_age > cu_prefs.max_age:
            continue
        if not preference_allows(cu_prefs.gender_preference, c.gender):
            continue

        distance = haversine(cu_location.latitude, cu_location.longitude, c.latitude, c.longitude)
        if cu_prefs.max_distance and distance > cu_prefs.max_distance:
            continue

        c_looking_for = looking_for_map.get(c.id, set())
        common_lf = cu_looking_for.intersection(c_looking_for)

        c_hobbies = hobbies_map.get(c.id, set())
        common_hobbies = cu_hobbies.intersection(c_hobbies)
        if not common_lf and not common_hobbies:
            continue

        # Simple match score based on shared interests and hobbies
        lf_score      = len(common_lf)      / max(len(cu_looking_for), 1)
        hobby_score   = len(common_hobbies) / max(len(cu_hobbies), 1)
        match_score   = round(((lf_score + hobby_score) / 2) * 100, 1)
        common_hobby_names = [
            hobby_name_map[hobby_id] for hobby_id in common_hobbies
            if hobby_id in hobby_name_map
        ]
        c_looking_for_list = list(c_looking_for)
        display_name = f"{c.first_name or ''} {c.last_name or ''}".strip() or c.username

        match_list.append({
            "id": c.id,
            "user_id": c.id,
            "username": c.username,
            "first_name":  c.first_name,
            "last_name": c.last_name,
            "name": display_name,
            "age": c_age,
            "gender": c.gender,
            "description": c.description,
            "bio": c.description,
            "location": c.location_name,
            "distance_km": round(distance, 1),
            "looking_for": c_looking_for_list,
            "lookingFor": ", ".join(c_looking_for_list),
            "photo": display_photo_url(photos_map.get(c.id)),
            "common_looking_for": list(common_lf),
            "common_hobbies": common_hobby_names,
            "interests": common_hobby_names,
            "match_score": match_score,
            "matchScore": match_score,
            "status": "pending",
            "isFavorite": c.id in favorite_ids,
            "avatarBg": "linear-gradient(135deg, #C0395A, #E8563A)"
        })

    match_list.sort(key=lambda x: (-x['match_score'], x['distance_km']))
    return jsonify(matches=match_list, match_list=match_list, total=len(match_list)), 200
 
 
@app.route('/api/v1/likes/<string:username>', methods=['POST'])
@token_required
def like_user(username):
    current_user = g.current_user

    target_user = db.session.execute(db.select(user).filter_by(username=username)).scalar()
    if not target_user:
        return jsonify(message="User not found"), 404
    if target_user.id == current_user.id:
        return jsonify(message="You cannot like yourself"), 400

    data = request.get_json(silent=True) or {}
    match_score = data.get('match_score')
    if match_score is not None:
        match_score = int(round(float(match_score)))

    existing = db.session.execute(
        db.select(likes).filter_by(swiper_id=current_user.id, swipee_id=target_user.id)
    ).scalar()
    if existing:
        if existing.action == 'like':
            return jsonify(message="You have already liked this user", matched=False), 409
        existing.action = 'like'
        existing.action_at = datetime.datetime.utcnow()
    else:
        db.session.add(likes(
            swiper_id=current_user.id,
            swipee_id=target_user.id,
            action_at=datetime.datetime.utcnow(),
            action='like'
        ))

    db.session.flush()

    # Mutual like check — create an active match if both users liked each other
    return_like = db.session.execute(
        db.select(likes).filter_by(
            swiper_id=target_user.id, swipee_id=current_user.id, action='like'
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
                match_score=match_score,
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
        db.select(likes).filter_by(swiper_id=current_user.id, swipee_id=target_user.id)
    ).scalar()
    if existing:
        existing.action = 'pass'
        existing.action_at = datetime.datetime.utcnow()
    else:
        # Store as action='pass' so they are excluded from future discovery
        db.session.add(likes(
            swiper_id=current_user.id,
            swipee_id=target_user.id,
            action_at=datetime.datetime.utcnow(),
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
            swiper_id=current_user.id, swipee_id=target_user.id, action='like'
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
            user_location.location_name,
            user_photo.photo_url,
            match.id.label('match_id'),
            match.matched_at,
            match.match_score
        )
        .join(match, db.or_(
            db.and_(match.user1_id == current_user.id, match.user2_id == user.id),
            db.and_(match.user2_id == current_user.id, match.user1_id == user.id)
        ))
        .join(user_profile, user_profile.user_id == user.id)
        .outerjoin(user_location, user_location.user_id == user.id)
        .outerjoin(user_photo, user_photo.user_id == user.id)
        .filter(user.id != current_user.id, match.status == 'active')
        .all()
    )

    if not matched_users:
        return jsonify(matches=[], total=0, total_unread=0), 200

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
    conversation_ids = list(convo_map.values())
    unread_count_map = {}

    if conversation_ids:
        unread_count_map = {
            sender_id: unread_count
            for sender_id, unread_count in db.session.query(
                message.sender_id,
                db.func.count(message.id)
            )
            .filter(
                message.conversation_id.in_(conversation_ids),
                message.sender_id != current_user.id,
                message.is_read == False
            )
            .group_by(message.sender_id)
            .all()
        }
    total_unread = sum(unread_count_map.values())

    return jsonify(
        matches=[
            {
                "id": m.id,
                "user_id": m.id,
                "username": m.username,
                "first_name": m.first_name,
                "last_name": m.last_name,
                "name": f"{m.first_name or ''} {m.last_name or ''}".strip() or m.username,
                "age": calculate_age(m.dob) if m.dob else None,
                "gender": m.gender,
                "description": m.description,
                "bio": m.description,
                "location": m.location_name,
                "photo": display_photo_url(m.photo_url),
                "match_id": m.match_id,
                "matchScore": m.match_score,
                "matched_at": m.matched_at.strftime('%Y-%m-%d'),
                "active": "Matched",
                "avatarBg": "linear-gradient(135deg, #C0395A, #E8563A)",
                "interests": [],
                "conversation_id": convo_map.get(m.id),
                "unread_count": unread_count_map.get(m.id, 0)
            }
            for m in matched_users
        ],
        total=len(matched_users),
        total_unread=total_unread
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
            last_message=message_text,
            updated_at=datetime.datetime.utcnow()
        )
        db.session.add(convo_obj)
        db.session.flush()
    else:
        convo_obj.last_message = message_text
        convo_obj.updated_at = datetime.datetime.utcnow()

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
            favorite.favorited_at
        )
        .join(favorite,    favorite.favorite_user_id == user.id)
        .join(user_profile, user_profile.user_id       == user.id)
        .outerjoin(user_photo, user_photo.user_id      == user.id)
        .filter(favorite.user_id == current_user.id)
        .order_by(favorite.favorited_at.desc())
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
                "photo": display_photo_url(row.photo_url),
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
        db.select(favorite).filter_by(user_id=current_user.id, favorite_user_id=target_user.id)
    ).scalar()
    if existing:
        return jsonify(message="Already in your favourites"), 409

    db.session.add(favorite(
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
        db.select(favorite).filter_by(user_id=current_user.id, favorite_user_id=target_user.id)
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
