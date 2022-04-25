import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import json
from datetime import datetime

jsonData = json.load(open('jsonData.json'))


app = Flask(__name__)
api = Api(app)
ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost/books_page'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bpyhmblqncxcfz:d1eb1b543181ce0e7c5e4b4bc750bba919d27ffb89486fcf51d128a32535c314@ec2-54-80-122-11.compute-1.amazonaws.com:5432/d3c9ooetnktt5n'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Books(db.Model):
    __tablename__ = 'Books'
    ISBN = db.Column(db.String(100), primary_key=True)
    Title = db.Column(db.String(200))
    Author = db.Column(db.String(200))
    noOfPages = db.Column(db.String(20))
    Cover = db.Column(db.String(400))
    Language = db.Column(db.String(200))
    dateOfPublication = db.Column(db.String(15))

    def __init__(self, ISBN, Title, Author, dateOfPublication, noOfPages, Cover, Language):
        self.ISBN = ISBN
        self.Title = Title
        self.Author = Author
        self.dateOfPublication = dateOfPublication
        self.noOfPages = noOfPages
        self.Cover = Cover
        self.Language = Language


class booksList(Resource):
    def get(self):
        data = []
        for book in Books.query.all():
            data.append({
                "ISBN": book.ISBN,
                "Title": book.Title,
                "Author": book.Author,
                "noOfPages": book.noOfPages,
                "Cover": book.Cover,
                "Language": book.Language,
                "dateOfPublication": book.dateOfPublication}
                )
        return data


class booksListSearch(Resource):
    def get(self, name, type):
        name = name
        type = type.capitalize()
        data = []
        for book in Books.query.all():
            data.append({
                "ISBN": book.ISBN,
                "Title": book.Title,
                "Author": book.Author,
                "noOfPages": book.noOfPages,
                "Cover": book.Cover,
                "Language": book.Language,
                "dateOfPublication": book.dateOfPublication}
                )
        data2 = []
        if type == "Date":
            data3 = []
            date1 = name.split("~")[0]
            date2 = name.split("~")[1]
            date1 = datetime.strptime(date1, '%d-%M-%Y')
            date2 = datetime.strptime(date2, '%d-%M-%Y')
            for book in data:
                if book["dateOfPublication"] == "missing data":
                    data3.append(book)
                elif len(book["dateOfPublication"]) == 4:
                    relDate = datetime.strptime(book["dateOfPublication"]+"-01-01", '%Y-%M-%d')
                    if relDate >= date1 and relDate <= date2:
                        data2.append(book)
                elif len(book["dateOfPublication"]) == 7:
                    relDate = datetime.strptime(book["dateOfPublication"]+"-01", '%Y-%M-%d')
                    if relDate >= date1 and relDate <= date2:
                        data2.append(book)
                else:
                    relDate = datetime.strptime(book["dateOfPublication"], '%Y-%M-%d')
                    if relDate >= date1 and relDate <= date2:
                        data2.append(book)
            return data2 + data3
        else:
            for book in data:
                if name.lower() in book[type].lower():
                    data2.append(book)
            return data2


api.add_resource(booksList, "/api/bookslist")
api.add_resource(booksListSearch, "/api/bookslist/search/<string:type>/<string:name>")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/title', methods=['POST'])
def search_title():
    if request.method == 'POST':
        searchq2 = "title/" + request.form['title']
    return render_template('index.html', searchq=searchq2)


@app.route('/search/author', methods=['POST'])
def search_author():
    if request.method == 'POST':
        searchq2 = "author/" + request.form['author']
    return render_template('index.html', searchq=searchq2)


@app.route('/search/language', methods=['POST'])
def search_language():
    if request.method == 'POST':
        searchq2 = "language/" + request.form['language']
    return render_template('index.html', searchq=searchq2)


@app.route('/search/date', methods=['POST'])
def search_date():
    if request.method == 'POST':
        searchq2 = "date/" + request.form['date1'] + "~" + request.form["date2"]
    return render_template('index.html', searchq=searchq2)


#@app.route('/submit')
#def submit():
#    data = Book(ISBN, Title, Author, dateOfPublication, noOfPages, Cover, Language)
#    db.session.add(data)
#    db.session.commit()

#for x in jsonData:
#    #print(x["dateOfPublication"].strftime("%m/%d/%Y"))
#    #print(x["Author"])
#    data = Books(x["ISBN"], x["Title"], x["Author"], x["dateOfPublication"], x["noOfPages"], x["Cover"], x["Language"])
#    db.session.add(data)
#    db.session.commit()


if __name__ == '__main__':
    app.run()
