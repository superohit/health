from markett import app
from markett.models import Item, User
from flask import render_template, redirect, url_for, flash, request
from markett.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from markett import db
from flask_login import login_user, logout_user, login_required, current_user
import pickle
import numpy as np


@app.route('/')
@app.route('/home')
def home_page():
    return render_template("home.html")

@app.route('/heart-test', methods =['GET', 'POST'])
def heart_page():

    model = pickle.load(open('markett\model-gb.pkl', 'rb')) 
    
    # Put all form entries values in a list 
    features = [float(i) for i in request.form.values()]
    # Convert features to array
    array_features = [np.array(features)]
    # Predict features
    prediction = model.predict(array_features)
    
    output = prediction
    
    # Check the output values and retrive the result with html tag based on the value
    if output == 1:
        return render_template('Heart Disease Classifier.html', 
                               result = 'The patient is not likely to have heart disease!')
    else:
        return render_template('Heart Disease Classifier.html', 
                               result = 'The patient is likely to have heart disease!')



@app.route('/lab', methods=['GET', 'POST'])
@login_required
def lab_page():
    return render_template('lab.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(username = form.username.data,
                              email_address = form.email.data,
                              password = form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f"Account created successfully! You are logged in as {user_to_create.username}", category="success")

        return redirect(url_for('lab_page'))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating an user {err_msg}!', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as {attempted_user.username}', category='success')
            return redirect(url_for('lab_page'))
        else:
            flash("Username or Password did'nt match! Please try again", category="danger")

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You are logged out successfully!', category='info')
    return redirect(url_for("home_page"))


