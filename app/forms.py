# Add any form classes for Flask-WTF here
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, PasswordField, SubmitField, IntegerField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, InputRequired, NumberRange, Length, regexp, optional
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[InputRequired(), Length(min=8, max=35), regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    firstname= StringField('First Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'First name must contain only letters')])
    lastname= StringField('Last Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'Last name must contain only letters')])
    dob= DateField('Date of Birth', validators=[InputRequired()])
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
    username = StringField('Username', validators=[InputRequired(), Length(min=8, max=35), regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')])
    firstname= StringField('First Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'First name must contain only letters')])
    lastname= StringField('Last Name', validators=[InputRequired(), Length(min=2, max=50), regexp('^[A-Za-z]+$', 0, 'Last name must contain only letters')])
    age = IntegerField('Age', validators=[NumberRange(min=18, max=120)])
    location = StringField('Location', validators=[Length(max=100)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    interests = StringField('Interests', validators=[Length(max=200)])

    photo = FileField('Profile Picture', validators=[
    FileRequired(),
    FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Update Profile')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[InputRequired(), Length(max=1000), regexp('^[A-Za-z0-9 .,!?@#$%^&*()_+-=]*$', 0, 'Message can only contain letters, numbers, spaces, and basic punctuation') ])
    submit = SubmitField('Send Message')