from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class AddIllForm(FlaskForm):
    name = StringField('Название', render_kw={'class': 'form-control'})
    st = StringField('Степень тяжести', render_kw={'class': 'form-control'})
    descrip = TextAreaField('Описание', render_kw={'class': 'form-control'})
    diag = TextAreaField('Методы диагностики', render_kw={'class': 'form-control'})
    meds = TextAreaField('Лекарства', render_kw={'class': 'form-control'})
    proc = TextAreaField('Процедуры', render_kw={'class': 'form-control'})
    causes = TextAreaField('Причины',render_kw={'class': 'form-control'})
    prof = TextAreaField('Методы профилактики',render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить')
