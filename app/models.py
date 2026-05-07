from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class user(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    visibility = db.Column(db.Boolean, index=True, default=True)  # True means visible to others, False means hidden
    joined_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relationships
    profile = db.relationship('user_profile', backref='user', uselist=False, cascade="all, delete-orphan")
    location = db.relationship('user_location', backref='user', uselist=False, cascade="all, delete-orphan")
    preferences = db.relationship('user_preferences', backref='user', uselist=False)
    looking_for = db.relationship('user_looking_for', backref='user', uselist=False)
    photos = db.relationship('user_photo', backref='user', lazy='dynamic')
    hobbies = db.relationship('hobby', secondary='user_hobbies', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username, email, password_hash, visibility=True, joined_at=None, updated_at=None, last_seen=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.visibility = visibility
        self.joined_at = joined_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.last_seen = last_seen or datetime.utcnow()


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class user_profile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    dob = db.Column(db.Date, index=True)
    gender = db.Column(db.String(16), index=True)
    description = db.Column(db.String(256), index=True)

    def __repr__(self):
        return '<User Profile {}>'.format(self.first_name)
        
class user_location(db.Model):
    __tablename__ = 'user_location'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False, unique=True)
    location_name = db.Column(db.String(64), index=True)
    latitude = db.Column(db.Float, index=True)
    longitude = db.Column(db.Float, index=True)

    def __repr__(self):
        return '<User Location {}>'.format(self.location_name)
    
class user_preferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False, unique=True)
    min_age = db.Column(db.Integer, index=True)
    max_age = db.Column(db.Integer, index=True)
    gender_preference = db.Column(db.String(16), index=True)
    max_distance = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<User Preference {}>'.format(self.min_age)
    
class user_looking_for(db.Model):
    __tablename__ = 'user_looking_for'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=False, unique=True)
    looking_for = db.Column(db.String(32), index=True) # firendship, dating, networking, etc.

    def __repr__(self):
        return '<User Looking For {}>'.format(self.looking_for)
    
class hobby(db.Model):
    __tablename__ = 'hobby'
    id = db.Column(db.Integer, primary_key=True)
    hobby_name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Hobby {}>'.format(self.hobby_name)

class user_hobbies(db.Model):
    __tablename__ = 'user_hobbies'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hobby_id = db.Column(db.Integer, db.ForeignKey('hobby.id'))

class user_photo(db.Model):
    __tablename__ = 'user_photo'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    photo_url = db.Column(db.String(256), index=True)
    uploaded_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<User Photo {}>'.format(self.photo_url)
    
class likes(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    swiper_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    swipee_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(16), index=True)
    action_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('swiper_id','swipee_id',name='unique_like'),)

    def __repr__(self):
        return '<Like {}>'.format(self.action)
    
class match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    matched_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    status = db.Column(db.String(16), index=True)

    __table_args__ = (db.UniqueConstraint('user1_id','user2_id',name='unique_match'),)

    def __repr__(self):
        return '<Match {}>'.format(self.id)
    
class conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    last_message = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user1_id','user2_id',name='unique_conversation'),)

    messages = db.relationship('message', backref='conversation', lazy='dynamic')

    def __repr__(self):
        return '<Conversation {}>'.format(self.id)
    
class message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    message_text = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, index=True)

    def __repr__(self):
        return '<Message {}>'.format(self.message_text)
    
class favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    favorite_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    favorited_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Favorite {}>'.format(self.id)