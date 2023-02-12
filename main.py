from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv("C:/Work/Python/.env")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("APP_SEC_KEY")
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##LOGIN DECLARATIONS
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CONFIGURE TABLES

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    # PARENT:Relationship bidir ONEtoMANY with BlogPost and Comment
    post = relationship('BlogPost', back_populates='author')
    comment = relationship('Comment', back_populates='comment_author')

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # CHILD:Relationship bidir ONEtoMANY with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = relationship('User', back_populates='post')
    # PARENT:Relationship bidir ONEtoMANY with Comment
    comment_on_blogpost = relationship('Comment', back_populates='commented_blogpost')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    # CHILD:Relationship bidir ONEtoMANY with User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_author = relationship('User', back_populates='comment')
    # CHILD:Relationship bidir ONEtoMANY with BlogPost
    blog_post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))
    commented_blogpost = relationship('BlogPost', back_populates='comment_on_blogpost')


db.create_all()

# Gravatar section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# post_obj = BlogPost.query.filter_by(title="DailyReview").first()
# print(post_obj.author)

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() != "1":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit() and request.method == "POST":
        reg_user = User.query.filter_by(email=form.email.data).first()
        if  reg_user:
            flash("Welcome back, please login")
            return redirect(url_for('login'))
        else:
            user = User(email= form.email.data,
                        password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                        name = form.name.data
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("You have been successfully registered")
            return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST":
        login_email = form.email.data
        login_pwd = form.password.data
        user = User.query.filter_by(email=login_email).first()
        if not user:
            flash("User with this credetials doesn't exist.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, login_pwd):
            flash("Incorrect password.")
            return redirect(url_for('login'))
        else:

            login_user(user)
            premenna = current_user.name
            flash(f"Welcome {premenna}!")
            print(current_user.post)
            print("hocico")
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit() and request.method == "POST":
        if current_user.is_active:
            new_comment = Comment(
                body = form.body.data,
                comment_author = current_user,
                commented_blogpost = requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
        else:
            flash("You have to be logged in if you want to comment.")
            return redirect(url_for('login'))
    return render_template("post.html", post=requested_post, form=form, comments=requested_post.comment_on_blogpost)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    #print(current_user.post[1])

    if form.validate_on_submit() and request.method == "POST":
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        #author=current_user.name,
        body=post.body
    )
    if edit_form.validate_on_submit() and request.method == "POST":
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        #post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
