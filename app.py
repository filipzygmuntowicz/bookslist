import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import json
from datetime import datetime


app = Flask(__name__)
api = Api(app)
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres123@localhost/books_page'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zglfmsrdjqtvwy:bd5d11e9973b2330f3121a135967fdbc34798ab4c53ecfc42cc99c472dd6743a@ec2-63-32-248-14.eu-west-1.compute.amazonaws.com:5432/d5kctntdrd9vnk'

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


def keyNoExistHandle(dict, key):
    if key not in list(dict.keys()):
        return "missing data"
    else:
        return dict[key]


def requestFromGoogleBooks(query):
    books=[]
    http = "https://www.googleapis.com/books/v1/volumes"
    data = requests.get(http+query)
    data = data.json()
    for x in data["items"]:
        Author = keyNoExistHandle(x["volumeInfo"], "authors")
        Title = keyNoExistHandle(x["volumeInfo"], "title")
        noOfPages = keyNoExistHandle(x["volumeInfo"], "pageCount")
        thumbnails = keyNoExistHandle(x["volumeInfo"], "imageLinks")
        if thumbnails != "missing data":
            Cover = thumbnails["smallThumbnail"]
        else:
            Cover = "missing data"
        dateOfPublication = keyNoExistHandle(x["volumeInfo"], "publishedDate")
        Language = keyNoExistHandle(x["volumeInfo"], "language")
        ISBN = keyNoExistHandle(x["volumeInfo"], "industryIdentifiers")
        if Author == "missing data":
            Author = ["missing data"]
        if ISBN != "missing data":
            for x in ISBN:
                if x["type"] == "ISBN_13":
                    ISBN = x["identifier"]
                    break
        if isinstance(ISBN, str) == False:
            for x in ISBN:
                if x["type"] == "OTHER":
                    ISBN = x["identifier"]
                    break
        books.append({
                    "ISBN": ISBN,
                    "Title": Title,
                    "Author": ', '.join([str(item) for item in Author]),
                    "noOfPages": noOfPages,
                    "Cover": Cover,
                    "Language": Language,
                    "dateOfPublication": dateOfPublication}
                    )
    return books


def addToDataBaseFromJSON(jsonData):
    for x in jsonData:
        print(x["dateOfPublication"].strftime("%m/%d/%Y"))
        print(x["Author"])
        data = Books(x["ISBN"], x["Title"], x["Author"], x["dateOfPublication"], x["noOfPages"], x["Cover"], x["Language"])
        db.session.add(data)
        db.session.commit()


jsonData = json.load(open('jsonData.json'))


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
    def get(self):
        acceptable = ["ISBN",  "title", "language",  "author", "date1", "date2"]
        args = request.args
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
        datas = []
        for arg in args:
            if arg in acceptable:
                tempdata = []
                if arg.lower() != "date1" and arg.lower() != "date2":
                    for book in data:
                        if args.get(arg).lower() in book[arg.capitalize()].lower():
                            tempdata.append(book)
                    datas.append(tempdata)
                else:
                    data2 = []
                    data3 = []
                    date1 = "01-01-0001"
                    date2 = "31-12-9999"
                    if "date1" in args:
                        date1 = args.get("date1")
                    if "date2" in args:
                        date2 = args.get("date2")
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
                        elif len(book["dateOfPublication"]) == 12:
                            relDate = datetime.strptime(book["dateOfPublication"], '%Y-%M-%d')
                            if relDate >= date1 and relDate <= date2:
                                data2.append(book)
                    datas.append(data2 + data3)
        finaldata = datas[0]
        del datas[0]
        for data in datas:
            finaldata2 = []
            for element in finaldata:
                if element in data:
                    finaldata2.append(element)
            finaldata = finaldata2.copy()
        return finaldata


api.add_resource(booksList, "/api/bookslist")
api.add_resource(booksListSearch, "/api/bookslist/search")


@app.route("/proba")
def proba():
    return render_template('proba.html')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/edit')
def editbook():
    return render_template('edit_form.html')


@app.route('/edited', methods = ['POST'])
def edited():
    if request.method == "POST":
        args = {
            "ISBN": request.form["ISBN"],
            "Title": request.form["title"],
            "Author": request.form["author"],
            "noOfPages": request.form["noofpages"],
            "Cover": request.form["cover"],
            "Language": request.form["language"],
            "dateOfPublication": request.form["dateofpublication"]
        }
        book = Books.query.filter_by(ISBN=args["ISBN"]).first()
        for key in args.keys():
            if args[key] != "":
                if key == "Title":
                    book.Title = args[key]
                if key == "Author":
                    book.Author = args[key]
                if key == "noOfPages":
                    book.noOfPages = args[key]
                if key == "Cover":
                    book.Cover = args[key]
                if key == "Language":
                    book.Language = args[key]
                if key == "dateOfPublication":
                    book.dateOfPublication = args[key]
        db.session.commit()
    return redirect(url_for('editbook'))


@app.route('/add')
def addbook():
    return render_template('add_form.html')


@app.route('/import')
def importbooks():
    return render_template('import_form.html')


@app.route('/imported', methods=['POST'])
def imported():
    if request.method == "POST":
        args = {
            "ISBN": request.form["ISBN"],
            "Title": request.form["title"],
            "Author": request.form["author"],
            "noOfPages": request.form["noofpages"],
            "Cover": request.form["cover"],
            "Language": request.form["language"],
            "dateOfPublication": request.form["dateofpublication"]
        }
    query = "?q="
    for key in args.keys():
        if args[key] != "":
            query = query +  args[key] + "+"
    query = query[:-1]
    data = str(requestFromGoogleBooks(query))
    #return data
    return render_template('import_final_step.html', dataq=data)


@app.route('/added', methods=['POST'])
def added():
    if request.method == "POST":
        data = Books(request.form["ISBN"], request.form["title"], request.form["author"], request.form["dateofpublication"], request.form["noofpages"], request.form["cover"], request.form["language"])
        db.session.add(data)
        db.session.commit()
    return redirect(url_for('addbook'))


@app.route('/search', methods=['POST'])
def query():
    if request.method == "POST":
        args = {
            "title": request.form["title"],
            "author": request.form["author"],
            "date1": request.form["date1"],
            "date2": request.form["date2"],
            "language": request.form["language"]
        }
        query = "?"
        for key in args.keys():
            if args[key] != "":
                query = query + key + "=" + args[key] + "&"
        query = query[:-1]
    return render_template('index.html', searchq=str(query))


if __name__ == '__main__':
    app.run()
