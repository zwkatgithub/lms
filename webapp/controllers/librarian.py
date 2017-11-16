from flask import Blueprint, render_template, url_for, redirect, current_app, flash,session,g
from webapp.models import Reader, Librarian, Book, Book_Copy, Transaction, db
from webapp.forms import RegisterReaderForm, AddBookForm, AddCopyForm,EditBookForm,BookForm, EditBookCopyForm,BookSearchForm,BorrowBookForm, ReturnBookForm, DeleteBook, DeleteEntity, Search
from flask_login import current_user

from webapp.constant import  TIME_OUT, TIME_IN,PAGINATION, BORROWED, DAMAGED, ON_THE_SHELF, LOST, DEALING
from webapp.extends import GetBook, download_picture
from webapp.permission import librarian_permission
import os
from datetime import timedelta, datetime
import re

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
        else:
            flash('Error')
            books = None
        
    return render_template('books.html',form=form,books = books,content=content,endpoint='librarian.get_books',summary='')
@librarian_blueprint.route('/books/ISBN/<string:content>/<int:page>',methods=['POST','GET'])
@librarian_permission
def get_books_ISBN(content,page):
    form = BookSearchForm()
    books = Book.query.filter_by(ISBN = content).paginate(page,PAGINATION)
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
        
    return render_template('books.html',form=form,books=books,content=content,endpoint='librarian.get_books_ISBN')
@librarian_blueprint.route('/books/title/<string:content>/<int:page>',methods=['POST','GET'])
@librarian_permission
def get_books_title(content,page):
    form  = BookSearchForm()
    books = Book.query.filter(Book.title.like('%'+content+'%')).paginate(page,PAGINATION)
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
    return  render_template('book_copies.html',book_copies = book_copies)

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

@librarian_blueprint.route('/edit_copy/<int:copy_id>',methods=['GET','POST'])
@librarian_permission
def edit_copy(copy_id):
    form = EditBookCopyForm()
    copy = Book_Copy.query.get(copy_id)
    if not copy:
        flash("Can't find this copy")
        return redirect(url_for('librarian.get_books',content='_',page=1))
    if form.validate_on_submit():
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
            path = 'default.png'
        if not path:
            flash('Download picture failed')
        form.book_form.form.file.filename = 'tmp' +'.'+ path.split('.')[-1]
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
        if form.book_form.form.file.filename.find('tmp') == -1:
            form.book_form.form.file.save(os.path.join(current_app.root_path+'/static/picture',picture))
        else:
            os.rename(os.path.join(current_app.root_path+'/static/picture','tmp.'+book.picture.split('.')[-1]),
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
    transactions = reader.transactions.all()
    for tran in transactions:
        if tran.status == TIME_IN and copy.copy_id == tran.copy_id:
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
            if copy[1].status == BORROWED:
                flash("This copy(%r) can't be borrowed" % str(copy.copy_id))
                return redirect(url_for('librarian.borrow_book'))
            if not check_same_book(reader,copy[1]):
                flash("This reader has borrowed a same book : %r" % copy.book.title)
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
    return 0.2
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
            copy.status = DEALING
            copy.return_date = None
            transaction.status = TIME_OUT
            reader.fine = calc_fine(copy,reader)
            db.session.add_all([copy,reader,transaction])
            db.session.commit()
            res.clear()

        return redirect(url_for('librarian.return_book'))
    return render_template('return_book.html',form=form)
        

    
        



@librarian_blueprint.route('/system_setting',methods=['GET','POST'])
@librarian_permission
def system_setting():
    pass
@librarian_blueprint.route('/return_fine',methods=['GET','POST'])
@librarian_permission
def return_fine():
    pass


# @librarian_blueprint.route('/borrow',methods=['GET','POST'])
# @librarian_permission
# def borrow_book():
#     form = BorrowBook()
#     if form.validate_on_submit():
#         reader = Reader.query.filter_by(ID=form.ID.data).first()
#         if not reader:
#             flash("Can't find this reader")
#             return redirect(url_for('librarian.borrow_book'))
#         copy =  Book_Copy.query.get(form.copy_id.data)
#         if not copy:
#             flash("Can't find this copy")
#             return redirect(url_for('librarian.borrow_book'))
#         trans = reader.transactions.all()
#         for t in trans:
#             if t.status == TIME_IN:
#                 tb = Book_Copy.query.get(t.copy_id)
#                 if tb.book.ISBN == copy.book.ISBN:
#                     flash('You have borrowd this book')
#                     return redirect(url_for('librarian.borrow_book'))
#         borrow_date = datetime.date(datetime.now())
#         return_date = datetime.date(datetime.now()) + timedelta(days=form.days.data)
#         copy.status = OUT
#         copy.return_date = return_date

#         transaction = Transaction(reader.reader_id,current_user.librarian_id,copy.copy_id,TIME_IN,
#             borrow_date,return_date)

#         db.session.add(copy)
#         db.session.add(transaction)
#         db.session.commit()
#         flash('Successful')
#         return redirect(url_for('librarian.borrow_book'))
#     return render_template('borrow.html',form=form)

# def check_none(obj,cont):
#     if not obj:
#         flash(cont)
#         return False
#     return True
        
# @librarian_blueprint.route('/return',methods=['GET','POST'])
# @librarian_permission
# def return_book():
#     form = ReturnBook()
#     if form.validate_on_submit():
#         #Reader = Reader.query.filter_by(Reader_number=form.Reader_number.data).first()
#        # if not check_none(Reader,"Cant' find this Reader"):
#        #     return redirect(url_for('admin.return_book'))
#         copy = Book_Copy.query.get(form.copy_id.data)
#         if not check_none(entity,"Cant' find this copy"):
#             return redirect(url_for('librarian.return_book'))
#         #check_none(Reader,"Cant' find this Reader",redirect(url_for('admin.return_book')))
#         borrow_transaction = Transaction.query.filter_by(
#             copy_id = form.copy_id.data,
#             status=TIME_IN).first()
#         if not check_none(borrow_transaction,"Can't find borrow transaction"):
#             return redirect(url_for('librarian.return_book'))
#         borrow_transaction.status = TIME_OUT
#         borrow_transaction.return_date = datetime.date(datetime.now())
#         copy.status = IN
#         copy.return_date = None

#         db.session.add_all([borrow_transaction,copy])
#         db.session.commit()

#         flash('Successful')
#         return redirect(url_for('librarian.return_book'))
#     return render_template('return.html',form=form)


# @librarian_blueprint.route('/enter/book',methods=['GET','POST'])
# @librarian_permission
# def enter_book():
#     form = BookForm()
#     if form.validate_on_submit():
#         picture = form.file.data.filename
#         new_book = Book(form.title.data,form.author.data,
#             form.press.data,form.publish_date.data,form.ISBN.data,
#             form.summary.data,form.price.data,form.location.data,
#             picture,form.reference_number.data)

#         db.session.add(new_book)
#         db.session.commit()

#         picture = str(new_book.book_id) + '.'+picture.split('.')[1]
#         new_book.picture = picture
#         db.session.add(new_book)
#         db.session.commit()

#         form.file.data.save(os.path.join(current_app.root_path+'/static/picture',picture))
#         for i in range(form.number.data):
#             book = Book_Copy(new_book.book_id,status=IN,return_date=None)
#             db.session.add(book)
#         db.session.commit()
#         flash('Successful')
#         return redirect(url_for('librarian.enter_book'))
#     return render_template('enter.html',form=form)

# @librarian_blueprint.route('/enter/entity',methods=['GET','POST'])
# @librarian_permission
# def enter_entity():
#     form = EntityForm()
#     if form.validate_on_submit():
#         book = Book.query.filter_by(ISBN= form.ISBN.data).first()
#         if not book:
#             flash("Can't find this book.")
#             return redirect(url_for('librarian.enter_entity'))
#         for i in range(1,form.number.data+1):
#             entity = Book_Copy(book.book_id,IN,None)
#             db.session.add(entity)
#         db.session.commit()
#         flash('Successful')
#         return redirect(url_for('librarian.enter_entity'))
#     return render_template('enter.html',form=form)
        
# @librarian_blueprint.route('/delete/book',methods=['GET','POST'])
# @librarian_permission
# def delete_book():
#     form = DeleteBook()
#     if form.validate_on_submit():
#         book = Book.query.filter_by(ISBN= form.ISBN.data).first()
#         if not check_none(book,"Can't find this book"):
#             return redirect(url_for('librarian.delete_book'))
#         for b in book.entities.all():
#             db.session.delete(b)
#         pic_path = os.path.join(current_app.root_path+'/static/picture/',book.picture)
#         os.remove(pic_path)
#         db.session.delete(book)
#         db.session.commit()
#         flash('Successful')
#         return redirect(url_for('librarian.delete_book'))
#     return render_template('delete.html',form=form)

# @librarian_blueprint.route('/delete/entity',methods=['GET','POST'])
# @librarian_permission
# def delete_entity():
#     form = DeleteEntity()
#     if form.validate_on_submit():
#         entity = Book_Copy.query.get(form.entity_id.data)
#         if not check_none(entity,"Can't find this book entity"):
#             return redirect(url_for('librarian.delete_entity'))
#         db.session.delete(entity)
#         db.session.commit()
#         flash('Successful')
#         return redirect(url_for('librarian.delete_entity'))
#     return render_template('delete.html',form=form)

# global_book = None
# @librarian_blueprint.route('/edit_search',methods=['POST','GET'])
# @librarian_permission
# def edit_search():
#     global global_book
#     search = Search()
#     if search.validate_on_submit():
#         global_book = Book.query.filter_by(ISBN=search.isbn.data).first()
#         #print(book)
#         if global_book is None:
#             flash("Can't find this book")
#             return render_template('edit_search.html',search=search)
#         #global_book = book.book_id
#         return redirect(url_for('librarian.edit_result',id = global_book.book_id))
    
#     return render_template('edit_search.html',search=search)

# @librarian_blueprint.route('/edit_result/<int:id>',methods=['POST','GET'])
# @librarian_permission
# def edit_result(id):
#     global global_book
#     form = EditBookForm()
#     #book = Book.query.get(id)
#     if global_book is None:
#         flash("Cant't find this book")
#         return redirect(url_for('librarian.edit_search'))

#     if form.validate_on_submit():
#         print('this')
#         #book = Book.query.get(id)
#         if global_book is None :
#             flash('Error')
#             return redirect(url_for('librarian.edit_search'))
        
#         global_book.title = form.title.data
#         global_book.author = form.author.data
#         global_book.press = form.press.data
#         global_book.publish_date = form.publish_date.data
#         global_book.ISBN = form.ISBN.data
#         global_book.price = form.price.data
#         global_book.summary = form.summary.data
#         global_book.location = form.location.data
#         if form.number.data != len(Book_Copy.query.filter_by(book_id=global_book.book_id).all()):
#             flash('The number of entity is not equal this number') 
#             return redirect(url_for('librarian.edit_search'))
#         global_book.reference_number = form.reference_number.data
#         if len(form.file.data.filename) != 0:
#             form.file.data.save(os.path.join(current_app.root_path+'/static/picture',global_book.picture))

#         db.session.add(global_book)
#         db.session.commit()
#         flash('Successful')

#         return redirect(url_for('librarian.edit_search'))

    
#     form.title.data = global_book.title
#     form.author.data = global_book.author
#     form.press.data = global_book.press
#     form.publish_date.data = global_book.publish_date
#     form.ISBN.data = global_book.ISBN
#     form.price.data = global_book.price
#     form.summary.data = global_book.summary
#     form.location.data = global_book.location
#     form.number.data = len(Book_Copy.query.filter_by(book_id=global_book.book_id).all())
#     form.reference_number.data = global_book.reference_number

#     return render_template('edit_result.html',form=form,picture=global_book.picture,book_id=global_book.book_id)
    



    