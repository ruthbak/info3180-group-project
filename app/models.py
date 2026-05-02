# Add any model classes for Flask-SQLAlchemy here
from . import db
from werkzeug.security import generate_password_hash

class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    visibility = db.Column(db.Boolean, index=True)
    joined_at = db.Column(db.DateTime, index=True)
    updated_at = db.Column(db.DateTime, index=True)
    last_seen = db.Column(db.DateTime, index=True)

    def __init__(self, username, email, password_hash, visibility, joined_at, updated_at, last_seen):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.visibility = visibility
        #Think about how to set the joined_at, updated_at, and last_seen fields when a user is created and when they log in. You may want to use the datetime module to set these fields to the current time instead of doing it with the form.
        self.joined_at = joined_at
        self.updated_at = updated_at
        self.last_seen = last_seen

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support
        
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class user_profile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    dob = db.Column(db.Date, index=True)
    gender = db.Column(db.String(16), index=True)
    description = db.Column(db.String(256), index=True)

    def __init__(self, user_id, first_name, last_name, dob, gender, description):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.gender = gender
        self.description = description

    def __repr__(self):
        return '<User Profile {}>'.format(self.first_name)
        
class user_location(db.Model):
    __tablename__ = 'user_location'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    location_name = db.Column(db.String(64), index=True)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)

    def __init__(self, user_id, location_name, latitude, longitude):
        self.user_id = user_id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '<User Location {}>'.format(self.location_name)
    
class user_preferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    min_age = db.Column(db.Integer, index=True)
    max_age = db.Column(db.Integer, index=True)
    gender_preference = db.Column(db.String(16), index=True)
    max_distance = db.Column(db.Integer, index=True)

    def __init__(self, user_id, min_age, max_age, gender_preference, max_distance):
        self.user_id = user_id
        self.min_age = min_age
        self.max_age = max_age
        self.gender_preference = gender_preference
        self.max_distance = max_distance

    def __repr__(self):
        return '<User Preference {}>'.format(self.min_age)
    
class user_looking_for(db.Model):
    __tablename__ = 'user_looking_for'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    looking_for = db.Column(db.String(32), index=True) # firendship, dating, networking, etc.

    def __init__(self, user_id, looking_for):
        self.user_id = user_id
        self.looking_for = looking_for

    def __repr__(self):
        return '<User Looking For {}>'.format(self.looking_for)
    
class hobby(db.Model):
    __tablename__ = 'hobby'
    id = db.Column(db.Integer, primary_key=True)
    hobby_name = db.Column(db.String(64), index=True)

    def __init__(self, user_id, hobby_name):
        self.user_id = user_id
        self.hobby_name = hobby_name

    def __repr__(self):
        return '<Hobby {}>'.format(self.hobby_name)

class user_hobbies(db.Model):
    __tablename__ = 'user_hobbies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobby.id'))

    def __init__(self, user_id, hobby_id):
        self.user_id = user_id
        self.hobby_id = hobby_id

    def __repr__(self):
        return '<User Hobby {}>'.format(self.hobby_id)
    
class user_photo(db.Model):
    __tablename__ = 'user_photo'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    photo_url = db.Column(db.String(256), index=True)
    uploaded_at = db.Column(db.DateTime, index=True)

    def __init__(self, user_id, photo_url, uploaded_at):
        self.user_id = user_id
        self.photo_url = photo_url
        self.uploaded_at = uploaded_at

    def __repr__(self):
        return '<User Photo {}>'.format(self.photo_url)
    
class swipe(db.Model):
    __tablename__ = 'swipe'
    id = db.Column(db.Integer, primary_key=True)
    swiper_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    swipee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(16), index=True)
    swiped_at = db.Column(db.DateTime, index=True)

    def __init__(self, swiper_id, swipee_id, action, swiped_at):
        self.swiper_id = swiper_id
        self.swipee_id = swipee_id
        self.action = action
        self.swiped_at = swiped_at

    def __repr__(self):
        return '<Swipe {}>'.format(self.action)
    
class matches(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    matched_at = db.Column(db.DateTime, index=True)
    status = db.Column(db.String(16), index=True)

    def __init__(self, user1_id, user2_id, matched_at, status):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.matched_at = matched_at
        self.status = status # status can be 'active', 'unmatched', 'blocked', etc.

    def __repr__(self):
        return '<Match {}>'.format(self.id)
    
class conversations(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    started_at = db.Column(db.DateTime, index=True)


    def __init__(self, user1_id, user2_id, started_at):
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.started_at = started_at


    def __repr__(self):
        return '<Conversation {}>'.format(self.id)
    
class messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message_text = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, index=True)
    is_read = db.Column(db.Boolean, index=True)

    def __init__(self, conversation_id, sender_id, message_text, sent_at, is_read=False):
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.message_text = message_text
        self.sent_at = sent_at
        self.is_read = is_read

    def __repr__(self):
        return '<Message {}>'.format(self.message_text)
    
class favorites(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    favorite_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    favorited_at = db.Column(db.DateTime, index=True)

    def __init__(self, user_id, favorite_user_id, favorited_at):
        self.user_id = user_id
        self.favorite_user_id = favorite_user_id
        self.favorited_at = favorited_at

    def __repr__(self):
        return '<Favorite {}>'.format(self.id)