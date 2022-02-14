from flask_wtf import FlaskForm
from flask import flash, redirect, Response
from flask_mail import Message
from app import mail
from wtforms import TextAreaField, SelectField, SubmitField, StringField
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms.widgets import TextArea



class Feedback(FlaskForm):
    comment = TextAreaField(label=('What are your thoughts?'), validators=[DataRequired(), Length(min=1, max=250, message='Comment must be between %(min)d and %(max)d characters')])
    option = SelectField('Feedback Topics (in Dropdown)', choices=['Data Displayed', 'Site\'s Performance', 'Site\'s Appearance', 'Other'])
    submit = SubmitField(label=('Submit'))

def form_validate(url, form):
    if form.submit.data and form.validate_on_submit():

        flash('Feedback Sent Successfully.')
            
        title = form.option.data
        body = form.comment.data

        msg = Message(title, body=body, sender='SDan.Testing@gmail.com', recipients=['SDan.Testing@gmail.com'])
        mail.send(msg)

        form.comment.data = ''

    return redirect(url + "#anchor")



class Machine_format(FlaskForm):
    tables = SelectField('tables', choices=[])
    columns = SelectField('columns', choices=[])
    values = SelectField('values', choices=[])
    formats = SelectField('formats', choices=[('CSV', 'CSV'), ('JSON', 'JSON'), ('XML', 'XML')])
    comment = StringField(label='Output', widget=TextArea())
    previous = StringField(label='Previous Selection', widget=TextArea())
    populate = SubmitField(label=('Reset Selection'))
    query = SubmitField(label=('Preview Selection'))
    generate = SubmitField(label=('Submit Selection'))

class Report(FlaskForm):
    save = SubmitField(label=('Download PDF Report'))


