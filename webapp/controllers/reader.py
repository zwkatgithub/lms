from flask import Blueprint, render_template
from os import path
from webapp.permission import reader_permission
from webapp.models import Transaction, Reader, Book_Copy
from flask_login import current_user
from webapp.constant import  TIME_IN, TIME_OUT

reader_blueprint = Blueprint('reader',__name__,
    static_folder=path.join(path.pardir,'static'),
    template_folder=path.join(path.pardir,'templates','reader'),
    url_prefix='/reader')

@reader_blueprint.route('/main')
@reader_permission
def main():
    reader = Reader.query.get(current_user.id)
    transactions = reader.transactions.all()
    ts = [(t,Book_Copy.query.get(t.entity_id)) for t in transactions if t.status==TIME_IN]
    
    return render_template('main.html',ts=ts)
