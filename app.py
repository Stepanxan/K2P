from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:19982804@localhost:3306/K2P'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "59ceec65a970fa3b1a00830e53081eb6f565c272"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


with app.app_context():
    db.create_all()
    migrate.init_app(app, db)

from routes.routes import *

if __name__ == '__main__':
    app.run(debug=True)
