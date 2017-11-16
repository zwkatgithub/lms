from flask import Blueprint, render_template, url_for, redirect, current_app, flash
import os
from webapp.permission import admin_permission
from webapp.forms import RegisterLibrarianForm, EditLibrarianForm
from webapp.models import Librarian,db


admin_blueprint = Blueprint('admin',__name__,
    static_folder=os.path.join(os.path.pardir,'static'),
    template_folder=os.path.join(os.path.pardir,'templates','admin'),
    url_prefix='/admin')
@admin_blueprint.route('/')
@admin_permission
def main():
    return redirect(url_for('admin.get_librarians'))

@admin_blueprint.route('/register_librarian',methods=['GET','POST'])
@admin_permission
def register_librarian():
    form = RegisterLibrarianForm()
    if form.validate_on_submit():
        librarian = Librarian(form.ID.data,form.name.data,form.sex.data)
        librarian.set_password(form.password.data)
        db.session.add(librarian)
        db.session.commit()
        return redirect(url_for('admin.main'))
    return render_template('register_librarian.html',form=form)

@admin_blueprint.route('/delete_librarian',methods=['GET','POST'])

@admin_blueprint.route('/librarians')
@admin_permission
def get_librarians():
    libs = Librarian.query.all()

    return render_template('librarians.html',ts=libs)

@admin_blueprint.route('/edit_librarian/<string:ID>',methods=['GET','POST'])
@admin_permission
def edit_librarian(ID):
    form = EditLibrarianForm()
    librarian = Librarian.query.filter_by(ID= ID).first()
    if not librarian:
        flash("Can't find this librarian")
        return redirect(url_for('admin.get_librarians'))
    if form.validate_on_submit():
        librarian.ID = form.ID.data
        librarian.name = form.name.data
        librarian.sex = form.sex.data
        db.session.add(librarian)
        db.session.commit()
        return redirect(url_for('admin.get_librarians'))
    form.ID.data = librarian.ID
    form.name.data = librarian.name
    form.sex.data = librarian.sex

    return render_template('edit_librarian.html',form=form)
        

@admin_blueprint.route('/delete_librarian/<string:ID>',methods=['GET','POST'])
@admin_permission
def delete_librarian(ID):
    librarian = Librarian.query.filter_by(ID = ID).first()
    print(librarian)
    if not librarian:
        flash("Can't find this librarian")
        return redirect(url_for('admin.get_librarians'))
    db.session.delete(librarian)
    db.session.commit()
    flash('Succefful')
    return redirect(url_for('admin.get_librarians'))


