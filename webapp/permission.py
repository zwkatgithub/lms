from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for

def any_permission(method):
    @wraps(method)
    def wrapper(*args,**kw):
        if current_user.is_authenticated:
            flash('You have logged in')
            return redirect(url_for('main.index'))
        return method(*args,**kw)
    return wrapper

def librarian_permission(method):
    @wraps(method)
    def wrapper(*args, **kw):
      
        if current_user.is_authenticated and current_user.is_librarian():
            return method(*args,**kw)
        else:
            flash('Permission Need')
            return redirect(url_for('main.index'))
    return wrapper

def reader_permission(method):
    @wraps(method)
    def wrapper(*args, **kw):
        if current_user.is_authenticated and current_user.is_reader():
            return method(*args,**kw)
        else:
            flash('Permission Need')
            return redirect(url_for('main.index'))
    return wrapper

def admin_permission(method):
    @wraps(method)
    def wrapper(*args, **kw):
        if current_user.is_authenticated and current_user.is_admin():
            return method(*args, **kw)
        else:
            flash('Permission Need')
            return redirect(url_for('main.index'))
    return wrapper