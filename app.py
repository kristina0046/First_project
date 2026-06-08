from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "tajny_kluc"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_NDSzGQOrT78J@ep-still-king-alwik2bx-pooler.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(255))
    role = db.Column(db.String(20))

class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    subject = db.Column(db.String(100))
    level = db.Column(db.String(50))
    lesson_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer)

class Registration(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return "Pouzivatel uspesne registrovany"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role
            return redirect("/")
        else:
            return "Nespravny email alebo heslo"
    return render_template("login.html")

@app.route("/create-lesson", methods=["GET", "POST"])
def create_lesson():
    if request.method == "POST":
        title = request.form["title"]
        subject = request.form["subject"]
        level = request.form["level"]
        lesson_date = request.form["lesson_date"]
        description = request.form["description"]

        new_lesson = Lesson(
            title=title,
            subject=subject,
            level=level,
            lesson_date=lesson_date,
            description=description,
            teacher_id=session["user_id"]
        )
        db.session.add(new_lesson)
        db.session.commit()
        return redirect("/lessons")
    return render_template("create_lesson.html")

@app.route("/lessons")
def lessons():
    subject = request.args.get("subject")
    level = request.args.get("level")
    query = Lesson.query
    if subject:
        query = query.filter(Lesson.subject.ilike(f"%{subject}%"))
    if level:
        query = query.filter(Lesson.level.ilike(f"%{level}%"))
    all_lessons = query.all()
    return render_template("lessons.html", lessons=all_lessons)

@app.route("/lesson/<int:lesson_id>")
def lesson_detail(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    return render_template("lesson_detail.html", lesson=lesson)

@app.route("/register-lesson/<int:lesson_id>", methods=["POST"])
def register_lesson(lesson_id):
    new_registration = Registration(
        lesson_id=lesson_id,
        user_id=session["user_id"],
    )
    db.session.add(new_registration)
    db.session.commit()
    return "Bol/a si prihlásený/á na lekciu"

@app.route("/manage-students/<int:lesson_id>")
def manage_students(lesson_id):
    lesson = Lesson.query.get(lesson_id)
    students = db.session.query(User).join(
        Registration, User.id == Registration.user_id).filter(Registration.lesson_id == lesson_id).all()
    return render_template("manage_students.html", lesson=lesson, students=students)
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)