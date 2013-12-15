from app import db, app
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
import flask.ext.whooshalchemy as whooshalchemy
from sqlalchemy.ext.associationproxy import association_proxy
from config import WHOOSH_ENABLED

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

tags = db.Table('tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag', db.Integer, db.ForeignKey('tag.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    password = db.Column(db.Text)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    # postcolor = db.Column(db.Text)
    nickname = db.Column(db.Text)
    bio = db.Column(db.Text)
    last_seen = db.Column(db.DateTime)
    last_seen_form = db.Column(db.Text)
    followed = db.relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return 'User %r>' % (self.email)

    def check_password(self, password):
        print self.password, password
        return check_password_hash(self.password, password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        return self.email
    
    def __init__(self, email, password, role):
        self.email = email
        self.set_password(password)
        self.role = role

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?s=%s&d=retro' % (md5(self.email).hexdigest(), str(size))

    # def follow(self, user):
    #     if not self.is_following(user):
    #         self.followed.append(user)
    #         return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
        
class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    title = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_time = db.Column(db.DateTime)
    post_time_form = db.Column(db.Text)
    link = db.Column(db.Text)
    tagged = db.relationship('Tag', 
        secondary = lambda:tags,
        primaryjoin = (tags.c.post_id == id),
        backref = db.backref('tags', lazy = 'dynamic'), 
        # lazy = 'dynamic'
        )
    
    post_tags = association_proxy('tagged','tag')

    def __repr__(self):
        return '<Post %r>' % (self.body)

class Tag(db.Model):
    __searchable__ = ['tag']

    id = db.Column(db.Integer, primary_key = True)
    tag = db.Column('tag',db.String(140))


if WHOOSH_ENABLED:
    import flask.ext.whooshalchemy as whooshalchemy
    whooshalchemy.whoosh_index(app, Post)
    whooshalchemy.whoosh_index(app, Tag)