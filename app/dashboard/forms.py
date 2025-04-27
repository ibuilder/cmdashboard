# app/dashboard/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class DashboardForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('completed', 'Completed'), ('pending', 'Pending')], validators=[DataRequired()])
    submit = SubmitField('Submit')