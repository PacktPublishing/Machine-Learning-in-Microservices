#Customer Management MS

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

service_name = "customer_management"
service_descr = "ABC-MSA Customer Management"
service_json = jsonify({"service_name":service_name, "service_descr":service_descr})

service_info =   """
<!DOCTYPE html>
<head>
   <title>CUSTOMER MANAGEMENT Microservice</title>
</head>
<body>  
   <h3>Customer Management Microservice Part of ABC-MSA System</h3>
</body>
                """


# The root / URL Route
# Returns an HTML with service info when service root is requested 
@app.route('/', methods=['GET'])
def about():
    return service_info


# The API '/customer' URL Route with Customer Management API functions
######################################################################

# API to add a customer
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    sql_stmt = "INSERT INTO customer (customer_name, customer_email, customer_phone, customer_addr_st1, customer_addr_st2, customer_addr_city, customer_addr_state, customer_addr_zip, customer_addr_country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_vals = (data['customer_name'], data['customer_email'], data['customer_phone'], data['customer_addr_st1'], data['customer_addr_st2'], data['customer_addr_city'], data['customer_addr_state'], data['customer_addr_zip'], data['customer_addr_country'])
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Customer added successfully'})

# API to get all customers in the db
@app.route('/customers', methods=['GET'])
def get_customers():
    mycursor.execute("SELECT * FROM customer")
    customers = mycursor.fetchall()
    customer_list = []
    for customer in customers:
        customer_dict = {'customer_id': customer[0], 'customer_name': customer[1], 'customer_email': customer[2], 'customer_phone': customer[3], 'customer_addr_st1': customer[4], 'customer_addr_st2': customer[5], 'customer_addr_city': customer[6], 'customer_addr_state': customer[7], 'customer_addr_zip': customer[8], 'customer_addr_country': customer[9]}
        customer_list.append(customer_dict)
    return jsonify({"success": True, 'result': customer_list, 'msg': 'Customer list returned successfully'})

# API to get a specific customer info using customer_id
@app.route('/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    mycursor.execute("SELECT * FROM customer WHERE customer_id = %s", (customer_id,))
    customer = mycursor.fetchone()
    if customer:
        customer_dict = {'customer_id': customer[0], 'customer_name': customer[1], 'customer_email': customer[2], 'customer_phone': customer[3], 'customer_addr_st1': customer[4], 'customer_addr_st2': customer[5], 'customer_addr_city': customer[6], 'customer_addr_state': customer[7], 'customer_addr_zip': customer[8], 'customer_addr_country': customer[9]}
        return jsonify(customer_dict)
        return jsonify({"success": True, 'result': customer_dict, 'msg': 'Customer info returned successfully'})
    else:
        return jsonify({"success": False, 'msg': 'Customer not found'})

# API to update customer info
@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    data = request.get_json()
    sql_stmt = "UPDATE customer SET customer_name = %s, customer_email = %s, customer_phone = %s, customer_addr_st1 = %s, customer_addr_st2 = %s, customer_addr_city = %s, customer_addr_state = %s, customer_addr_zip = %s, customer_addr_country = %s WHERE customer_id = %s"
    sql_vals = (data['customer_name'], data['customer_email'], data['customer_phone'], data['customer_addr_st1'], data['customer_addr_st2'], data['customer_addr_city'], data['customer_addr_state'], data['customer_addr_zip'], data['customer_addr_country'], id)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Customer info updated successfully'})

# API to delete a customer
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    mycursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Customer successfully deleted'})


if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
