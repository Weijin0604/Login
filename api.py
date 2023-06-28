from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid,re
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/elliot/Desktop/Senao/env/Login/todo.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer)

@app.route('/user', methods=['GET'])
def get_all_users():

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
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
    user_data['name'] = user.name
    user_data['password'] = user.password

    return jsonify({'user' : user_data})


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['name']
    password = data['password']

    if not re.match(r'^.{3,32}$', username):
        return jsonify({'success': False, 'reason': 'Invalid username!'}), 400

    if len(password) < 8:
        return jsonify({'success': False, 'reason': 'Password too short!'}), 400

    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,32}$', password):
        return jsonify({'success': False, 'reason': 'Invalid password!'}), 400

    existing_user = User.query.filter_by(name=username).first()
    if existing_user:
        return jsonify({'success': False, 'reason': 'Username already exists!'}), 409

    hashed_password = generate_password_hash(password, method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': True, 'message': 'New user created!'}), 201


@app.route('/user', methods = ['PUT'])
def promote_user():
    return ''

@app.route('/user/<user_id>', methods = ['DELETE'])
def delete_user():
    return ''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host = "localhost",port=8900,debug=True)