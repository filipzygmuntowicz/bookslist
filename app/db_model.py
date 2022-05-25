from flask_sqlalchemy import SQLAlchemy


def db_model(app):
    db = SQLAlchemy(app)

    class Book(db.Model):
        __tablename__ = 'Books'
        isbn = db.Column(db.String(100), primary_key=True)
        title = db.Column(db.String(200))
        author = db.Column(db.String(200))
        date_of_publication = db.Column(db.String(15))
        pages_number = db.Column(db.String(20))
        cover = db.Column(db.String(400))
        language = db.Column(db.String(200))

        def __init__(
                self, isbn, title,
                author, date_of_publication, pages_number, cover, language
                    ):
            self.isbn = isbn
            self.title = title
            self.author = author
            self.date_of_publication = date_of_publication
            self.pages_number = pages_number
            self.cover = cover
            self.language = language
    return db, Book
