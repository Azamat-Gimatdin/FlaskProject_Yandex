from flask import Flask, render_template, redirect, request
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
    """Загружает пользователя из базы данных по user_id для Flask-Login."""
    global user
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    return user

@app.route('/', methods=['GET'])
def home():
    """Отображает главную страницу (home.html)."""
    return render_template("home.html", title="Главная страница")

@app.route('/my_questions')
def my_questions():
    """Загружает из БД все объекты Questions и передаёт их в шаблон my_questions.html."""
    try:
        global user
        db_sess = db_session.create_session()
        questions = db_sess.query(Questions).all()
        return render_template("my_questions.html", title="Мои вопросы", questions=questions, user=user)
    except:
        return redirect("/logout")

@app.route('/questions/<catalog_id>')
def questions(catalog_id):
    """Отображает список вопросов, относящихся к заданному catalog_id."""
    global user
    try:
        db_sess = db_session.create_session()
        questions = db_sess.query(Questions).filter(Questions.catalog_id == catalog_id).all()
        return render_template('questions.html', catalog_id=catalog_id, user=user, questions=questions, title="Вопросы")
    except:
        return render_template('questions.html', catalog_id=catalog_id, user="", questions=questions, title="Вопросы")


@app.route('/questions/<catalog_id>/<question_id>', methods=['GET', 'POST'])
def answers(catalog_id, question_id): 
    """Показывает вопрос и список ответов на него, обрабатывает отправку нового ответа"""
    global user
    try:
        form = AnswerForm()
        db_sess = db_session.create_session()
        question = db_sess.query(Questions).filter(Questions.question_id == question_id,
                                                Questions.catalog_id == catalog_id).first()
        answers = db_sess.query(Answers).filter(Answers.question_id == question_id,
                                                Answers.catalog_id == catalog_id).all()
        if form.validate_on_submit():
            if not form.answer:
                return render_template("answers.html", title="Ответы на вопрос", question=question, answers=answers, 
                                catalog_id=catalog_id, user=user, form=form, message="Ответ не должен быть пустым")
            answer = Answers(
                answer=form.answer.data,
                author=user.name,
                datetime=str(datetime.datetime.now())[:16],
                catalog_id=catalog_id,
                question_id=question_id,
                user_id=user.id
            )
            db_sess.add(answer)
            db_sess.commit()
            return redirect("/questions/" + catalog_id + "/" + question_id)
        return render_template("answers.html", title="Ответы на вопрос", question=question, answers=answers, 
                            catalog_id=catalog_id, form=form, user=user)
    except:
        return redirect("/logout")

@app.route('/create_question/<catalog_id>', methods=['GET', 'POST'])
def create_question(catalog_id):
    """Создание нового вопроса в заданном каталоге."""
    global user
    try:
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
                user_id=user.id
            )
            db_sess.add(question)
            db_sess.commit()
            return redirect("/questions/" + catalog_id)
        return render_template('create_question.html', title="Создание вопроса", form=form, catalog_id=catalog_id)
    except:
        return redirect("/logout")

@app.route('/question_redactor/<catalog_id>/<question_table_id>', methods=['GET', 'POST'])
def question_redactor(catalog_id, question_table_id):
    """Редактирует существующий вопрос."""
    global user
    try:
        form = QuestionForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            question = db_sess.query(Questions).filter(Questions.id == question_table_id).first()
            form.title.data = question.title
            form.content.data = question.content
        if form.validate_on_submit():
            if not form.title:
                return render_template('question_redactor.html', form=form, title="Редактирование вопроса", 
                                    message="Заголовок не может быть пустым", 
                                    catalog_id=catalog_id, question_table_id=question_table_id)
            db_sess = db_session.create_session()
            question = db_sess.query(Questions).filter(Questions.id == question_table_id).first()
            question.title = form.title.data
            question.content = form.content.data
            question.datetime = "Изменено - " + str(datetime.datetime.now())[:16]
            db_sess.commit()
            return redirect('/')
        return render_template('question_redactor.html', title='Редактирование вопроса', catalog_id=catalog_id,
                            form=form)
    except:
        return redirect("/logout")
    
@app.route('/answer_redactor/<answer_table_id>', methods=['GET', 'POST'])
def answer_redactor(answer_table_id):
    """Редактирует существующий ответ."""
    global user
    try:
        form = AnswerForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            answer = db_sess.query(Answers).filter(Answers.id == answer_table_id).first()
            form.answer.data = answer.answer
        if form.validate_on_submit():
            if not form.answer:
                return render_template('answer_redactor.html', form=form, title="Редактирование ответа", 
                                    message="Ответ не может быть пустым", 
                                    catalog_id=answer.catalog_id, question_id=answer.question_id)
            db_sess = db_session.create_session()
            answer = db_sess.query(Answers).filter(Answers.id == answer_table_id).first()
            answer.answer = form.answer.data
            answer.datetime = "Изменено - " + str(datetime.datetime.now())[:16]
            db_sess.commit()
            return redirect('/')
        return render_template('answer_redactor.html', title='Редактирование ответа', catalog_id=answer.catalog_id,
                            form=form, question_id=answer.question_id)
    except:
        return redirect("/logout")

@app.route('/answer_delete/<answer_table_id>', methods=['GET', 'POST'])
def answer_delete(answer_table_id):
    """Удаляет ответ по его id из БД."""
    db_sess = db_session.create_session()
    answer = db_sess.query(Answers).filter(Answers.id == answer_table_id).first()
    db_sess.delete(answer)
    db_sess.commit()
    return redirect('/')

@app.route('/question_delete/<question_table_id>', methods=['GET', 'POST'])
def question_delete(question_table_id):
    """Удаляет вопрос по его id из БД."""
    db_sess = db_session.create_session()
    question = db_sess.query(Questions).filter(Questions.id == question_table_id).first()
    db_sess.delete(question)
    db_sess.commit()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])    
def register():
    """Обрабатывает регистрацию пользователя."""
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
    """Авторизация пользователя."""
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
    """Завершает сессию пользователя."""
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
