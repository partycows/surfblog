from flask import render_template, flash, redirect, session, url_for,request,g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from models import User, ROLE_USER, ROLE_ADMIN, Post, followers, Tag, tags
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, WHOOSH_ENABLED
from mail import follower_email

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
    obj = db.session.query(followers).filter_by(follower_id=current_user.id).all()
    obj = [j for i,j in obj]
    obj1 = db.session.query(User).filter(User.id.in_(obj)).all()
    posts = db.session.query(Post).filter_by(user_id=current_user.id).order_by(Post.post_time.desc()).all()
    print 'type', type(current_user.posts)
    print 'listtype', type(posts)
    return render_template("index.html",
        title='Home',
        user=current_user,
        posts= posts,
        followed_users=obj1)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    return render_template('login.html', 
        title = 'Sign In'
        )

@app.route('/performlogin', methods=['POST'])
def performlogin():
    email = request.form.get("email")
    password = request.form.get("password")
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        login_user(user, remember=True)
        session['logged_in'] = True
        return redirect(request.args.get("next") or url_for(".index"))
        # return render_template('/base.html')
    else:
        flash("Invalid email address or password", "error")
        return redirect(url_for('.login'))

@app.route('/performregister', methods=["POST"])
def performregister():
    email = request.form.get("email")
    password = request.form.get("password")    
    if email and password:  
        existing_user = User.query.filter_by(email=email).first()#seems to make sense? this has to exist?
        if existing_user:
            flash("That email address is already in use", "error")
            return redirect(url_for(".login"))
        else:
            new_user = User(email = email, password=password, role=ROLE_USER
                # , postcolor='#ccd4d9'
                )
            db.session.add(new_user)
            db.session.commit()
            # print new_user.email, new_user.password, new_user.role
            login_user(new_user, remember=True)
            session['logged_in'] = True
            return redirect(request.args.get("next") or url_for(".index"))
    else:
        flash("Please fill out all fields", "error")
        return redirect(url_for(".login"))

@app.before_request
def before_request():
    current_user.last_seen=datetime.utcnow()
    current_user.last_seen_form=datetime.now().ctime()
    db.session.commit()
    current_user.search_enabled = WHOOSH_ENABLED

@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    return render_template('settings.html', user=current_user, title='Profile')

@app.route('/feed', methods=['GET','POST'])
@login_required
def feed():
    return render_template('feed.html', title='Posts Feed',
        user=current_user, posts=Post.query.order_by(Post.post_time.desc()).all())

@app.route('/changesettings', methods=["POST"])
@login_required
def changesettings():
    password = request.form.get("password")  
    nickname = request.form.get("nickname")
    # postcolor = request.form.get("postcolor")
    bio = request.form.get("bio")
    if password is not current_user.password:
        if nickname is not current_user.nickname:
            current_user.nickname = nickname
            current_user.password = password
            db.session.commit()
        else:
            current_user.password = password
            db.session.commit()
    elif nickname is not current_user.nickname:
        current_user.nickname = nickname
        db.session.commit()
    # if postcolor is not current_user.postcolor:
    #     current_user.postcolor = postcolor
    #     db.session.commit()
    if bio is not current_user.bio:
        current_user.bio = bio
        db.session.commit()
    flash("settings changed")
    return redirect(url_for(".settings"))
    # return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
@login_required
def add_entry():
    user_id = current_user.id
    body = request.form.get("body")
    title = request.form.get("title")
    link = request.form.get("link")
    tags = request.form.get("tags")
    post_time_form = datetime.now().ctime()
    post_time = datetime.utcnow()
    new_post=Post(user_id=user_id,body=body, title=title, post_time=post_time, post_time_form=post_time_form, link=link)
    if not session.get('logged_in'):
        abort(401)
    # g.db.execute('insert into entries (title, text) values (?, ?)',
    #              [request.form['title'], request.form['text']])
    # g.db.commit()

    db.session.add(new_post)
    db.session.commit()
    if tags:
        print 'tags', tags
        tagbatch = tags.rsplit(' ')
        print 'tagbatch', tagbatch
        for tag in tagbatch:
            tag_ = Tag(tag=tag)
            print 'tag', tag_.tag
            new_post.tagged.append(tag_)
            db.session.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('.index'))

@app.route('/delete',methods=['POST','GET'])
def delete():
    post_id = request.form.get('delete')
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted!")
    return redirect(url_for('.index'))

@app.route('/like',methods=['POST','GET'])
def like():
    post_id = request.form.get('like')
    flash("Nothing happens right now. Deal with it.")
    return redirect(url_for('.index'))

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/users', methods=['GET'])
@login_required
def users():
    return render_template('users.html', title = 'Users', users=User.query.all(), user=current_user,
        already_foll_users=current_user.followed)

@app.route('/follow', methods=['POST','GET'])
@login_required
def follow():
    followed_userid = int(request.form.get("userid"))
    # followed_user = User.query.filter_by(User.id==followed_userid).all()
    followed_user = db.session.query(User).filter_by(id=followed_userid).first()
    if followed_userid == current_user.id:
        flash("No, you can't follow yourself, dink")
        return redirect(url_for('.users'))
    else:
        # current_user.followed.append(User.query.filter_by(followed_userid=id).first())
        current_user.followed.append(followed_user)
        # followers.add(current_user.id, followed_userid)
        db.session.commit()
        follower_email(followed_user,current_user)
        flash("That user has been notified that you're now following them! There are no secrets on the internet!")
        return redirect(url_for('.index'))

@app.route('/unfollow', methods=['POST','GET'])
@login_required
def unfollow():
    print 'got here'
    unfollowed_userid = int(request.form.get("userid1"))
    unfollowed_user = User.query.filter_by(id=unfollowed_userid).first()
    current_user.followed.remove(unfollowed_user)
    # followers.add(current_user.id, followed_userid)
    print 'unfollowed?'
    db.session.commit()
    return redirect(url_for('.index'))

@app.route('/search', methods=['GET','POST'])
@login_required
def search():
    return render_template('search.html', results=[], user=current_user)

@app.route('/searchresults/', methods=['GET'])
@login_required
def searchresults():   
    query = request.args.get("postsearch")
    # results = db.session.query(Post).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    results = []
    non_whoosh = []
    if WHOOSH_ENABLED==True:
        results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    else:
        non_whoosh = Post.query.filter(Post.body.ilike('%'+query+'%')).all()    
    resultssize = len(results)
    nw_size = len(non_whoosh)    
    return render_template('search.html', title='Results', keyword=query, results=results, query=1, len=resultssize, 
        user=current_user,non_whoosh=non_whoosh, nwlen=nw_size)
    
@app.route('/searchtags/', methods=['GET','POST'])
@login_required
def searchtags():   
    query = request.form.get("search")
    print query, 'QUERY'
    # if query is None:
    #     query = 
    # results = db.session.query(Post).whoosh_search(query, MAX_SEARCH_RESULTS).all()
    taggedposts =[]
    non_whoosh_taggedposts=[]
    allposts = Post.query.all()
    if WHOOSH_ENABLED==True:
        tag = Tag.query.whoosh_search(query, MAX_SEARCH_RESULTS).first()
        for post in allposts:
            for posttag in post.tagged:
                if tag==posttag:
                    taggedposts.append(post)
    else:
        non_whoosh_tag = Tag.query.filter_by(tag=query).first()
        for post in allposts:
            for posttag in post.tagged:
                if non_whoosh_tag==posttag:
                    non_whoosh_taggedposts.append(post)
    resultssize = len(taggedposts)
    nw_size = len (non_whoosh_taggedposts)
    return render_template('search.html', title = 'Results', keyword=query, results=taggedposts, query=2, len=resultssize, 
        user=current_user, non_whoosh=non_whoosh_taggedposts, nwlen=nw_size)