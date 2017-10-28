from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

from flask import session as login_session
import random
import string
import bleach

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Menu Application"

engine = create_engine('sqlite:///joeslist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# List all categories
@app.route('/')
def showCategory():
    categorylist = session.query(Category).order_by(Category.name)
    items = session.query(Item).order_by(Item.date_added.desc()).limit(10)
    # check url to see if they just logged in
    return render_template(
        'index.html', categorylist=categorylist, items=items)


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    categorylist = session.query(Category).order_by(Category.name)
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template(
        'login.html', categorylist=categorylist, STATE=state)


# Show item list for a category
@app.route('/<int:category_id>/', methods=['GET', 'POST'])
def showItemList(category_id):
    categorylist = session.query(Category).order_by(Category.name)
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template(
        'itemlist.html', categorylist=categorylist, category=category,
        items=items, category_id=category_id)


# Create a new item
@app.route('/<int:category_id>/new', methods=['GET', 'POST'])
def newItem(category_id):
    categorylist = session.query(Category).order_by(Category.name)
    category = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['year']:
            year = int(request.form['year'])
        else:
            year = 2010
        if request.form['miles']:
            miles = int(request.form['miles'].replace(",", ""))
        else:
            miles = 30000
        if request.form['price']:
            price = float(
                request.form['price'].replace(",", "").replace("$", ""))
        else:
            price = 10000.00
        newItem = Item(
            year=year,
            make=bleach.clean(request.form['make']),
            model=bleach.clean(request.form['model']),
            miles=miles,
            description=bleach.clean(request.form['description']),
            price=price,
            user_id=login_session['user_id'],
            category_id=category_id)
        session.add(newItem)
        session.commit()
        flash("Vehicle added")
        return redirect(url_for('showItemList', category_id=category_id))
    else:
        return render_template(
            'new.html', categorylist=categorylist, category=category,
            category_id=category_id)


# Show item
@app.route('/<int:category_id>/<int:item_id>/', methods=['GET', 'POST'])
def showItem(category_id, item_id):
    categorylist = session.query(Category).order_by(Category.name)
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    edit = request.args.get('edit')
    if edit and 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST' and creator.name == login_session['username']:
        if request.form['year']:
            year = int(request.form['year'])
        else:
            year = 2010
        if request.form['miles']:
            miles = int(request.form['miles'].replace(",", ""))
        else:
            miles = 30000
        if request.form['price']:
            price = float(
                request.form['price'].replace(",", "").replace("$", ""))
        else:
            price = 10000.00
        item.year = year
        item.make = bleach.clean(request.form['make'])
        item.model = bleach.clean(request.form['model'])
        item.miles = miles
        item.price = price
        item.description = bleach.clean(request.form['description'])
        session.add(item)
        session.commit()
        flash("Vehicle updated")
    return render_template(
        'item.html', category_id=category_id, item_id=item_id,
        categorylist=categorylist, category=category, item=item,
        creator=creator, edit=edit)


# Delete item
@app.route('/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    categorylist = session.query(Category).order_by(Category.name)
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert(n\
            'You are not authorized to delete.');n\
            window.location='/'}</script>n\
            <body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Vehicle deleted')
        return redirect(url_for('showItemList', category_id=category_id))
    else:
        return render_template(
            'delete.html', categorylist=categorylist, item=itemToDelete)


# JSON category list
@app.route('/JSON')
def categoryListJSON():
    category = session.query(Category).all()
    return jsonify(category=[r.serialize for r in category])


# JSON items list by category
@app.route('/<int:category_id>/JSON')
def itemListJSON(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Catitems=[i.serialize for i in items])


# JSON item data
@app.route('/<int:category_id>/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    catItem = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=catItem.serialize)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if not creat one.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    return redirect('/?loggedin=true')
    return output


# User Helper Functions
@app.context_processor
def utility_processor():
    def format_price(amount, currency=u'$'):
        return u'{1}{0:,.0f}'.format(amount, currency)
    return dict(format_price=format_price)


@app.context_processor
def utility_processor():
    def format_price_plain(amount, currency=u'$'):
        return u'{0:.0f}'.format(amount, currency)
    return dict(format_price_plain=format_price_plain)


@app.context_processor
def utility_processor():
    def format_miles(num):
        return '{0:,.0f}'.format(num)
    return dict(format_miles=format_miles)


def getState():
    if 'state' not in login_session:
        state = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for x in range(32))
        login_session['state'] = state
        return state
    else:
        return login_session['state']


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not" \
            "connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return "<script>function myFunction() {alert('You are logged out.');" \
            "window.location = '/';}</script><body onload='myFunction()''>"
    else:
        response = make_response(json.dumps("Failed to revoke token for "
                                            "given user.", 400))
        response.headers['Content-Type'] = 'application/json'
        return "<script>function myFunction() {alert('Log out error. Failed " \
            "to revoke token.');window.location = '/';}</script>" \
            "<body onload='myFunction()''>"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
