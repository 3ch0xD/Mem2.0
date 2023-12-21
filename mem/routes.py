#/---------------------------------------------------------------------------------------------------/#
# Imports
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from mem import app, db, bcrypt, mail
from mem.forms import SignUp, signin, UpdateProfileForm, CreatePost, Search, RequestResetForm, ResetPasswordForm
from mem.models import User, Mems
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

#/---------------------------------------------------------------------------------------------------/#


#/---------------------------------------------------------------------------------------------------/#
#Upload Folder
app.config['UPLOAD_FOLDER'] = 'static/memes'
#/---------------------------------------------------------------------------------------------------/#


#/---------------------------------------------------------------------------------------------------/#
#-Page Routes-#

#Home Page
@app.route('/')
def home1():
    page = request.args.get('page', 1, type=int)
    mem_posts = Mems.query.order_by(Mems.date_posted.desc()).paginate(page=page, per_page=20)
    return render_template('home.html', navtitle='Home', style='home.css', mem_posts=mem_posts)


#About Page
@app.route("/about")
def about():
    return render_template('about.html', title="About", style="about.css", navtitle='About')


#Discover Page
@app.route('/discover', methods=['GET', 'POST'])
def discover():
    if request.method == 'POST':
        search_query = request.form.get('title')
        return redirect(url_for('search', query=search_query))
    return render_template('discover.html', title='Discover', style="discover.css", navtitle='Discover')


#Search Page
@app.route('/search')
def search():
    search_query = request.args.get('query')
    if search_query:
        mem_posts = Mems.query.filter(Mems.title.ilike(f"%{search_query}%")).all()
    else:
        mem_posts = []

    return render_template('search_results.html', mem_posts=mem_posts, search_query=search_query, style="search.css", title=f'Search Result {search_query}')


#-Connection Processer-#
@app.context_processor
def searchpls():
    form = Search()
    return dict(form=form)
#/---------------------------------------------------------------------------------------------------/#


#/---------------------------------------------------------------------------------------------------/#
#- Authentication Pages -#

#LogIn
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home1'))
    form = signin()
    if form.validate_on_submit():
            user =  User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                 login_user(user, remember=form.remember.data)
                 next_page = request.args.get('next')
                 flash(f'Welcome {current_user.username}!', 'success')
                 if current_user.username == 'AxeDee':
                    rank = url_for('static', filename='ranks/owner.png')
                    current_user.username == 'AxeDee' + rank
                 return redirect(next_page) if next_page else redirect(url_for('home1'))
            else:
                flash('Login Credentials Invalid! Please Try Again!', 'danger')
    print(form.errors)
    return render_template('login.html', title="LogIn", form=form, style="login.css")


#SignUp

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home1'))
    
    form = SignUp()
    
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=encrypted_password)
        db.session.add(user)
        db.session.commit()
        flash('Mem Account Was Successfully Made. Please Login To Continue!', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', title="SignUp", form=form, style="signup.css")


#- Image Saving Functions-#
#PFP Saver
def save_pfps(form_pfps):
    randomizer = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pfps.filename)
    picture_fn = randomizer + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_pfps)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn



#Profile
@app.route("/profile", methods=['POST', 'GET'])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.pfp.data:
            picture_file = save_pfps(form.pfp.data)
            current_user.profile_picture = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your Account Has Been Updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me
    profile_picture = url_for('static', filename='profile_pictures/' + current_user.profile_picture)
    return render_template('profile.html', title='Profile', style='profile.css', profile_picture=profile_picture, form=form)


#LogOut
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home1'))
#/---------------------------------------------------------------------------------------------------/#

#/---------------------------------------------------------------------------------------------------/#
#- Functional Pages -#

#- Saving The Mem Picture Function -#
def save_memes(form_pfps):
    randomizer = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pfps.filename)
    picture_fn = randomizer + f_ext
    picture_path = os.path.join(app.root_path, 'static/memes', picture_fn)
    i = Image.open(form_pfps)
    i.save(picture_path, save_all=True, duration=100, loop=0)
    return picture_fn


#Create New Mem
@app.route("/mem/new", methods=['POST', 'GET'])
@login_required
def new_post():
    form = CreatePost()
    if form.validate_on_submit():
        meme_filename = None  # Default value if no meme file is provided
        if 'meme' in request.files:
            meme_file = request.files['meme']
            if meme_file.filename != '':
                meme_filename = save_memes(meme_file)

        mem = Mems(title=form.title.data, description=form.description.data, author=current_user, meme=meme_filename)
        db.session.add(mem)
        db.session.commit()
        flash('New Mem Was Created!', 'success')
        return redirect(url_for('home1'))

    return render_template('create_post.html', style="create_post.css", title="New Post", form=form)


#View Singular Post

@app.route('/ms/<int:mem_id>')
def ms(mem_id):
    mem = Mems.query.get_or_404(mem_id)
    return render_template('ms.html', style="ms.css", mem=mem)


#Update Post
@app.route('/ms/<int:mem_id>/update', methods=['POST', 'GET'])
@login_required
def update_ms(mem_id):
    mem = Mems.query.get_or_404(mem_id)
    if mem.author != current_user:
        abort(403)
    form = CreatePost()
    if form.validate_on_submit():
        mem.title = form.title.data
        mem.description = form.description.data
        db.session.commit()
        flash('You Post Was Updated!', 'success')
        return redirect(url_for('ms', mem_id=mem.id))
    elif request.method == 'GET':
        form.title.data = mem.title
        form.description.data = mem.description
    return render_template('update_post.html', style="create_post.css", title=f"Update #{mem.title}", form=form, mem=mem)

#Delete Post
@app.route("/ms/<int:mem_id>/delete", methods=['POST'])
@login_required
def delete_post(mem_id):
    mem = Mems.query.get_or_404(mem_id)
    if mem.author != current_user:
        abort(403)
    db.session.delete(mem)
    db.session.commit()
    flash('Your post was deleted', 'success')
    return redirect(url_for('home1'))


@app.route("/@<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    mem_posts = Mems.query.filter_by(author=user).order_by(Mems.date_posted.desc()).paginate(page=page, per_page=20)
    return render_template('usersprofile.html', mem_posts=mem_posts, user=user, style="usersprofile.css", navtitle=user.username)
#/---------------------------------------------------------------------------------------------------/#

#/---------------------------------------------------------------------------------------------------/#
#-Errors-#

@app.errorhandler(404)
def error404(e):
    return render_template('404.html', error="Sorry! The page you are looking for doesnot exist!"), 404

@app.errorhandler(403)
def error403(e):
    return render_template('403.html', error="You donot have permission to modify this post!"), 403

@app.errorhandler(500)
def error500(e):
    return render_template('500.html', error="Sorry! There was an internal server error!"), 500
#/---------------------------------------------------------------------------------------------------/#

#/---------------------------------------------------------------------------------------------------/#
#$-Account Handling Routes-$#


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Mem - Reset Your Password', sender='noreply@memplatform.net', recipients=[user.email])
    msg.body = f'''A request to reset your mem accounts password from this email was made:
{user.email}

To Reset Your Password Click On The Following Link, This Will Expire In 30 minutes:

{url_for('reset_token', token=token, _external=True)}

If this request was not made by you, simply ignore this email and nothing will be changed.

    -Regards TeamMem "Have the goof of a lifetime"
'''
    mail.send(msg)

#Request Reset Password // Sends Email Of Token
@app.route("/reset_password", methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('home1'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email with instructions have been sent to your account to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request_password.html', title="Reset Password", form=form, style='signup.css')


#Reset Password Here// Enter Link
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home1'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That Token Was Either Expired Or Invalid.', 'warning')
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = encrypted_password
        db.session.commit()
        flash('Your password was successfully changed. Please login to continue!', 'success')
        return redirect(url_for('login'))
    return render_template('request_token.html', title="Reset Password", form=form, style='signup.css')


#/---------------------------------------------------------------------------------------------------/#

#/---------------------------------------------------------------------------------------------------/#
#Database Admin Privilages.
app.app_context().push()
#/---------------------------------------------------------------------------------------------------/#