import requests
from flask import Blueprint, request,  render_template, redirect, url_for, flash

def keyNoExistHandle(dict, key):
    if key not in list(dict.keys()):
        return "missing data"
    else:
        return dict[key]


def requestFromGoogleBooks(query):
    books = []
    http = "https://www.googleapis.com/books/v1/volumes"
    data = requests.get(http+query)
    data = data.json()
    if str(data["totalItems"]) != "0":
        for x in data["items"]:
            author = keyNoExistHandle(x["volumeInfo"], "authors")
            title = keyNoExistHandle(x["volumeInfo"], "title")
            pages_number = keyNoExistHandle(x["volumeInfo"], "pageCount")
            thumbnails = keyNoExistHandle(x["volumeInfo"], "imageLinks")
            if thumbnails != "missing data":
                cover = thumbnails["smallThumbnail"]
            else:
                cover = "missing data"
            date_of_publication = keyNoExistHandle(
                        x["volumeInfo"], "publishedDate"
                                                )
            language = keyNoExistHandle(x["volumeInfo"], "language")
            isbn = keyNoExistHandle(x["volumeInfo"], "industryIdentifiers")
            if author == "missing data":
                author = ["missing data"]
            if isbn != "missing data":
                for x in isbn:
                    if x["type"] == "ISBN_13":
                        isbn = x["identifier"]
                        break
            if isinstance(isbn, str) is False:
                for x in isbn:
                    if x["type"] == "OTHER":
                        isbn = x["identifier"]
                        break
            books.append({
                        "isbn": str(isbn).replace('"', '').replace("'", ""),
                        "title": str(title).replace('"', '').replace("'", ""),
                        "author": ', '.join(
                            [str(item).replace(
                                '"', '').replace("'", "") for item in author]
                            ),
                        "noOfPages": str(pages_number).replace(
                            '"', '').replace("'", ""),
                        "Cover": str(cover).replace('"', '').replace("'", ""),
                        "Language": str(language).replace('"', '').replace(
                            "'", ""),
                        "dateOfPublication": str(date_of_publication).replace(
                            '"', '').replace("'", "")})
    return books


routing = Blueprint(
    "routing", __name__, static_folder="static", template_folder="templates")


@routing.route('/')
def index():
    return render_template('index.html')


@routing.route('/edit')
def editbook():
    return render_template('edit_form.html')


@routing.route(
    '/edited', methods=['POST']
    )
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
        if (request.form["ISBN"] != "" and request.form["title"] != "" and
            request.form["author"] != "" and
                request.form["dateofpublication"] != "" and
                request.form["noofpages"] != "" and
                request.form["cover"] != "" and
                request.form["language"] != ""):
            book = Book.query.filter_by(ISBN=args["ISBN"]).first()
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
        else:
            flash('You have left an empty field! Fill it and try again.')
    return redirect(url_for('editbook'))


@routing.route('/add')
def addbook():
    return render_template('add_form.html')


@routing.route('/added', methods=['POST'])
def added():
    if request.method == "POST":
        data = Books(
            request.form["ISBN"], request.form["title"],
            request.form["author"], request.form["dateofpublication"],
            request.form["noofpages"], request.form["cover"],
            request.form["language"]
        )
        if (request.form["ISBN"] != "" and request.form["title"] != "" and
            request.form["author"] != "" and
                request.form["dateofpublication"] != "" and
                request.form["noofpages"] != "" and
                request.form["cover"] != "" and
                request.form["language"] != ""):
            db.session.add(data)
            db.session.commit()
        else:
            flash('You have left an empty field! Fill it and try again.')
        return redirect(url_for('addbook'))
    return redirect(url_for('addbook'))


@routing.route('/import')
def importbooks():
    return render_template('import_form.html')


@routing.route('/googleapisearchresuls', methods=['POST'])
def googleapisearchresuls():
    datafinal = []
    if request.method == "POST":
        args = {
            "anything": request.form["anything"],
            "isbn": request.form["isbn"],
            "Title": request.form["title"],
            "Author": request.form["author"],
        }
        query = "?q="
        if args["anything"] != "":
            query = query + args["anything"] + "+"
        for key in args.keys():
            if key != "anything" and args[key] != "":
                query = query + key + "=" + args[key] + "&"
        if query[-1] in ["=", "&"]:
            query = query[:-1]
        data = requestFromGoogleBooks(query)
        data2 = []
        for book in Books.query.all():
            data2.append(book.ISBN)
        data3 = []
        for d in data:
            if d["ISBN"] not in data2:
                data3.append(d)
        datafinal = {"necessery": data3}
    return render_template('import_final_step.html',  dataq=datafinal)


@routing.route('/imported', methods=['POST'])
def imported():
    if request.method == "POST":
        isbn = request.form["ISBN"]
        data = requestFromGoogleBooks("?q=isbn:"+isbn)
        for x in data:
            if x["ISBN"] == isbn:
                bookToAdd = Books(
                    x["ISBN"], x["Title"], x["Author"],
                    x["dateOfPublication"],
                    x["noOfPages"], x["Cover"], x["Language"]
                    )
                db.session.add(bookToAdd)
                db.session.commit()
                break
        return redirect(url_for('index'))


@routing.route('/search', methods=['POST'])
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