import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm

from werkzeug.security import check_password_hash
from app.forms import LoginForm, UploadForm
from flask_login import login_required
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # Instantiate your form class
    form = UploadForm()

    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('File uploaded', 'success')
        return redirect(url_for('upload'))

    return render_template('upload.html', form=form)

    # Validate file upload on submit
    if form.validate_on_submit():
        # Get file data and save to your uploads folder
        username = form.username.data
        password = form.password.data

        user = UserProfile.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # Log the user in and go to home page if the password is right
            login_user(user)
            flash('Logged in.', 'success')
            return redirect(url_for('upload'))
        else:
            #do not log in
            flash('Invalid username or password.', 'failed')

    return render_template('upload.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = UserProfile.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            login_user(user)
            flash('You have successfully logged in', 'success')
            return redirect(url_for('upload'))

        flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error), 'unfortunate')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


from flask import send_from_directory

@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_uploaded_images():
    """
    Returns a list of filenames of all uploaded images in the uploads folder
    """
    rootdir = os.getcwd()
    upload_dir = os.path.join(rootdir, 'uploads')
    uploaded_images = []
    for subdir, dirs, files in os.walk(upload_dir):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png') or file.endswith('.gif'):
                uploaded_images.append(file)
    return uploaded_images

from flask import render_template, url_for
import os

@app.route('/files')
@login_required
def files():
    images = get_uploaded_images()
    image_urls = [url_for('get_image', filename=image) for image in images]
    return render_template('files.html', image_urls=image_urls)

from flask_login import logout_user

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('home'))
