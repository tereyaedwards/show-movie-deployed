from flask import render_template, flash, redirect, url_for, request
from app import application, db
from app.forms import LoginForm, RegistrationForm, IndexForm
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User, Movies
from werkzeug.urls import url_parse
import requests


@application.route('/')
@application.route('/index')
@login_required
def index():
    form = IndexForm()
    return render_template('index2.html', title='Home', form=form)


@application.route('/search/saving', methods=['GET','POST'])
def saving():
    form = IndexForm()

    if form.validate_on_submit:

        # 1st API call
        url = "https://imdb8.p.rapidapi.com/title/find"

        # gets show from form entry
        show_to_search = request.values.get('movie_title')
        querystring = {"q": show_to_search}

        headers = {
            'x-rapidapi-host': "imdb8.p.rapidapi.com",
            'x-rapidapi-key': "5a64743a7bmsh79b17ce5d033775p102796jsneae2a4334407"
        }

        response = requests.request("GET", url, headers=headers, params=querystring).json()

        # Grabbing Tconst, title from API call
        tconst = response['results'][0]['id'].split('/')[2]
        title = response['results'][0]['title']
        # Grab plot
        plot_url = "https://imdb8.p.rapidapi.com/title/get-plots"

        plot_querystring = {"tconst": tconst}

        plot_headers = {'x-rapidapi-host': "imdb8.p.rapidapi.com",
                         'x-rapidapi-key': "5a64743a7bmsh79b17ce5d033775p102796jsneae2a4334407"}

        plot_response = requests.request("GET", plot_url,
                                          headers=plot_headers,
                                          params=plot_querystring).json()

        plot = plot_response['plots'][0]['text']



        # check if show info is already in DB if not then add it
        name_exists = db.session.query(db.exists().where(Movies.tconst == tconst)).scalar()
        if not name_exists:
            movie_info = Movies(tconst=tconst, title=title, plot=plot)
            db.session.add(movie_info)
            db.session.commit()


        # 2nd API Call to "get similar show"
        tconst_url = "https://imdb8.p.rapidapi.com/title/get-more-like-this"

        tconst_querystring = {"currentCountry": "US", "purchaseCountry": "US", "tconst": tconst}

        tconst_headers = {
            'x-rapidapi-host': "imdb8.p.rapidapi.com",
            'x-rapidapi-key': "5a64743a7bmsh79b17ce5d033775p102796jsneae2a4334407"
        }

        tconst_response = requests.request("GET", tconst_url, headers=tconst_headers, params=tconst_querystring).json()

        # Gets responses, takes 1st element, splits and takes the tconstant
        # of show that is similar to initially searched show
        similar_show_tconst = tconst_response[0].split('/')[2]

        # if similar_show (tconst) is in DB
        # query info from DB instead of calling API
        name_exists = db.session.query(db.exists().where(Movies.tconst == similar_show_tconst)).scalar()
        if name_exists:
            title_name = Movies.query.filter_by(tconst=similar_show_tconst).first()
            similar_show = title_name.title
            similar_plot = title_name.plot
            return render_template('display.html', title1=similar_show, plot=similar_plot)

        else:
            # 3rd API call only if needed
            final_url = "https://imdb8.p.rapidapi.com/title/get-plots"

            final_querystring = {"tconst": similar_show_tconst}

            final_headers = {'x-rapidapi-host': "imdb8.p.rapidapi.com",
                             'x-rapidapi-key': "5a64743a7bmsh79b17ce5d033775p102796jsneae2a4334407"}

            final_response = requests.request("GET", final_url,
                                              headers=final_headers,
                                              params=final_querystring).json()

            similar_show_title1 = final_response['base']['title']
            similar_show_plot = final_response['plots'][0]['text']

            # Save this similar show in DB too to reduce the amount of overall API calls used
            # check if show info is already in DB if not then add it
            name_exists = db.session.query(db.exists().where(Movies.tconst == similar_show_tconst)).scalar()
            if not name_exists:
                similar_show_info = Movies(tconst=similar_show_tconst, title=similar_show_title1, plot=similar_show_plot)
                db.session.add(similar_show_info)
                db.session.commit()

    return render_template('display.html', title1=similar_show_title1, plot=similar_show_plot)



@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username  or  password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@application.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
