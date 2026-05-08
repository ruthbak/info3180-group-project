# Add any form classes for Flask-WTF here
from flask_wtf import FlaskForm
from datetime import date
from wtforms import DateField, SelectField, StringField, PasswordField, SubmitField, IntegerField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, Length, regexp, Optional, NumberRange, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[InputRequired(), Length(min=8, max=35), regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    firstname= StringField('First Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'First name must contain only letters')])
    lastname= StringField('Last Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'Last name must contain only letters')])
    dob= DateField('Date of Birth', validators=[InputRequired(),])
    latitude = FloatField('Latitude', validators=[DataRequired()])
    longitude = FloatField('Longitude', validators=[DataRequired()])
    location_name = StringField('Location Name', validators=[InputRequired(), Length(max=100)])
    gender= SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[InputRequired()])
    lookingfor= SelectField('Looking for', choices=[('dating', 'Dating'), ('friendship', 'Friendship'), ('relationship', 'Relationship')], validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=12, max=128), regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$', 0, 'Password must be at least 12 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=12, max=128), regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$', 0, 'Password must be at least 12 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character')])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[Optional(), Length(min=8, max=35), regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    firstname= StringField('First Name', validators=[Optional(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'First name must contain only letters')])
    lastname= StringField('Last Name', validators=[Optional(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'Last name must contain only letters')])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    interests = StringField('Interests', validators=[Optional(), Length(max=200)])
    interested_in = StringField('Interested In', validators=[InputRequired(message='Please select who you are interested in'), Length(min=4,max=6), regexp('^[A-Za-z]+$', 0, 'Interested in must contain only letters')])
    min_age = IntegerField('Minimum Age',validators=[Optional(),NumberRange(min=18, max=100, message='Minimum age must be between 18 and 100')])
    max_age = IntegerField('Maximum Age',validators=[Optional(),NumberRange(min=18, max=100, message='Maximum age must be between 18 and 100')])
    photo = FileField('Profile Picture', validators=[Optional(),FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    max_distance = IntegerField('Maximum Distance',validators=[Optional(),NumberRange(min=1, max=200000, message='Distance must be between 1 and 200000')])
    submit = SubmitField('Update Profile')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[InputRequired(), Length(max=1000), regexp('^[A-Za-z0-9 .,!?@#$%^&*()_+-=]*$', 0, 'Message can only contain letters, numbers, spaces, and basic punctuation') ])
    submit = SubmitField('Send Message')
