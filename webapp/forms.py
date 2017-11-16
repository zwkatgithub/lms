from flask_wtf import FlaskForm
from wtforms import SelectField,FormField,FieldList,FileField ,TextAreaField,StringField, SubmitField, PasswordField, DateField,BooleanField ,IntegerField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange
from webapp.constant import choices, DEFAULT_LENGTH, sex_choices, login_choices, book_choices
from webapp.models import Reader, Librarian, Admin
from flask import flash

class SearchForm(FlaskForm):
    methods = SelectField('Methods',validators=[DataRequired()],coerce=int,choices = choices)
    content = StringField('Content',validators=[DataRequired(),Length(max=127)])

class BookSearchForm(FlaskForm):
    methods = SelectField('Methods',validators=[DataRequired()],coerce=int,choices=book_choices)
    content = StringField('Content',validators=[DataRequired(), Length(max=127)])
    search = SubmitField('Search')


class LoginForm(FlaskForm):
    id = StringField('ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember')
    #librarian = BooleanField('Librarian')
    #admin = BooleanField('Admin')

    role = SelectField('Role',validators=[DataRequired()],coerce=int,choices=login_choices)
    login = SubmitField('Log in')

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False
        
        # if not self.librarian.data :
        #     user = Reader.query.filter_by(reader_number = self.id.data).first()
        # else:
        #     user = Librarian.query.filter_by(librarian_number = self.id.data).first()
        user = None
        if self.role.data == 1:
            #reader
            user = Reader.query.filter_by(ID = self.id.data).first()
        elif self.role.data == 2 :
            user = Librarian.query.filter_by(ID = self.id.data).first()
        elif self.role.data == 3:
            user = Admin.query.filter_by(ID = self.id.data).first()
        else:
            flash('Role wrong')
            return False

        if not user:
            flash('Invalid id or password')
            return False

        if not user.check_password(self.password.data):
            flash('Invalid id or password')
            return False
        return True

class RegisterLibrarianForm(FlaskForm):
    
    ID = StringField('ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    name = StringField('Name',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    sex = SelectField('Sex',validators=[DataRequired()],choices=sex_choices,coerce=int)
    password = PasswordField('Password',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    confirm = PasswordField('Confirm Password',[DataRequired(),EqualTo('password')])
    register = SubmitField('Register')

    def validate(self):
        check_validate = super(RegisterLibrarianForm,self).validate()

        if not check_validate:
            return False

        librarian = Librarian.query.filter_by(ID=self.ID.data).first()

        if librarian:
            flash('The user has been registered')
            return False

        return True

class BookForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    author = StringField('Author',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    press = StringField('Press',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    publish_date = StringField('Publish Date',validators=[DataRequired()])
    ISBN = StringField('ISBN',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    price = FloatField('Price',validators=[DataRequired()])
    summary = TextAreaField('Summary',validators=[DataRequired()])
    number = IntegerField('Number',validators=[DataRequired()])
    


    file = FileField('Picture')

    submit = SubmitField('Submit')
class EditBookForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    author = StringField('Author',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    press = StringField('Press',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    publish_date = StringField('Publish Date',validators=[DataRequired()])
    ISBN = StringField('ISBN',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    price = FloatField('Price',validators=[DataRequired()])
    summary = TextAreaField('Summary',validators=[DataRequired()])



    file = FileField('Picture')

    submit = SubmitField('Submit')

class EditBookCopyForm(FlaskForm):
    status = SelectField('Status',validators=[DataRequired()],coerce=int,choices=[(1,'On the shelf'),
    (2,'Borrowed'),(8,'Damaged'),(16,'Lost'),(32,'Dealing')])
    location = StringField('Location',validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddCopyForm(FlaskForm):
    #copy_number = IntegerField('Copy Number',validators=[DataRequired()],default=1)
    add = SubmitField('Add')
    locations = FieldList(StringField('Location'),label='Copies',min_entries=1)
    submit = SubmitField('Submit')

class BookInfoForm(FlaskForm):
    title = StringField('Title')
    author = StringField('Author')
    press = StringField('Press')
    publish_date = StringField('Publish Date')
    ISBN = StringField('ISBN')
    price = StringField('Price')
    summary = TextAreaField('Summary')
    file = FileField('Picture')
class CopyForm(FlaskForm):
    add = SubmitField('Add')
    locations = FieldList(StringField('Location'),label='Copies',min_entries=1)
class AddBookForm(FlaskForm):
    ISBN = StringField('ISBN',validators=[DataRequired()])
    book_form = FormField(BookInfoForm,'Book Information')
    copies = FormField(CopyForm,'Add Copy')
    submit = SubmitField('Submit')


class EditLibrarianForm(FlaskForm):
    ID = StringField('ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    name = StringField('Name',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    sex = SelectField('Sex',validators=[DataRequired()],choices=sex_choices,coerce=int)
    submit = SubmitField('Submit')

class RegisterReaderForm(FlaskForm):
    ID = StringField('ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    name = StringField('Name',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    sex = SelectField('Sex',validators=[DataRequired()],choices=sex_choices,coerce=int)
    password = PasswordField('Password',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    confirm = PasswordField('Confirm Password',[DataRequired(),EqualTo('password')])
    deposit = FloatField('Deposit',validators=[DataRequired()],default=300.0)
    check_deposit = BooleanField('Check Deposit')
    register = SubmitField('Register')

    def validate(self):
        check_validate = super(RegisterReaderForm,self).validate()

        if not check_validate:
            return False

        reader = Reader.query.filter_by(ID=self.ID.data).first()

        if reader:
            flash('The user has been registered')
            return False
        if not self.check_deposit.data:
            flash('Require deposit')
            return False

        return True


class BorrowBookForm(FlaskForm):
    ID = StringField('ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    
    copy_ids = FieldList(IntegerField('Copy ID'),min_entries=1,max_entries=2)
    
    
    add = SubmitField('Add')
    days = IntegerField('Days',validators=[DataRequired(),NumberRange(min=1,max=60,message="[1-60]")],default=30)
    borrow = SubmitField('Borrow')
    submit = SubmitField('Submit')

class ReturnBookForm(FlaskForm):
    #Reader_number = StringField('Reader ID',validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    copy_ids = FieldList(IntegerField(' '),'Copy ID',min_entries=1)
    add = SubmitField('Add')
    return_ = SubmitField('Return')
    submit = SubmitField('Submit')

class DeleteBook(FlaskForm):
    ISBN = StringField("ISBN",validators=[DataRequired(),Length(max=DEFAULT_LENGTH)])
    delete = SubmitField('Delete')

class DeleteEntity(FlaskForm):
    entity_id = IntegerField('Entity ID',validators=[DataRequired()])
    delete = SubmitField('Delete')

class Search(FlaskForm):
    isbn = StringField('ISBN',validators=[DataRequired(),Length(max=13)])
    search = SubmitField('Search')



    