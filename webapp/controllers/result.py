from flask import Blueprint, render_template, flash
from webapp.constant import PAGINATION
from webapp.models import Book, Book_Copy
from os import path

result_blueprint = Blueprint('result',__name__,
    static_folder=path.join(path.pardir,'static'),
    template_folder=path.join(path.pardir,'templates','result')
    ,url_prefix='/result')

@result_blueprint.route('/title/<string:content>/<int:page>')
def result_title(content,page=1):
    books = Book.query.filter(Book.title.like('%'+content+'%')).paginate(page,PAGINATION)
    if len(books.items) == 0:
        flash("No Results")
    return render_template('result.html', content=content,books=books, endpoint='result.result_title')

@result_blueprint.route('/author/<string:content>/<int:page>')
def result_author(content,page=1):
    books = Book.query.filter(Book.author.like('%'+content+'%')).paginate(page,PAGINATION)
    if len(books.items) == 0:
        flash("No Results")
    return render_template('result.html', content=content,books=books, endpoint='result.result_author')

@result_blueprint.route('/ISBN/<string:content>')
def result_ISBN(content,page=1):
    book = Book.query.filter_by(ISBN=content).paginate(page,PAGINATION)
    if len(book.items) == 0:
        flash("No Results")
    return render_template('result.html',content=content,books=book, endpoint='result.result_author')

@result_blueprint.route('/entity/<int:book_id>')
def result_entity(book_id):
    book_info = Book.query.filter_by(book_id=book_id).paginate(1,1)
    books = Book_Copy.query.filter_by(book_id=book_id).all()
    if len(books) == 0:
        flash("No Results")
    return render_template('entity.html', book_info=book_info, books=books)
    