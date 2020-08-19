from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AddMedForm(FlaskForm):
    title = StringField('Название лекарcтва', validators=[DataRequired()],render_kw={'class': 'form-control'})
    content = TextAreaField('Описание',render_kw={'class': 'form-control'})
    cost = StringField('Средняя цена',render_kw={'class': 'form-control'})
    submit = SubmitField('Сохранить')
