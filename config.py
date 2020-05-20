import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:adminadmin@broadwaydb-1.cf4rkq7ardim.us-east-1.rds' \
                              '.amazonaws.com/broadwaydb'
        # os.environ.get('DATABASE_URL') or \
        # 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False