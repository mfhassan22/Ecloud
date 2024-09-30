from flask import Flask, request, jsonify
from models.user import User, db, bcrypt
import re

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
bcrypt.init_app(app)

def sanitize_input(data):
    return re.sub(r'[^\w\s]', '', data)


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = sanitize_input(data.get('username'))
    password = sanitize_input(data.get('password'))
    active = data.get('active', True)

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User(username=username, active=active)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'active': user.active
    })


@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)

    username = sanitize_input(data.get('username', user.username))
    password = sanitize_input(data.get('password', ''))
    active = data.get('active', user.active)

    user.username = username
    if password:
        user.set_password(password)
    user.active = active

    db.session.commit()

    return jsonify({'message': 'User updated successfully'})


@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
