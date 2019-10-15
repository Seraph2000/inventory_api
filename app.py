from flask import Flask, render_template, request, g, redirect, url_for, \
    session, jsonify
from database import connect_db, get_db
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
# from flask_restplus import Resource
# from flask_marshmallow import Marshmallow

import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# congigure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/seraphina/Documents/TRAINING/training_2019/JOB_APPLICATIONS/verv/verv_2/inventory_api/inventory.db'
# instantiate db
db = SQLAlchemy(app)
# instantiate a migrate object
migrate = Migrate(app, db)

# Data models
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(30))
    passwd = db.Column(db.String(15))

class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(50))
    item_price = db.Column(db.Float)
    item_quantity = db.Column(db.Integer)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_user():
    user_result = None

    if 'email' in session:
        email = session['email']
        db = get_db()
        user_cur = db.execute('select id, first_name, last_name, email, passwd from users where email = ?', [email])
        # determines whether we have a logged in user or not
        user_result = user_cur.fetchone()
    return user_result


@app.route('/')
def index():
    user = get_current_user()
    if user is not None:
        return jsonify({'message': 'User {} is logged in.'.format(user['email'])})
    return jsonify({'message': 'No users logged in at present.'})

# ○ api/v1/account/register (PUT) - Register a new user (first name, last name, email, password) 
@app.route('/account/register', methods=['PUT'])
def register():
    db = get_db()

    # already in db - update user
    new_member = request.get_json()
    email = str(new_member['email'])
    member_cur = db.execute('select id, first_name, last_name, email, passwd from users where email = ?', [email])
    if member_cur.fetchone() is None:
        first_name = str(new_member['first_name'])
        last_name = str(new_member['last_name'])
        email = str(new_member['email'])
        passwd = str(new_member['passwd'])
        hashed_password = generate_password_hash(passwd, method="sha256")

        db.execute('insert into users (first_name, last_name, email, passwd) values (?, ?, ?, ?)', [first_name, last_name, email, hashed_password])
        db.commit()

        # checking user has been added to database
        member_cur = db.execute('select id, first_name, last_name, email, passwd from users where email = ?', [email])
        new_member = member_cur.fetchone()

        # return json representation of new member
        return jsonify({'member': {'id': new_member['id'], 'first_name': new_member['first_name'], 'last_name': new_member['last_name'], 'email': new_member['email'], 'passwd': new_member['passwd']}})

    # not in db yet - create user
    edit_member = request.get_json()
    first_name = str(edit_member['first_name'])
    last_name = str(edit_member['last_name'])
    email = str(edit_member['email'])
    passwd = str(edit_member['passwd'])
    hashed_password = generate_password_hash(passwd, method="sha256")

    db.execute('update users set first_name = ?, last_name = ?, passwd = ? where email = ?', [first_name, last_name, hashed_password, email])
    db.commit()

    # checking user has been added to database
    member_cur = db.execute('select id, first_name, last_name, email, passwd from users where email = ?', [email])
    edit_member = member_cur.fetchone()

    # return json representation of new member
    return jsonify({'updated_member': {'id': edit_member['id'], 'first_name': edit_member['first_name'], 'last_name': edit_member['last_name'], 'email': edit_member['email'], 'passwd': edit_member['passwd']}})


# ○ api/v1/account/login (POST)- Login for a user (email, password) 
@app.route('/account/login', methods=['POST'])
def login():
    login_data = request.get_json()
    email = login_data['email']
    passwd = login_data['passwd']
    db = get_db()
    user_cur = db.execute('select id, email, passwd from users where email = ?', [email])
    user_result = user_cur.fetchone()

    # check if password is same as password in database
    if check_password_hash(user_result['passwd'], passwd):
        session['email'] = user_result['email']
        return jsonify({'message': 'Welcome {}, you are now logged in!'.format(email)})
    else:
        return jsonify({'message': 'Login unsuccessful!'})


# ○ api/v1/account/logout (POST)- Logout for a user 
@app.route('/account/logout', methods=['POST'])
def logout():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'You are not authorised to access this page. Please log in first.'})

    # pop user out of session - replace email with None in session
    session.pop('email', None)
    return jsonify({'message': 'You have now successfully logged out!'})


# ○ api/v1/account/show (GET)- Show current user details
@app.route('/account/show/<int:id>', methods=['GET'])
def show(id):
    user = get_current_user()
    if not user:
        return jsonify({'message': 'You are not authorised to access this page. Please log in first.'})

    db = get_db()
    member_cur = db.execute('select id, first_name, last_name, email, passwd from users where id = ?', [id])
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'first_name': member['first_name'], 'last_name': member['last_name'], 'email': member['email'], 'passwd': member['passwd']}})


# ○ api/v1/inventory/create (PUT)- Create a new item
@app.route('/inventory/create', methods=['PUT'])
def create():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'You are not authorised to access this page. Please log in first.'})

    db = get_db()

    new_item = request.get_json()
    item_name = str(new_item['item_name'])
    item_price = float(new_item['item_price'])
    item_quantity = int(new_item['item_quantity'])

    db.execute('insert into items (item_name, item_price, item_quantity) values (?, ?, ?)', [item_name, item_price, item_quantity])
    db.commit()

    # test
    # return 'Item Name: {}. Item Price: {}. Item Quantity: {}'.format(item_name, item_price, item_quantity)

    # checking item has been added to database
    item_cur = db.execute('select id, item_name, item_price, item_quantity from items where item_name = ?', [item_name])
    new_item = item_cur.fetchone()

    # return json representation of new member
    return jsonify({'id': new_item['id'], 'item_name': new_item['item_name'], 'item_price': new_item['item_price'], 'item_quantity': new_item['item_quantity']})

# ○ api/v1/inventory/remove (DEL)- Remove an existing item
@app.route('/inventory/remove/<int:id>', methods=['DELETE'])
def remove_item(id):
    user = get_current_user()
    if not user:
        return jsonify({'message': 'You are not authorised to access this page. Please log in first.'})

    db = get_db()
    db.execute('delete from items where id = ?', [id])
    db.commit()
    return jsonify({'message': 'Item {} has been sucessfully removed from the database.'.format(id)})

# ○ api/v1/inventory/list (GET)- List the entire inventory 
@app.route('/inventory/list', methods=['GET'])
def list_inventory():
    user = get_current_user()
    if not user:
        return jsonify({'message': 'You are not authorised to access this page. Please log in first.'})

    db = get_db()
    items_cur = db.execute('select id, item_name, item_price, item_quantity from items')
    items = items_cur.fetchall()

    return_items = []

    for item in items:
        item_dict = {}
        item_dict['id'] = item['id']
        item_dict['item_name'] = item['item_name']
        item_dict['item_price'] = item['item_price']
        item_dict['item_quantity'] = item['item_quantity']

        return_items.append(item_dict)

    return jsonify({'stock': return_items})


if __name__ == '__main__':
    app.run(debug=True)
