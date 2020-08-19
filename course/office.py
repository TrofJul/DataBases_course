from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class Office(FlaskForm):
    id = StringField('id', render_kw={'class': 'form-control'})
    fio = StringField('ФИО', render_kw={'class': 'form-control'})
    tel = StringField('Телефон', render_kw={'class': 'form-control'})
    mail = StringField('Почта', render_kw={'class': 'form-control'})
    field = StringField('Область медицины', render_kw={'class': 'form-control'})