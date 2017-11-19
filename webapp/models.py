from flask_sqlalchemy import SQLAlchemy
from webapp.constant import DEFAULT_LENGTH, ISBN_LENGTH, NAME_LENGTH
from webapp.extends import bcrypt
from flask_login import AnonymousUserMixin

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'book'

    book_id = db.Column(db.Integer(), primary_key = True)
    title = db.Column(db.String(DEFAULT_LENGTH))
    author = db.Column(db.String(DEFAULT_LENGTH))
    press = db.Column(db.String(DEFAULT_LENGTH))
    publish_date = db.Column(db.String(DEFAULT_LENGTH))
    ISBN = db.Column(db.String(ISBN_LENGTH))
    price = db.Column(db.Float())
    summary = db.Column(db.String(10*DEFAULT_LENGTH))
    #location = db.Column(db.String(DEFAULT_LENGTH)) 每本书的location可能不一样
    picture = db.Column(db.String(DEFAULT_LENGTH)) #书的图片的相对地址


    copies = db.relationship('Book_Copy',backref='book',lazy='dynamic')


    def __init__(self, title, author, press, publish_date, ISBN, summary, price,
         picture):
        self.title = title
        self.author = author
        self.press = press
        self.publish_date = publish_date
        self.ISBN= ISBN
        self.price = price
        self.summary = summary
        #self.location = location
        self.picture = picture
        #self.reference_number = reference_number

    def __repr__(self):
        return "<Book %r>" % self.title

class Book_Copy(db.Model):
    __tablename__ = 'book_copy'

    copy_id = db.Column(db.Integer(), primary_key = True)

    book_id = db.Column(db.Integer(),db.ForeignKey('book.book_id'))
    status = db.Column(db.Integer())
    return_date = db.Column(db.Date())
    location = db.Column(db.String(DEFAULT_LENGTH))

    def __init__(self,book_id, status, return_date, location):
        self.book_id = book_id
        self.status = status
        self.return_date = return_date
        self.location = location

    def __repr__(self):
        return '<Book Copy %d-%d>' % (self.book_id, self.copy_id)
#system setting: fine 1/day ,borrow days , 
class Reader(db.Model):
    __tablename__ = 'reader'

    reader_id = db.Column(db.Integer(),primary_key = True)
    ID = db.Column(db.String(DEFAULT_LENGTH))
    name = db.Column(db.String(NAME_LENGTH))
    sex = db.Column(db.Integer())
    password = db.Column(db.String(DEFAULT_LENGTH))
    fine = db.Column(db.Float())
    deposit = db.Column(db.Float())

    transactions = db.relationship('Transaction',backref='reader',lazy='dynamic')


    def __init__(self,ID,name,sex,fine,deposit):
        self.ID = ID
        self.name = name
        self.sex = sex
        self.fine = fine
        self.deposit = deposit

    def __repr__(self):
        return "<Reader %r>" % self.ID

    def set_password(self,password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)

    def is_authenticated(self):
        if isinstance(self,AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.ID)

    def is_reader(self):
        return True

    def is_librarian(self):
        return False
 
    def is_admin(self):
        return False

class Librarian(db.Model):
    __tablename__ = 'librarian'

    librarian_id = db.Column(db.Integer(),primary_key = True)
    ID = db.Column(db.String(DEFAULT_LENGTH))
    name = db.Column(db.String(NAME_LENGTH))
    sex = db.Column(db.Integer())
    password = db.Column(db.String(DEFAULT_LENGTH))

    transactions = db.relationship('Transaction',backref='librarian',lazy='dynamic')

    def __init__(self,ID,name,sex):
        self.ID = ID
        self.name = name
        self.sex = sex

    def __repr__(self):
        return '<Librarian %r>' % self.ID

    def set_password(self,password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)

    def is_authenticated(self):
        if isinstance(self,AnonymousUserMixin):
            return False
        else:
            return True
    def is_active(self):
        return True
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False
    def get_id(self):
        return str(self.ID)
    
    
    def is_reader(self):
        return False
   
    def is_librarian(self):
        return True
   
    def is_admin(self):
        return False

class Admin(db.Model):
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer(),primary_key = True)
    ID = db.Column(db.String(DEFAULT_LENGTH))
    password = db.Column(db.String(DEFAULT_LENGTH))

    def __init__(self,ID):
        self.ID = ID

    def __repr__(self):
        return '<Admin %r>' % self.ID

    def set_password(self,password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self,password):
        return bcrypt.check_password_hash(self.password,password)

    def is_authenticated(self):
        if isinstance(self,AnonymousUserMixin):
            return False
        else:
            return True
    def is_active(self):
        return True
    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False
    def get_id(self):
        return str(self.ID)
    
  
    def is_reader(self):
        return False

    def is_librarian(self):
        return False

    def is_admin(self):
        return True


class Transaction(db.Model):
    __tablename__ = 'transaction'

    transaction_id = db.Column(db.Integer(),primary_key = True)
    reader_id = db.Column(db.Integer(), db.ForeignKey('reader.reader_id'))
    copy_id = db.Column(db.Integer(), db.ForeignKey('book_copy.copy_id'))
    librarian_id = db.Column(db.Integer(), db.ForeignKey('librarian.librarian_id'))

    status = db.Column(db.Integer())
    borrow_date = db.Column(db.Date())
    return_date = db.Column(db.Date())
    truely_return_date = db.Column(db.Date())

    def __init__(self, reader_id, librarian_id,copy_id,status,borrow_date,return_date):
        self.reader_id = reader_id
        self.copy_id = copy_id
        self.librarian_id = librarian_id
        self.status = status
        self.borrow_date = borrow_date
        self.return_date = return_date

    def __repr__(self):
        return '<Transaction %d-%d-%d>' %(self.reader_id,self.copy_id,self.librarian_id)

class FineChange(db.Model):
    __tablename__='finechange'

    finechange_id = db.Column(db.Integer(),primary_key=True)
    start_date = 	db.Column(db.Date())
    fine = db.Column(db.Float())

    def __init__(self,start_date, fine):
        self.start_date = start_date
        self.fine  = fine

    def __repr__(self):
        return '<Start Date %r : Fine %r>' %(self.start_date, self.fine)

class Income(db.Model):
    __tablename__ = 'income'
    income_id = db.Column(db.Integer(),primary_key=True)
    date = db.Column(db.Date())
    week = db.Column(db.Integer())
    year = db.Column(db.Integer())
    month = db.Column(db.Integer())
    income = db.Column(db.Float())

    def __init__(self,date,year,month,week,income):
        self.date = date
        self.income = income

    def __repr__(self):
        return '<Date : %r - Income : %r>' %(self.date, self.income)

class System(db.Model):
    __tablename__='system'
    system_id = db.Column(db.Integer(),primary_key=True)
    fine = db.Column(db.Float())
    damage_fine = db.Column(db.Float())
   
    def __init__(self,fine,damage_fine):
        self.fine = fine
        self.damage_fine = damage_fine

    def __repr__(self):
       return '<Fine : %r Damage Fine : %r>' %(self.fine, self.damage_fine)

