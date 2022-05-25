from flask import Flask
from flask_restful import Api
import json
from datetime import datetime
from db_model import db_model
from rest_api import rest_api
from user.routing import routing
app = Flask(__name__)
app.register_blueprint(routing, url_prefix="")
app.secret_key = "don't tell anyone"
api = Api(app)
ENV = 'dev'

if ENV == 'dev':
    configLocal = open('configLocal.txt', 'r').read()
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = configLocal
else:
    configHeroku = open('configheroku.txt', 'r').read()
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = configHeroku

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db, Book = db_model(app)
booksList, booksListSearch = rest_api(db, Book)
api.add_resource(booksList, "/api/bookslist")
api.add_resource(booksListSearch, "/api/bookslist/search")


def addToDataBaseFromJSON(jsonData):
    for x in jsonData:
        book = Book(
            x["isbn"], x["title"], x["author"], x["date_of_publication"],
            x["pages_number"], x["cover"], x["language"]
                    )
        db.session.add(book)
        db.session.commit()


jsonData = json.load(open('jsonData.json'))


if __name__ == '__main__':
    app.run()
