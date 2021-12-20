from flask import render_template, flash, redirect, url_for
from app import app, mail
from flask_mail import Message
from app.forms import Feedback

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# url_for('index') - #3

@app.route('/email')
def email():
    msg = Message('Hello',body='There', sender='SDan.Testing@gmail.com', recipients=['SDan.Testing@gmail.com', 'farhaan.dan@gmail.com'])
    mail.send(msg)
    return 'Sent!'
    #https://www.google.com/settings/security/lesssecureapps


@app.route('/feedback', methods=['GET', 'POST'])
def feed():
    form = Feedback()
    if form.validate_on_submit():
        flash('Feedback Sent Successfully.')
            
        title = form.option.data
        body = form.comment.data

        msg = Message(title, body=body, sender='SDan.Testing@gmail.com', recipients=['SDan.Testing@gmail.com'])
        mail.send(msg)

        # return redirect('/feedback')
    return render_template('feedback.html', form=form)