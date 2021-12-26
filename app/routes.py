from flask import render_template, flash, redirect, url_for
from app import app, mail
from flask_mail import Message
from app.forms import Feedback
from app.sources.General_Population import population
from app.sources.ICT_Baskets import baskets
from app.sources.ICT_Indicators import indicators
from app.sources.Internet_Exchange_Points import ixp
from app.sources.Population_Density import density
from app.sources.Root_Servers import root
from app.sources.Speed_Index import speedindex
from app.sources.Submarine_Cables import submarine
from app.sources.Top_Level_Domains import tld

from app.modules.maps import create_map


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# url_for('index') - #3

@app.route('/test')
def test():
    # print(population())
    # print(baskets())
    # print(indicators())
    # print(ixp())
    print(density())
    # print(root())
    # print(speedindex())
    # print(submarine())
    # print(tld())
    create_map()
    print("successful")
    return render_template('test.html')

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