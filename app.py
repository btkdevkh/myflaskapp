from flask import (
    Flask,
    request,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    logging,
)
import pymysql.cursors
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)


# Classes
class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = StringField(
        "Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Password do not match"),
        ],
    )
    confirm = PasswordField("Confirm Password")


class CreateForm(Form):
    title = StringField("Title", [validators.Length(min=1, max=30)])
    body = TextAreaField("Description", [validators.Length(min=30)])


class ArticleForm(Form):
    title = StringField("Title")
    body = TextAreaField("Description")


# Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="myflaskapp",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


# Helpers
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unautorized, Please login", "danger")
            return redirect(url_for("login"))

    return wrap


# Routes
@app.route("/")
def index():
    return render_template("home.html")


@app.route("/articles")
def articles():
    try:
        with connection.cursor() as cursor:
            # Articles
            sql = "SELECT * FROM `articles`"
            cursor.execute(sql)
            Articles = cursor.fetchall()

            return render_template("articles.html", articles=Articles)
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")


@app.route("/create", methods=["GET", "POST"])
@is_logged_in
def create():
    form = CreateForm(request.form)

    if request.method == "POST" and form.validate():
        title = form.title.data
        body = form.body.data

        try:
            # Articles
            with connection.cursor() as cursor:
                sql = "INSERT INTO `articles` (title, body, author) VALUES(%s, %s, %s)"
                cursor.execute(sql, (title, body, session["username"]))

                # Commit to DB
                connection.commit()

                flash("Article created", "success")

                return redirect(url_for("articles"))

        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")

    return render_template("create.html", form=form)


@app.route("/update/<string:id>", methods=["GET", "POST"])
@is_logged_in
def update(id):
    form = ArticleForm(request.form)

    try:
        # Articles
        with connection.cursor() as cursor:
            sql = "SELECT * FROM articles WHERE id = %s"
            cursor.execute(sql, (id))
            data = cursor.fetchone()

            form.title.data = data["title"]
            form.body.data = data["body"]

            if request.method == "POST" and form.validate():
                title = request.form["title"]
                body = request.form["body"]

                sql = "UPDATE articles SET title = %s, body = %s WHERE id = %s"
                cursor.execute(sql, (title, body, id))

                # Commit to DB
                connection.commit()

                flash("Article edited", "success")
                return redirect(url_for("articles"))
            return render_template("update.html", form=form)

    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")


@app.route("/article/<string:id>")
def article(id):
    try:
        # Articles
        with connection.cursor() as cursor:
            sql = "SELECT * FROM articles WHERE id = %s"
            result = cursor.execute(sql, (id))

            if result > 0:
                data = cursor.fetchone()
                return render_template("article.html", article=data)
            else:
                error = "Username not found"
                return render_template("login.html", error=error)

    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        try:
            # Articles
            with connection.cursor() as cursor:
                sql = "INSERT INTO `users` (name, email, username, password) VALUES(%s, %s, %s, %s)"
                cursor.execute(sql, (name, email, username, password))

                connection.commit()

                flash("You are now registered and can log in", "success")

                return redirect(url_for("index"))

        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password_input = request.form["password"]

        try:
            # Articles
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username = %s"
                result = cursor.execute(sql, (username))

                if result > 0:
                    data = cursor.fetchone()
                    password = data["password"]

                    if sha256_crypt.verify(password_input, password):
                        session["logged_in"] = True
                        session["username"] = username

                        flash("You are now logged in", "success")

                        return redirect(url_for("dashboard"))
                    else:
                        error = "Invalid login"
                        return render_template("login.html", error=error)

                else:
                    error = "Username not found"
                    return render_template("login.html", error=error)

        except pymysql.Error as e:
            print(f"Error connecting to MySQL: {e}")

    return render_template("login.html")


@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


# Debug
if __name__ == "__main__":
    app.secret_key = "Bella123"
    app.run(debug=True)
