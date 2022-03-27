from app import app
from flask import flash, redirect, Response
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField, StringField
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms.widgets import TextArea

# Import the send_email function
from app.email import send_email

class Feedback(FlaskForm):
    ''' Feedback form class '''
    # Feedback text box with length validation and data required validation
    comment = TextAreaField(label=('What are your thoughts?'), validators=[DataRequired(), Length(min=1, max=250, message='Comment must be between %(min)d and %(max)d characters')])
    # Feedback dropdown
    option = SelectField('Feedback Topics (in Dropdown)', choices=['Data Displayed', 'Site\'s Performance', 'Site\'s Appearance', 'Other'])
    # Submit button
    submit = SubmitField(label=('Submit'))

def form_validate(url, form):
    ''' This function validates the data entered into the form class and emails it to an auth account '''
    # If submit button pressed and validation successful
    if form.submit.data and form.validate_on_submit():
        # Flash message
        flash('Feedback Sent Successfully.')
            
        title = form.option.data        # Email title
        body = form.comment.data        # Email body
        send_email(title, body)         # Send feedback via email

        form.comment.data = ''          # Reset feedback textbox

    return redirect(url + "#anchor")    # Redirect page to the feedback form

class Machine_format(FlaskForm):
    ''' Form class to query a machine format and generate/download a preview '''
    tables = SelectField('tables', choices=[])          # Database tables dropdown
    columns = SelectField('columns', choices=[])        # Database columns dropdown
    values = SelectField('values', choices=[])          # Database values dropdown
    # Available machine formats
    formats = SelectField('formats', choices=[('CSV', 'CSV'), ('JSON', 'JSON'), ('XML', 'XML')])
    preview = StringField(label='Preview', widget=TextArea())   # Database query preview
    reset = SubmitField(label=('Reset Selection'))      # Reset dropdowns button
    query = SubmitField(label=('Submit Selection'))     # Download query button

class Report(FlaskForm):
    ''' Form class to download a report '''
    save = SubmitField(label=('Create a Report'))       # button