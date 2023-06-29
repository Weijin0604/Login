from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid,re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.abspath('.')+"/user.db"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(80))

'''
查詢用api
@app.route('/user', methods=['GET'])
def get_all_users():

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        output.append(user_data)

    return jsonify({'users' : output})

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['username'] = user.username
    user_data['password'] = user.password

    return jsonify({'user' : user_data})
'''
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not re.match(r'^.{3,32}$', username):
        return jsonify({'success': False, 'reason': 'Invalid username!'}), 400

    if len(password) < 8:
        return jsonify({'success': False, 'reason': 'Password too short!'}), 400
    elif len(password) > 32:
        return jsonify({'success': False, 'reason': 'Password too long!'}), 400
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,32}$', password):
        return jsonify({'success': False, 'reason': 'Invalid password!'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'success': False, 'reason': 'Username already exists!'}), 409

    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'New user created!'}), 201

password_attempts = {}
@app.route('/user/verify', methods = ['POST'])
def verify_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in password_attempts:
        attempts = password_attempts[username]['attempts']
        last_attempt_time = password_attempts[username]['time']
        if attempts >= 5 and datetime.now() < last_attempt_time + timedelta(minutes=1):
            print(password_attempts)
            return jsonify({'success': False, 'reason': 'Too many failed attempts. Please wait before trying again.'}), 429
        
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        if username in password_attempts:
            password_attempts[username]['attempts'] += 1
            password_attempts[username]['time'] = datetime.now()
        else:
            password_attempts[username] = {'attempts': 1, 'time': datetime.now()}

        return jsonify({'success': False, 'reason': 'Invalid username or password.'}), 401    

    if username in password_attempts:
        print(password_attempts)
        del password_attempts[username]

    return jsonify({'success': True})

'''
刪除用api
@app.route('/user/<public_id>', methods=['DELETE'])
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message' : 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message' : 'The user has been deleted!'})
'''
if __name__ == '__main__':
   
    app.run(host = "0.0.0.0",port=5001,debug=True)