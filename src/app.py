from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/square/<int:number>")
def square(number):
    return str(number ** 2)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
