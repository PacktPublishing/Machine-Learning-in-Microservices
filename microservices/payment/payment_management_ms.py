#Payment Management MS

from flask import Flask, request, jsonify
import mysql.connector

# create a Flask instance
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="abc_msa"
)

mycursor = mydb.cursor()

service_name = "payment_management"
service_descr = "ABC-MSA Payment Management"
service_json = jsonify({"service_name":service_name, "service_descr":service_descr})

service_info =   """
<!DOCTYPE html>
<head>
   <title>PAYMENT MANAGEMENT Microservice</title>
</head>
<body>  
   <h3>Payment Management Microservice Part of ABC-MSA System</h3>
</body>
                """

# The root / URL Route
# Returns an HTML with service info when service root is requested 
@app.route('/', methods=['GET'])
def about():
    return service_info

# The API '/payments' URL Route with Payment Management API functions
######################################################################
# API endpoint to add a new payment for an order
@app.route('/payments', methods=['POST'])
def add_payment():
    data = request.get_json()
    order_id = data['order_id']
    amount = data['amount']
    payment_date = data.get('payment_date')
    sql_stmt = "INSERT INTO payments (order_id, payment_date, amount) VALUES (%s, %s, %s)"
    sql_vals = (order_id, payment_date, amount)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    sql_stmt = "UPDATE orders SET total_price = total_price + %s WHERE id = %s"
    sql_vals = (amount, order_id)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({'msg': 'Payment added successfully'})

# API to get all processed payments
@app.route('/payments', methods=['GET'])
def get_payments():
    mycursor.execute("SELECT * FROM payment")
    payments = mycursor.fetchall()
    payment_list = []
    for payment in payments:
        payment_dict = {'payment_id': payment[0], 'order_id': payment[1], 'payment_date': payment[2], 'amount': float(payment[3])}
        payment_list.append(payment_dict)
    return jsonify({"success": True, 'result': payment_list, 'msg': 'Payment list successfully returned'})

# API to get a single processed payment
@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    mycursor.execute("SELECT * FROM payment WHERE payment_id = %s", (payment_id,))
    payment = mycursor.fetchone()
    if payment:
        payment_dict = {'payment_id': payment[0], 'order_id': payment[1], 'payment_date': payment[2], 'amount': float(payment[3])}
        return jsonify({"success": True, 'result':payment_dict, 'msg': 'Payment info successfully returned'})
    else:
        return jsonify({"success": False, 'msg': 'Payment not found'})

# API to update the payment
@app.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    # Update payment in payments table
    sql_stmt = "UPDATE payment SET payment_date = %s, amount = %s WHERE payment_id = %s"
    sql_vals = (data['payment_date'], data['amount'], payment_id)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Payment updated'})


if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
