from flask_script import Manager, Server
from webapp.main import create_app
from webapp.models import Book, Book_Copy, Reader, Librarian, Transaction, db, Admin

import os

env = os.environ.get('WEBAPP_ENV','dev')
app = create_app('webapp.config.%sConfig' % env.capitalize())

manager = Manager(app)

manager.add_command('server',Server())



@manager.shell
def make_shell_context():
    return dict(app=app,db=db,Book=Book,Book_Copy=Book_Copy,
                Reader=Reader,Librarian=Librarian,Transaction=Transaction,Admin=Admin)

if __name__ == '__main__':
    #manager.run()
    app.run()

