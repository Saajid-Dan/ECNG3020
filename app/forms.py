from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Length

class Feedback(FlaskForm):
    comment = TextAreaField(label=('What are your thoughts?'), validators=[DataRequired(), Length(min=1, max=250, message='Comment must be between %(min)d and %(max)d characters')])
    option = SelectField('Feedback Topics (in Dropdown)', choices=['Data Displayed', 'Site\'s Performance', 'Site\'s Appearance', 'Other'])
    submit = SubmitField(label=('Submit'))