from flask import Flask, render_template, url_for, redirect
from webapp.config import DevConfig
from webapp.models import db,Income
from flask_bootstrap import Bootstrap
from webapp.extends import bcrypt, login_manager,get_month,get_week,get_year
from flask_apscheduler import APScheduler
from datetime import datetime

from webapp.controllers.main import main_blueprint 
from webapp.controllers.result import result_blueprint
from webapp.controllers.librarian import librarian_blueprint
from webapp.controllers.reader import reader_blueprint
from webapp.controllers.admin import admin_blueprint


def income():
    
    with db.app.app_context():
        date = datetime.date(datetime.now())
        if not Income.query.filter_by(date=date).first() :
            inco = Income(date,get_year(date),get_month(date),get_week(date),0.0)
            
         
            db.session.add(inco)
            db.session.commit()

def create_app(object_name):
    scheduler = APScheduler()

    app = Flask(__name__)
    app.config.from_object(object_name)

    db.app=app
    db.init_app(app)
    Bootstrap(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    scheduler.init_app(app)

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(result_blueprint)
    app.register_blueprint(librarian_blueprint)
    app.register_blueprint(reader_blueprint)
    
    @app.route('/')
    def index():
        return redirect(url_for('main.index'))
    scheduler.start()
    return app

if __name__=='__main__':
    
    scheduler = APScheduler()

    app = Flask(__name__)
    app.config.from_object(object_name)

    db.app=app
    db.init_app(app)
    Bootstrap(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    scheduler.init_app(app)

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(result_blueprint)
    app.register_blueprint(librarian_blueprint)
    app.register_blueprint(reader_blueprint)
    
    @app.route('/')
    def index():
        return redirect(url_for('main.index'))
    scheduler.start()
    app.run()

