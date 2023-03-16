#Inventory MS

from flask import Flask, request, jsonify
import os, time, random, csv
import mysql.connector

# create a Flask instance
app.config['JSON_SORT_KEYS'] = False

# Connect to MySQL database
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="abc_msa"
)

mycursor = mydb.cursor()


service_name = "inventory_management"
service_descr = "ABC-MSA Inventory Management"
service_json = jsonify({"service_name":service_name, "service_descr":service_descr})

delay_cfg_filename = "ms_delays.cfg"

service_info =   """
<!DOCTYPE html>
<head>
   <title>INVENTORY MANAGEMENT Microservice</title>
</head>
<body>  
   <h3>Inventory Management Microservice Part of ABC-MSA System</h3>
</body>
                """

# curl http://localhost:8080/api?func=about
api_funcs = [
    "about",
    "service_info",
    "check_inventory",
    "update_inventory",
    "delay_response"
]

# The root / URL Route
# Returns an HTML with service info when service root is requested 
@app.route('/', methods=['GET'])

def simulate_delay():
    global delay_cfg_filename
    
    delay_min_sec = 0
    delay_max_sec = 0
    file_exists = os.path.isfile(delay_cfg_filename)
    if file_exists:
        #print("Found the delay cfg file, assigning delays...")
        with open(delay_cfg_filename, 'r') as f:
            delay_cfg = csv.reader(f)
            # The file should have only one row "delay_min_sec,delay_max_sec"
            for row in delay_cfg:
                delay_min_sec = float(row[0])
                delay_max_sec = float(row[1])
        #print("Delay min & max values = %s and %s" %(delay_min_sec, delay_max_sec))
    else:
        #print("Did NOT find the file delay cfg file, initiating...")
        f = open(delay_cfg_filename, "w")
        f.write("0,0")

    f.close()
        
    #Simulate a delay if received an API to do so
    if delay_max_sec > 0:
        delay_seconds = round(delay_min_sec + random.random()*(delay_max_sec-delay_min_sec), 3)
        #print("Adding a delay %s ..." %delay_seconds)
        time.sleep(delay_seconds)
        
    return ""

        
def about():    
    simulate_delay()
    return service_info

# The API '/api' URL Route with API functions
#############################################
# Returns an error message if wrong arguments are passed.
@app.route('/api', methods=['GET'])
def abc_msa():
    global delay_cfg_filename

    simulate_delay()
                
    # A def to return a json with an error message if API usage error is detected
    def usage_error(msg_details):
        error_message =  f"{request.args[0]} usage error"
        return jsonify({'success':False, 'msg': f"{error_message}: {msg_details}"}) 
    
    # Copy all API args into a new dict
    request_args = request.args

    def service_info():
        # returns a JSON with service information
        return service_json
    
    # Check if a valid API function has been called
    func_call = request_args['func']
    if not ( func_call in (api_funcs) ):
        #usage_error("Invalid API function called") 
        return jsonify({'success': False, 'msg': f"{request.args[0]}: Invalid API function called"}) 


##############################################
##### SIMULATE A RESPONSE DELAY API CALL #####
##############################################
    if func_call == "delay_response":
        delay_min_sec = round( int(request.args['delay_min']) / 1000, 3)
        delay_max_sec = round( int(request.args['delay_max']) / 1000, 3)

        f = open(delay_cfg_filename, "w")
        f.write("%s,%s" %(delay_min_sec, delay_max_sec) )
        f.close()
        
        return jsonify({'msg':"delay response assigned successfully"}) 
        
            
###########################
## service_info API CALL ##
###########################        
    if func_call == "service_info":    
        return service_info()
            

###########################
##### ABOUT API CALL  #####
###########################        
    if func_call == "about":
        return jsonify({"success": True, "developer_name":"Mohamed Osam", "version":"0.1"})


###########################
##### check_inventory ####
###########################        
    if func_call == "check_inventory":
        item_id = request.args['item_id']
        mycursor.execute("SELECT * FROM item WHERE item_id = %s", (item_id,))
        product = mycursor.fetchone()
        if product:
            product_dict = {'item_id': product[0], 'item_name': product[1], 'item_price': float(product[2]), 'item_descr': product[3], 'item_catalog_pic': product[4], 'item_stock_qty': product[5]}
            return jsonify({"success": True, 'result': product_dict, 'msg': 'Product info successfully returned'})    
        else:
            return jsonify({"success": False, 'msg': 'Product not found'})

    
    
###########################
##### update_inventory ####
###########################        
    if func_call == "update_inventory":
        data = request.get_json()
        # Update product in products table
        sql_stmt = "UPDATE item SET item_name = %s, item_price = %s, item_descr = %s, item_catalog_pic = %s, item_stock_qty = %s WHERE item_id = %s"
        sql_vals = (data['item_name'], data['item_price'], data['item_descr'], data['item_catalog_pic'], data['item_stock_qty'], item_id)
        mycursor.execute(sql_stmt, sql_vals)
        mydb.commit()
        return jsonify({"success": True, 'msg': 'Product updated successfully'})

    
    

    

if __name__ == "__main__":
        # for debugging locally
        # app.run(debug=True, host='0.0.0.0',port=8080)

        # for production
        app.run(host='0.0.0.0', port=8080)
