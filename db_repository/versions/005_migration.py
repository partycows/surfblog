from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=140)),
    Column('title', String(length=120)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('post_time', DateTime),
    Column('post_time_form', Text),
    Column('link', Text),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('password', Text),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('nickname', Text),
    Column('bio', Text),
    Column('last_seen', DateTime),
    Column('last_seen_form', Text),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['post'].columns['link'].create()
    post_meta.tables['post'].columns['post_time'].create()
    post_meta.tables['post'].columns['post_time_form'].create()
    post_meta.tables['post'].columns['title'].create()
    post_meta.tables['user'].columns['bio'].create()
    post_meta.tables['user'].columns['last_seen'].create()
    post_meta.tables['user'].columns['last_seen_form'].create()
    post_meta.tables['user'].columns['nickname'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['post'].columns['link'].drop()
    post_meta.tables['post'].columns['post_time'].drop()
    post_meta.tables['post'].columns['post_time_form'].drop()
    post_meta.tables['post'].columns['title'].drop()
    post_meta.tables['user'].columns['bio'].drop()
    post_meta.tables['user'].columns['last_seen'].drop()
    post_meta.tables['user'].columns['last_seen_form'].drop()
    post_meta.tables['user'].columns['nickname'].drop()
