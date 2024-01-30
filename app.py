# app.py
""" This is the main file for the Flask Blog application.
It contains the routes and views for the application.
"""
from flask import Flask, render_template, redirect, url_for, flash, request, session
from forms import RegistrationForm, LoginForm, PostForm
from models import db, User, Post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YhGI3F<%`rV.vg6Ph0g?dKa]0&W*O.'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/", methods=['GET', 'POST'])
def index():
    """ Default page
    Anyone can view blog posts, but only logged in users can create posts.    
    """
    form = PostForm()
    if form.validate_on_submit() and 'user_id' in session:
        header = form.header.data
        content = form.content.data
        user_id = session['user_id']

        new_post = Post(header=header, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', form=form, posts=posts)

# create post
@app.route("/create_post", methods=['GET', 'POST'])
def create_post():
    """ Create post
    This is the form for creating a new post.
    """
    form = PostForm()
    if form.validate_on_submit() and 'user_id' in session:
        header = form.header.data
        content = form.content.data
        user_id = session['user_id']

        new_post = Post(header=header, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

    return redirect(url_for('index'))

@app.route("/delete_post/<int:post_id>", methods=['POST'])
def delete_post(post_id):
    """ Delete Post
    This route allows a user to delete their own post.
    """
    post = Post.query.get_or_404(post_id)
    if 'user_id' in session and post.user_id == session['user_id']:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', 'success')
    else:
        flash('You do not have permission to delete this post.', 'danger')
    return redirect(url_for('index'))

@app.route("/home")
def home():
    """ Home page
    If the user is an admin, they will see a list of all users and their status.
    If the user is not an admin, they will see the default page.
    """
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.status == 'admin':
            users = User.query.all()
            return render_template('home.html', users=users)
    form = PostForm()
    if form.validate_on_submit() and 'user_id' in session:
        header = form.header.data
        content = form.content.data
        user_id = session['user_id']

        new_post = Post(header=header, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('index.html', form=form, posts=posts)

@app.route("/about")
def about():
    """ About Page
    This is a static page with information about the application.
    """
    return render_template('about.html')

# Route for the registration page
@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Register Page
    This is the form for registering a new user.
    """
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password != confirm_password:
            flash('Passwords must match.', 'danger')
            return render_template('register.html', form=form)

        # if username is taken
        if User.query.filter_by(username=username).first():
            flash('Username is taken.', 'danger')
            return render_template('register.html', form=form)

        # if email is taken
        if User.query.filter_by(email=email).first():
            flash('Email is taken.', 'danger')
            return render_template('register.html', form=form)

        if email == 'admin@admin.com':
            new_user = User(username=username, email=email, status='admin')
        else:
            new_user = User(username=username, email=email, status='user')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['status'] = new_user.status

        flash('Registration successful! Welcome to Flask Blog.', 'success')
        return redirect(url_for('home'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('register.html', form=form)

# Route for the login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Login Page
    This is the form for logging in a user.
    """
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['status'] = user.status
            flash('Login successful.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field.capitalize()}: {error}', 'danger')

    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    """ Logout Route
    This route logs the user out by clearing the session.
    """
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('status', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    """ Page Not Found
    If the user tries to access a page that does not exist, they will be redirected 
    to the default page.
    """
    print(e)
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_server_error(e):
    """ Internal Server Error
    If the user tries to access a page that does not exist, they will be redirected
    to the default page.
    """
    print(e)
    return redirect(url_for('index'))

@app.route("/change_status/<int:user_id>", methods=['POST'])
def change_status(user_id):
    """ change status
    This route allows an admin to change the status of a user.
    """
    if 'user_id' not in session or User.query.get(session['user_id']).status != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))

    user_to_change = User.query.get_or_404(user_id)
    new_status = request.form.get('new_status')

    if new_status not in ['admin', 'user']:
        flash('Invalid status.', 'danger')
    else:
        user_to_change.status = new_status
        db.session.commit()
        flash(f"User '{user_to_change.username}' status changed to '{new_status}'.", 'success')

    return redirect(url_for('home'))

@app.route("/delete_user/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    """ delete user
    This route allows an admin to delete a user.
    """
    if 'user_id' not in session or User.query.get(session['user_id']).status != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('home'))

    user_to_delete = User.query.get_or_404(user_id)
    # Delete all posts by the user
    Post.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Delete the user
    db.session.delete(user_to_delete)
    db.session.commit()

    # If the user deleted their own account, end the session
    if user_to_delete.id == session['user_id']:
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('status', None)
        flash('You have been logged out.', 'success')

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
    