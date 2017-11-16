from flask import Blueprint, render_template, redirect, url_for, flash
from webapp.forms import SearchForm, LoginForm, RegisterLibrarianForm
from webapp.constant import PAGINATION 
from webapp.models import Reader, Librarian, db, Admin
from flask_login import login_user, logout_user, current_user, login_required
from flask_login.mixins import AnonymousUserMixin
from webapp.permission import any_permission
from os import path

main_blueprint = Blueprint('main',__name__,
    static_folder=path.join(path.pardir,'static'),
    template_folder=path.join(path.pardir,'templates','main')
    ,url_prefix='/main')



@main_blueprint.route('/login',methods=['GET','POST'])
@any_permission
def login():
    # if current_user.is_authenticated:
    #     flash('You have logged in')
    #     return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.role.data == 1:

            user = Reader.query.filter_by(ID=form.id.data).first()
        elif form.role.data == 2:

            user = Librarian.query.filter_by(ID=form.id.data).first()
        elif form.role.data == 3:

            user = Admin.query.filter_by(ID = form.id.data).first()
        else:
            user = None

        if user is not None:
            login_user(user,remember=form.remember.data)
            
            return redirect(url_for('main.index'))
    return render_template('login.html',form=form)




@main_blueprint.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('main.index'))

@main_blueprint.route('/',methods=['GET','POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        method = form.methods.data
        content = form.content.data
        if method == 1:
            return redirect(url_for('result.result_title',content=content,page=1))
        elif method == 2:
            return redirect(url_for('result.result_author',content=content,page=1))
        elif method == 3:
            return redirect(url_for('result.result_ISBN',content=content))  
        else:
            return None
    return render_template('index.html',form=form)
