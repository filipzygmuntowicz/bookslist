from flask_restful import Resource, reqparse
from flask import request
from datetime import datetime
from dateutil.parser import parse
from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    post_dump,
    post_load,
    ValidationError,
)


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def rest_api(db, Book):
    def search(args):
        acceptable = [
            "isbn",  "title", "language",  "author"
        ]
        all_books = []
        for book in Book.query.all():
            all_books.append({
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "pages_number": book.pages_number,
                "cover": book.cover,
                "language": book.language,
                "date_of_publication": book.date_of_publication}
            )
        all_search_results = []
        for arg in args:
            if arg in acceptable:
                search_results_from_keyword = []
                for book in all_books:
                    if args.get(arg).lower() in book[
                            arg].lower():
                        search_results_from_keyword.append(book)
                all_search_results.append(
                    search_results_from_keyword
                )  # get search results and store them in a nested array
        if "date1" in args or "date2" in args:
            search_results_from_dates = []
            search_results_from_dates_if_missing = []
            date_from = "01-01-0001"
            date_to = "31-12-9999"
            if "date1" in args:
                date_from = args.get("date1")
            if "date2" in args:
                date_to = args.get("date2")
            date_from = datetime.strptime(date_from, '%d-%m-%Y')
            date_to = datetime.strptime(date_to, '%d-%m-%Y')
            for book in all_books:
                if book["date_of_publication"] == "missing data":
                    search_results_from_dates_if_missing.append(book)
                elif len(book["date_of_publication"]) == 4:
                    date = datetime.strptime(
                        book["date_of_publication"], '%Y'
                    )
                    if date >= date_from and date <= date_to:
                        search_results_from_dates.append(book)
                elif len(book["date_of_publication"]) == 7:
                    date = datetime.strptime(
                        book["date_of_publication"], '%Y-%m'
                    )
                    if date >= date_from and date <= date_to:
                        search_results_from_dates.append(book)
                elif len(book["date_of_publication"]) == 12:
                    date = datetime.strptime(
                        book["date_of_publication"], '%Y-%m-%d'
                    )
                    if date >= date_from and date <= date_to:
                        search_results_from_dates.append(book)
            all_search_results.append(
                search_results_from_dates +
                search_results_from_dates_if_missing
                )  # get search results by dates later than date1
    # and earlier than date2
        search_return = all_search_results[0]
        del all_search_results[0]
        for search_results in all_search_results:
            new_search_return = []
            for element in search_return:
                if element in search_results:
                    new_search_return.append(element)
            search_return = new_search_return.copy()  # search_return will be a
    # list of books that were present in every single search_result
        return search_return
   
    class booksListSearch(Resource):
        def get(self):
            args = request.args
            return search(args)
    parser = reqparse.RequestParser()
    parser.add_argument('isbn', type=str)
    parser.add_argument('title', type=str)
    parser.add_argument('author', type=str)
    parser.add_argument('pages_number', type=str)
    parser.add_argument('cover', type=str)
    parser.add_argument('language', type=str)
    parser.add_argument('date_of_publication', type=str)

    class booksList(Resource):
        def get(self):
            return_books = []
            for book in Book.query.all():
                return_books.append({
                    "isbn": book.isbn,
                    "title": book.title,
                    "author": book.author,
                    "pages_number": book.pages_number,
                    "cover": book.cover,
                    "language": book.language,
                    "date_of_publication": book.date_of_publication}
                )
            return return_books
#   https://stackoverflow.com/questions/61243848/simple-request-parsing-without-reqparse-requestparser

        def post(self):
            args = parser.parse_args()
            if is_date(args["date_of_publication"]):
                book = Book(
                    args["isbn"], args["title"], args["author"],
                    args["date_of_publication"],
                    args["pages_number"], args["cover"], args["language"]
                        )
                db.session.add(book)
                db.session.commit()
            else:
                print("Not a date!")

    class booksListEdit(Resource):
        def post(self):
            args = parser.parse_args()
            print(args)
            book = Book.query.filter_by(isbn=args["isbn"]).first()
            for key in args.keys():
                if args[key] != "":
                    if key == "title":
                        book.title = args[key]
                    if key == "author":
                        book.author = args[key]
                    if key == "pages_number":
                        book.pages_number = args[key]
                    if key == "cover":
                        book.cover = args[key]
                    if key == "language":
                        book.language = args[key]
                    if key == "date_of_publication":
                        book.date_of_publication = args[key]
            db.session.commit()

    return booksList, booksListSearch, booksListEdit
