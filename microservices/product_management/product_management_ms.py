#Product Management MS

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

service_name = "product_management"
service_descr = "ABC-MSA Product Management"
service_json = jsonify({"service_name":service_name, "service_descr":service_descr})

service_info =   """
<!DOCTYPE html>
<head>
   <title>PRODUCT MANAGEMENT Microservice</title>
</head>
<body>  
   <h3>Product Management Microservice Part of ABC-MSA System</h3>
</body>
                """

# The root / URL Route
# Returns an HTML with service info when service root is requested 
@app.route('/', methods=['GET'])
def about():
    return service_info

# API to add a new product
@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    # Insert product into products table
    sql_stmt = "INSERT INTO item (item_name, item_price, item_descr, item_catalog_pic, item_stock_qty) VALUES (%s, %s, %s, %s, %s)"
    sql_vals = (data['item_name'], data['item_price'], data['item_descr'], data['item_catalog_pic'], data['item_stock_qty'])
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Product added successfully'})

# API to get all products
@app.route('/products', methods=['GET'])
def get_products():
    mycursor.execute("SELECT * FROM item")
    products = mycursor.fetchall()
    product_list = []
    for product in products:
        product_dict = {'item_id': product[0], 'item_name': product[1], 'item_price': float(product[2]), 'item_descr': product[3], 'item_catalog_pic': product[4], 'item_stock_qty': product[5]}
        product_list.append(product_dict)
    return jsonify({"success": True, 'result': product_list, 'msg': 'Product list successfully returned'})

# API to get a single product using product_id
@app.route('/products/<int:item_id>', methods=['GET'])
def get_product(item_id):
    mycursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
    product = mycursor.fetchone()
    if product:
        product_dict = {'item_id': product[0], 'item_name': product[1], 'item_price': float(product[2]), 'item_descr': product[3], 'item_catalog_pic': product[4], 'item_stock_qty': product[5]}
        return jsonify({"success": True, 'result': product_dict, 'msg': 'Product info successfully returned'})    
    else:
        return jsonify({"success": False, 'msg': 'Product not found'})

# API to update a product info
@app.route('/products/<int:item_id>', methods=['PUT'])
def update_product(item_id):
    data = request.get_json()
    # Update product in products table
    sql_stmt = "UPDATE item SET item_name = %s, item_price = %s, item_descr = %s, item_catalog_pic = %s, item_stock_qty = %s WHERE item_id = %s"
    sql_vals = (data['item_name'], data['item_price'], data['item_descr'], data['item_catalog_pic'], data['item_stock_qty'], item_id)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Product updated successfully'})

# API to delete a product
@app.route('/products/<int:item_id>', methods=['DELETE'])
def delete_product(item_id):
    # Delete product from products table
    sql_stmt = "DELETE FROM item WHERE item_id = %s"
    sql_vals = (item_id,)
    mycursor.execute(sql_stmt, sql_vals)
    mydb.commit()
    return jsonify({"success": True, 'msg': 'Product deleted successfully'})


if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
