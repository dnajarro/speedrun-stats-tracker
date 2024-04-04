from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from os import environ

app = Flask(__name__)
CORS(app)   # Enable CORS for all routes
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL')
db = SQLAlchemy(app)

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     def json(self):
#         return {'id': self.id, 'name': self.name, 'email': self.email}


# db.create_all()

# # create a test route


@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'The server is running'})

# # create a user


# @app.route('/api/flask/users', methods=['POST'])
# def create_user():
#     try:
#         data = request.get_json()
#         new_user = User(name=data['name'], email=data['email'])
#         db.sesssion.add(new_user)
#         db.session.commit()

#         return jsonify({
#             'id': new_user.id,
#             'name': new_user.name,
#             'email': new_user.email
#         }), 201

#     except Exception as e:
#         return make_response(jsonify({'message': 'error creating user', 'error': str(e)}), 500)
