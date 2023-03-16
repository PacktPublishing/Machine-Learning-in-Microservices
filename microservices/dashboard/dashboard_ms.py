#Inventory MS

from flask import Flask, render_template, request, redirect, jsonify
import requests

# create a Flask instance
app.config['JSON_SORT_KEYS'] = False

# Product Management API endpoints
PRODUCTS_API = "http://localhost:8004/products"
PRODUCT_API = "http://localhost:8004/products/{}"

# Customer Management API endpoints
CUSTOMERS_API = "http://localhost:8003/customers"
CUSTOMER_API = "http://localhost:8003/customers/{}"

# Order Management API endpoints
ORDERS_API = "http://localhost:8005/orders"
ORDER_API = "http://localhost:8005/orders/{}"

# Payment Management API endpoints
PAYMENTS_API = "http://localhost:8009/payments"
PAYMENT_API = "http://localhost:8009/payments/{}"

# Inventory Management API endpoints
INVENTORY_API = "http://localhost:8006/inventory"
INVENTORY_ITEM_API = "http://localhost:8006/inventory/{}"


# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="abc_msa"
)

mycursor = mydb.cursor()

##############################
###### The root / URL Route points to the home page
@app.route('/')
def home():
    return render_template('index.html')

##############################
###### Product list page
@app.route('/products')
def products():
    response = requests.get(PRODUCTS_API)
    products = response.json()['products']
    return render_template('products.html', products=products)

##############################
###### Product detail page
@app.route('/products/<int:item_id>')
def product_detail(item_id):
    response = requests.get(PRODUCT_API.format(item_id))
    product = response.json()
    return render_template('product_detail.html', product=product)

##############################
###### Cart page
@app.route('/cart')
def cart():
    cart = request.cookies.get('cart')
    if cart:
        cart = [int(item) for item in cart.split(',')]
        products = []
        total_price = 0
        for item in cart:
            response = requests.get(PRODUCT_API.format(item))
            product = response.json()
            products.append(product)
            total_price += product['item_price']
        return render_template('cart.html', products=products, total_price=total_price)
    else:
        return render_template('cart.html')

    
##############################
###### Add product to cart
@app.route('/cart/add/<int:item_id>')
def add_to_cart(item_id):
    cart = request.cookies.get('cart')
    if cart:
        cart = cart + ',' + str(item_id)
    else:
        cart = str(item_id)
    response = redirect('/products')
    response.set_cookie('cart', cart)
    return response

##############################
###### Remove product from cart
@app.route('/cart/remove/<int:item_id>')
def remove_from_cart(item_id):
    cart = request.cookies.get('cart')
    if cart:
        cart_list = [int(item) for item in cart.split(',')]
        if id in cart_list:
            cart_list.remove(item_id)
        cart = ','.join(str(item) for item in cart_list)
        response = redirect('/cart')
        response.set_cookie('cart', cart)
        return response
    else:
        return redirect('/cart')

##############################
###### Checkout page
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Get form data
        customer_name = request.form['customer_name']
        customer_email = request.form['customer_email']
        customer_addr_st1 = request.form['customer_addr_st1']
        customer_addr_st2 = request.form['customer_addr_st2']
        customer_addr_city = request.form['customer_addr_city']
        customer_addr_state = request.form['customer_addr_state']
        customer_addr_zip = request.form['customer_addr_zip']
        customer_addr_country = request.form['customer_addr_country']

        # Create customer
        customer_data = {'customer_name': customer_name, 'customer_email': customer_email, 'customer_addr_st1': customer_addr_st1, 'customer_addr_st2': customer_addr_st2, 'customer_addr_city': customer_addr_city, 'customer_addr_state': customer_addr_state, 'customer_addr_zip': customer_addr_zip, 'customer_addr_country': customer_addr_country, 'customer_phone': customer_phone}
        response = requests.post(CUSTOMERS_API, json=customer_data)
        customer = response.json()

        # Create order
        cart = request.cookies.get('cart')
        cart_list = [int(item) for item in cart.split(',')]
        order_data = {'customer_id': customer['customer_id'], 'status': 'processing', 'total_price': 0}
        response = requests.post(ORDERS_API, json=order_data)
        order = response.json()

        # Add products to order
        total_price = 0
        for item in cart_list:
            response = requests.get(PRODUCT_API.format(item))
            product = response.json()
            order_item_data = {'order_id': order['order_id'], 'item_id': product['item_id'], 'quantity': 1, 'price': product['item_price']}
            response = requests.post(ORDER_API.format(order['order_id']), json=order_item_data)

            # Update inventory
            response = requests.get(INVENTORY_ITEM_API.format(product['item_id']))
            inventory_item = response.json()
            inventory_item['quantity'] -= 1
            response = requests.put(INVENTORY_ITEM_API.format(product['item_id']), json=inventory_item)

            total_price += product['item_price']

        # Update order total price
        order['total_price'] = total_price
        response = requests.put(ORDER_API.format(order['order_id']), json=order)

        # Process payment
        payment_data = {'customer_id': customer['customer_id'], 'order_id': order['order_id'], 'amount': total_price}
        response = requests.post(PAYMENTS_API, json=payment_data)

        # Clear cart
        response = redirect('/')
        response.delete_cookie('cart')
        return response

    else:
        cart = request.cookies.get('cart')
        if cart:
            cart_list = [int(item) for item in cart.split(',')]
            products = []
            total_price = 0
            for item in cart_list:
                response = requests.get(PRODUCT_API.format(item))
                product = response.json()
                products.append(product)
                total_price += product['item_price']
            return render_template('checkout.html', products=products, total_price=total_price)
        else:
            return redirect('/cart')


if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
