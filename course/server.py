from flask import Flask, request, render_template, redirect, session
import sys
sys.path.insert(0, "D:\Программирование\tasks\venv\project")
from loginform import LoginForm
from add_medicine import AddMedForm
from medicines import MedForm
from medicine import MedicineForm
from illness import IllnessForm
from add_illness import AddIllForm
from office import Office
from redact import Redact
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

import pypyodbc


class DB:
    def __init__(self):
        conn = pypyodbc.connect('Driver={SQL Server}; Server=MSI; Database=Справочник_болезней;')
        self.conn = conn
    def get_connection(self):
        return self.conn
    def __del__(self):
        self.conn.close()


db = DB()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Домашняя страница')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user_name = form.username.data
    password = form.password.data
    user_model = UsersModel(db.get_connection())
    if form.validate_on_submit():
        exists = user_model.exists(int(user_name), str(password))
        if exists[0]:
            session['user_id'] = exists[1]
            return redirect('/')
        else:
            return redirect('/login')
    return render_template('login.html', title='Авторизация', form=form)

class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def exists(self, user_name, password_hash):
        password = 'doctor'  # пароль для врачей
        name = 0000  # логин для главврача
        gpassword = 'glavdoctor'  # пароль для главврача
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Врачи WHERE id_врача = ?", (user_name,))
        row = cursor.fetchone()
        if row and password_hash == password:
            return (True, row[0])
        elif user_name == name and password_hash == gpassword:
            return (True, name)
        else:
            return (False,)

class Medicine:
    def __init__(self, connection):
        self.connection = connection

    def insert(self, title, content, cost):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO Лекарства VALUES (?,?,?)", (title, content, cost))
        cursor.close()
        self.connection.commit()

    def get_names(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Название FROM Лекарства")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    def search_by_name(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Название FROM Лекарства WHERE Название LIKE ?+'%'", (str(name),))
        row = cursor.fetchall()
        cursor.close()
        return row
    def redact(self, title, content, cost):
        cursor = self.connection.cursor()
        query = 'UPDATE Лекарства SET Описание = ?, Ср_цена = ? WHERE Название = ?'
        cursor.execute(query, (content, cost, title))
        cursor.close()
        self.connection.commit()
    def Descrip(self, name):
        cursor = self.connection.cursor()
        query="SELECT Описание FROM Лекарства WHERE Название=?"
        cursor.execute(query,(name,))
        row = cursor.fetchone()
        cursor.close()
        return row[0]
    def Cost(self, name):
        cursor = self.connection.cursor()
        query="SELECT Ср_цена FROM Лекарства WHERE Название=?"
        cursor.execute(query,(name,))
        row = cursor.fetchone()
        cursor.close()
        return row[0]

class Doctor:
    def __init__(self, connection):
        self.connection = connection

    def get_doctors(self, fieldid):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id_области FROM Области_медицины WHERE Название=?", (fieldid,))
        field = cursor.fetchone()
        cursor.execute("SELECT ФИО, Телефон, Почта FROM Врачи WHERE Область = ?", (field[0],))
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            row = [x.strip("' ()") for x in str(row).split(",")]
        return rows

    def get_fields(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Название FROM Области_медицины")
        rows = cursor.fetchall()
        cursor.close()

        return rows

    def Office(self, id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM Врачи WHERE id_врача=?", (id,))
        row = cursor.fetchone()
        cursor.close()
        row = [x.strip("' ()") for x in str(row).split(",")]
        return row

    def redact_doct(self, id, fio, tel, mail):
        cursor = self.connection.cursor()
        query = 'UPDATE Врачи SET ФИО = ?, Телефон = ?, Почта = ? WHERE id_врача = ?'
        tel = '(' + tel + ')'
        cursor.execute(query, (fio, tel, mail, id))
        cursor.close()
        self.connection.commit()

class Illness:
    def __init__(self, connection):
        self.connection = connection

    def get_names(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Название FROM Болезни")
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def search_by_name(self, name):
        cursor = self.connection.cursor()
        cursor.execute("SELECT Название FROM Болезни WHERE Название LIKE ?+'%'", (str(name),))
        row = cursor.fetchall()
        cursor.close()
        return row

    def info(self, name):
        cursor = self.connection.cursor()
        cursor.execute('SELECT id_болезни FROM Болезни WHERE Название = ?', (name,))
        id = cursor.fetchone()

        cursor.execute('SELECT Название, Степень_тяжести, Описание FROM Болезни WHERE id_болезни = ?', (id[0],))
        result = []
        res = cursor.fetchone()
        for row in res:
            result.append(row)

        query = 'SELECT Название FROM Диагностика JOIN Болезнь_Диагностика ON( ДиагностикаID = id_диагностики) WHERE БолезньID = ?'
        cursor.execute(query, (id[0],))
        rows = cursor.fetchall()
        rows = [str(x).strip("(),'") for x in rows]
        result.append(rows)

        query = 'SELECT Название FROM Лекарства WHERE id_лекарства IN( SELECT ЛекарствоID FROM Лечение WHERE БолезньID = ?)'
        cursor.execute(query, (id[0],))
        rows = cursor.fetchall()
        rows = [str(x).strip("(),'") for x in rows]
        result.append(rows)

        query = 'SELECT Название FROM Процедуры WHERE id_процедуры IN( SELECT ПроцедураID FROM Лечение WHERE БолезньID = ?)'
        cursor.execute(query, (id[0],))
        rows = cursor.fetchall()
        rows = [str(x).strip("(),'") for x in rows]
        result.append(rows)

        query = 'SELECT Описание FROM Причины JOIN Болезнь_Причина ON( ПричинаID = id_причины) WHERE БолезньID = ?'
        cursor.execute(query, (id[0],))
        rows = cursor.fetchall()
        rows = [str(x).strip("(),'") for x in rows]
        result.append(rows)

        query = 'SELECT Описание FROM Профилактика JOIN Болезнь_Профилактика ON( ПрофилактикаID = id_профилактики) WHERE БолезньID = ?'
        cursor.execute(query, (id[0],))
        rows = cursor.fetchall()
        rows = [str(x).strip("(),'") for x in rows]
        result.append(rows)

        return result

    def insert(self, name, st, descrip, diag, meds, proc, prof):
        cursor = self.connection.cursor()

        cursor.close()
        self.connection.commit()

@app.route('/office', methods=['GET', 'POST'])
def office():
    form = Office()
    doct = Doctor(db.get_connection())
    info = doct.Office(session['user_id'])
    form.id.data = info[0]
    form.fio.data = info[1]
    form.tel.data = info[2]
    form.mail.data = info[3]
    form.field.data = info[4]
    return render_template('office.html', title='Личный кабинет', form= form)

@app.route('/redact', methods=['GET', 'POST'])
def redact():
    form = Redact()
    doct = Doctor(db.get_connection())
    info = doct.Office(session['user_id'])
    form.id.data = info[0]
    form.fio.data = info[1]
    form.tel.data = info[2]
    form.mail.data = info[3]
    form.field.data = info[4]
    if form.validate_on_submit():
        idd = form.id.data
        fio = form.fio.data
        tel = form.tel.data
        mail = form.mail.data
        doct.redact_doct(idd, fio, tel, mail)
        return redirect('/office')
    return render_template('redact.html', title='Редактирование', form=form)

@app.route('/illnesses', methods=['GET', 'POST'])
def illnesses():
    il = Illness(db.get_connection())
    if request.method == 'POST':
        if request.form['action'] == 'Nazvanie':
            name = request.form.get('nazv')
            names = il.search_by_name(name)
        elif request.form['action'] =='Symptom':
            symptoms = request.form.get('symp')
            sympt = [x.strip() for x in symptoms.split(',')]
            if len(sympt) < 3:
                for i in range(3 - len(sympt)):
                    sympt.append('')
            names = il.search_by_symptom(sympt[0],sympt[1],sympt[2])
    else:
        names = il.get_names()
    return render_template('illnesses.html', title='Болезни', names=names)

@app.route('/illness/<name>',  methods=['GET', 'POST'])
def illness(name):
    form = IllnessForm()
    il = Illness(db.get_connection())
    info = il.info(name)
    form.name.data = info[0]
    form.st.data = info[1]
    form.descrip.data = info[2]
    form.diag.data = str(info[3]).strip('[]')
    form.meds.data = str(info[4]).strip('[]')
    form.proc.data = str(info[5]).strip('[]')
    form.causes.data = str(info[6]).strip('[]')
    form.prof.data = str(info[7]).strip('[]')
    return render_template('illness.html', title='Болезнь', form=form, name=name)

@app.route('/add_illness',methods=['GET', 'POST'])
def add_illness():
    form = AddIllForm()
    il = Illness(db.get_connection())
    if form.validate_on_submit():
        name = form.name.data
        st = form.st.data
        descrip = form.descrip.data
        diag = form.diag.data
        meds = form.meds.data
        proc = form.proc.data
        prof = form.prof.data
        il.insert(name, st, descrip, diag, meds, proc, prof)
        return redirect('/illnesses')
    return render_template('add_illness.html', title='Добавление юолезни', word='Добавление', form= form )

@app.route('/redact_illness/<name>', methods=['GET', 'POST'])
def redact_illness(name):
    form = AddIllForm()
    il = Illness(db.get_connection())
    info = il.info(name)
    form.name.data = info[0]
    form.st.data = info[1]
    form.descrip.data = info[2]
    form.diag.data = str(info[3]).strip('[]')
    form.meds.data = str(info[4]).strip('[]')
    form.proc.data = str(info[5]).strip('[]')
    form.causes.data = str(info[6]).strip('[]')
    form.prof.data = str(info[7]).strip('[]')
    if form.validate_on_submit():
        #обработка
        return redirect('/illnesses')
    return render_template('add_illness.html', title='Редактирование болезни', word='Редактирование', form=form)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    form = AddMedForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        cost = form.cost.data
        nm = Medicine(db.get_connection())
        nm.insert(title, content, cost)
        return redirect("/medicines")
    return render_template('add_medicine.html', title='Добавление лекарства', word='Добавление', form=form)

@app.route('/redact_medicine/<name>', methods=['GET','POST'])
def redact_medicine(name):
    form = AddMedForm()
    nm = Medicine(db.get_connection())
    form.title.data = name
    form.content.data = nm.Descrip(name)
    form.cost.data = nm.Cost(name)
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        cost = form.cost.data
        nm = Medicine(db.get_connection())
        nm.redact(title, content, cost)
        return redirect("/medicines")
    return render_template('add_medicine.html', title='Редактирование лекарства', word='Редактирование', form=form)


@app.route('/medicine/<name>', methods=['GET', 'POST'])
def medicine(name):
    form = MedicineForm()
    nm = Medicine(db.get_connection())
    form.name.data = name
    form.descript.data = nm.Descrip(name)
    form.cost.data = nm.Cost(name)
    return render_template('medicine.html', title='Лекарство', name = name, form=form)


@app.route('/medicines', methods=['GET', 'POST'])
def medicines():
    form = MedForm()
    nm = Medicine(db.get_connection())
    if form.validate_on_submit():
        name = form.search.data
        names = nm.search_by_name(str(name))
    else:
        names = nm.get_names()
    return render_template('medicines.html', title='Лекарства', form=form, names=names)

@app.route('/doctors', methods=['GET', 'POST'])
def doctors():
    doct = Doctor(db.get_connection())
    fields = doct.get_fields()
    return render_template('doctors.html', title ='Врачи', fields=fields)

@app.route('/fields/<name>', methods=['GET', 'POST'])
def fields(name):
    doct = Doctor(db.get_connection())
    doctors=doct.get_doctors(name)
    return render_template('fields.html', title='Врачи в выбранной области', name=name, doctors=doctors)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
