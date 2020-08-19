from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class MedicineForm(FlaskForm):
    name = StringField('Название', render_kw={'class': 'form-control'})
    descript = TextAreaField('Описание', render_kw={'class': 'form-control'})
    cost = StringField('Cредняя цена', render_kw={'class': 'form-control'})