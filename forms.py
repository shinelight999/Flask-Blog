""" Forms for blog app
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    """ Form for registering a new user
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=100)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                     EqualTo('password', message='Passwords Must Match')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    """ Form for logging in a user
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    """ Form for creating a post 
    """
    header = StringField('Header', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Create Post')
    