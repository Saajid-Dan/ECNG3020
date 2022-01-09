from flask_wtf import FlaskForm
from flask import flash, redirect
from flask_mail import Message
from app import mail
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length

class Feedback(FlaskForm):
    comment = TextAreaField(label=('What are your thoughts?'), validators=[DataRequired(), Length(min=1, max=250, message='Comment must be between %(min)d and %(max)d characters')])
    option = SelectField('Feedback Topics (in Dropdown)', choices=['Data Displayed', 'Site\'s Performance', 'Site\'s Appearance', 'Other'])
    submit = SubmitField(label=('Submit'))

def form_validate(url, form):
    flash('Feedback Sent Successfully.')
        
    title = form.option.data
    body = form.comment.data

    msg = Message(title, body=body, sender='SDan.Testing@gmail.com', recipients=['SDan.Testing@gmail.com'])
    mail.send(msg)

    form.comment.data = ''

    return redirect(url + "#anchor")