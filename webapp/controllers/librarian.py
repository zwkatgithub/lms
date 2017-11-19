from flask import Blueprint, render_template, url_for, redirect, current_app, flash,session,g
from webapp.models import System,Reader, Librarian, Book, Book_Copy, Transaction, db, FineChange, Income
from webapp.forms import SystemForm,IncomeForm,ReturnFineForm, EditReaderForm, ReaderSearchForm,RegisterReaderForm, AddBookForm, AddCopyForm,EditBookForm,BookForm, EditBookCopyForm,BookSearchForm,BorrowBookForm, ReturnBookForm, DeleteBook, DeleteEntity, Search
from flask_login import current_user

from webapp.constant import  TIME_OUT, TIME_IN,PAGINATION, BORROWED, DAMAGED, ON_THE_SHELF, LOST, DEALING
from webapp.extends import GetBook, download_picture, get_month, get_week, get_year
from webapp.permission import librarian_permission
import os
from datetime import timedelta, datetime
import re

from sqlalchemy import func

librarian_blueprint = Blueprint('librarian',__name__,
    static_folder=os.path.join(os.path.pardir,'static'),
    template_folder=os.path.join(os.path.pardir,'templates','librarian'),
    url_prefix='/librarian')

@librarian_blueprint.route('/')
@librarian_permission
def main():
    return redirect(url_for('librarian.get_books',content='_',page=1))


@librarian_blueprint.route('/books/<string:content>/<int:page>',methods=['GET','POST'])
@librarian_permission
def get_books(content='_',page=1):
    books = Book.query.paginate(page,PAGINATION)
    
    form = BookSearchForm()
    if form.validate_on_submit():
        if form.methods.data == 1:
            return redirect(url_for('librarian.get_books_ISBN',content=form.content.data,page=1))
        elif form.methods.data == 2:
            return redirect(url_for('librarian.get_books_title',content=form.content.data,page=1))
        elif form.methods.data == 3:
            return redirect(url_for('librarian.get_books_author',content=form.content.data,page=1))
        elif form.methods.data==4:
            return redirect(url_for('librarian.get_book_copy',copy_id=int(form.content.data)))
        else:
            flash('Error')
            books = None
        
    return render_template('books.html',form=form,books = books,content=content,endpoint='librarian.get_books',summary='')
@librarian_blueprint.route('/books/ISBN/<string:content>/<int:page>',methods=['POST','GET'])
@librarian_permission
def get_books_ISBN(content,page):
    form = BookSearchForm()
    books = Book.query.filter_by(ISBN = content).paginate(page,PAGINATION)
    if len(books.items) == 0:
        flash("No Results")
        return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_ISBN',flag=True)
        
    if form.validate_on_submit():
        if form.methods.data == 1:
            return redirect(url_for('librarian.get_books_ISBN',content=form.content.data,page=1))
        elif form.methods.data == 2:
            return redirect(url_for('librarian.get_books_title',content=form.content.data,page=1))
        elif form.methods.data == 3:
            return redirect(url_for('librarian.get_books_author',content=form.content.data,page=1))
        else:
            flash('Error')
            books = None
        
    return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_ISBN',flag=True)
@librarian_blueprint.route('/books/title/<string:content>/<int:page>',methods=['POST','GET'])
@librarian_permission
def get_books_title(content,page):
    form  = BookSearchForm()
    books = Book.query.filter(Book.title.like('%'+content+'%')).paginate(page,PAGINATION)
    if len(books.items) == 0:
        flash("No Results")
    if form.validate_on_submit():
        if form.methods.data == 1:
            return redirect(url_for('librarian.get_books_ISBN',content=form.content.data,page=1))
        elif form.methods.data == 2:
            return redirect(url_for('librarian.get_books_title',content=form.content.data,page=1))
        elif form.methods.data == 3:
            return redirect(url_for('librarian.get_books_author',content=form.content.data,page=1))
        else:
            flash('Error')
            books = None
    return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_title',summary='this')
@librarian_blueprint.route('/books/author/<string:content>/<int:page>',methods=['POST','GET'])
@librarian_permission
def get_books_author(content,page):
    form  = BookSearchForm()
    books = Book.query.filter(Book.author.like('%'+content+'%')).paginate(page,PAGINATION)
    if len(books.items) == 0:
        flash("No Results")
        return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_ISBN',flag=True)
    if form.validate_on_submit():
        if form.methods.data == 1:
            #ISBN
            #books = Book.query.filter(ISBN = form.content.data).paginate(page,PAGINATION)
            return redirect(url_for('librarian.get_books_ISBN',form.content.data,page=1))
        elif form.methods.data == 2:
            #books = Book.query.filter(Book.title.like('%'+form.content.data+'%')).paginate(page,PAGINATION)
            return redirect(url_for('librarian.get_books_title',form.content.data,page=1))
        elif form.methods.data == 3:
            #books = Book.query.filter(Book.author.like('%'+form.content.data+'%')).paginate(page,PAGINATION)
            return redirect(url_for('librarian.get_books_author',form.content.data,page=1))
        else:
            flash('Error')
            books = None
    return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_author')

@librarian_blueprint.route('/book_copies/<int:book_id>')
@librarian_permission
def get_book_copies(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Can't find this book")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    book_copies = book.copies.all()
    return  render_template('book_copies.html',book_=book,book_copies = book_copies)

@librarian_blueprint.route('/book_copy/<int:copy_id>')
@librarian_permission
def get_book_copy(copy_id):
    copy = Book_Copy.query.get(copy_id)
    if not copy:
        flash("Can't find this copy")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    return render_template('book_copy.html',copy = copy)

@librarian_blueprint.route('/edit_book/<int:book_id>',methods=['GET','POST'])
@librarian_permission
def edit_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Can't find this book")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    form = EditBookForm()
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.press = form.press.data
        book.publish_date = form.publish_date.data
        book.ISBN = form.ISBN.data
        book.price = form.price.data

        if len(form.file.data.filename) != 0:
            form.file.data.save(os.path.join(current_app.root_path+'/static/picture',book.picture))
        book.summary = form.summary.data
        db.session.add(book)
        db.session.commit()
        flash('Successful')
        return redirect(url_for('librarian.get_books',content='_',page=1))
    form.title.data = book.title
    form.author.data = book.author
    form.press.data = book.press
    form.publish_date.data = book.publish_date
    form.ISBN.data = book.ISBN
    form.price.data = book.price
    form.summary.data = book.summary

    return render_template('edit_book.html',form=form,picture=book.picture)

@librarian_blueprint.route('/damage_lost/<int:reader_id>/<float:fine>',methods=['GET','POST'])
@librarian_permission
def damage(reader_id,fine):
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('librarian.get_books',content='_',page=1))

    reader.fine += fine
    db.session.add(reader)
    db.session.commit()
    flash('Successful')
    return redirect(url_for('librarian.get_books',content='_',page=1))


@librarian_blueprint.route('/edit_copy/<int:copy_id>',methods=['GET','POST'])
@librarian_permission
def edit_copy(copy_id):
    form = EditBookCopyForm()
    copy = Book_Copy.query.get(copy_id)
    if not copy:
        flash("Can't find this copy")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    if form.validate_on_submit():
        if copy.status == BORROWED and form.status.data ==DAMAGED:
            tran = Transaction.query.filter_by(copy_id=copy.copy_id,status=TIME_IN).first()
            if not tran:
                flash('Error1')
                return redirect(url_for('librarian.edit_copy',copy_id=copy.copy_id))
            reader = Reader.query.get(tran.reader_id)
            if not reader:
                flash('Error2')
                return redirect(url_for('librarian.edit_copy',copy_id=copy.copy_id))
            damage_fine = System.query.get(1).damage_fine
            return render_template('damage.html',form=form,copy=copy,reader=reader,fine=damage_fine,header='Damage')
            
        if copy.status == BORROWED and form.status.data ==LOST:
            tran = Transaction.query.filter_by(copy_id=copy.copy_id,status=TIME_IN).first()
            if not tran:
                flash('Error1')
                return redirect(url_for('librarian.edit_copy',copy_id=copy.copy_id))
            reader = Reader.query.get(tran.reader_id)
            if not reader:
                flash('Error2')
                return redirect(url_for('librarian.edit_copy',copy_id=copy.copy_id))
            lost_fine = copy.book.price
            return render_template('damage.html',form=form,copy=copy,reader=reader,fine=lost_fine,header='Lost')

        copy.status = form.status.data
        copy.location = form.location.data

        db.session.add(copy)
        db.session.commit()
        flash('Successful')
        return redirect(url_for('librarian.get_book_copies',book_id=copy.book_id))
    form.status.data = copy.status
    
    form.location.data = copy.location

    return render_template('edit_copy.html',form=form,copy=copy)



@librarian_blueprint.route('/delete_book/<int:book_id>')
@librarian_permission
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash("Can't find this book")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    copies = book.copies.all()
    for copy in copies:
        if copy.status == BORROWED:
            flash("This book has borrowing copies")
            return redirect(url_for('librarian.get_books',content='_',page=1))
    for copy in copies:
        db.session.delete(copy)
    try:
        os.remove(os.path.join(current_app.root_path+'/static/picture',book.picture))
    except Exception:
        pass
    db.session.delete(book)
    db.session.commit()
    flash('Successful')
    return redirect(url_for('librarian.get_books',content='_',page=1))

@librarian_blueprint.route('/delete_copy/<int:copy_id>')
@librarian_permission
def delete_copy(copy_id):
    copy = Book_Copy.query.get(copy_id)
    if copy.status == 2:
        flash("Can't delete this book")
        return redirect(url_for('librarian.get_book_copies',book_id=copy.book_id))
    if not copy:
        flash("Can't find this copy")
        return redirect(url_for('librarian.get_book_copies',book_id=copy.book_id))
    db.session.delete(copy)
    db.session.commit()
    flash('Successful')
    return redirect(url_for('librarian.get_book_copies',book_id=copy.book_id))

@librarian_blueprint.route('/add_copy/<int:book_id>',methods=['GET','POST'])
@librarian_permission
def add_copy(book_id):
    form = AddCopyForm()
    book = Book.query.get(book_id)
    if not book:
        flash("Can't fin this book")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    if form.add.data:
        form.locations.append_entry()
  

    if not form.add.data and form.submit.data:
        data = [d for d in form.locations.data if len(d)!=0]
        number = len(data)
        print('this')
        #message = "Copy ID : \n"
        messages = []
        for d in data:
            copy = Book_Copy(book_id,1,None,d)
            db.session.add(copy)
            db.session.commit()
            messages.append((d,copy.copy_id))
            #message += d+" : "+str(copy.copy_id)+'\n'
        for index, message in enumerate(messages):
            flash(str(index+1)+'. '+message[0]+' copy id : ' + str(message[1]))
        

        return redirect(url_for('librarian.get_books',content='_',page=1))
        #form.locations.append_entry()
    return render_template('add_copy.html',form=form,book_id=book_id)
pic = None
@librarian_blueprint.route('/add_book',methods=['GET','POST'])
@librarian_permission
def add_book():
    global pic
    form = AddBookForm()
    if form.submit.data and not form.book_form.form.ISBN.data:
        res = Book.query.filter_by(ISBN = form.ISBN.data).first()
        if res is not None:
            flash('This book already exists in librarian')
            return render_template('add_book.html',form=form,picture=None)
        try:
            book = GetBook(isbn=form.ISBN.data).book
        except Exception:
            flash('The network is wrong')
            return render_template('add_book.html',form=form,picture=None)
        if book is None:
            flash("Can't find this book info")
            return render_template('add_book.html',form=form,picture=None)
       
        form.book_form.form.title.data = book['title']
        form.book_form.form.author.data = book['author']
        form.book_form.form.press.data = book['press']
        form.book_form.form.publish_date.data = book['publish_date']
        prices = re.findall('[-+]?([0-9]*\.[0-9]+|[0-9]+)',book['price'])
        print(prices)
        if len(prices) == 0:
            price = '80.0'
        else:
            price = prices[0]
        form.book_form.form.price.data = price
        print(form.book_form.form.price.data)
        form.book_form.form.ISBN.data = book['ISBN']
        form.book_form.form.summary.data = book['summary']
        #download picture
        try:
            path = download_picture(book['image_path'],os.path.join(current_app.root_path+'/static/picture/'))
        except Exception:
            print('de')
            path = 'default.png'
        if not path:
            flash('Download picture failed')
        form.book_form.form.file.filename = os.path.basename(path)
        pic = form.book_form.form.file.filename
        return render_template('add_book.html',form=form,picture=form.book_form.form.file.filename)
    if form.copies.form.add.data:
        form.copies.form.locations.append_entry()
        return render_template('add_book.html',form=form,picture=pic)
    if form.submit.data and len([d for d in form.copies.form.locations.data if len(d)!=0])!=0:  
        form.book_form.form.file.filename = pic
        book = Book(form.book_form.form.title.data,
            form.book_form.form.author.data,
            form.book_form.form.press.data,
            form.book_form.form.publish_date.data,
            form.book_form.form.ISBN.data,
            form.book_form.form.summary.data,
            float(form.book_form.form.price.data),
            form.book_form.form.file.filename)
        db.session.add(book)
        db.session.commit()
        picture = str(book.book_id)+'.'+form.book_form.form.file.filename.split('.')[-1]
        if form.book_form.form.file.filename.find(pic.split('.')[0]) == -1:
            form.book_form.form.file.save(os.path.join(current_app.root_path+'/static/picture',picture))
        else:
            os.rename(os.path.join(current_app.root_path+'/static/picture',pic.split('.')[0]+'.'+book.picture.split('.')[-1]),
            os.path.join(current_app.root_path+'/static/picture',picture))
        book.picture = picture
        
        
        db.session.add(book)
        db.session.commit()
        locations = [d for d in form.copies.form.locations.data if len(d) != 0]
        messages = []
        for location in locations:
            copy = Book_Copy(book.book_id,1,None,location)
            db.session.add(copy)
            db.session.commit()
            messages.append((location,copy.copy_id))
        if len(messages) == 0:
            flash('Successful')
        else:
            for index, message in enumerate(messages):
                flash(str(index+1)+'. '+message[0]+' copy id : ' + str(message[1]))
        return redirect(url_for('librarian.get_books',content='_',page=1))
        
    return render_template('add_book.html',form=form,picture=None)
        
        


@librarian_blueprint.route('/register_reader',methods=['GET','POST'])
@librarian_permission
def register_reader():
    form = RegisterReaderForm()
    if form.validate_on_submit():
        reader = Reader(form.ID.data,form.name.data,form.sex.data,0,form.deposit.data)
        reader.set_password(form.password.data)
        db.session.add(reader)
        db.session.commit()
        flash('Successful')
        return redirect(url_for('librarian.get_books',content='_',page=1))
    return render_template('register_reader.html',form=form)

def check_fine(reader):
    ''' has_fine ?'''
    if reader.fine > 0.0:
        return False
    return True
def check_borrowed_books(reader):
    transactions = reader.transactions.all()
    num = 0
    for tran in transactions:
        if tran.status == TIME_IN:
            num += 1
    if num >= 2:
            return False
    return True

def check_same_book(reader,copy):
    transactions = Transaction.query.filter_by(reader_id=reader.reader_id, status=TIME_IN).all()
    for tran in transactions:
        this_copy = Book_Copy.query.get(tran.copy_id)
        if  copy.book.ISBN == this_copy.book.ISBN:
            return False

    return True

      
def borrow_book_(reader_id,copy_ids,borrow_date,return_date):

    copys=[]
    for copy_id in copy_ids:
        
        copys.append(Book_Copy.query.get(copy_id))
    for copy in copys:
        if not copy:
            flash("Can't find this copy")
            return redirect(url_for('librarian.borrow_book'))
    for copy in copys:
        transaction = Transaction(reader_id,
            current_user.librarian_id,
            copy.copy_id,TIME_IN,
            borrow_date,return_date)
        copy.status = BORROWED
        copy.return_date = return_date
        db.session.add_all([copy,transaction])
        db.session.commit()
    flash('Successful')
    return redirect(url_for('librarian.borrow_book'))

@librarian_blueprint.route('/borrow_book',methods=['GET','POST'])
@librarian_permission
def borrow_book():
    form = BorrowBookForm()

    if form.add.data:
        try:
            form.copy_ids.append_entry()
        except Exception:
            flash('At most 2 books one time')
        
    if form.borrow.data:

        reader = Reader.query.filter_by(ID = form.ID.data).first()
        if not reader:
            flash("Can't find this reader")
            return redirect(url_for('librarian.borrow_book'))
        copys = [ (c,Book_Copy.query.get(c)) for c in form.copy_ids.data if c is not None]
        for copy in copys:
            if not copy[1]:
                flash("Can't find this book copy : "+str(copy[0]))
                return redirect(url_for('librarian.borrow_book'))
            if copy[1].status != ON_THE_SHELF :
                flash("This copy(%r) can't be borrowed" % str(copy[1].copy_id))
                return redirect(url_for('librarian.borrow_book'))
            if not check_same_book(reader,copy[1]):
                flash("This reader has borrowed a same book : %r" % copy[1].book.title)
                return redirect(url_for('librarian.borrow_book'))
        if not check_fine(reader):
            flash("This reader has fine.")
            return redirect(url_for('librarian.borrow_book'))
        if not check_borrowed_books(reader):
            flash("This reader has borrowed 2 books")
            return redirect(url_for('librarian.borrow_book'))
        
        borrow_date = datetime.date(datetime.now())
        return_date = datetime.date(datetime.now()) + timedelta(days=form.days.data)
       
        copys = [copy for _,copy in copys]
        if len(copys) >=2 and copys[0].book.ISBN == copys[1].book.ISBN:
            flash("Can't borrow same book")
            return redirect(url_for('librarian.borrow_book'))
        copy_ids = [copy.copy_id for copy in copys]
        return render_template('borrow_book_.html',form=form,
            reader=reader,
            copys=copys,
            borrow_date=borrow_date,
            return_date=return_date,
            copy_ids = copy_ids)

        
        
    if form.submit.data:
        reader = Reader.query.filter_by(ID = form.ID.data).first()
        copys = [ (c,Book_Copy.query.get(c)) for c in form.copy_ids.data if c is not None]
        borrow_date = datetime.date(datetime.now())
        return_date = datetime.date(datetime.now()) + timedelta(days=form.days.data)
        copys = [copy for _,copy in copys]
        copy_ids = [copy.copy_id for copy in copys]
        return borrow_book_(reader.reader_id,copy_ids,borrow_date,return_date)
    
    return render_template('borrow_book.html',form=form)





def calc_fine(copy,reader):
    return_date = copy.return_date
    print(copy.location)
    current_date = datetime.date(datetime.now())
    if return_date >= current_date:
        return 0.0
    #time out
    res = 0.0
    fines = FineChange.query.order_by(FineChange.start_date).all()
    start = None
    for index, fine in enumerate(fines):
        if fine.start_date <= return_date:
            start = index
            print(start)
    
    if start is not None:
        while start+1 < len(fines) and current_date > fines[start+1].start_date:
            res += (fines[start+1].start_date - return_date).days * fines[start].fine
            print(res)
            return_date = fines[start+1].start_date
            start +=1
        res += (current_date - return_date).days * fines[start].fine
          
            
    return res
        





res = []
@librarian_blueprint.route('/return_book',methods=['GET','POST'])
@librarian_permission
def return_book():
    global res
    form = ReturnBookForm()
    #input : copy id
    if form.add.data:
        form.copy_ids.append_entry()

    if form.return_.data:
        copy_ids = [c for c in form.copy_ids.data if c is not None]
        if len(copy_ids) == 0:
            
            flash('Content is null')
            return render_template('return_book.html',form=form)
        copys = [Book_Copy.query.get(c) for c in copy_ids]
        res.clear()
        borrow_dates = []
        return_dates = []
        fines = []
        for copy_id, copy in zip(copy_ids,copys):
            if not copy:
                flash("Can't find this copy : %r" % str(copy_id))
                continue
            if copy.status != BORROWED:
                flash('This copy is not borrowed')
                continue
            transaction = Transaction.query.filter_by(copy_id = copy_id, status = TIME_IN).first()
            if not transaction:
                flash("Can't find the transaction")
                continue
            reader = Reader.query.get(transaction.reader_id)
            fine = calc_fine(copy,reader)
            res.append(copy)
            borrow_dates.append(transaction.borrow_date)
            return_dates.append(transaction.return_date)
            fines.append(fine)

        #picture copy borrow_date return_date current_date fine 
        return render_template('return_book_.html',form=form,data=zip(res,borrow_dates,return_dates,fines),current_date=datetime.date(datetime.now()))
    if form.submit.data:
        
        for copy in res:
            transaction = Transaction.query.filter_by(copy_id = copy.copy_id, status = TIME_IN).first()
            reader = Reader.query.get(transaction.reader_id)
            reader.fine += calc_fine(copy,reader)
            copy.status = DEALING
            copy.return_date = None
            transaction.status = TIME_OUT
            transaction.truely_return_date = datetime.date(datetime.now())
            
            db.session.add_all([copy,reader,transaction])
            db.session.commit()
            res.clear()
            flash('Successful')

        return redirect(url_for('librarian.return_book'))
    return render_template('return_book.html',form=form)
        

    
@librarian_blueprint.route('/readers/<string:content>/<int:page>',methods=['GET','POST'])
@librarian_permission   
def get_readers(content='_',page=1):
    form  = ReaderSearchForm()
    if form.validate_on_submit():
        reader = Reader.query.filter_by(ID = form.content.data).paginate(page,PAGINATION)
        if not reader:
            flash("Can't find this reader")
            return redirect(url_for('librarian.get_readers',content='_',page=1))
        
        return render_template('readers.html',form=form,readers=reader,content=content,endpoint='librarian.get_readers',flag=True)
    readers = Reader.query.paginate(page,PAGINATION)
        
    return render_template('readers.html',form=form,readers=readers,content=content,endpoint='librarian.get_readers')

@librarian_blueprint.route('/records/<int:reader_id>/<int:page>',methods=['GET','POST'])
@librarian_permission
def get_records(reader_id,page=1):
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    transactions = reader.transactions.paginate(page,PAGINATION)
    res = list()
    for tran in transactions.items:
        copy = Book_Copy.query.get(tran.copy_id)
        res.append(dict({'Reader_ID':reader.ID,'Title': copy.book.title,'ISBN':copy.book.ISBN,
        'Copy_ID':copy.copy_id,'Borrow_Date':tran.borrow_date, 'Return_Date':tran.return_date,'Truely_Return_Date':tran.truely_return_date,
        'Status':tran.status}))
    return render_template('records.html',transactions = transactions,res=res,reader_id=reader_id,endpoint='librarian.get_records')

@librarian_blueprint.route('/borrowing_books/<int:reader_id>',methods=['GET','POST'])
@librarian_permission
def borrowing_books(reader_id):
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    trans = Transaction.query.filter_by(reader_id = reader_id, status=TIME_IN).all()
    if len(trans) > 2:
        print(trans)
        flash('Error1')
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    copies = [Book_Copy.query.get(tran.copy_id) for tran in trans]
    for copy in copies:
        if copy is None:
            flash('Error2')
            return redirect(url_for('librarian.get_readers',content='_',page=1))
    return render_template('borrowing_books.html',copies = copies)


@librarian_blueprint.route('/edit_reader/<int:reader_id>',methods=['GET','POST'])
@librarian_permission
def edit_reader(reader_id):
    
    form = EditReaderForm()
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    if form.validate_on_submit():
        reader.ID = form.ID.data
        reader.name = form.name.data
        reader.sex = form.sex.data
        db.session.add(reader)
        db.session.commit()
        flash('Successful')
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    form.ID.data = reader.ID
    form.name.data = reader.name
    form.sex.data = reader.sex
    return render_template('edit_reader.html',form=form)

@librarian_blueprint.route('/cancel_reader/<int:reader_id>',methods=['GET','POST'])
@librarian_permission
def cancel_reader(reader_id):
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't find this reader")
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    trans = Transaction.query.filter_by(reader_id = reader.reader_id, status=TIME_IN).all()
    if len(trans) != 0:
        flash("This reader has borrowed books")
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    if reader.fine > 0:
        flash("This reader has fine")
        return redirect(url_for('librarian.get_readers',content='_',page=1))

    db.session.delete(reader)
    db.session.commit()


@librarian_blueprint.route('/system_setting',methods=['GET','POST'])
@librarian_permission
def system_setting():
    form = SystemForm()
    system = System.query.get(1)
    if not system:
        system = System(1.0,20.0)
        db.session.add(system)
        db.session.commit()
    if form.validate_on_submit():
        system.fine = form.fine.data
        system.damage_fine = form.damage_fine.data
        db.session.add(system)
        db.session.commit()
        flash('Successful')
        return redirect(url_for('librarian.system_setting'))
    form.fine.data = system.fine
    form.damage_fine.data = system.damage_fine

    return render_template('system.html',form=form)
        
@librarian_blueprint.route('/income',methods=['GET','POST'])
@librarian_permission
def income():
    form = IncomeForm()
    x = []
    y = []
    if form.validate_on_submit():
        if form.way.data == 1:
            #year
            data = db.session.query(Income.year,func.sum(Income.income)).group_by(Income.year).all()
            x = [str(d[0]) for d in data]
            y = [d[1] for d in data]
            return render_template('income.html',form=form,data=zip(x,y))

        elif form.way.data ==2:
            #month
            res = dict()
            data = db.session.query(Income.year, Income.month, func.sum(Income.income)).group_by(Income.year,Income.month).all()
            # for d in data:
            #     if res.get(d[0],-1) == -1:
            #         res[d[0]] = [(d[1],d[2])]
            #     else:
            #         res[d[0]].append((d[1],d[2]))
            # labels = [str(i+1) for i in range(12)]   
            # datesets = []

            x = [str(d[0])+'-'+str(d[1]) for d in data]
            y = [d[2] for d in data]
            return render_template('income.html',form=form,data=zip(x,y))
        elif form.way.data == 3:
            #week
            data = db.session.query(Income.year, Income.week, func.sum(Income.income)).group_by(Income.year,Income.week).all()
    
            x = [str(d[0])+'-'+str(d[1]) for d in data]
            y = [d[2] for d in data] 
            return render_template('income.html',form=form,data=zip(x,y))
        elif form.way.data == 4:
            #day
          
            data = db.session.query(Income.date, Income.income).all()
            x = [str(d[0]) for d in data]
            y = [d[1] for d in data]
            return render_template('income.html',form=form,data=zip(x,y))

        else:
            pass
    return render_template('income.html',form=form,data=zip(x,y))

@librarian_blueprint.route('/return_fine/<int:reader_id>',methods=['GET','POST'])
@librarian_permission
def return_fine(reader_id):
    form = ReturnFineForm()
    reader = Reader.query.get(reader_id)
    if not reader:
        flash("Can't fine this reader")
        return redirect(url_for('librarian.get_readers',content='_',page=1))

    if form.validate_on_submit():
        
        
        if form.fine.data > reader.fine:
            flash("The return fine large than reader fine")
            return redirect(url_for('librarian.return_fine',reader_id=reader_id))
        reader.fine -= form.fine.data
        income = Income.query.filter_by(date=datetime.date(datetime.now())).first()
        if not income:
            income = Income(date,get_year(date),get_month(date),get_week(date),0.0)
            db.session.add(income)
            db.session.commit()
        income.income += form.fine.data
        db.session.add_all([reader,income])
        db.session.commit()


        flash('Successful')
        return redirect(url_for('librarian.get_readers',content='_',page=1))
    return render_template('return_fine.html',form=form,reader_id=reader_id)




    