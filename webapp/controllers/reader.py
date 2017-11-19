from flask import Blueprint, render_template
from os import path
from webapp.permission import reader_permission
from webapp.models import Transaction, Reader, Book_Copy
from flask_login import current_user
from webapp.constant import  TIME_IN, TIME_OUT, PAGINATION

reader_blueprint = Blueprint('reader',__name__,
    static_folder=path.join(path.pardir,'static'),
    template_folder=path.join(path.pardir,'templates','reader'),
    url_prefix='/reader')

@reader_blueprint.route('/main')
@reader_permission
def main():
    reader = Reader.query.get(current_user.reader_id)      
    
    
    return render_template('reader/main.html',reader=reader)

@reader_blueprint.route('/records/<int:reader_id>/<int:page>',methods=['GET','POST'])
@reader_permission
def get_records(reader_id,page=1):
    reader = current_user
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('reader.main'))
    transactions = reader.transactions.paginate(page,PAGINATION)
    res = list()
    for tran in transactions.items:
        copy = Book_Copy.query.get(tran.copy_id)
        res.append(dict({'Reader_ID':reader.ID,'Title': copy.book.title,'ISBN':copy.book.ISBN,
        'Copy_ID':copy.copy_id,'Borrow_Date':tran.borrow_date, 'Return_Date':tran.return_date,'Truely_Return_Date':tran.truely_return_date,
        'Status':tran.status}))
    return render_template('reader/records.html',transactions = transactions,res=res,reader_id=reader_id,endpoint='reader.get_records')
@reader_blueprint.route('/borrowing_books/<int:reader_id>',methods=['GET','POST'])
@reader_permission
def borrowing_books(reader_id):
    reader = current_user
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('reader.main'))
    trans = Transaction.query.filter_by(reader_id = reader_id, status=TIME_IN).all()
    if len(trans) > 2:
        
        flash('Error1')
        return redirect(url_for('reader.main'))
    copies = [Book_Copy.query.get(tran.copy_id) for tran in trans]
    for copy in copies:
        if copy is None:
            flash('Error2')
            return redirect(url_for('reader.main'))
    return render_template('reader/borrowing_books.html',copies = copies)