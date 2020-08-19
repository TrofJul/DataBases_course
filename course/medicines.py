from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class MedForm(FlaskForm):
    search = StringField('Введите название лекарства', validators=[DataRequired()])
    submit = SubmitField('Искать')