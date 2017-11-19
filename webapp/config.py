from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
class Config(object):
    SECRET_KEY = 'Librarian_Manage_System'
    JOBS = [  
            {  
               'id':'income1',  
               'func':'webapp.main:income',  
               'args': '',  
               'trigger': 'interval' ,
               'hours':24
               #'seconds':5
  
             }  
        ]  
    # SCHEDULER_JOBSTORES = {
    #     'default': SQLAlchemyJobStore(url='mysql+pymysql://webapp:webapp@localhost:3306/lms')
    # }

class ProbConfig(Config):
    pass

class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://webapp:webapp@localhost:3306/lms'
