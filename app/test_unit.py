from app import *
import pytest
import requests

api_url = "https://bookslistzygmuntowicz.herokuapp.com/api/bookslist"


def advancedapisearch(search):
    acceptable = [
        "ISBN",  "title", "language",  "author", "date1", "date2"
    ]
    data = jsonData
    datas = []
    for arg in (search.keys()):
        if arg in acceptable:
            tempdata = []
            if arg.lower() != "date1" and arg.lower() != "date2":
                for book in data:
                    if search[arg].lower() in book[
                        arg.capitalize()
                    ].lower():
                        tempdata.append(book)
                datas.append(tempdata)
            else:
                data2 = []
                data3 = []
                date1 = "01-01-0001"
                date2 = "31-12-9999"
                if "date1" in search.keys():
                    date1 = search["date1"]
                if "date2" in search.keys():
                    date2 = search["date2"]
                date1 = datetime.strptime(date1, '%d-%M-%Y')
                date2 = datetime.strptime(date2, '%d-%M-%Y')
                for book in data:
                    if book["dateOfPublication"] == "missing data":
                        data3.append(book)
                    elif len(book["dateOfPublication"]) == 4:
                        relDate = datetime.strptime(
                            book["dateOfPublication"]+"-01-01", '%Y-%M-%d'
                        )
                        if relDate >= date1 and relDate <= date2:
                            data2.append(book)
                    elif len(book["dateOfPublication"]) == 7:
                        relDate = datetime.strptime(
                            book["dateOfPublication"]+"-01", '%Y-%M-%d'
                        )
                        if relDate >= date1 and relDate <= date2:
                            data2.append(book)
                    elif len(book["dateOfPublication"]) == 12:
                        relDate = datetime.strptime(
                            book["dateOfPublication"], '%Y-%M-%d'
                        )
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


class Test:

    def test_googleapi(self):
        result = requestFromGoogleBooks("?q=witcher")[0]
        result2 = requestFromGoogleBooks("?q=isbn:9781506713946")[0]
        assert list(result.keys()) == [
            "ISBN", "Title", "Author", "noOfPages",
            "Cover", "Language", "dateOfPublication"
        ] and list(result2.keys()) == [
            "ISBN", "Title", "Author", "noOfPages",
            "Cover", "Language", "dateOfPublication"]

    def test_simpleapisearch(self):
        data = requests.get(
            api_url + "/search?author=Andrzej Sapkowski").json()
        data2 = requests.get(
            api_url + "/search?title=Wiedzmin Ostatnie zyczenie").json()

        trueorfalse = False
        trueorfalse2 = False

        for book in data:
            if book["Author"] == "Andrzej Sapkowski":
                trueorfalse = True
        for book in data2:
            if book["Title"] == "Wiedzmin Ostatnie zyczenie":
                trueorfalse2 = True
        assert trueorfalse is True and trueorfalse2 is True

    def test_advancedsearch(self):

        search = {
            "title": "Wiedzmin",
            "author": "Andrzej Sapkowski",
            "language": "pl",
            "date1": "01-01-2013",
            "date2": "01-12-2014"
        }

        expected_result = [
            {
                "ISBN": "9788375780635",
                "Title": "Wiedzmin Ostatnie zyczenie",
                "Author": "Andrzej Sapkowski",
                "noOfPages": 332,
                "Cover": "missing data",
                "Language": "pl",
                "dateOfPublication": "2014-01"
            },
            {
                "ISBN": "9788375780666",
                "Title": "Wiedzmin 4 Czas pogardy",
                "Author": "Andrzej Sapkowski",
                "noOfPages": 368,
                "Cover": "missing data",
                "Language": "pl",
                "dateOfPublication": "2014-01"
            },
            {
                "ISBN": "9788375780697",
                "Title": "Wiedzmin 7 Pani Jeziora",
                "Author": "Andrzej Sapkowski",
                "noOfPages": 596,
                "Cover": "missing data",
                "Language": "pl",
                "dateOfPublication": "2014-01"
            },
            {
                "ISBN": "9788375780659",
                "Title": "Wiedzmin 3 Krew elfow",
                "Author": "Andrzej Sapkowski",
                "noOfPages": 340,
                "Cover": "missing data",
                "Language": "pl",
                "dateOfPublication": "2014-01"
            }
        ]
        assert json.dumps(advancedapisearch(
            search)) == json.dumps(expected_result)
