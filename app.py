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


# Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="myflaskapp",
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)


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
    finally:
        # Close the connection
        cursor.close()


@app.route("/article/<string:id>")
def article(id):
    return render_template("article.html", id=id)


@app.route("/about")
def about():
    return render_template("about.html")


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
        finally:
            # Close the connection
            connection.close()

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

        finally:
            # Close the connection
            connection.close()

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
