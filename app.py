from flask import Flask, render_template, flash, redirect, url_for, session, logging
import pymysql.cursors
app = Flask(__name__)


# Connect to the database
connection = pymysql.connect(
  host='localhost',
  user='root',
  password='',
  database='myflaskapp',
  cursorclass=pymysql.cursors.DictCursor
)

with connection:
  with connection.cursor() as cursor:

    # Articles
    sql = "SELECT * FROM `articles`"
    cursor.execute(sql)
    Articles = cursor.fetchall()

# Routes
@app.route('/')
def index():
    return render_template('home.html')

    
@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>')
def article(id):
  return render_template('article.html', id = id)

@app.route('/about')
def about():
    return render_template('about.html')

# Debug
if __name__ == '__main__':
  app.run(debug=True)
  