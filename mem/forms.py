from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_login import current_user
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email, email_validator
from mem.models import User
from flask import flash, redirect, url_for, render_template

class SignUp(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=10)])
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                                validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirm Password', 
                                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
            user_with_username = User.query.filter_by(username=username.data).first()
            if user_with_username:
                flash('Username already taken! Please choose a different one.', 'danger')
                raise ValidationError('Username already taken!')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account with that email already exists', 'danger')

        
    
            
    
class signin(FlaskForm):
    email = StringField('Email', 
                            validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                                validators=[DataRequired()])
    remember = BooleanField('Remember Me?')
    submit = SubmitField('Login')




class UpdateProfileForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    about_me = TextAreaField('AboutMe', 
                           validators=[Length(max=120)])

    pfp = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Save Changes')

    def validate_username(self, username):
        if username.data != current_user.username:
            user_with_username = User.query.filter_by(username=username.data).first()
            if user_with_username:
                flash('Username already taken! Please choose a different one.', 'danger')
                raise ValidationError('Username already taken!')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with that email already exists!')
            

class CreatePost(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Goof Description', validators=[DataRequired(), Length(max=300)])
    meme = FileField('Meme Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    video = FileField('Meme Video', validators=[FileAllowed(['mp4'])])
    submit = SubmitField('Create Mem!')
    submitU = SubmitField('Update Mem!')


class Search(FlaskForm):
    searched = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                            validators=[DataRequired(), Email()])
    submit = SubmitField('Request A Password Reset')
            

class ResetPasswordForm(FlaskForm):
        password = PasswordField('Password', 
                                validators=[DataRequired(), Length(min=8)])
        password_confirm = PasswordField('Confirm Password', 
                                            validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Reset Password')
    
    