import requests
from flask import Blueprint, request,  render_template, redirect, url_for, \
    flash


def keyNoExistHandle(dict, key):
    if key not in list(dict.keys()):
        return "missing data"
    else:
        return dict[key]


# def requestFromGoogleBooks(query, obj):
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
                "date_of_publication": str(date_of_publication).replace(
                    '"', '').replace("'", ""),
                "pages_number": str(pages_number).replace(
                    '"', '').replace("'", ""),
                "cover": str(cover).replace('"', '').replace("'", ""),
                "language": str(language).replace('"', '').replace(
                    "'", "")
            })
#            books.append(obj(
#                        str(isbn).replace('"', '').replace("'", ""),
#                        str(title).replace('"', '').replace("'", ""),
#                        ', '.join(
#                            [str(item).replace(
#                                '"', '').replace("'", "") for item in author]
#                            ),
#                        str(date_of_publication).replace(
#                            '"', '').replace("'", ""),
#                        str(pages_number).replace(
#                            '"', '').replace("'", ""),
#                        str(cover).replace('"', '').replace("'", ""),
#                        str(language).replace('"', '').replace(
#                            "'", ""),
#                        ))
    return books


def create_dict_for_book():
    return {
        "isbn": request.form["isbn"],
        "title": request.form["title"],
        "author": request.form["author"],
        "date_of_publication": request.form["date_of_publication"],
        "pages_number": request.form["pages_number"],
        "cover": request.form["cover"],
        "language": request.form["language"]
    }


def fields_non_empty():
    if (request.form["isbn"] != "" and request.form["title"] != "" and
            request.form["author"] != "" and
            request.form["date_of_publication"] != "" and
            request.form["pages_number"] != "" and
            request.form["cover"] != "" and
            request.form["language"] != ""):
        return True
    return False


routing = Blueprint(
    "routing", __name__, static_folder="static", template_folder="templates")


@routing.route('/')
def index():
    return render_template('index.html')


@routing.route('/edit')
def editbook():
    return render_template('edit_form.html')


@routing.route('/edited', methods=['POST'])
def edited():
    if request.method == "POST":
        data = create_dict_for_book()
        if fields_non_empty():
            requests.post(request.host_url+'api/bookslist/update', json=data)
        else:
            flash('You have left an empty field! Fill it and try again.')
    return redirect(url_for('.editbook'))


@routing.route('/add')
def addbook():
    return render_template('add_form.html')


@routing.route('/added', methods=['POST'])
def added():
    if request.method == "POST":
        if fields_non_empty():
            data = create_dict_for_book()
            requests.post(request.host_url+'api/bookslist', json=data)
        else:
            flash('You have left an empty field! Fill it and try again.')
    return redirect(url_for('.addbook'))


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
            "title": request.form["title"],
            "author": request.form["author"],
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
        books = requests.get(request.host_url+'api/bookslist').json()
        for book in books:
            data2.append(book["isbn"])
        data3 = []
        for d in data:
            if d["isbn"] not in data2:
                data3.append(d)
        datafinal = {"necessery": data3}
    return render_template('import_final_step.html',  dataq=datafinal)


@routing.route('/imported', methods=['POST'])
def imported():
    if request.method == "POST":
        isbn = request.form["isbn"]
        data = requestFromGoogleBooks("?q=isbn:"+isbn)
        for x in data:
            if x["isbn"] == isbn:
                requests.post(request.host_url+'api/bookslist', json=x)
                break
        return redirect(url_for('.index'))


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
