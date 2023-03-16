#ORDER MS

from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

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

service_name = "order"
service_descr = "ABC-MSA Order Management"
service_json = jsonify({"service_name":service_name, "service_descr":service_descr})

#!!! Configuration Params (to be part of a conf file later)
REQ_TIMEOUT = 5


#!!! Define the MS network location
inventory_ms_host = "localhost:8006"
payment_ms_host = "localhost:8009"

service_info =   """
<!DOCTYPE html>
<head>
   <title>ORDER MANAGEMENT Microservice</title>
</head>
<body>  
   <h3>Order Management Microservice Part of ABC-MSA System</h3>
</body>
                """

# The root / URL Route
# Returns an HTML with service info when service root is requested 
@app.route('/', methods=['GET'])
def about():
    return service_info

mysql = MySQL(app)


# An API to create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        # Parse the JSON request body
        order_data = request.json
        customer_id = order_data['customer_id']
        items = order_data['items']

        # Get the customer details from the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT customer_name, customer_email FROM customer WHERE customer_id = %s', (customer_id,))
        customer = cur.fetchone()
        if not customer:
            return jsonify({'error': 'Invalid customer ID'})

        # Insert the new order into the database
        cur.execute('INSERT INTO order (customer_id) VALUES (%s)', (customer_id,))
        order_id = cur.lastrowid

        # Insert the items into the order_item table
        for item in items:
            item_id = item['item_id']
            item_qty = item['item_qty']
            cur.execute('INSERT INTO order_item (order_id, item_id, item_qty) VALUES (%s, %s, %s)',
                        (order_id, item_id, item_qty))

            # Decrement the item stock quantity
            cur.execute('UPDATE item SET item_stock_qty = item_stock_qty - %s WHERE item_id = %s',
                        (item_qty, item_id))

        mysql.connection.commit()
        cur.close()

        # Return the new order ID
        return jsonify({'order_id': order_id})
    except Exception as e:
        return jsonify({'error': str(e)})


# Route to get an order by ID
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        # Get the order details from the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM order WHERE order_id = %s', (order_id,))
        order = cur.fetchone()
        if not order:
            return jsonify({'error': 'Invalid order ID'})

        # Get the customer details from the database
        customer_id = order['customer_id']
        cur.execute('SELECT customer_name, customer_email FROM customer WHERE customer_id = %s', (customer_id,))
        customer = cur.fetchone()

        # Get the items in the order from the database
        cur.execute('SELECT oi.item_id, i.item_name, i.item_price, oi.item_qty FROM order_item oi '
                    'INNER JOIN item i ON oi.item_id = i.item_id '
                    'WHERE oi.order_id = %s', (order_id,))
        items = cur.fetchall()

        cur.close()

        # Return the order details, customer details, and items
        return jsonify({
            'order_id': order['order_id'],
            'customer_name': customer['customer_name'],
            'customer_email': customer['customer_email'],
            'order_timestamp': order['order_timestamp'],
            'items': items
        })
    except Exception as e:
        return jsonify({'error': str(e)})


# Route to get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT o.order_id, o.order_timestamp, c.customer_name, c.customer_email FROM order o JOIN customer c ON o.customer_id = c.customer_id")
        data = cur.fetchall()
        cur.close()

        order_list = []
        for order in data:
            order_dict = {'order_id': order[0], 'order_timestamp': order[1], 'customer_name': order[2], 'customer_email': order[3]}
            order_list.append(order_dict)

        return jsonify(order_list)
    except Exception as e:
        return jsonify({'error': str(e)})
    

if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
