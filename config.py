import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
# SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/app.db'

CSRF_ENABLED = True
SECRET_KEY = 'secret_k3y'

# WHOOSH_ENABLED = os.environ.get('HEROKU') is None
WHOOSH_ENABLED = False

POSTS_PER_PAGE = 3

MAX_SEARCH_RESULTS = 50

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'surfblog.bot@gmail.com'
MAIL_PASSWORD = 'beansbooze'
ADMIN = ['surfblog.bot@gmail.com']