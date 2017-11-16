class Config(object):
    SECRET_KEY = 'Librarian_Manage_System'

class ProbConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://webapp:webapp@localhost:3306/lms'
