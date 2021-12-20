from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class Feedback(FlaskForm):
    comment = TextAreaField('What are your thoughts?', validators=[DataRequired(), Length(1, 250)])
    option = SelectField('Feedback Topics (in Dropdown)', choices=['Data Displayed', 'Site\'s Performance', 'Site\'s Appearance', 'Other'])
    submit = SubmitField('Submit')