from flask import Flask, render_template, url_for, redirect
from webapp.config import DevConfig
from webapp.models import db
from flask_bootstrap import Bootstrap
from webapp.extends import bcrypt, login_manager


from webapp.controllers.main import main_blueprint 
from webapp.controllers.result import result_blueprint
from webapp.controllers.librarian import librarian_blueprint
from webapp.controllers.reader import reader_blueprint
from webapp.controllers.admin import admin_blueprint




def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)
    Bootstrap(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(admin_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(result_blueprint)
    app.register_blueprint(librarian_blueprint)
    app.register_blueprint(reader_blueprint)
    
    @app.route('/')
    def index():
        return redirect(url_for('main.index'))

    return app
    

