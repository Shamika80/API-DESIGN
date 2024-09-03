from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask.blueprints import Blueprint  

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RATELIMIT_DEFAULT'] = "100 per minute, 1000 per hour"
app.config['RATELIMIT_HEADERS_ENABLED'] = True

db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "1000 per hour"]
)

# Models

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
  

    position = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position
        }


# Blueprints

employees_bp = Blueprint('employees', __name__)
production_bp = Blueprint('production', __name__)
orders_bp = Blueprint('orders', __name__)
customers_bp = Blueprint('customers', __name__)

@employees_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")
def create_employee():
    data = request.get_json()
    new_employee = Employee(name=data['name'], position=data['position'])
    db.session.add(new_employee)
    db.session.commit()
    return jsonify({'message': 'Employee created', 'employee': new_employee.to_dict()}), 201

@employees_bp.route('/', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([employee.to_dict() for employee in employees]), 200

# Register blueprints
app.register_blueprint(employees_bp, url_prefix='/employees')
app.register_blueprint(production_bp, url_prefix='/production-records')
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(customers_bp, url_prefix='/customers')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)