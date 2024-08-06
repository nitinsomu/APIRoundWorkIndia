from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import yaml
import secrets
import string

app = Flask(__name__)

adminAuthorization = "adminAccessOnly12345"
userId = 1
carId = 1

db = yaml.load(open('db.yaml'),Loader=yaml.SafeLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

def generate_token(length=32):
    characters = string.ascii_letters + string.digits + string.punctuation
    accessToken = ''.join(secrets.choice(characters) for _ in range(length))
    return accessToken

@app.route('/api/signup', methods= ['POST'])
def signup():
    data = request.get_json()
    global userId
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO USERS(userId, username, password, email) VALUES (%s, %s, %s, %s)", (userId, username, password, email))
    mysql.connection.commit()
    cur.close()

    response = {
        "status": "Account successfully created",
        "status_code": 200,
        "user_id": userId
    }
    userId += 1
    return jsonify(response), 200

@app.route('/api/login', methods= ['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM USERS WHERE username = %s", (username,))
    
    retreivedPassword = cur.fetchone()[0]
    mysql.connection.commit()
    cur.close()
    if(password == retreivedPassword):
        cur = mysql.connection.cursor()
        cur.execute("SELECT userId FROM USERS WHERE username = %s", (username,))
        retreivedUserId = cur.fetchone()[0]
        mysql.connection.commit()
        accessToken = generate_token()
        cur.execute("UPDATE USERS SET accessToken = %s WHERE username = %s", (accessToken, username))
        mysql.connection.commit()
        cur.close()
        response = {
            "status": "Login Successful",
            "status_code": 200,
            "user_id": retreivedUserId,
            "access_token": accessToken
        }
        return jsonify(response), 200
    else:
        response = {
            "status": "Incorrect username/password provided. Please retry",
            "status_code": 401
        }
        return jsonify(response), 401
    
@app.route('/api/add_car', methods=['POST'])
def add_car():
    global carId
    data = request.get_json()
    category = data.get('category')
    model = data.get('model')
    number_plate = data.get('number_plate')
    current_city = data.get('current_city')
    rent_per_hr = data.get('rent_per_hr')
    rent_history = data.get('rent_history')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO CARS(category, model, number_plate, current_city, rent_per_hr, rent_history, carId) VALUES (%s, %s, %s, %s, %s, %s, %s)", (category, model, number_plate, current_city, rent_per_hr, rent_history, carId))
    mysql.connection.commit()
    cur.close()

    response = {
        "message": "Car added successfully",
        "car_id": carId,
        "status_code": 200
    }
    carId += 1
    return jsonify(response), 200
    
@app.route('/api/car/update-rent-history', methods=['POST'])
def update_rent_history():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1]
    print(token)
    if token != adminAuthorization:
        return jsonify({"status": "Unauthorized", "status_code": 403}), 403

    data = request.get_json()

    car_id = data.get('car_id')
    ride_details = data.get('ride_details')

    cur = mysql.connection.cursor()
    cur.execute("UPDATE CARS SET rent_history = %s WHERE carId = %s", (ride_details, car_id))
    mysql.connection.commit()
    cur.close()

    response = {
        "status": "Car's rent history updated successfully",
        "status_code": 200
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)

