from flask import Flask, render_template, redirect
from data import db_session
from forms.user import RegisterForm, LoginForm
from forms.question import QuestionForm
from forms.answer import AnswerForm
from data.users import User
from data.questions import Questions
from data.answers import Answers
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
import datetime


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader 
def load_user(user_id):
    global user
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user


@app.route('/', methods=['GET'])
def home():
    return render_template("home.html", title="Главная страница")


@app.route('/questions/<catalog_id>')
def questions(catalog_id):
    global user
    db_sess = db_session.create_session()
    questions = db_sess.query(Questions).filter(Questions.catalog_id == catalog_id).all()
    return render_template('questions.html', catalog_id=catalog_id, questions=questions, title="Вопросы")

@app.route('/questions/<catalog_id>/<question_id>', methods=['GET', 'POST'])
def answers(catalog_id, question_id):
    global user
    form = AnswerForm()
    db_sess = db_session.create_session()
    question = db_sess.query(Questions).filter(Questions.question_id == question_id,
                                               Questions.catalog_id == catalog_id).first()
    answers = db_sess.query(Answers).filter(Answers.question_id == question_id,
                                            Answers.catalog_id == catalog_id).all()
    if form.validate_on_submit():
        if not form.answer:
            return render_template("answers.html", title="Ответы на вопрос", question=question, answers=answers, 
                            catalog_id=catalog_id, form=form, message="Ответ не должен быть пустым")
        answer = Answers(
            answer=form.answer.data,
            author=user.name,
            datetime=str(datetime.datetime.now())[:16],
            catalog_id=catalog_id,
            question_id=question_id,
        )
        db_sess.add(answer)
        db_sess.commit()
        return redirect("/questions/" + catalog_id + "/" + question_id)
    return render_template("answers.html", title="Ответы на вопрос", question=question, answers=answers, 
                        catalog_id=catalog_id, form=form)    

@app.route('/create_question/<catalog_id>', methods=['GET', 'POST'])
def create_question(catalog_id):
    global user
    form = QuestionForm()
    if form.validate_on_submit():
        if not form.title:
            return render_template('create_question.html', form=form, title="Создание вопроса", 
                                   message="Заголовок не может быть пустым", catalog_id=catalog_id)
        db_sess = db_session.create_session()
        length = len(db_sess.query(Questions).filter(Questions.catalog_id == catalog_id).all())
        question = Questions(
            title=form.title.data,
            content=form.content.data,
            author=user.name,
            datetime=str(datetime.datetime.now())[:16],
            catalog_id=catalog_id,
            question_id=str(length + 1),
        )
        db_sess.add(question)
        db_sess.commit()
        return redirect("/questions/" + catalog_id)
    return render_template('create_question.html', title="Создание вопроса", form=form, catalog_id=catalog_id)

@app.route('/redactor/<id>', methods=['GET', 'POST'])
def redactor():
    form = QuestionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        question = Questions(
            title=form.title.data,
            content=form.content.data,
            author=user.name,
            datetime=str(datetime.datetime.now())[:16],
            catalog_id=catalog_id,
            question_id=str(length + 1)
        )
        db_sess.merge(question)
        db_sess.commit()
        return redirect('/')
    return render_template('redactor.html', title='Изменение вопроса', 
                           form=form)

@app.route('/register', methods=['GET', 'POST'])    
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Этот электронный адрес уже зарегистрирован")
        user = User(
            name=form.name.data,
            email=form.email.data,
            hashed_password=generate_password_hash(form.password.data)
        )
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()